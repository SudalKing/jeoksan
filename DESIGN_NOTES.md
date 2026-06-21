# 작성자

- 지원자 성명: 이정민
- Git profile URL: https://github.com/SudalKing

# 설계 노트

> 구현의 핵심 설계 판단을 기록하는 문서입니다. 코드만으로는 드러나지 않는 **"왜 그렇게 했는가"** 를 남겨 주세요.
> - 분량·형식은 자유입니다. 아래 항목은 출발점일 뿐이며, 필요에 따라 더하거나 빼도 됩니다.
> - 코드에 대한 설명 보다는 시스템 설계과정에 대한 서사를 기술해 주세요.

## 0. 리뷰어에게 전달 할 사항

- 현재 시점: **필수 기능(ETL + 조회/검색 API + 코드 구조)만 구현 완료**된 상태입니다.
- 보너스는 `외부 단가 수집(1)`, `시점/버전 관리(2)`, `데이터 품질/이상치 탐지(4)`를 선택했고, 자유제안으로 `단가 변동 이력 조회 API`를 추가할 예정이며 필수 구현이 끝난 뒤 순서대로 진행합니다. 본 문서는 진행 단계마다 갱신합니다.
- 기술스택: Python 3.9, FastAPI, SQLAlchemy 2.0, PostgreSQL, Alembic, Podman. 미들웨어(DB)부터 애플리케이션까지 모두 컨테이너화했으며 추후 추가되는 모든 미들웨어도 컨테이너화 할 예정입니다.

## 1. 도메인·요구사항 분석

`DOMAIN.md`를 따라 다음 순서를 확인했습니다.

```
공종(work_type) → 분류 계층 5단계(level1~5) → 산출항목(item, 계층 말단) → 표준시장단가(시점별)
```

- `construction_classification`과 `std_market_price`는 둘 다 조달청 원천이지만 별개 소스이며 `산출항목코드`(qtyCalcCtyclcd)로 연결되는 것으로 추정되나, `DATA_SCHEMA.md`에서 코드 공백 행, 양쪽 중 한쪽에만 존재하는 코드 존재한다는 점에서 보장된 FK 관계가 아니라 느슨하게 연결되는 두 마스터/이력 데이터라고 판단했습니다.
- 시스템이 제공해야 하는 핵심 기능은 "분류 계층을 타고 내려가며 산출항목을 찾고, 그 산출항목의 표준시장단가를 확인하는 것"을 목표로 했습니다.
- 단가는 "현재 값 하나"가 아니라 "공시 시점마다 새로 발표되는 값"이라는 점에서, 단가 데이터를 덮어쓰는 갱신형이 아니라 누적형 이력 데이터로 모델링했습니다.

## 2. 데이터 분석

`DATA_SCHEMA.md`에 명시된 원본 데이터의 특이사항과 실제 처리 방침:

| 이슈                                     | 분석                                                                         | 처리 방침                                                                                      |
|----------------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| 단위 표기 불일치 (`m`/`M`, `m^2`/`M^2`, 공백 등) | 같은 의미의 단위가 시스템·입력자에 따라 다르게 표기된 전형적인 마스터데이터 오염                              | `unit_alias` 사전 테이블로 매핑, raw 값은 보존하고 canonical 값을 별도 컬럼에 저장                                |
| `qtyCalcCtyclcd` 공백 행                  | 분류 체계상 말단이 아닌 중간 행 또는 결측치로 추정                                              | 코드 없는 행은 분류·산출항목으로서 식별 불가능하므로 적재 제외, 건수는 ETL 로그로 추적                                        |
| 두 파일 간 코드 불일치                          | classification에만 있는 코드 → 단가 미발표 산출항목<br/>price에만 있는 코드 → 분류 체계 변경/누락으로 인한 고아 단가 | API 응답에서는 전자를 `has_price=false`로, 후자는 일단 적재는 허용하되 DB 레벨 FK 제약은 걸지 않음 |
| 단가 미입력 항목                              | 재료비/노무비/경비 모두 NULL인 경우 존재                                                  | NULL 허용 컬럼으로 두고, API에서 `has_price` 플래그로 명시                                                 |

## 3. 정규화 방침

**핵심 결정: 5단계 분류 계층을 별도 정규화 테이블로 쪼개지 않고, `classification` 단일 테이블에 컬럼으로 비정규화했습니다.**

**판단 근거**
- 분류 깊이가 5단계로 고정되어 있어, 가변 깊이 트리에 쓰이는 정규화의 이점이 약하다고 판단, 고정 깊이에 정규화를 적용하면 매 조회마다 5단계 self-join이 필요해 조회 비용이 크다고 판단
- 분류 코드/명/설명은 산출항목과 항상 1:1이며, 분류만 단독으로 CRUD되는 요구사항이 없음 → update anomaly 위험이 낮음
- 필수 API의 핵심 동작이 "5단계 필터 + 키워드 검색"이라, 평탄화 테이블이 인덱스 설계와 쿼리 단순성 측면에서 유리함

**이 설계가 깨지는 시점**
- 분류 체계 자체가 시점에 따라 개정되어, 같은 산출항목이 다른 상위 분류로 재배치될 때 → 분류를 시간 축을 가진 독립 엔티티로 승격해야 함
- 분류 계층 자체에 메타데이터(담당 부서, 적용 룰 등)가 붙기 시작할 때 → 분류가 더는 단순 라벨이 아니므로 정규화 필요
- 계층 깊이가 가변적으로 운영될 때 → 컬럼 펼치기 자체가 불가능, 인접 리스트/closure table 등으로 전환 필요
- 분류만 단독으로 관리하는 어드민 기능이 생길 때 → 평탄화 테이블은 N개 행을 동시에 고쳐야 하는 실질적 update anomaly가 발생

반대로 단위(unit)는 별도 사전 테이블(`unit_alias`)로 정규화했습니다. 이건 분류와 달리, 표기가 계속 늘어날 수 있는 "값 사전" 성격이라 별도 테이블로 관리해야 신규 표기 대응이 코드 변경 없이 데이터 추가로 끝납니다.

## 4. DB 스키마 설계

외부 API 컬럼명을 그대로 쓰지 않고 내부 컨벤션(`snake_case`, 풀네임)으로 번역했습니다. 외부 식별자 값은 보존하되 컬럼명은 우리 도메인 언어를 따르도록 해, 외부 소스가 바뀌어도 ETL 매핑 레이어만 교체하면 되도록 분리했습니다.

```
classification                              std_market_price (append-only)
├ item_code (PK)                 ←───       ├ id (PK)
├ work_type_code/name                       ├ item_code (FK 제약 없음, 고아 허용)
├ level1~5_code/name/description            ├ work_type_code/name
├ item_name                                 ├ product_name, spec
├ spec, raw_unit, canonical_unit            ├ raw_unit, canonical_unit
├ created_at, updated_at                    ├ material_cost / labor_cost / expense_cost
                                            ├ published_date, price_condition_note
                                            ├ created_at
                                            └ unique(item_code, published_date)

unit_alias
├ raw_unit (PK)
├ canonical_unit
└ created_at
```

- `std_market_price.item_code`에 DB 레벨 FK를 걸지 않은 것은 의도적인 선택입니다 — 원본 데이터에 고아 단가가 실재하는데 FK 제약을 걸면 그 행들이 적재 자체가 안 되어 데이터 손실이 발생합니다. 대신 인덱스만 걸어 조회 성능은 유지합니다.
- `unique(item_code, published_date)`로 같은 시점에 같은 산출항목 단가가 중복 적재되는 것을 막고, 동시에 ETL 재실행 시 upsert 키로 사용해 멱등성을 보장합니다.

## 5. 아키텍처·코드 구조

```
app/
├── core/          공통 관심사 (config, db session, 공통 응답 포맷)
├── models/        SQLAlchemy ORM — DB 테이블 매핑 (영속성 계층)
├── schemas/       Pydantic — API 요청/응답 DTO (DB 모델과 독립)
├── repository/    쿼리 캡슐화 — 비즈니스 로직 없음
├── services/      비즈니스 로직 — repository 결과를 schema로 가공
├── api/routes/    FastAPI 라우터 — HTTP 계층
└── main.py        앱 엔트리포인트

etl/               app과 분리된 별도 패키지 — 적재 전용 (extract → normalize → load → run)
alembic/           스키마 마이그레이션 이력
```

- `etl/`을 `app/`과 완전히 분리한 이유: ETL은 API 서버 프로세스와 무관하게 배치로 실행되는 별도 프로세스로 같은 패키지에 두면 책임의 경계가 모호해집니다. `app.models`만 공유하고 나머지는 독립적입니다.

## 6. 시스템의 한계와 확장 전략

- **분류 계층이 정적이라는 가정에 의존**: 3장에서 다룬 비정규화는 분류 체계가 자주 바뀌지 않는다는 전제 위에 있습니다. 조달청이 분류를 개정하면 즉각적인 스키마 변경이 필요합니다.
- **검색이 `ILIKE` 기반**: 산출항목명 키워드 검색이 현재 단순 `ILIKE '%keyword%'`라 데이터/트래픽이 커지면 풀텍스트 인덱스 또는 검색 전용 엔진으로 이전이 필요합니다.

## 7. 보너스 과제 설계안

(필수 구현 완료 후 순서대로 진행 예정)

- [x] 1: 외부 단가 수집 파이프라인 (설계)
- [x] 2: 시점/버전 관리 (구현)
- [x] 3: 검색/조회 성능과 확장 (설계)
- [x] 4: 데이터 품질/이상치 탐지 (설계)
- [ ] 자유제안: 단가 변동 이력/추이 조회 API

### 보너스 1. 외부 단가 수집 파이프라인 (설계)

#### 배경 및 목표

현재 ETL은 GCS에 올려둔 스냅샷 파일을 1회성으로 적재하는 방식입니다. <br>
조달청 나라장터 OpenAPI(https://www.data.go.kr/data/15129415/openapi.do)를 주기적으로 호출해 새로운 공시 단가를 자동으로 수집·적재하는 파이프라인을 설계합니다.

#### 관련 외부 API 엔드포인트

전체 API 목록 중 본 시스템의 스코프에 해당하는 엔드포인트는 두 개로 파악했습니다.

| 엔드포인트 | 용도 | 현재 매핑 |
|---|---|---|
| `GET /getStdMarkUprcinfoList` | 표준시장단가 수집 | `std_market_price` 테이블 |
| `GET /getCnsttyClsfcInfoList` | 공종분류 카탈로그 수집 | `classification` 테이블 |

나머지(시설공통자재, 시장시공가격 등)는 다른 가격 유형으로 현재 과제 범위 밖이라고 판단했습니다.

#### 수집 주기

표준시장단가는 매년 상·하반기 2회 공시(공시일자 `pblctDate` 기준)됩니다. 따라서 일 1회 새벽 배치로 수집하면 충분합니다. 
<br> 분 단위 폴링은 불필요하며 API 할당량 낭비라고 생각했습니다..

> 가정 시나리오: 일 1회 새벽 2시 배치 실행, 타임아웃 30초 ~ 1분(운영하며 변경 가능), 최대 3회 재시도

#### 증분 수집 전략

매 실행마다 전체를 재수집하면 API 할당량 소진과 중복 적재 부담이 있어 아래 방식으로 증분 수집합니다.

```
1. DB에서 현재 적재된 MAX(published_date) 조회
2. API 호출 시 해당 날짜 이후 데이터만 요청 (조달청 API의 날짜 필터 파라미터 활용)
3. 응답이 비어있으면 새 공시 없음 → 적재 스킵
4. 응답이 있으면 기존 load_price() 재사용해 upsert 적재
```

이미 `std_market_price`가 `unique(item_code, published_date)` 기반 upsert로 설계되어 있으므로, 중복 실행해도 멱등성이 보장됩니다.

#### 파이프라인 흐름

```
[조달청 OpenAPI]
      ↓ HTTP GET (증분 날짜 필터, API 키)
[etl/fetch_price.py] ← 신규 추가될 모듈
  - 페이지네이션 처리 (numOfRows / pageNo)
  - 응답 파싱 → 기존 load_price()와 동일한 dict 형태로 변환
      ↓
[etl/load_price.py] ← 기존 재사용
  - publication upsert
  - std_market_price upsert
      ↓
    [DB]
```

기존 `load_price()`를 그대로 재사용할 수 있도록 `fetch_price.py`의 출력 포맷을 `std_market_price.jsonl`의 레코드 구조와 동일하게 맞춰, 소스가 파일이든 API든 적재 로직을 바꾸지 않아도 되도록 합니다.

#### 실패/재시도 처리

| 상황 | 처리 방침 |
|----|---|
| API 타임아웃 / 5xx | 지수 백오프(1초 → 2초 → 4초) 후 최대 3회 재시도 |
| 4xx (인증 오류 등 클라이언트 에러) | 재시도 없이 즉시 실패 처리, 알림 발송 |
| 부분 성공 (N페이지 중 일부 실패) | 실패 페이지 번호를 로그에 기록, 다음 배치에서 해당 구간부터 재시도 |
| API 할당량 초과 | 당일 수집 중단, 익일 재시도 |

#### 이 설계가 깨지는 시점

- 조달청이 API 스펙(파라미터명, 응답 구조)을 변경하면 `fetch_price.py`의 파싱 로직 수정 필요
- 공시 주기가 월 단위처럼 잦아지면 배치 주기 조정 필요
- 단가 외 다른 데이터(자재 관련 등)를 추가 수집해야 할 경우, 엔드포인트별 파서를 별도로 만들어야 하므로 `fetch_price.py`의 책임을 분리하여 소스별 fetcher 클래스로 분리 검토 필요

### 보너스 2. 시점/버전 관리 (구현)

#### 배경

표준시장단가는 매 공시마다 새 값이 발표됩니다. "지금 단가"뿐 아니라 "특정 시점의 단가"를 조회할 수 있어야 하며, 새 공시가 들어와도 과거 이력이 사라지면 안 됩니다.

#### 핵심 결정 1 — Append-Only 적재

`std_market_price`는 `UPDATE` 없이 공시마다 새 행을 쌓는 Append-Only 테이블로 설계했습니다.

**판단 근거**: 단가 데이터는 회계·견적 근거로 사용됩니다. 이전 시점의 단가를 덮어쓰면 "그 시점에 얼마였는가"를 소급해서 답할 수 없습니다. `unique(item_code, published_date)` 제약으로 같은 시점·같은 항목의 중복 행만 차단하고, ETL 재실행 시에는 upsert로 멱등성을 보장합니다.

**이 설계가 깨지는 시점**: 단가 수정 공고가 발생할 경우(예: 오류 정정) — 현재 설계에서는 동일 `published_date`의 행을 upsert로 덮어쓰므로 정정 데이터 재적재는 가능하나, "정정 전 원본"을 별도로 보존하려면 버전 컬럼이나 별도 이력 테이블이 필요합니다.

#### 핵심 결정 2 — `publication` 테이블을 독립 엔티티로

공시 날짜를 `std_market_price`의 컬럼으로만 두지 않고 `publication` 테이블로 독립시켰습니다.

```
publication
├ published_date (PK)
├ description (공시 조건 설명)
└ created_at
```

**판단 근거**: `publication_date` 컬럼만 있으면 "어떤 공시가 존재하는가"를 알려면 `std_market_price`를 GROUP BY해야 합니다. `publication`을 독립 엔티티로 두면 공시 목록 조회(`GET /publication`)가 단순 SELECT가 되고, 향후 공시별 다양한 메타데이터를 붙일 수 있는 확장점이 됩니다.

ETL에서 단가를 적재하기 전에 `publication`을 먼저 upsert해 공시 엔티티를 선행 보장합니다.

#### 핵심 결정 3 — `as_of` 파라미터와 쿼리 설계

`GET /quantity-item?as_of=2024-06-30` 형태로 특정 시점의 단가를 조회합니다.

쿼리는 중첩 서브쿼리 2단계로 구성했습니다.

```sql
-- 1단계: as_of 이하의 최신 공시일 per item_code
WITH latest AS (
    SELECT item_code, MAX(published_date) AS max_date
    FROM std_market_price
    WHERE published_date <= :as_of        -- as_of 없으면 조건 제거
    GROUP BY item_code
)
-- 2단계: 그 시점의 실제 단가 행
, latest_price AS (
    SELECT p.*
    FROM std_market_price p
    JOIN latest ON p.item_code = latest.item_code
               AND p.published_date = latest.max_date
)
-- 3단계: classification과 LEFT JOIN
SELECT c.*, lp.material_cost, lp.labor_cost, lp.expense_cost, lp.published_date
FROM classification c
LEFT JOIN latest_price lp ON c.item_code = lp.item_code
```

`as_of` 없이 호출하면 1단계 WHERE 조건이 제거되어 "현재 시점 최신 단가"를 반환합니다. 동일한 쿼리 구조로 두 케이스를 모두 처리합니다.

---

### 보너스 3. 검색/조회 성능과 확장 (설계)

#### 배경 및 가정 시나리오

> 산출항목 10만 건, DAU 1,000명, 피크 100 req/s, p99 응답시간 목표 200ms

현재 시스템은 소규모 적재 데이터에 단순 LIKE 검색으로 동작합니다. 데이터·트래픽이 커지면 병목이 되는 지점을 단계별로 짚고, 각 단계에서 취할 수 있는 가장 비용 효율적인 대응을 설계합니다.

#### 현재 인덱스 전략과 한계

| 인덱스 | 위치 | 효과 |
|---|---|---|
| 복합 인덱스 `(work_type_code, level1_code, …, level5_code)` | classification | 분류 계층 필터 쿼리에서 인덱스 스캔 |
| 단일 인덱스 `(item_name)` | classification | 정확 일치 조회에는 유효, `LIKE '%keyword%'`는 무효 |
| 유니크 인덱스 `(item_code, published_date)` | std_market_price | 단가 조회·upsert 키 |

핵심 병목: `LIKE '%keyword%'` 쿼리는 앞에 `%`가 붙으면 B-tree 인덱스를 타지 못해 전체 행 순차 스캔으로 처리됩니다. 데이터가 10만 건을 넘기 시작하면 응답 시간이 선형으로 증가할 것으로 예상됩니다.

#### 단계별 확장 전략

**1단계 — PostgreSQL 내에서 해결 (데이터 10만 건, req/s 100 이하)**

- `pg_trgm` 익스텐션을 활성화하고 `item_name`에 GIN 트라이그램 인덱스를 추가합니다.

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX ix_classification_item_name_trgm
    ON classification USING GIN (item_name gin_trgm_ops);
```

트라이그램 인덱스는 `LIKE '%keyword%'` 패턴도 인덱스를 활용할 수 있어, 추가 인프라 없이 검색 성능을 개선할 수 있습니다.

**2단계 — 읽기 캐시 도입 (req/s 300 이상)**

분류 계층 트리와 최신 단가처럼 자주 조회되지만 변경이 드문 데이터는 Redis/ValKey 등에 캐싱합니다.

| 캐시 대상 | TTL | 무효화 트리거 |
|---|---|---|
| 분류 전체 트리 | 1시간 | ETL 완료 후 캐시 삭제 이벤트 |
| 최신 단가 목록 | 30분 | 새 공시 적재 후 해당 item_code 캐시 삭제 |


캐시 전략은 Write-Around(ETL이 직접 캐시에 쓰지 않고, 다음 조회 시 채워지는 방식)로 운영합니다. ETL 완료 후 `CACHE_INVALIDATE` 이벤트로 관련 키를 삭제하고, 첫 조회가 들어올 때 DB를 읽어 캐시에 채우는 Lazy Loading 방식입니다.

**3단계 — 검색 전용 엔진 분리 (키워드 검색 req/s 500 이상 또는 복합 검색어 지원 필요 시)**

PostgreSQL LIKE로 커버하기 어려운 요구사항이 생기면 ElasticSearch/OpenSearch로 검색 레이어를 분리합니다.

- 분류명, 품명, 규격을 복합 필드로 색인하면 오타 허용 검색(fuzzy), 형태소 분석 기반 검색이 가능해집니다.
- ETL 완료 시점에 ES에도 문서를 색인하는 방식을 사용합니다.
- 단, ES 도입은 운영 복잡도(스키마 마이그레이션, 인덱스 재구축, 데이터 동기화, 모니터링 등)가 크게 올라가므로, 1·2단계로 해결이 안 될 때 선택합니다.

**4단계 — DB Read Replica (DB CPU가 병목)**

단가 이력 조회나 집계 쿼리처럼 무거운 읽기 요청이 늘면 Read Replica를 추가합니다. 쓰기(ETL)는 Primary, API 읽기는 Replica로 라우팅합니다. SQLAlchemy의 `Engine` 레벨에서 라우팅 전략을 주입하면 서비스 코드 변경 없이 대응할 수 있습니다.

#### 이 설계가 깨지는 시점

- 검색 요구사항이 "같은 의미의 유사어 검색"(예: "포장" → "아스팔트 덧씌우기")처럼 시맨틱 검색 수준으로 올라가면 트라이그램 인덱스로 커버할 수 없어 벡터 검색(임베딩 + pgvector 또는 ES KNN) 레이어가 필요합니다.
- 단가 이력 데이터가 수천만 건을 넘어서면 `std_market_price` 테이블을 `published_date` 기준으로 일별/월별/연별 파티셔닝을 검토해야 합니다.

---

### 보너스 4. 데이터 품질/이상치 탐지 (설계)

#### 배경

현재 ETL은 데이터를 적재할 때 파싱 불가 행만 `skipped` 카운트를 기록하고 나머지는 모두 그대로 넣습니다. 원천 데이터의 품질 문제를 가시화하고 운영 중 이상 징후를 포착하기 위한 체계가 없는 상태입니다.

#### 탐지할 이슈 유형

| issue_type | 탐지 기준 | 임계치/기준값 |
|---|---|---|
| `missing_item_code` | classification 행의 `qtyCalcCtyclcd`가 공백·NULL | 해당 행 적재 제외 |
| `orphan_price` | `std_market_price.item_code`가 `classification`에 없는 경우 | 전체 적재 후 SQL 집합 연산 |
| `unmapped_unit` | `raw_unit` 값이 `unit_alias` 테이블에 없는 경우 | 전체 적재 후 SQL 집합 연산 |
| `price_outlier` | 전 공시 시점 대비 단가 변동률이 임계치 초과 | ±50% (운영하며 조정) |

> **임계치 근거**: 표준시장단가는 반기별 공시로, 물가 상승률·인건비 변동을 감안해도 반기 50% 초과는 통상적으로 데이터 오류이거나 품목 자체의 대체/삭제를 의미할 가능성이 높다고 판단했습니다. 운영해보며 데이터 축적 후 히스토그램을 보고 조정할 수 있습니다.

#### 스키마 설계

```
etl_run                             data_quality_issue
├ id (PK)                     ←──   ├ id (PK)
├ source (varchar)                  ├ etl_run_id (FK)
├ status (running/success/failed)   ├ issue_type (varchar)
├ inserted_count                    ├ target_code (item_code 또는 raw_unit 등)
├ skipped_count                     ├ detail (text — 상세 내용)
├ started_at                        └ detected_at
└ finished_at
```

`etl_run`은 ETL 실행 단위를 추적합니다. 어떤 실행에서 어떤 이슈가 발생했는지를 연결할 수 있어, "이번 배치에서 새로 발생한 이슈"와 "이전부터 있던 이슈"를 구분할 수 있습니다.

#### 처리 방침

탐지된 이상 데이터를 **적재 차단하지 않고 기록 후 허용** 합니다.

- **이유**: 원천 데이터가 공공 OpenAPI이기 때문에 우리에게 수정 권한이 없습니다. 차단하면 데이터 손실이 발생하고, 이상 데이터도 이력 관점에서 보존 가치가 있을 수 있습니다.
- 대신 API를 통해 운영자가 현황을 조회하고 판단할 수 있도록 합니다.
- 심각도가 높은 이슈에 대해서는 향후 Slack 알림 등 외부 알림 채널을 연결하는 확장을 고려할 수 있습니다.

#### 이 설계가 깨지는 시점

- 품질 기준이 항목 유형별로 달라져야 하면(예: 토목은 ±30%, 전기는 ±70%) `issue_type`별 임계치 테이블을 별도로 관리해야 합니다.
- 이상 감지 결과를 단순 조회가 아니라 "승인/반려" 워크플로우로 처리해야 하면 `data_quality_issue`에 `status`, `reviewer`, `resolved_at` 컬럼이 추가되는 형태로 확장합니다.

---

## 8. AI 활용

- 도메인/데이터 분석, DB 정규화 방침, 코드 레이어 구조에 대한 설계 논의를 제가 먼저 설계를 제안하면 AI가 리뷰하는 방식으로 진행했습니다. AI가 제시한 옵션을 그대로 받아들이지는 않고, 실제로 깨지는 조건이 있는가를 기준으로 검증해 채택/기각했습니다.

**분류 테이블 정규화/비정규화 선택 — 내 설계와 다른 AI의 제안을 받아들이면서, "언제 깨지는가"를 추가로 요구해 설계의 한계를 명시**

```
Q: 난 분류 테이블을 정규화 하는게 더 나을 것 같아 보이는데 어때?

A: 현재 상황에서 비정규화(평탄화)가 낫습니다. 5단계 깊이가 고정이고, 분류가 산출항목과
   항상 1:1로 동행해 update anomaly 위험이 낮으며, 필수 API가
   필터+키워드 검색이라 평탄화가 인덱스/쿼리 측면에서 유리합니다.


Q: 그러면 비정규화의 설계가 깨지게 되는 한계 상황은 언제일까?

A: 분류 체계 자체가 시점별로 개정될 때, 분류에 독립 메타데이터가 붙을 때, 
   계층 깊이가 가변적으로 바뀔 때, 분류 단독 CRUD 어드민 기능이 생길 때입니다.
```
→ "지금 과제 스코프에서는 이 깨지는 조건이 해당되지 않는다"는 점을 직접 확인한 뒤 AI의 리뷰를 받아들여 비정규화로 확정했습니다.


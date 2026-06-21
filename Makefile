# 제출물 실행용 Makefile
#
# make setup  →  make run  →  make down

COMPOSE = python3 -m podman_compose -f podman-compose.yml

.PHONY: setup run down

# 환경 구성: podman 머신 기동, 의존성 설치, 데이터 다운로드, 이미지 빌드, DB 마이그레이션/ETL
setup:
	python3 -m pip install --quiet podman-compose
	-podman machine init 2>/dev/null
	podman machine start 2>/dev/null || true
	mkdir -p data
	test -f data/construction_classification.jsonl || curl -sf -o data/construction_classification.jsonl \
		https://storage.googleapis.com/timwork-hiring-data/construction-price/construction_classification.jsonl
	test -f data/std_market_price.jsonl || curl -sf -o data/std_market_price.jsonl \
		https://storage.googleapis.com/timwork-hiring-data/construction-price/std_market_price.jsonl
	$(COMPOSE) build
	$(COMPOSE) up -d db
	$(COMPOSE) run --rm app alembic upgrade head
	$(COMPOSE) run --rm -v $(PWD)/data:/srv/data app python -m etl.run
	$(COMPOSE) down

# 앱 실행: 서버 기동 (완료 후 http://localhost:8080 에서 API 응답)
run:
	$(COMPOSE) up -d

# 리소스 정리: 컨테이너·볼륨·임시 파일 등 실행에 사용한 모든 리소스 정리
down:
	$(COMPOSE) down -v

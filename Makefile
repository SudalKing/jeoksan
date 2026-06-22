# 제출물 실행용 Makefile
#
# make setup  →  make run  →  make down

COMPOSE = docker compose -f docker-compose.yml

.PHONY: setup run down

# 환경 구성: podman 머신 기동, 의존성 설치, 데이터 다운로드, 이미지 빌드, DB 마이그레이션/ETL
setup:
	@docker info >/dev/null 2>&1 || { \
  		echo "Docker daemon이 실행되고 있지 않습니다."; \
  		echo "Docker desktop을 실행한 뒤 다시 시도해주세요."; \
  		exit 1; \
  	}
	mkdir -p data
	test -f data/construction_classification.jsonl || curl -sf -o data/construction_classification.jsonl \
		https://storage.googleapis.com/timwork-hiring-data/construction-price/construction_classification.jsonl
	test -f data/std_market_price.jsonl || curl -sf -o data/std_market_price.jsonl \
		https://storage.googleapis.com/timwork-hiring-data/construction-price/std_market_price.jsonl
	$(COMPOSE) build
	$(COMPOSE) up -d db
	$(COMPOSE) run --rm app alembic upgrade head
	$(COMPOSE) run --rm -v $(PWD)/data:/srv/data app python -m etl.run
	$(COMPOSE) stop db && $(COMPOSE) rm -f db 2>/dev/null || true

# 앱 실행: 서버 기동 (완료 후 http://localhost:8080 에서 API 응답)
run:
	@docker info >/dev/null 2>&1 || { \
  		echo "Docker daemon이 실행되고 있지 않습니다."; \
  		echo "Docker desktop을 실행한 뒤 다시 시도해주세요."; \
  		exit 1; \
  	}
	$(COMPOSE) up -d

# 리소스 정리: 컨테이너·볼륨·로컬 빌드 이미지 등 실행에 사용한 모든 리소스 정리
# docker pull한 이미지는 일부러 지우지 않도록 했습니다.
down:
	$(COMPOSE) down -v --rmi local

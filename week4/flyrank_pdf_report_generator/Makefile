.PHONY: up down logs test lint seed schedule clean

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api worker

test:
	pytest

lint:
	ruff check .

seed:
	docker compose exec api python scripts/seed.py --count 60

schedule:
	docker compose --profile schedule up --build

clean:
	docker compose down -v
	rm -f artifacts/*.pdf report_generator.db test_report_generator.db

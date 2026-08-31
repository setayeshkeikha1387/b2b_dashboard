.PHONY: help up down build logs migrate makemigrations superuser seed \
        shell test lint fmt clean

help:
	@echo "B2B Dashboard — common commands"
	@echo "  make up               Start the app + database"
	@echo "  make down             Stop everything"
	@echo "  make build            Rebuild the image"
	@echo "  make logs             Tail logs"
	@echo "  make migrate          Apply migrations"
	@echo "  make makemigrations   Generate new migrations"
	@echo "  make superuser        Create a Django superuser"
	@echo "  make seed             Load demo data (business units, risks, tasks)"
	@echo "  make shell            Open a Django management shell"
	@echo "  make test             Run the test suite (pytest)"
	@echo "  make lint             Run flake8"
	@echo "  make fmt              Run black"
	@echo "  make clean            Remove containers and volumes"

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

superuser:
	docker compose exec web python manage.py createsuperuser

seed:
	docker compose exec web python manage.py seed_demo_data

shell:
	docker compose exec web python manage.py shell

test:
	pytest

lint:
	flake8 apps config

fmt:
	black apps config

clean:
	docker compose down -v --remove-orphans

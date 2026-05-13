.PHONY: setup test build up down clean help

# Variables
DOCKER_COMPOSE = docker-compose

help:
	@echo "Sentinel Orchestrator Management Commands:"
	@echo "  setup   - Install dependencies for backend and frontend"
	@echo "  test    - Run backend tests"
	@echo "  build   - Build Docker containers"
	@echo "  up      - Spin up the entire stack with Docker"
	@echo "  down    - Stop and remove Docker containers"
	@echo "  clean   - Remove local databases, caches, and logs"

setup:
	@echo "Setting up backend..."
	cd backend && python -m venv .venv && .venv/Scripts/activate && pip install -r requirements.txt
	@echo "Setting up frontend..."
	cd frontend && npm install

test:
	python -m pytest backend/tests.py -v

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up

down:
	$(DOCKER_COMPOSE) down

clean:
	@echo "Cleaning up..."
	rm -rf backend/__pycache__
	rm -rf backend/.pytest_cache
	rm -f backend/traces.sqlite3
	rm -f backend/checkpoints.sqlite
	rm -rf backend/chroma_db
	rm -rf frontend/.next

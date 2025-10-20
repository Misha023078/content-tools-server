.PHONY: init migrate run scheduler test clean

# Initialize the project
init:
	@echo "Initializing content-tools-server..."
	@if [ ! -f .env ]; then cp env.example .env; echo "Created .env from template"; fi
	@if [ ! -f config.yaml ]; then cp config.yaml.example config.yaml; echo "Created config.yaml from template"; fi
	@echo "Please edit .env and config.yaml with your configuration"

# Run database migrations
migrate:
	@echo "Running database migrations..."
	docker-compose exec app alembic upgrade head

# Run the application
run:
	@echo "Starting content-tools-server..."
	docker-compose up -d --build

# Run only the scheduler
scheduler:
	@echo "Starting scheduler..."
	docker-compose up -d scheduler

# Run tests
test:
	@echo "Running tests..."
	docker-compose exec app python -m pytest tests/ -v

# Clean up containers and volumes
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f

# Show logs
logs:
	docker-compose logs -f

# Import sources from Excel
import-sources:
	@echo "Importing sources from Excel..."
	docker-compose exec app python tools/import_sources.py tools/sources_template.xlsx

# Manual triggers
trigger-ingest:
	@echo "Triggering RSS ingest..."
	curl -X POST http://localhost:8000/run/ingest

trigger-transform:
	@echo "Triggering NLP transform..."
	curl -X POST http://localhost:8000/run/transform

trigger-publish:
	@echo "Triggering publish..."
	curl -X POST http://localhost:8000/run/publish

# Health check
health:
	@echo "Checking application health..."
	curl http://localhost:8000/health

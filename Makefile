.PHONY: build run clean test migrate

# Build all services
build:
	@echo "Building Docker images..."
	docker-compose build

# Run the entire stack
run:
	@echo "Starting patient dashboard stack..."
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Running database migrations..."
	docker-compose exec api python scripts/migrate_users.py
	docker-compose exec api python scripts/migrate_patients.py
	docker-compose exec api python scripts/migrate_questions_schema.py
	docker-compose exec api python scripts/migrate_forms.py
	@echo "Patient Dashboard is running!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Documentation: http://localhost:8000/docs"

# Stop and remove containers
clean:
	@echo "Stopping and removing containers..."
	docker-compose down
	@echo "Removing volumes..."
	docker-compose down -v
	@echo "Removing images..."
	docker-compose down --rmi all

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && poetry install && poetry run pytest
	@echo "Running frontend tests..."
	cd frontend && npm test -- --watchAll=false

# Run database migrations
migrate:
	@echo "Running database migrations..."
	docker-compose exec api python scripts/migrate_users.py
	docker-compose exec api python scripts/migrate_patients.py
	docker-compose exec api python scripts/migrate_questions_schema.py
	docker-compose exec api python scripts/migrate_forms.py

# Show logs
logs:
	docker-compose logs -f

# Show status
status:
	docker-compose ps 
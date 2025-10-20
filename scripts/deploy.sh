#!/bin/bash
# Deploy content-tools-server

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <git-repo-url>"
    echo "Example: $0 https://github.com/yourusername/content-tools-server.git"
    exit 1
fi

GIT_REPO_URL=$1
APP_DIR="/opt/content-tools-server"

echo "Deploying content-tools-server from $GIT_REPO_URL..."

# Clone or update repository
if [ -d "$APP_DIR/.git" ]; then
    echo "Updating existing repository..."
    cd $APP_DIR
    git pull origin main
else
    echo "Cloning repository..."
    git clone $GIT_REPO_URL $APP_DIR
    cd $APP_DIR
fi

# Copy configuration files if they don't exist
if [ ! -f "$APP_DIR/.env" ]; then
    echo "Creating .env from template..."
    cp env.example .env
    echo "Please edit .env with your configuration before starting the application"
fi

if [ ! -f "$APP_DIR/config.yaml" ]; then
    echo "Creating config.yaml from template..."
    cp config.yaml.example config.yaml
    echo "Please edit config.yaml with your configuration before starting the application"
fi

# Build and start services
echo "Building and starting services..."
docker compose up -d --build

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Run migrations
echo "Running database migrations..."
docker compose exec app alembic upgrade head

echo "Deployment completed!"
echo ""
echo "Application is running at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "To check logs: docker compose logs -f"
echo "To stop: docker compose down"
echo "To restart: docker compose restart"

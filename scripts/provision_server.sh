#!/bin/bash
# Provision server with Docker and Docker Compose

set -e

echo "Provisioning server for content-tools-server..."

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install Docker
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "Docker installed successfully"
else
    echo "Docker already installed"
fi

# Install Docker Compose plugin
echo "Installing Docker Compose plugin..."
if ! docker compose version &> /dev/null; then
    sudo apt-get install -y docker-compose-plugin
    echo "Docker Compose plugin installed successfully"
else
    echo "Docker Compose plugin already installed"
fi

# Install additional dependencies
echo "Installing additional dependencies..."
sudo apt-get install -y git curl wget

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /opt/content-tools-server
sudo chown $USER:$USER /opt/content-tools-server

echo "Server provisioning completed!"
echo "Please log out and log back in for Docker group changes to take effect."
echo "Then run: ./scripts/deploy.sh <git-repo-url>"

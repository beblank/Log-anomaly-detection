#!/bin/bash
# Quick start script for local development

set -e

echo "🚀 Starting Multi-Tenant ML SaaS Platform Setup..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your configuration"
else
    echo "✅ .env file already exists"
fi

# Check if Docker is running
if docker info > /dev/null 2>&1; then
    echo "🐳 Docker is running"
    
    # Start services with Docker Compose
    echo "🚢 Starting services with Docker Compose..."
    cd docker
    docker-compose up -d postgres mlflow prometheus grafana
    cd ..
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
else
    echo "⚠️  Docker is not running. Please start Docker or install PostgreSQL manually."
fi

# Run the application
echo "🎯 Starting the application..."
echo ""
echo "Application will be available at:"
echo "  - API: http://localhost:8080"
echo "  - API Docs: http://localhost:8080/docs"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo ""

python -m src.app.main

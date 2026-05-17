#!/bin/bash

# CodeBot AI Setup Script
# This script helps you get started quickly

set -e

echo "🤖 CodeBot AI - Setup Script"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your Anthropic API key"
    echo "   Get your API key from: https://console.anthropic.com/"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
else
    echo "✅ .env file already exists"
fi

# Check if ANTHROPIC_API_KEY is set
source .env
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
    echo "❌ ANTHROPIC_API_KEY is not set in .env file"
    echo "   Please add your API key to the .env file"
    exit 1
fi

echo "✅ Anthropic API key is configured"
echo ""

# Check if target repository exists
if [ ! -d "./target_repo" ]; then
    echo "📦 No target repository found"
    read -p "Do you want to clone a repository to analyze? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter repository URL: " repo_url
        echo "Cloning repository..."
        git clone "$repo_url" ./target_repo
        echo "✅ Repository cloned to ./target_repo"
    else
        echo "⚠️  Please manually place your repository in ./target_repo"
        echo "   Or update REPO_PATH in .env to point to your repository"
    fi
else
    echo "✅ Target repository found at ./target_repo"
fi

echo ""
echo "🚀 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is healthy!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts - waiting for API..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ API failed to start. Check logs with: docker-compose logs api"
    exit 1
fi

echo ""
echo "📊 Triggering initial repository indexing..."
curl -X POST http://localhost:8000/api/repo/index
echo ""

echo ""
echo "✅ Setup complete!"
echo ""
echo "=============================="
echo "📚 Quick Start Guide:"
echo "=============================="
echo ""
echo "1. Check status:"
echo "   curl http://localhost:8000/health"
echo ""
echo "2. Try a chat query:"
echo "   curl -X POST http://localhost:8000/api/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\": \"Find authentication code\"}'"
echo ""
echo "3. View logs:"
echo "   docker-compose logs -f api"
echo ""
echo "4. Stop services:"
echo "   docker-compose down"
echo ""
echo "5. Access databases:"
echo "   Neo4j Browser: http://localhost:7474"
echo "   PostgreSQL: docker exec -it codebot-postgres psql -U postgres -d codebot"
echo ""
echo "📖 Full documentation: README.md"
echo ""

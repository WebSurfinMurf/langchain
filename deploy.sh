#!/bin/bash
set -e

PROJECT_NAME="langchain"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Deploying LangChain stack (LangServe, LangSmith, LangGraph)..."

# Load environment
if [ -f "../secrets/${PROJECT_NAME}.env" ]; then
    source ../secrets/${PROJECT_NAME}.env
else
    echo "Error: Environment file not found at ../secrets/${PROJECT_NAME}.env"
    exit 1
fi

# Create networks if they don't exist
docker network create traefik-net 2>/dev/null || true
docker network create postgres-net 2>/dev/null || true

# Stop existing containers
docker compose down 2>/dev/null || true

# Pull latest Python image
docker pull python:3.11-slim

# Start services
docker compose up -d

echo "Waiting for LangServe to start..."
sleep 10

# Check health
echo "Checking service health..."
for i in {1..30}; do
    if curl -f http://localhost:8001/health 2>/dev/null; then
        echo "✅ LangServe is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Health check timeout - checking logs..."
        docker logs langserve --tail 20
    fi
    sleep 2
done

echo ""
echo "==================================="
echo "LangChain Stack Deployment Complete"
echo "==================================="
echo ""
echo "Services:"
echo "  - LangServe API: http://127.0.0.1:8001 (loopback-only, no public route)"
echo "  - API Docs: http://localhost:8001/docs"
echo "  - Health: http://localhost:8001/health"
echo "  - Chains: http://localhost:8001/chains"
echo ""
echo "Available Endpoints:"
echo "  - /chat - Simple chat with AI"
echo "  - /rag - RAG with vector search"
echo "  - /graph - Multi-step reasoning (LangGraph)"
echo ""
echo "Vector Database:"
echo "  - Host: postgres-vector:5432"
echo "  - Database: vectordb"
echo ""
echo "Monitoring:"
if [ -n "$LANGSMITH_API_KEY" ]; then
    echo "  - LangSmith: https://smith.langchain.com (Project: $LANGSMITH_PROJECT)"
else
    echo "  - LangSmith: Not configured (add LANGSMITH_API_KEY to secrets/langchain.env)"
fi
echo ""
echo "View logs: docker logs langserve -f"
echo ""

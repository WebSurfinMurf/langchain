# LangChain Stack Installation Summary

**Date**: 2025-09-30
**Status**: ✅ Successfully Installed and Running

## What Was Installed

### Core Components
1. **LangServe** - REST API server for LangChain applications
2. **LangSmith** - Observability and tracing platform (optional monitoring)
3. **LangGraph** - Multi-agent workflow orchestration framework
4. **PostgreSQL Vector Integration** - Connected to existing postgres-vector database

### Python Packages Installed
```
langchain==0.3.27
langserve (latest)
langsmith (latest)
langgraph (latest)
langchain-postgres==0.0.15
langchain-openai==0.3.33
langchain-community==0.3.30
psycopg==3.2.10 (PostgreSQL v3 driver)
psycopg2-binary (PostgreSQL v2 driver for compatibility)
uvicorn (ASGI server)
fastapi (Web framework)
```

## Deployment Details

### Container Information
- **Container Name**: langserve
- **Base Image**: python:3.11-slim
- **External Port**: 8001
- **Internal Port**: 8000
- **Networks**: traefik-net, postgres-net

### Access Points
- **Production URL**: none — loopback-only since 2026-07-31 (Traefik router removed)
- **Local API**: http://127.0.0.1:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## Available API Endpoints

### 1. Chat Endpoint (`/chat`)
Simple conversational AI using OpenAI models
- **POST** `/chat/invoke` - Single request/response
- **POST** `/chat/stream` - Streaming responses
- **POST** `/chat/batch` - Batch processing

### 2. RAG Endpoint (`/rag`)
Retrieval Augmented Generation with vector database
- **POST** `/rag/invoke` - Query with context from vector store
- **POST** `/rag/stream` - Streaming RAG responses

### 3. LangGraph Endpoint (`/graph`)
Multi-step reasoning workflow (analyze → answer)
- **POST** `/graph/invoke` - Execute workflow
- **POST** `/graph/stream` - Stream workflow steps

## Database Integration

### PostgreSQL Vector Database
- **Host**: postgres-vector:5432 (internal)
- **Database**: vectordb
- **Collection**: langchain_docs
- **Extension**: pgvector (for vector similarity search)
- **Connection String**: `postgresql://vector_admin:Pass123qp@postgres-vector:5432/vectordb`

### Embedding Dimensions
- **OpenAI Ada-002**: 1536 dimensions
- **Other Models**: Configurable per use case

## Configuration Files

### Project Structure
```
/home/administrator/projects/langchain/
├── app/
│   └── server.py          # FastAPI application
├── docker-compose.yml      # Container configuration
├── deploy.sh              # Deployment script
├── README.md              # User documentation
├── CLAUDE.md              # AI assistant notes
├── test_example.py        # Test script
└── .gitignore
```

### Environment Configuration
- **File**: `$HOME/projects/secrets/langchain.env`
- **Permissions**: 600 (read/write by owner only)

#### Required Variables
```bash
OPENAI_API_KEY=your_key_here  # Required for LLM operations
```

#### Optional Variables
```bash
LANGSMITH_API_KEY=your_key_here      # For tracing/monitoring
LANGSMITH_PROJECT=langchain-project  # Project name in LangSmith
```

#### Auto-Configured Variables
```bash
POSTGRES_HOST=postgres-vector
POSTGRES_PORT=5432
POSTGRES_DB=vectordb
POSTGRES_USER=vector_admin
POSTGRES_PASSWORD=Pass123qp  # From postgres-vector deployment
```

## Network Configuration

### Docker Networks
1. **traefik-net** - External HTTPS access via Traefik reverse proxy
2. **postgres-net** - Internal database connectivity

### Traefik Labels (HTTPS Routing) — REMOVED 2026-07-31
The `langserve.ai-servicers.com` router (websecure / Let's Encrypt / backend 8000)
was deleted as part of the security remediation plan Phase 1c: it served `/docs`
and the model-backed invoke/stream endpoints with no auth middleware. The container
remains attached to `traefik-net` but publishes no router. Host port 8001 is bound
to `127.0.0.1`.

## Verification Steps Completed

✅ Container created and started
✅ All required packages installed
✅ Vector store connection successful
✅ All three chain endpoints available
✅ Health check endpoint responding
✅ Traefik routing configured
✅ Networks properly connected

### Health Status
```json
{
  "status": "healthy",
  "services": {
    "langserve": true,
    "langsmith": true,
    "openai": true,
    "vectorstore": true,
    "postgres": true
  }
}
```

## Next Steps

### 1. Add OpenAI API Key
Edit `$HOME/projects/secrets/langchain.env`:
```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

Then restart:
```bash
cd /home/administrator/projects/langchain
docker compose restart
```

### 2. (Optional) Enable LangSmith Monitoring
1. Sign up at https://smith.langchain.com
2. Get API key from settings
3. Add to environment file:
```bash
LANGSMITH_API_KEY=lsv2_pt_your-key-here
```

### 3. Test API Endpoints
```bash
# Check health
curl http://localhost:8001/health

# List chains
curl http://localhost:8001/chains

# Test chat (requires OpenAI key)
curl -X POST http://localhost:8001/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"input": "Hello!"}}'
```

### 4. Add Documents to Vector Store
See README.md for examples of adding documents for RAG functionality.

## Common Operations

### View Logs
```bash
docker logs langserve -f
```

### Restart Service
```bash
cd /home/administrator/projects/langchain
docker compose restart
```

### Stop Service
```bash
docker compose down
```

### Redeploy
```bash
./deploy.sh
```

## Monitoring & Observability

### LangSmith (Optional)
When configured, all API calls are traced to LangSmith:
- **Dashboard**: https://smith.langchain.com
- **Project**: langchain-project
- **Features**: Request tracing, metrics, debugging, evaluation

### Container Logs
All logs are collected by Promtail and sent to Loki:
- **Grafana**: https://grafana.ai-servicers.com
- **Loki**: https://loki.ai-servicers.com
- **Query**: `{container_name="langserve"}`

### Health Monitoring
Automatic Docker healthcheck every 30 seconds:
```bash
curl -f http://localhost:8000/health
```

## Documentation References

### Project Documentation
- **README.md** - User guide with examples
- **CLAUDE.md** - AI assistant development notes
- **postgres-vector/CLAUDE.md** - Vector database documentation

### System Documentation
- **AINotes/SYSTEM-OVERVIEW.md** - Infrastructure overview
- **AINotes/network.md** - Network configuration
- **AINotes/security.md** - Security policies

### External Resources
- [LangChain Docs](https://python.langchain.com/)
- [LangServe Docs](https://python.langchain.com/docs/langserve)
- [LangSmith Docs](https://docs.smith.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)

## Troubleshooting

### Service Won't Start
```bash
docker logs langserve
```

### Vector Store Connection Issues
```bash
# Test postgres-vector connectivity
docker exec langserve python -c "
import psycopg2
conn = psycopg2.connect('postgresql://vector_admin:Pass123qp@postgres-vector:5432/vectordb')
print('✅ Connected!')
"
```

### Package Issues
```bash
# Check installed packages
docker exec langserve pip list | grep langchain
```

## Installation Issues Resolved

### Issue 1: psycopg Module Errors
**Problem**: `langchain-postgres` requires `psycopg` (v3), not `psycopg2`
**Solution**: Installed both `psycopg[binary]` and `psycopg2-binary` for full compatibility

### Issue 2: TypedDict Compatibility
**Problem**: Python 3.11 requires `typing_extensions.TypedDict`
**Solution**: Changed import from `typing.TypedDict` to `typing_extensions.TypedDict`

### Issue 3: Vector Store Initialization
**Problem**: Vector store failed to initialize due to missing psycopg2
**Solution**: Added both psycopg versions to package installation command

## Security Notes

- ✅ Secrets stored in `$HOME/projects/secrets/` (not in project directory)
- ✅ Environment file has 600 permissions (owner read/write only)
- ✅ No secrets hardcoded in source code
- ✅ Database password secured via environment variables
- ✅ Network isolation via Docker networks
- ⚠️  No authentication on API endpoints (consider OAuth2 proxy for production)

## Support

For issues or questions:
1. Check logs: `docker logs langserve`
2. Review documentation in `/home/administrator/projects/langchain/`
3. Test health endpoint: `curl http://localhost:8001/health`
4. Verify environment: `docker exec langserve env | grep -E "OPENAI|POSTGRES"`

---
**Installation Completed**: 2025-09-30
**Installed By**: Claude AI Assistant
**Status**: ✅ Ready for use (add OpenAI API key to enable AI features)

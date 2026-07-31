# Claude AI Assistant Notes - LangChain Stack

> **For overall environment context, see: `/home/administrator/projects/AINotes/SYSTEM-OVERVIEW.md`**
> **Network details: `/home/administrator/projects/AINotes/network.md`**
> **Security configuration: `/home/administrator/projects/AINotes/security.md`**

## 📋 Project Overview

Complete LangChain deployment providing REST API endpoints for AI applications:
- **LangServe**: FastAPI server for LangChain applications
- **LangSmith**: Observability and tracing for LangChain workflows
- **LangGraph**: Complex multi-step reasoning and agent workflows
- **Vector Integration**: Connected to postgres-vector database with pgvector

## 🟢 Current State (2025-09-30)

- **Status**: ✅ Ready for deployment
- **Container**: langserve
- **Image**: python:3.11-slim (with LangChain packages)
- **Port**: 127.0.0.1:8001 (host, loopback-only), 8000 (internal)
- **URL**: none — loopback-only since 2026-07-31 (public Traefik router removed)
- **Vector DB**: postgres-vector:5432

## 📝 Recent Work & Changes

### Session: 2026-07-31 — Public exposure closed (security remediation Phase 1c)
- Removed the Traefik router labels (`langserve.ai-servicers.com` served `/docs` and the
  invoke/stream endpoints with **no auth middleware**).
- Rebound the host port `8001:8000` → `127.0.0.1:8001:8000`. Label removal alone was
  cosmetic — the container was publishing on `0.0.0.0`.
- Verified: public hostname → 404, `ss -ltn` shows a single `127.0.0.1:8001` listener,
  LAN IP `:8001` does not answer, `localhost:8001/health` → 200, `/chains` → 200.
- ⚠️ Recreating the container re-ran the **unpinned** `pip install` in `command:`, moving
  the whole dependency set forward (langchain 1.0.3 → 1.3.14, fastapi 0.121 → 0.141,
  qdrant-client 1.15.1 → 1.18.0). Pre-change versions captured in
  `docs/rollback-pip-freeze-2026-07-31.txt`. **This will happen on every restart** —
  see Known Issues.
- Container remains on `traefik-net` (no labels ⇒ no router). Detaching it is the correct
  end state but is coupled to `traefik/fix-network-automated.sh`, a different project.

### Session: 2025-09-30
- **Initial Setup**: Created LangChain project structure
  - Created docker-compose.yml with LangServe container
  - Developed FastAPI server with multiple chain endpoints
  - Configured postgres-vector database integration
  - Set up LangSmith tracing (optional)
  - Implemented three chain types: chat, RAG, LangGraph workflow
  - Added comprehensive README and deployment scripts

## 🏗️ Architecture

### Network Configuration
- **traefik-net**: External HTTPS access via Traefik reverse proxy
- **postgres-net**: Internal connection to postgres-vector database
- **Port 8001**: External access (mapped from internal 8000)

### Components
```
LangServe Container (python:3.11-slim)
├── FastAPI Application (server.py)
├── LangChain Components
│   ├── Chat Chain (simple Q&A)
│   ├── RAG Chain (vector search + generation)
│   └── LangGraph Workflow (multi-step reasoning)
├── OpenAI Integration
├── PostgreSQL Vector Store (pgvector)
└── LangSmith Tracing (optional)
```

### Installed Packages
- `langchain` - Core LangChain framework
- `langserve` - REST API server for chains
- `langsmith` - Observability and monitoring
- `langgraph` - Workflow orchestration
- `langchain-postgres` - PostgreSQL vector store
- `langchain-openai` - OpenAI integration
- `langchain-community` - Community integrations
- `psycopg2-binary` - PostgreSQL adapter
- `uvicorn[standard]` - ASGI server
- `fastapi` - Web framework
- `sse-starlette` - Server-sent events

## ⚙️ Configuration

### Important Files & Paths
- **Project**: `/home/administrator/projects/langchain/`
- **Docker Compose**: `docker-compose.yml`
- **Server Code**: `app/server.py`
- **Deploy Script**: `deploy.sh`
- **Secrets**: `$HOME/projects/secrets/langchain.env`
- **Data Volume**: `langchain_data`

### Environment Variables
```bash
# Required
OPENAI_API_KEY=<see secrets/langchain.env>

# Optional (for LangSmith monitoring)
LANGSMITH_API_KEY=<see secrets/langchain.env>
LANGSMITH_PROJECT=langchain-project

# Database (auto-configured)
POSTGRES_HOST=postgres-vector
POSTGRES_PORT=5432
POSTGRES_DB=vectordb
POSTGRES_USER=vector_admin
POSTGRES_PASSWORD=<see secrets/langchain.env>
```

## 🌐 Access & Management

### URLs
- **Production API**: none — no public route. Loopback-only since 2026-07-31.
- **Local API**: http://127.0.0.1:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Available Chains**: http://localhost:8001/chains

### API Endpoints

#### 1. Chat Endpoint (`/chat`)
Simple conversational AI:
```bash
POST /chat/invoke
POST /chat/stream
POST /chat/batch
```

#### 2. RAG Endpoint (`/rag`)
Retrieval Augmented Generation:
```bash
POST /rag/invoke
POST /rag/stream
```

#### 3. LangGraph Endpoint (`/graph`)
Multi-step reasoning workflow:
```bash
POST /graph/invoke
POST /graph/stream
```

### Authentication
- **API**: No authentication (internal use)
- **Traefik**: Public HTTPS access
- **Vector DB**: Password authentication via environment

## 🔗 Integration Points

### Connected Services
- **postgres-vector**: Vector database for embeddings (port 5432 internal)
- **OpenAI API**: LLM and embeddings generation
- **LangSmith**: Optional tracing and monitoring
- **Traefik**: HTTPS reverse proxy

### Vector Database
- **Host**: postgres-vector:5432
- **Database**: vectordb
- **Collection**: langchain_docs
- **Extension**: pgvector
- **Dimensions**: 1536 (OpenAI embeddings)

### Network Dependencies
- Must be on `traefik-net` for HTTPS access
- Must be on `postgres-net` to reach postgres-vector
- OpenAI API requires internet access

## 🛠️ Operations

### Deployment
```bash
# Initial deployment
cd /home/administrator/projects/langchain
./deploy.sh

# Restart
docker compose restart

# View logs
docker logs langserve -f

# Stop
docker compose down
```

### Testing Endpoints
```bash
# Health check
curl http://localhost:8001/health

# List chains
curl http://localhost:8001/chains

# Test chat
curl -X POST http://localhost:8001/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"input": "Hello!"}}'

# Test RAG (requires documents in vector store)
curl -X POST http://localhost:8001/rag/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"question": "What is LangChain?"}}'
```

### Adding Documents to Vector Store
```python
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

CONNECTION_STRING = "postgresql://vector_admin:Pass123qp@postgres-vector:5432/vectordb"

embeddings = OpenAIEmbeddings()
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name="langchain_docs",
    connection=CONNECTION_STRING,
)

docs = [
    Document(page_content="Your content here"),
]
vectorstore.add_documents(docs)
```

### Monitoring with LangSmith
If `LANGSMITH_API_KEY` is configured:
1. Visit https://smith.langchain.com
2. Navigate to project: `langchain-project`
3. View traces, metrics, and debugging info

## 🔧 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs langserve --tail 50

# Verify environment
docker exec langserve env | grep -E "OPENAI|POSTGRES|LANGSMITH"

# Check networks
docker inspect langserve | grep -A 10 Networks
```

### Vector Store Connection Issues
```bash
# Test postgres-vector connectivity
docker exec langserve python -c "
import psycopg2
conn = psycopg2.connect('postgresql://vector_admin:Pass123qp@postgres-vector:5432/vectordb')
print('✅ Connection successful!')
conn.close()
"
```

### OpenAI API Errors
- Verify `OPENAI_API_KEY` in secrets/langchain.env
- Check API quota/billing at https://platform.openai.com
- Test with: `docker exec langserve python -c "import openai; print(openai.__version__)"`

### Package Installation Issues
```bash
# Force reinstall packages
docker compose down
docker compose up -d --force-recreate

# Check installed versions
docker exec langserve pip list | grep -E "langchain|langserve|langsmith|langgraph"
```

## 📋 Standards & Best Practices

### Development Workflow
1. Update `app/server.py` with new chains
2. Test locally: `docker compose restart`
3. Verify endpoints: `curl http://localhost:8001/chains`
4. Update documentation in CLAUDE.md

### Security
- **API Keys**: Stored in secrets/langchain.env (600 permissions)
- **Network Isolation**: On postgres-net for database access
- **No Secrets in Code**: All credentials from environment
- **HTTPS Only**: Public access via Traefik

### Monitoring
- **LangSmith**: Enable for production (requires API key)
- **Health Checks**: Automated via Docker healthcheck
- **Logs**: Centralized via Loki/Promtail
- **Metrics**: Available via /health endpoint

## 🔐 Backup & Security

### Environment Backup
```bash
# Backup environment file
cp $HOME/projects/secrets/langchain.env \
   $HOME/projects/secrets/langchain.env.backup
```

### Vector Store Backup
See postgres-vector documentation for database backup procedures.

### Security Considerations
- OpenAI API key has access to OpenAI services
- LangSmith API key uploads traces to LangSmith cloud
- Vector database contains embedded documents
- No authentication on API endpoints (internal use only)

## 🔄 Related Services

- **postgres-vector**: Vector database with pgvector
- **Open WebUI**: AI chat interface (could integrate LangServe chains)
- **LiteLLM**: Alternative LLM gateway (could route through LangServe)
- **Traefik**: Reverse proxy for HTTPS access

## Known Issues & TODOs

- [ ] **Unpinned dependency install.** `docker-compose.yml`'s `command:` runs a bare
      `pip install langchain langserve>=0.0.30 ...` on every container start, so any
      recreation silently upgrades the entire stack from PyPI. Correct fix: a Dockerfile
      with a pinned `requirements.txt` (seed it from
      `docs/rollback-pip-freeze-2026-07-31.txt`). Until then, "restart" is an
      uncontrolled upgrade and rollback-by-config does not restore the working version set.
- [ ] **`OPENAI_API_KEY` is a placeholder** (`your_ope...here`) in
      `secrets/langchain.env` — vector store init fails 401, so `/rag` is not registered
      and `/chains` lists only `chat` and `graph`. Pre-existing, unrelated to the
      2026-07-31 exposure change.
- [ ] **qdrant-client 1.18.0 vs qdrant server 1.15.5** version-skew warning, introduced by
      the unpinned reinstall above. Client currently works; pin or upgrade the server.
- [ ] Detach from `traefik-net` (no router since 2026-07-31) — coupled to
      `traefik/fix-network-automated.sh:84`, which force-attaches langserve.
- [ ] Add authentication to API endpoints (OAuth2 proxy?)
- [ ] Create example notebooks for common use cases
- [ ] Add more chain examples (SQL, agents, tools)
- [ ] Implement caching layer for LLM responses
- [ ] Add rate limiting for production use
- [ ] Create Grafana dashboard for LangSmith metrics
- [ ] Document custom chain deployment
- [ ] Add websocket support for real-time streaming

## Future Development Plans

1. **Authentication**: Add OAuth2 proxy for production
2. **More Chains**: SQL query, web scraping, data analysis
3. **Agent Framework**: Tool-using agents with LangGraph
4. **Caching**: Redis-based semantic caching
5. **Rate Limiting**: Per-user/per-endpoint limits
6. **Observability**: Custom Grafana dashboards
7. **Documentation**: Interactive API examples

---
*Created: 2025-09-30 by Claude*
*Last Updated: 2025-09-30*
*Next Review: After initial deployment and testing*

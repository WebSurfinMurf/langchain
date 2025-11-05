# LangChain Stack

Complete LangChain deployment with LangServe, LangSmith, and LangGraph integrated with PostgreSQL Vector Database.

## Components

- **LangServe**: REST API server for LangChain applications
- **LangSmith**: Observability and monitoring for LangChain workflows
- **LangGraph**: Multi-agent and complex workflow orchestration
- **PostgreSQL + pgvector**: Vector database for embeddings and semantic search

## Quick Start

### 1. Configure API Keys

Edit `$HOME/projects/secrets/langchain.env`:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (for monitoring)
LANGSMITH_API_KEY=lsv2_...
```

### 2. Deploy

```bash
cd /home/administrator/projects/langchain
./deploy.sh
```

### 3. Access

- **API Docs**: http://localhost:8001/docs
- **Production**: https://langserve.ai-servicers.com
- **Health Check**: http://localhost:8001/health

## Available Endpoints

### Chat Endpoint (`/chat`)
Simple conversational AI:

```bash
curl -X POST http://localhost:8001/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"input": "Hello, how are you?"}}'
```

### RAG Endpoint (`/rag`)
Retrieval Augmented Generation with vector search:

```bash
curl -X POST http://localhost:8001/rag/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"question": "What is LangChain?"}}'
```

### LangGraph Endpoint (`/graph`)
Multi-step reasoning workflow:

```bash
curl -X POST http://localhost:8001/graph/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"question": "Explain quantum computing"}}'
```

### Streaming Responses

```bash
curl -X POST http://localhost:8001/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"input": {"input": "Tell me a story"}}'
```

## Python Client Examples

### Using LangServe Client

```python
from langserve import RemoteRunnable

# Connect to chat endpoint
chat = RemoteRunnable("http://localhost:8001/chat")
response = chat.invoke({"input": "Hello!"})
print(response)

# Stream responses
for chunk in chat.stream({"input": "Tell me about AI"}):
    print(chunk, end="", flush=True)
```

### Using RAG

```python
from langserve import RemoteRunnable

rag = RemoteRunnable("http://localhost:8001/rag")
result = rag.invoke({"question": "What is vector search?"})
print(result)
```

### Using LangGraph Workflow

```python
from langserve import RemoteRunnable

graph = RemoteRunnable("http://localhost:8001/graph")
result = graph.invoke({"question": "Explain machine learning"})
print(f"Analysis: {result['analysis']}")
print(f"Answer: {result['answer']}")
```

## Adding Documents to Vector Store

```python
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

# Connection to postgres-vector
CONNECTION_STRING = "postgresql://vector_admin:Pass123qp@postgres-vector:5432/vectordb"

# Initialize
embeddings = OpenAIEmbeddings()
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name="langchain_docs",
    connection=CONNECTION_STRING,
)

# Add documents
docs = [
    Document(page_content="LangChain is a framework for building LLM applications."),
    Document(page_content="Vector databases store embeddings for semantic search."),
]
vectorstore.add_documents(docs)

# Search
results = vectorstore.similarity_search("What is LangChain?", k=3)
for doc in results:
    print(doc.page_content)
```

## LangSmith Monitoring

If `LANGSMITH_API_KEY` is configured:

1. Visit https://smith.langchain.com
2. Navigate to your project (default: `langchain-project`)
3. View traces, metrics, and debugging info for all API calls

## Architecture

```
Client Request
     ↓
LangServe API (port 8001)
     ↓
LangChain Components
     ├─ Chat Chain
     ├─ RAG Chain → PostgreSQL Vector (pgvector)
     └─ LangGraph Workflow
     ↓
OpenAI API
     ↓
LangSmith (Tracing)
```

## Network Configuration

- **traefik-net**: External HTTPS access via Traefik
- **postgres-net**: Internal connection to postgres-vector database

## Database Connection

Vector database details:
- **Internal**: `postgres-vector:5432`
- **External**: `localhost:5434`
- **Database**: `vectordb`
- **Collection**: `langchain_docs`

## Monitoring & Logs

```bash
# View real-time logs
docker logs langserve -f

# Check health
curl http://localhost:8001/health

# List available chains
curl http://localhost:8001/chains
```

## Common Operations

### Restart Service

```bash
cd /home/administrator/projects/langchain
docker compose restart
```

### Update Dependencies

```bash
docker compose down
docker compose up -d --force-recreate
```

### View Installed Packages

```bash
docker exec langserve pip list | grep -E "langchain|langserve|langsmith|langgraph"
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker logs langserve

# Verify environment
docker exec langserve env | grep -E "OPENAI|POSTGRES|LANGSMITH"
```

### Vector Store Connection Issues

```bash
# Test postgres-vector connection
docker exec langserve python -c "
import psycopg2
conn = psycopg2.connect('postgresql://vector_admin:Pass123qp@postgres-vector:5432/vectordb')
print('Connection successful!')
conn.close()
"
```

### API Key Issues

Ensure API keys are properly set in `$HOME/projects/secrets/langchain.env`:
- `OPENAI_API_KEY` is required
- `LANGSMITH_API_KEY` is optional but recommended

## Related Documentation

- **Vector Database**: `/home/administrator/projects/postgres-vector/CLAUDE.md`
- **System Overview**: `/home/administrator/projects/AINotes/SYSTEM-OVERVIEW.md`
- **Network Config**: `/home/administrator/projects/AINotes/network.md`

## Official Resources

- [LangChain Docs](https://python.langchain.com/)
- [LangServe Docs](https://python.langchain.com/docs/langserve)
- [LangSmith Docs](https://docs.smith.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)

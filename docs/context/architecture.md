# Architecture

> Partial. Seeded 2026-07-31 by the exposure-remediation refocus. Not a full
> `/context-save init` scaffold — the remaining canonical files are unwritten.

## Components

- [IMPLEMENTED] `langserve` — single container, `python:3.11-slim`, runs
  `uvicorn server:app` on internal port `8000`. App code bind-mounted from `./app`.
- [IMPLEMENTED] Vector store: **Qdrant** (`qdrant:6333`, collection `langchain_docs`).
  CLAUDE.md's older text referencing `postgres-vector`/pgvector is stale — compose
  wires `qdrant-net` and `QDRANT_*` env, not postgres.
- [IMPLEMENTED] LLM + embeddings: OpenAI via `langchain-openai`.
- [IMPLEMENTED] LangSmith tracing, optional, key-gated.

## Perimeter — loopback-only since 2026-07-31

- [IMPLEMENTED] **No public route.** The Traefik router for
  `langserve.ai-servicers.com` was deleted (security remediation Phase 1c). The
  hostname returns 404.
- [IMPLEMENTED] **Host port bound to loopback**: `127.0.0.1:8001:8000`. Previously
  `8001:8000`, i.e. `0.0.0.0` + `[::]` — LAN-reachable. Both edits were required;
  label removal alone was cosmetic.
- [IMPLEMENTED] Container is still attached to `traefik-net`. With no
  `traefik.*` labels and Traefik's `exposedByDefault: false`, membership creates no
  route. Kept because `traefik/fix-network-automated.sh:84` force-attaches it.
- [PLANNED] Detach from `traefik-net` — must land together with pruning that script,
  or the two drift.

## Consumers

- [IMPLEMENTED] `deploy.sh:36` health check → `http://localhost:8001/health`
- [IMPLEMENTED] `test_example.py:9` → `http://localhost:8001`
- No programmatic consumer of the public hostname exists (traced across open-webui,
  litellm, n8n, mcp, pipecat — zero hits).

## Route registration is conditional

`app/server.py` registers chains only when their dependencies initialized:

| Path | Gate | Currently |
|---|---|---|
| `/chat` | `if llm` | registered |
| `/graph` | `if llm` | registered |
| `/rag` | `if llm and vectorstore` (`server.py:101`) | **not registered** — vector store init 401s |

`/chains` reflects this at runtime; a missing path means a failed dependency, not a
routing bug.

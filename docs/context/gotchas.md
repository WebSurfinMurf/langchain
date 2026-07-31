# Gotchas

> Non-obvious behavior. Seeded 2026-07-31.

## Every container start is an uncontrolled dependency upgrade

`docker-compose.yml`'s `command:` runs a bare, **unpinned**
`pip install ... langchain 'langserve>=0.0.30' langgraph ...` on every boot. There is no
Dockerfile and no `requirements.txt`.

Consequences:
- Any restart or recreation silently moves the whole stack to whatever PyPI serves that
  day. The 2026-07-31 port rebind alone jumped langchain 1.0.3 → 1.3.14, langchain-core
  1.0.3 → 1.5.3, starlette 0.49.3 → **1.3.1 (major)**, fastapi 0.121 → 0.141.
- **Reverting the compose file does NOT revert the dependencies.** Config rollback and
  version rollback are different operations here.
- **Always `docker exec langserve pip freeze > docs/<date>.txt` before recreating.** That
  snapshot is the only real rollback artifact. See `docs/README-pip-freezes.md`.
- Boot takes minutes (apt-get + pip). `deploy.sh`'s health loop is ~70s and `curl -f`
  inside an `if` does not trip `set -e` — so deploy.sh can print
  `⚠️ Health check timeout` and still exit 0. Do not read that as a broken deploy, and
  do not read exit 0 as a passing health check. Poll `/health` yourself.
- Correct fix: Dockerfile + pinned `requirements.txt`.

## A missing chain in `/chains` is a credential failure, not a routing bug

`app/server.py:101` gates `/rag` on `if llm and vectorstore:`. When
`OPENAI_API_KEY` is bad, vector store init 401s, `vectorstore` stays `None`, and `/rag`
is simply never registered — `/health` still reports `"status":"healthy"` with
`"vectorstore":false`. Check the health payload's per-service booleans, not the top-level
status.

## Removing a Traefik label does not close a published port

The container published `8001` on `0.0.0.0` **and** `[::]`. Deleting the router labels
killed `https://langserve.ai-servicers.com` but would have left `http://<host-ip>:8001`
wide open on the LAN. Verify with `ss -ltn | grep ':8001'` — require exactly one line,
`127.0.0.1:8001`. A surviving `[::]:8001` means the rebind did not take.

## This repo's working tree contains home dotfiles

`.bashrc`, `.gitconfig`, `.profile`, `.zshrc`, `.mcp.json`, `.idea` sit untracked at the
repo root, and the remote is a **public-capable GitHub repo**
(`git@github.com:WebSurfinMurf/langchain.git`). `git add -A` or `git add .` here would
publish them. **Stage by explicit path.** A `.gitignore` is the real fix.

## CLAUDE.md's vector-store section is stale

It documents `postgres-vector` / pgvector / `vectordb`. The compose file actually wires
**Qdrant** (`qdrant-net`, `QDRANT_HOST`, `langchain_docs`). `deploy.sh` still creates a
`postgres-net` that compose no longer uses.

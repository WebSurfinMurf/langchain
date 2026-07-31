# Dependency snapshots — 2026-07-31

`docker-compose.yml`'s `command:` runs an **unpinned** `pip install` on every container
start. Recreating the container (which the loopback port rebind required) therefore moved
the entire dependency set forward. Both sides are captured here because config rollback
does **not** restore a version set.

| File | What it is | Use it for |
|---|---|---|
| `rollback-pip-freeze-2026-07-31.txt` | **Pre-change** set — the container that had run healthy for 3 weeks | Rollback target if the new stack misbehaves |
| `pip-freeze-2026-07-31-post-change.txt` | **Post-change** set — what is running now | Seeding a pinned `requirements.txt` for the current deployment |

Notable drift across the recreation:

| Package | Pre | Post |
|---|---|---|
| langchain | 1.0.3 | 1.3.14 |
| langchain-core | 1.0.3 | 1.5.3 |
| langgraph | 1.0.2 | 1.2.10 |
| fastapi | 0.121.0 | 0.141.1 |
| starlette | 0.49.3 | 1.3.1 (major) |
| openai | 2.7.1 | 2.52.0 |
| qdrant-client | 1.15.1 | 1.18.0 |
| langserve | 0.3.3 | 0.3.3 (unchanged) |

Dropped: `dataclasses-json`, `marshmallow`, `mypy_extensions`, `typing-inspect`.
Added: `langchain-protocol`, `uuid_utils`.

Post-change verification: `/health` 200, `/chains` 200, docker healthcheck `healthy`.
`/rag` is absent from `/chains` — this is **pre-existing and unrelated to the drift**:
`app/server.py:101` gates the route on `if llm and vectorstore:`, and vector store init
fails 401 because `OPENAI_API_KEY` in `secrets/langchain.env` is the literal placeholder
`your_ope...here`.

**The architecturally correct fix** is a Dockerfile with a pinned `requirements.txt` seeded
from the post-change file, so restarts stop being uncontrolled upgrades. Tracked in
`CLAUDE.md` → Known Issues.

# Operations

> Partial. Seeded 2026-07-31 by the exposure-remediation refocus.

## Deploy

```bash
cd /home/administrator/projects/langchain && ./deploy.sh
```

`deploy.sh` sources `../secrets/langchain.env`, `docker compose down`, pulls
`python:3.11-slim`, `up -d`, then polls health.

⚠️ **Capture `docker exec langserve pip freeze` before any deploy** — `down`/`up`
recreates the container and re-runs the unpinned pip install. See `gotchas.md`.

⚠️ deploy.sh's health loop is ~70s and cannot fail the script (`curl -f` inside `if`,
so `set -e` does not trip). Exit 0 ≠ healthy. Verify independently.

## Verify

```bash
ss -ltn | grep ':8001'                                    # expect exactly: 127.0.0.1:8001
curl -s http://localhost:8001/health                      # 200 + per-service booleans
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8001/chains   # 200
docker inspect langserve --format '{{.State.Health.Status}}'            # healthy
```

Perimeter regression checks (both must hold):

```bash
curl -sk -o /dev/null -w '%{http_code}\n' https://langserve.ai-servicers.com/   # 404
curl -s -m 4 -o /dev/null -w '%{http_code}\n' http://$(hostname -I|awk '{print $1}'):8001/health  # no answer
```

## Networking

| Network | Purpose |
|---|---|
| `qdrant-net` | reaches `qdrant:6333` — load-bearing |
| `traefik-net` | **vestigial** — no router labels, no route. Kept only because `traefik/fix-network-automated.sh:84` force-attaches langserve. Detach both together. |

Host port: `127.0.0.1:8001` → container `8000`. Loopback-only, deliberately.

## Logs

```bash
docker logs langserve -f
```

Also auto-collected by Promtail → Loki.

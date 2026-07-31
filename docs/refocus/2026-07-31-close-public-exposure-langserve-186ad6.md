---
id: 2026-07-31-close-public-exposure-langserve-186ad6
status: in-progress
child_session_id: 186ad6a4-1c7a-44d7-ac19-fad323fd126d
spawn_mode: execute
tier: medium
spawned_at: 2026-07-31T15:27:07Z
launched_at: 2026-07-31T15:27:25Z
completed_at: 2026-07-31T15:40:00Z
source_dir: /home/administrator/projects/cicd
source_session_id: unknown
dest_dir: /home/administrator/projects/langchain
slug: close-public-exposure-langserve
parent_refocus_id: null
related_refocus_ids: []
done_when:
  - "public hostname returns 404, ss -ltn shows 8001 bound to 127.0.0.1 only, the localhost health check still passes, change committed"
out_of_scope:
  - "Do NOT edit the nginx portal page or traefik scripts (different projects - surface as follow-ups), do NOT remove the port entirely (localhost consumers need it)"
related: []
---

# Brief: Remove public exposure from langserve and rebind port 8001 to loopback

## Why this branch exists
The ecosystem exam found `langserve.ai-servicers.com` redirecting to an open /docs with no auth, exposing paid model-backed invoke/stream endpoints. Critically, the container ALSO publishes 8001 on 0.0.0.0 — so removing the Traefik label alone would be cosmetic remediation.

## Inherited context
- Source: `cicd/docs/security-remediation-plan.md` (full plan) and `cicd/docs/reviews/ecosystem-exam.final.md` (the 3-node Review Board exam that found this). READ THE PLAN FIRST.
- The exam found this service answering **unauthenticated** on its public Traefik route. An independent consumer trace found **zero** consumers that depend on the public hostname.
- SEVERITY CAVEAT: all probes ran from linuxserver.lan itself. A 200 proves LAN reachability, not internet reachability. Close it regardless; do not escalate urgency language.
- Traefik auth is opt-in per router label. The working pattern is `middlewares=auth-redirect@file,keycloak-auth@file` (defined in `traefik/dynamic/redirect.yml`). Grafana uses it correctly and returns 403 unauthenticated.
- Verification standard: after the change `curl -sk -o /dev/null -w "%{http_code}" https://<name>.ai-servicers.com/` must return **404** (router gone), NOT 200.
- Rollback: re-add the label block and redeploy. Compose/deploy files are git-tracked. Nothing here touches data.
- Commit your change with a clear message referencing the security remediation plan. Do NOT push to main without checking the project's own conventions.
- Traefik labels: `docker-compose.yml:30-36`.
- **CRITICAL — TWO EDITS REQUIRED.** The container publishes `8001` on `0.0.0.0` (confirmed via `ss -ltn`). Removing the Traefik label kills the https route but leaves `http://<host-ip>:8001` open on the LAN. You MUST ALSO rebind the ports entry to `127.0.0.1:8001:8000`. The correct pattern already exists on this host: `mcp-playwright` binds `127.0.0.1:9075`.
- CONSUMER TRACE (independent agent): zero programmatic consumers. Grepped open-webui, litellm, n8n, mcp, pipecat for 'langserve' - no files. The only two consumers are `deploy.sh:36` (health check) and `test_example.py:9`, BOTH using `localhost:8001` — a loopback rebind keeps both working.
- `nginx/sites/langchain-portal/index.html:170-252` has `<a href>` links and a `<pre>` curl example only — no fetch/axios/XHR. Cosmetic, not a functional dependency. That file is in a DIFFERENT project (nginx); surface it as a follow-up, do not edit it.
- `traefik/fix-network-automated.sh:84` lists langserve among containers force-attached to traefik-net; that list goes stale. Different project — surface as follow-up.

## Open questions / desired deliverables
- Remove the Traefik labels AND rebind port 8001 to 127.0.0.1.
- Redeploy; verify the public hostname 404s and that 8001 no longer listens on 0.0.0.0 (`ss -ltn | grep 8001` must show 127.0.0.1, not 0.0.0.0).
- Verify `deploy.sh`'s localhost health check still passes.
- Commit.

## Hard rule for child
- Children are leaves. If you discover work that belongs in a different
  directory, do NOT call /refocus. Surface it in Result.suggested_follow_ups
  for the parent to decide.

## Pointer back
- Source session: `~/.claude/projects/-home-administrator-projects-cicd/unknown.jsonl`
- To resume this child's session: `cd /home/administrator/projects/langchain && claude --resume 186ad6a4-1c7a-44d7-ac19-fad323fd126d` — ordinary resume; works the same whether this child was parent-auto-spawned (execute), hand-launched, or headless.

---

## Result

### Status
- **completed**

### Definition-of-Done met
- [x] **Public hostname returns 404.** `https://langserve.ai-servicers.com/` → `404`, and
      `/docs` → `404`. Router gone, not merely auth-gated.
- [x] **`ss -ltn` shows 8001 bound to 127.0.0.1 only.** Exactly one listener:
      `LISTEN 127.0.0.1:8001`. The pre-change `0.0.0.0:8001` **and** `[::]:8001` are both
      gone. Cross-checked functionally: `http://192.168.1.13:8001/health` (host LAN IP)
      does not answer.
- [x] **Localhost health check still passes.** `http://localhost:8001/health` → `200`
      `{"status":"healthy",...}`; `/chains` → `200`; docker healthcheck reports `healthy`.
      `deploy.sh` completed exit 0 with no timeout warning (health returned at ~30s).
- [x] **Change committed.** `b38bb68` (the change) and `dc6664e` (dependency-drift docs).
      **Local commits only — not pushed.** The brief said not to push to main without
      checking project conventions; this repo's remote is
      `git@github.com:WebSurfinMurf/langchain.git` and no push convention was documented.

### Summary
Removed the seven `traefik.*` router labels and rebound the published port from
`8001:8000` to `127.0.0.1:8001:8000` in `docker-compose.yml`, then redeployed via
`deploy.sh`. Both edits were necessary — the container published on `0.0.0.0`, so label
removal alone would have left `http://<host-ip>:8001` open on the LAN. Verified by direct
measurement rather than inference: the hostname 404s, a single loopback listener remains,
the LAN IP refuses, and the two real consumers (`deploy.sh:36` health check,
`test_example.py:9`) both use `localhost` and are unaffected.

**Severity correction for the parent's sequencing** (stated as fact, not urgency
escalation): `OPENAI_API_KEY` in `secrets/langchain.env` is the literal placeholder
`your_ope...here`. Vector store init 401s against OpenAI, and `/chat/invoke` would have
done the same. So the exam's framing — "exposing paid model-backed invoke/stream
endpoints" — overstates what was live: **the paid-abuse vector was not functional; the
real exposure was `/docs` information disclosure plus an unauthenticated public route.**
Closing it was still correct and is now done.

**Risk introduced, disclosed:** the compose `command:` runs an **unpinned** `pip install`
on every start. Recreating the container to change the port therefore upgraded the whole
stack (langchain 1.0.3 → 1.3.14, langchain-core 1.0.3 → 1.5.3, starlette 0.49.3 → 1.3.1
major, fastapi 0.121 → 0.141, qdrant-client 1.15.1 → 1.18.0; `dataclasses-json` /
`marshmallow` / `typing-inspect` dropped). The service is healthy on the new set, but
**config rollback does not restore the old versions** — both freezes are committed for
that reason. `/rag` is absent from `/chains`; this was checked, not assumed —
`app/server.py:101` gates the route on `if llm and vectorstore:`, so it is caused by the
placeholder API key and is pre-existing, not drift.

### Artifacts produced
- `docker-compose.yml` — Traefik labels removed; port rebound to `127.0.0.1:8001:8000`
- `docs/rollback-pip-freeze-2026-07-31.txt` — pre-change dependency set (rollback target)
- `docs/pip-freeze-2026-07-31-post-change.txt` — currently-running dependency set
- `docs/README-pip-freezes.md` — which freeze is which, the drift table, and the fix
- `CLAUDE.md` / `README.md` / `INSTALLATION_SUMMARY.md` / `deploy.sh` — stopped advertising
  the dead public URL; added the drift, placeholder-key, and qdrant-skew Known Issues

### Suggested follow-ups (parent decides)
- **`projects/nginx`** — `remove-langserve-link-from-portal`: `sites/langchain-portal/index.html:170-252`
  still links `https://langserve.ai-servicers.com` and shows a curl example against it.
  Cosmetic only (`<a href>` + `<pre>`, no fetch/XHR), but it now advertises a 404.
- **`projects/traefik`** — `prune-stale-force-attach-list`: `fix-network-automated.sh:84`
  force-attaches `langserve` to `traefik-net`; the list is stale.
- **`projects/traefik` + here (paired)** — `detach-langserve-from-traefik-net`: the correct
  end state is that a service with no router is not on the ingress network. Left in place
  deliberately — removing it from compose while the script above re-attaches it produces
  drift, so the two must change together. **Not a residual exposure:** with no labels and
  `exposedByDefault: false`, network membership alone creates no route.
- **`projects/secrets`** — `fix-langchain-openai-key`: `langchain.env`'s `OPENAI_API_KEY` is
  a placeholder. `/rag` cannot register and `/chat` cannot serve until it is real. Decide
  whether this service is wanted at all before spending a key on it.
- **`projects/qdrant`** — `resolve-client-server-version-skew`: client 1.18.0 vs server
  1.15.5 now exceeds the supported minor delta (warning logged, still functional).
- **Repo hygiene (here, low priority)** — the `langchain` repo's working tree contains
  untracked home dotfiles at its root (`.bashrc`, `.gitconfig`, `.mcp.json`, `.idea`,
  `.ssh`-adjacent config). A `git add -A` in this repo would publish them to GitHub.
  Staging was done by explicit path this session; add a `.gitignore` before that bites.

### Material changes (for /context-save)
- **architecture** — langserve is now **loopback-only**: no Traefik router, no public
  hostname, host port bound to `127.0.0.1:8001`. Consumers must use `localhost`. Container
  remains attached to `traefik-net` (no labels ⇒ no route) pending the paired detach above.
- **gotchas** — the compose `command:` installs dependencies **unpinned at every container
  start**, so any restart is an uncontrolled upgrade and rolling back config does not roll
  back the dependency set. Capture `pip freeze` before recreating this container.
- **gotchas** — `/rag` is conditionally registered (`app/server.py:101`,
  `if llm and vectorstore:`). Its absence from `/chains` indicates a credential/vector-store
  failure, not a routing bug.
- **security** — Traefik auth is opt-in per router label; this service had a public
  `websecure` router with no auth middleware. The systemic fix (a CI check rejecting public
  routers without auth) is `projects/cicd` scope, §6 of the remediation plan.

### Child session
- Session jsonl: `~/.claude/projects/-home-administrator-projects-langchain/186ad6a4-1c7a-44d7-ac19-fad323fd126d.jsonl`
- Completed at: 2026-07-31T15:40Z

<!--
When the child completes, /refocus-complete appends here:

### Status
- completed       # met all done_when criteria
- blocked         # hit a blocker requiring work in another directory; parent must orchestrate

### Definition-of-Done met
<checklist matching done_when from frontmatter, each item checked or noted as not met>

### Summary
<one paragraph: what was accomplished or where it blocked>

### Artifacts produced
- `<path>` — `<one-line description>`

### Suggested follow-ups (parent decides)
<bullets of "I noticed work belongs at <dir>" items the child surfaced for
parent to orchestrate. Each entry: dir, slug, one-line reason.>

### Material changes (for /context-save)
<list of decisions, contracts, or architecture changes that should be
promoted into <dest>/docs/context/* as canonical state. Each entry: which
context file (architecture | interfaces | conventions | gotchas | …) and
the one-line summary. Or: "N/A — investigation only, no canonical state
changed." Mandatory; child must enumerate explicitly before status flips.>

### Child session
- Session jsonl: `~/.claude/projects/__ENCODED_DEST_CWD__/186ad6a4-1c7a-44d7-ac19-fad323fd126d.jsonl`
- Completed at: <ISO ts>
-->

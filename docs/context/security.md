# Security

> Partial. Seeded 2026-07-31 by the exposure-remediation refocus.

## Trust boundary

- [IMPLEMENTED] **Tier 1 (internal tooling).** Loopback-only: no public hostname, no
  Traefik router, host port on `127.0.0.1`. Reachable from this host only.
- [IMPLEMENTED] **No application-level auth.** There is none, and none is needed at
  the current perimeter — the loopback bind *is* the control. If this service is ever
  re-exposed, auth must land in the same change, not after.

## History — why the perimeter changed

- 2026-07-31: `langserve.ai-servicers.com` was serving `/docs` and the
  invoke/stream endpoints **unauthenticated** on a public `websecure` router. Found by
  the Review Board ecosystem exam; closed under `cicd/docs/security-remediation-plan.md`
  Phase 1c.
- Root cause is systemic, not local: **Traefik auth is opt-in per router label**, and
  nothing rejects a public router that omits the middleware. `exposedByDefault: false`
  prevents accidental *discovery*, not accidental *exposure*. The working pattern is
  `middlewares=auth-redirect@file,keycloak-auth@file`.
- Severity, stated accurately: all probes ran from `linuxserver.lan` itself, so a 200
  proved LAN reachability, not internet reachability. And `OPENAI_API_KEY` was a
  placeholder, so the model-backed endpoints would have 401'd — **the paid-abuse vector
  was not live.** The real exposure was `/docs` information disclosure plus an open
  public route.

## Secrets

- [IMPLEMENTED] All credentials come from `$HOME/projects/secrets/langchain.env` via
  compose `env_file:`. None in the repo.
- ⚠️ `OPENAI_API_KEY` is currently the literal placeholder `your_ope...here`. Vector
  store init fails 401 and `/rag` never registers.

## Re-exposure checklist (if a public route is ever wanted again)

1. Add `middlewares=auth-redirect@file,keycloak-auth@file` **in the same commit** as the
   router labels — never as a follow-up.
2. Keep the host port on `127.0.0.1`; let Traefik reach the container over the docker
   network. A published host port is a second, unauthenticated door.
3. Verify unauthenticated → 403, not 200.

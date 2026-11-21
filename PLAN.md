# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

field-onboarding

## Roadmap

### project-skeleton — Project skeleton with FastAPI backend and React frontend

Status: done

Acceptance:
- Backend FastAPI app starts and serves health endpoint

Implementation: `backend/app/main.py`

Tests: `backend/tests/test_health.py`

### auth-oidc — OIDC authentication with Keycloak

Status: done

Acceptance:
- Login redirects to Keycloak

Implementation: `backend/app/models/auth.py`

Tests: `backend/tests/test_auth.py`

### skill-registry — Skill registry and management API

Status: done

Acceptance:
- CRUD for skills with versioning

Implementation: `backend/app/models/skill.py`

Tests: `backend/tests/test_skills.py`

### statistical-genetics — Statistical genetics workflow: locus compare

Status: done

Acceptance:
- Fetch GWAS Catalog region data

Implementation: `backend/app/services/genetics/gwas.py`

Tests: `backend/tests/test_genetics.py`

### field-onboarding — Field onboarding workflow

Status: in_progress

Acceptance:
- Prerequisite framework assessment

Implementation: `backend/app/services/onboarding/engine.py`, `backend/app/services/onboarding/state.py`, `backend/app/api/onboarding.py`

Tests: `backend/tests/test_onboarding.py`

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)

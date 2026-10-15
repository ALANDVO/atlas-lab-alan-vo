# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

auth-oidc

## Roadmap

### project-skeleton — Project skeleton with FastAPI backend and React frontend

Status: done

Acceptance:
- Backend FastAPI app starts and serves health endpoint
- Frontend Vite+React+TS builds and serves
- Docker compose brings up backend, frontend, Keycloak, PostgreSQL
- Backend tests run with pytest
- Frontend typecheck and tests run

Implementation: `backend/app/main.py`, `backend/requirements.txt`, `backend/Dockerfile`, `frontend/package.json`, `frontend/Dockerfile`, `compose.yaml`, `.github/workflows/ci.yml`

Tests: `backend/tests/test_health.py`, `frontend/src/__tests__/health.test.tsx`

### auth-oidc — OIDC authentication with Keycloak

Status: in_progress

Acceptance:
- Login redirects to Keycloak
- Callback exchanges code for tokens with PKCE
- Protected endpoints reject unauthenticated requests
- Role-based access control (viewer/operator/admin)

Implementation: `backend/app/core/auth.py`, `backend/app/api/auth.py`, `frontend/src/auth/`

Tests: `backend/tests/test_auth.py`, `frontend/src/__tests__/auth.test.tsx`

### skill-registry — Skill registry and management API

Status: planned

Acceptance:
- CRUD for skills with versioning
- Skill metadata validation
- List/search skills by category

Implementation: `backend/app/models/skill.py`, `backend/app/services/skill_registry.py`, `backend/app/api/skills.py`

Tests: `backend/tests/test_skills.py`

### statistical-genetics — Statistical genetics workflow: locus compare

Status: planned

Acceptance:
- Fetch GWAS Catalog region data
- Fetch eQTL Catalogue region data
- Compute LD from 1000 Genomes
- Render locus compare 4-panel plot
- End-to-end workflow execution

Implementation: `backend/app/services/genetics/gwas.py`, `backend/app/services/genetics/eqtl.py`, `backend/app/services/genetics/ld.py`, `backend/app/services/genetics/locuscompare.py`, `backend/app/api/genetics.py`

Tests: `backend/tests/test_genetics.py`

### field-onboarding — Field onboarding workflow

Status: planned

Acceptance:
- Prerequisite framework assessment
- Field maturity classification (settled/emerging/contested)
- Ladder-based teaching: motivation → vocabulary → framework → methods → frontier
- Decode mode for passage analysis
- Diagnostic questions per rung

Implementation: `backend/app/services/onboarding/engine.py`, `backend/app/services/onboarding/state.py`, `backend/app/api/onboarding.py`

Tests: `backend/tests/test_onboarding.py`

### frontend-dashboard — Frontend dashboard with workflow UIs

Status: planned

Acceptance:
- Skill browser and search
- Locus compare workflow UI with plot display
- Field onboarding chat-style UI
- Loading/error/empty states

Implementation: `frontend/src/components/`, `frontend/src/pages/`, `frontend/src/api/`

Tests: `frontend/src/__tests__/dashboard.test.tsx`

### docs-packaging — Documentation, packaging, and CI/CD

Status: planned

Acceptance:
- README with install/run/test steps
- Mermaid architecture diagram
- API reference
- portfolio.json
- CHANGELOG.md
- LICENSE
- pyproject.toml
- .env.example
- CI passes

Implementation: `README.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`, `portfolio.json`, `.env.example`, `docs/`


# Changelog

## 1.6.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.5.1 — work-in-progress checkpoint

### Added
- field-onboarding: Prerequisite framework assessment endpoint (`POST /api/v1/onboarding/assess`)
- field-onboarding: Field maturity classification endpoint (`POST /api/v1/onboarding/classify`)
- field-onboarding: Ladder-based teaching progression API (`GET/POST /api/v1/onboarding/ladder/step`)
- field-onboarding: Decode mode for passage analysis (`POST /api/v1/onboarding/decode`)
- field-onboarding: Session retrieval endpoint (`GET /api/v1/onboarding/session/{session_id}`)
- field-onboarding: Engine, state, and rung service modules (`backend/app/services/onboarding/`)
- field-onboarding: Targeted test suite (`backend/tests/test_onboarding.py`, 10 tests)

### Changed
- Updated PLAN.md: current_feature → field-onboarding, status → in_progress
- Updated feature-plan.json: added field-onboarding feature entry

### Fixed
- Import error in rungs.py: added missing `List` typing import

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — 2026-11-08

### Fixed
- statistical-genetics: Combined locus compare panel now merges GWAS, eQTL, and LD variant data for proper 4-panel visualization
- statistical-genetics: Added frontend-compatible endpoint `/api/v1/genetics/locuscompare` accepting sentinel SNP (rsID) and window size in kilobases
- statistical-genetics: Added sentinel SNP resolution via GWAS Catalog REST API to convert rsID to genomic coordinates
- statistical-genetics: Updated frontend API client to call the new endpoint

### Added
- statistical-genetics: New `LocusCompareFrontendRequest` and `LocusCompareFrontendResponse` models for frontend-backend compatibility
- statistical-genetics: Test coverage for frontend-compatible locus compare endpoint

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-15

### Added
- Initial project scaffold with FastAPI backend and React + TypeScript + Vite frontend
- Docker Compose with backend, frontend, Keycloak, and PostgreSQL services
- Health check endpoints (`/api/v1/health`, `/api/v1/health/db`)
- OIDC authentication framework with Keycloak realm configuration (viewer/operator/admin roles)
- Skill registry API structure (CRUD endpoints)
- Statistical genetics workflow API structure (GWAS/eQTL fetch, LD compute, locus compare)
- Field onboarding workflow API structure (assess, ladder, decode)
- Frontend dashboard with system health display
- Frontend pages: Skills browser, Genetics locus compare UI, Onboarding (assess/ladder/decode)
- Frontend login page with demo mode
- CI/CD workflow (backend tests, frontend typecheck/build/test, Docker builds, integration test)
- Configuration via `.env` / `pydantic-settings`
- SQLite default database with async SQLAlchemy
- Comprehensive README with architecture diagram, API reference, AI/ML evaluation section
- Portfolio metadata (`portfolio.json`)
- MIT License

### Security
- Non-root Docker users
- HttpOnly SameSite cookie-ready auth design
- PKCE for SPA OIDC flow
- No secrets in repository (`.env.example` only)
- CORS restricted to configured origins

### Known Limitations (v1.0.0)
- OIDC login uses demo token; full Keycloak integration pending
- Skill registry, genetics, and onboarding endpoints return placeholder responses
- Database migrations not yet configured (Alembic)
- LLM adapters not implemented
- Frontend tests use mocks; integration test runs in CI only

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)

# Changelog

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
"""Targeted tests for the field onboarding workflow API."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


class TestOnboardingAssess:
    """Test prerequisite framework assessment endpoint."""

    @pytest.mark.asyncio
    async def test_assess_returns_framework_assessment(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/onboarding/assess",
            json={"user_id": "test-user-123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "assessed_at" in data
        assert "framework_gaps" in data
        assert "readiness_score" in data
        assert "recommended_starting_rung" in data
        assert isinstance(data["readiness_score"], float)
        assert 0.0 <= data["readiness_score"] <= 1.0
        assert 1 <= data["recommended_starting_rung"] <= 5

    @pytest.mark.asyncio
    async def test_assess_without_user_id(self, client: AsyncClient):
        response = await client.post("/api/v1/onboarding/assess", json={})
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data


class TestOnboardingClassify:
    """Test field maturity classification endpoint."""

    @pytest.mark.asyncio
    async def test_classify_returns_field_maturity(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/onboarding/classify",
            json={"user_id": "test-user-456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "level" in data
        assert "confidence" in data
        assert "indicators" in data
        assert data["level"] in ("settled", "emerging", "contested")
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0
        assert isinstance(data["indicators"], list)


class TestOnboardingLadder:
    """Test ladder-based teaching progression endpoints."""

    @pytest.mark.asyncio
    async def test_ladder_step_valid_rung(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/onboarding/ladder/step",
            json={"current_rung": 1, "user_id": "test-user"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "rung" in data
        assert "current_rung" in data
        assert data["current_rung"] == 1
        assert data["rung"]["number"] == 1
        assert "title" in data["rung"]
        assert "motivation" in data["rung"]

    @pytest.mark.asyncio
    async def test_ladder_step_invalid_rung(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/onboarding/ladder/step",
            json={"current_rung": 6, "user_id": "test-user"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ladder_step_all_rungs(self, client: AsyncClient):
        for rung in range(1, 6):
            response = await client.post(
                "/api/v1/onboarding/ladder/step",
                json={"current_rung": rung, "user_id": "test-user"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["current_rung"] == rung
            assert data["rung"]["number"] == rung


class TestOnboardingDecode:
    """Test decode mode for passage analysis."""

    @pytest.mark.asyncio
    async def test_decode_valid_mode(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/onboarding/decode",
            json={"mode": "literal", "passage": "Sample passage text", "questions": ["Q1?", "Q2?"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "literal"
        assert data["num_questions"] == 2

    @pytest.mark.asyncio
    async def test_decode_invalid_mode(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/onboarding/decode",
            json={"mode": "invalid_mode", "passage": "text"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_decode_no_questions(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/onboarding/decode",
            json={"mode": "critical", "passage": "A longer passage for critical analysis"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["num_questions"] == 0


class TestOnboardingSession:
    """Test session retrieval endpoint."""

    @pytest.mark.asyncio
    async def test_get_session_returns_structure(self, client: AsyncClient):
        # Create a session ID and try to retrieve it
        session_id = "test-session-abc123"
        response = await client.get(f"/api/v1/onboarding/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "user_id" in data
        assert "current_rung" in data
        assert "answered_rungs" in data

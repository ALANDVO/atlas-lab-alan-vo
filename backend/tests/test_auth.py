import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.core.config import settings
from app.models.auth import User, UserRole, AuthState
from app.core.database import async_session_maker
from sqlalchemy import select
from datetime import datetime, timedelta, timezone


@pytest.fixture
def mock_oidc_config():
    return {
        "issuer": "http://keycloak:8080/realms/atlas-lab",
        "authorization_endpoint": "http://keycloak:8080/realms/atlas-lab/protocol/openid-connect/auth",
        "token_endpoint": "http://keycloak:8080/realms/atlas-lab/protocol/openid-connect/token",
        "jwks_uri": "http://keycloak:8080/realms/atlas-lab/protocol/openid-connect/certs",
        "userinfo_endpoint": "http://keycloak:8080/realms/atlas-lab/protocol/openid-connect/userinfo",
        "end_session_endpoint": "http://keycloak:8080/realms/atlas-lab/protocol/openid-connect/logout",
    }


@pytest.fixture
def mock_jwks():
    return {
        "keys": [
            {
                "kid": "test-key-1",
                "kty": "RSA",
                "use": "sig",
                "n": "test-modulus",
                "e": "AQAB",
            }
        ]
    }


class TestAuth:
    @pytest.mark.asyncio
    async def test_login_redirects_when_oidc_disabled(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/login", follow_redirects=False)
        assert response.status_code == 200
        data = response.json()
        assert "OIDC not enabled" in data["message"]
        assert "demo_login_url" in data

    @pytest.mark.asyncio
    async def test_demo_login_creates_user_and_sets_cookies(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/demo-login", follow_redirects=False)
        assert response.status_code == 307
        cookies = response.headers.get("set-cookie", "")
        assert "access_token=demo-token" in cookies
        assert "refresh_token=demo-refresh" in cookies

    @pytest.mark.asyncio
    async def test_me_endpoint_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_demo_token(self, client: AsyncClient):
        # Use Authorization header with demo token (as the auth middleware supports)
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer demo-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "demo"
        assert data["role"] == "operator"

    @pytest.mark.asyncio
    async def test_logout_clears_cookies(self, client: AsyncClient):
        await client.get("/api/v1/auth/demo-login")
        response = await client.post("/api/v1/auth/logout", follow_redirects=False)
        assert response.status_code == 307
        cookies = response.headers.get("set-cookie", "")
        # Check that cookies are cleared (expires in past or max-age=0)
        assert "Max-Age=0" in cookies or "expires=" in cookies.lower()

    @pytest.mark.asyncio
    @patch("app.services.auth.auth_service.get_oidc_config")
    @patch("app.services.auth.auth_service.get_jwks")
    @patch("app.services.auth.auth_service.validate_id_token")
    @patch("app.services.auth.httpx.AsyncClient.post")
    async def test_callback_validates_state_and_exchanges_code(
        self, mock_post, mock_validate_id_token, mock_get_jwks, mock_get_oidc_config, client: AsyncClient
    ):
        mock_get_oidc_config.return_value = MagicMock(
            authorization_endpoint="http://keycloak:8080/auth",
            token_endpoint="http://keycloak:8080/token",
            userinfo_endpoint="http://keycloak:8080/userinfo",
            jwks_uri="http://keycloak:8080/certs",
            end_session_endpoint="http://keycloak:8080/logout",
        )
        mock_get_jwks.return_value = {"keys": []}
        
        # Mock the token exchange response
        mock_token_response = MagicMock()
        mock_token_response.json.return_value = {
            "access_token": "test-access-token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "test-refresh-token",
            "id_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # Valid JWT format
            "scope": "openid profile email roles",
        }
        mock_token_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_token_response
        
        # Mock validate_id_token to return user info
        from app.services.auth import UserInfo
        mock_validate_id_token.return_value = UserInfo(
            sub="test-user-123",
            email="test@example.com",
            preferred_username="testuser",
            name="Test User",
            realm_access={"roles": ["operator"]}
        )

        async with async_session_maker() as db:
            auth_state = AuthState(
                state="test-state-123",
                nonce="test-nonce-123",
                code_verifier="test-verifier",
                redirect_uri="http://localhost:5173/callback",
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            )
            db.add(auth_state)
            await db.commit()

        response = await client.get(
            "/api/v1/auth/callback",
            params={"code": "test-code", "state": "test-state-123"},
            follow_redirects=False,
        )

        assert response.status_code == 307


class TestRoleBasedAccess:
    @pytest.fixture
    def admin_user(self):
        return User(
            id=1,
            subject="admin-sub",
            email="admin@test.com",
            username="admin",
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
        )

    @pytest.fixture
    def viewer_user(self):
        return User(
            id=2,
            subject="viewer-sub",
            email="viewer@test.com",
            username="viewer",
            full_name="Viewer User",
            role=UserRole.VIEWER,
            is_active=True,
        )
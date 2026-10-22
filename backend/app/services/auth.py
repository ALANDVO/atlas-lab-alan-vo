import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx
from jose import jwt, jwk
from jose.exceptions import JWTError, ExpiredSignatureError
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.auth import User, UserRole, AuthState


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    scope: Optional[str] = None


class UserInfo(BaseModel):
    sub: str
    email: Optional[str] = None
    preferred_username: Optional[str] = None
    name: Optional[str] = None
    realm_access: Optional[Dict[str, Any]] = None


class OIDCConfig(BaseModel):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    jwks_uri: str
    userinfo_endpoint: str
    end_session_endpoint: Optional[str] = None


class AuthService:
    def __init__(self):
        self._oidc_config: Optional[OIDCConfig] = None
        self._jwks_cache: Optional[Dict[str, Any]] = None
        self._jwks_fetched_at: Optional[datetime] = None

    async def get_oidc_config(self) -> OIDCConfig:
        if self._oidc_config is None:
            if not settings.oidc_issuer_url:
                raise ValueError("OIDC issuer URL not configured")
            async with httpx.AsyncClient(timeout=10.0) as client:
                discovery_url = f"{settings.oidc_issuer_url.rstrip('/')}/.well-known/openid-configuration"
                resp = await client.get(discovery_url)
                resp.raise_for_status()
                data = resp.json()
                self._oidc_config = OIDCConfig(**data)
        return self._oidc_config

    async def get_jwks(self) -> Dict[str, Any]:
        if self._jwks_cache is None or (
            self._jwks_fetched_at and datetime.now(timezone.utc) - self._jwks_fetched_at > timedelta(hours=1)
        ):
            oidc_config = await self.get_oidc_config()
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(oidc_config.jwks_uri)
                resp.raise_for_status()
                self._jwks_cache = resp.json()
                self._jwks_fetched_at = datetime.now(timezone.utc)
        return self._jwks_cache

    def generate_pkce_pair(self) -> tuple[str, str]:
        code_verifier = secrets.token_urlsafe(64)[:128]
        code_challenge = secrets.token_urlsafe(32)
        return code_verifier, code_challenge

    def generate_state_nonce(self) -> tuple[str, str]:
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        return state, nonce

    async def build_authorization_url(self, redirect_uri: str, code_challenge: str, state: str, nonce: str) -> str:
        oidc_config = await self.get_oidc_config()
        params = {
            "response_type": "code",
            "client_id": settings.oidc_client_id,
            "redirect_uri": redirect_uri,
            "scope": settings.oidc_scopes,
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        if settings.oidc_audience:
            params["audience"] = settings.oidc_audience
        return f"{oidc_config.authorization_endpoint}?{urlencode(params)}"

    async def exchange_code_for_tokens(
        self, code: str, redirect_uri: str, code_verifier: str
    ) -> TokenResponse:
        oidc_config = await self.get_oidc_config()
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": settings.oidc_client_id,
            "client_secret": settings.oidc_client_secret,
            "code_verifier": code_verifier,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(oidc_config.token_endpoint, data=data)
            resp.raise_for_status()
            return TokenResponse(**resp.json())

    async def validate_id_token(self, id_token: str, nonce: str) -> UserInfo:
        jwks = await self.get_jwks()
        unverified_header = jwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")
        if not kid:
            raise JWTError("Missing kid in token header")

        key = None
        for jwk_key in jwks.get("keys", []):
            if jwk_key.get("kid") == kid:
                key = jwk.construct(jwk_key)
                break
        if not key:
            raise JWTError("Signing key not found in JWKS")

        try:
            payload = jwt.decode(
                id_token,
                key,
                algorithms=["RS256"],
                audience=settings.oidc_client_id,
                issuer=settings.oidc_issuer_url,
                options={"verify_at_hash": False},
            )
        except ExpiredSignatureError:
            raise JWTError("ID token expired")
        except JWTError as e:
            raise JWTError(f"Invalid ID token: {e}")

        if payload.get("nonce") != nonce:
            raise JWTError("Nonce mismatch")

        return UserInfo(**payload)

    async def get_userinfo(self, access_token: str) -> UserInfo:
        oidc_config = await self.get_oidc_config()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                oidc_config.userinfo_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            return UserInfo(**resp.json())

    async def get_or_create_user(self, db: AsyncSession, userinfo: UserInfo, roles: list[str]) -> User:
        result = await db.execute(select(User).where(User.subject == userinfo.sub))
        user = result.scalar_one_or_none()

        role = UserRole.VIEWER
        if "admin" in roles:
            role = UserRole.ADMIN
        elif "operator" in roles:
            role = UserRole.OPERATOR

        if user is None:
            user = User(
                subject=userinfo.sub,
                email=userinfo.email or "",
                username=userinfo.preferred_username,
                full_name=userinfo.name,
                role=role,
                extra_data={},
            )
            db.add(user)
        else:
            user.email = userinfo.email or user.email
            user.username = userinfo.preferred_username or user.username
            user.full_name = userinfo.name or user.full_name
            user.role = role
            user.last_login_at = datetime.now(timezone.utc)

        await db.flush()
        return user

    async def store_auth_state(
        self,
        db: AsyncSession,
        state: str,
        nonce: str,
        code_verifier: str,
        redirect_uri: str,
    ) -> AuthState:
        auth_state = AuthState(
            state=state,
            nonce=nonce,
            code_verifier=code_verifier,
            redirect_uri=redirect_uri,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        db.add(auth_state)
        await db.flush()
        return auth_state

    async def get_and_consume_auth_state(self, db: AsyncSession, state: str) -> Optional[AuthState]:
        result = await db.execute(
            select(AuthState).where(AuthState.state == state, AuthState.used == False)
        )
        auth_state = result.scalar_one_or_none()
        if auth_state:
            # Ensure both datetimes are timezone-aware for comparison
            expires_at = auth_state.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at > datetime.now(timezone.utc):
                auth_state.used = True
                await db.flush()
                return auth_state
        return None

    def map_realm_roles(self, realm_access: Optional[Dict[str, Any]]) -> list[str]:
        if not realm_access:
            return []
        return realm_access.get("roles", [])


auth_service = AuthService()
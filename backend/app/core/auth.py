from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk
from jose.exceptions import JWTError, ExpiredSignatureError
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.auth import User, UserRole
from app.services.auth import auth_service


class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int
    iss: str
    aud: str
    realm_access: Optional[dict] = None
    preferred_username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None


class CurrentUser(BaseModel):
    id: int
    subject: str
    email: str
    username: Optional[str]
    full_name: Optional[str]
    role: UserRole
    is_active: bool


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    if not settings.oidc_enabled:
        if token == "demo-token":
            result = await db.execute(select(User).where(User.subject == "demo-user"))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    subject="demo-user",
                    email="demo@example.com",
                    username="demo",
                    full_name="Demo User",
                    role=UserRole.OPERATOR,
                    is_active=True,
                )
                db.add(user)
                await db.flush()
            return CurrentUser(
                id=user.id,
                subject=user.subject,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        jwks = await auth_service.get_jwks()
        unverified_header = jwt.get_unverified_header(token)
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

        payload_dict = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.oidc_client_id,
            issuer=settings.oidc_issuer_url,
        )
        payload = TokenPayload(**payload_dict)

        if payload.exp < datetime.now(timezone.utc).timestamp():
            raise ExpiredSignatureError("Token expired")

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.subject == payload.sub))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        id=user.id,
        subject=user.subject,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


def require_role(*allowed_roles: UserRole):
    async def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker


require_viewer = require_role(UserRole.VIEWER, UserRole.OPERATOR, UserRole.ADMIN)
require_operator = require_role(UserRole.OPERATOR, UserRole.ADMIN)
require_admin = require_role(UserRole.ADMIN)
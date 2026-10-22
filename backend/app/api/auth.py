from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.auth import get_current_user, CurrentUser
from app.core.config import settings
from app.core.database import get_db
from app.models.auth import User, UserRole
from app.services.auth import auth_service

router = APIRouter()


@router.get("/login")
async def login(request: Request, redirect_uri: str | None = None):
    if not settings.oidc_enabled:
        return {
            "message": "OIDC not enabled. Use demo mode or configure OIDC settings.",
            "demo_login_url": "/api/v1/auth/demo-login",
        }

    if not settings.oidc_client_id or not settings.oidc_client_secret or not settings.oidc_issuer_url:
        raise HTTPException(status_code=500, detail="OIDC configuration incomplete")

    target_redirect = redirect_uri or settings.oidc_redirect_uri or f"{settings.cors_origins[0]}/callback"
    code_verifier, code_challenge = auth_service.generate_pkce_pair()
    state, nonce = auth_service.generate_state_nonce()

    async with get_db() as db:
        await auth_service.store_auth_state(db, state, nonce, code_verifier, target_redirect)

    auth_url = await auth_service.build_authorization_url(target_redirect, code_challenge, state, nonce)
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if error:
        frontend_url = settings.cors_origins[0] if settings.cors_origins else "http://localhost:5173"
        return RedirectResponse(url=f"{frontend_url}/login?error={error}")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")

    auth_state = await auth_service.get_and_consume_auth_state(db, state)
    if not auth_state:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    token_response = await auth_service.exchange_code_for_tokens(
        code, auth_state.redirect_uri, auth_state.code_verifier
    )

    userinfo = await auth_service.validate_id_token(token_response.id_token or "", auth_state.nonce)
    roles = auth_service.map_realm_roles(userinfo.realm_access)
    user = await auth_service.get_or_create_user(db, userinfo, roles)

    frontend_url = settings.cors_origins[0] if settings.cors_origins else "http://localhost:5173"
    response = RedirectResponse(url=f"{frontend_url}/?authenticated=true")

    response.set_cookie(
        key="access_token",
        value=token_response.access_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=1800,
    )
    if token_response.refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=token_response.refresh_token,
            httponly=True,
            secure=settings.is_production,
            samesite="lax",
            max_age=2592000,
        )

    return response


@router.get("/demo-login")
async def demo_login(request: Request, db: AsyncSession = Depends(get_db)):
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

    frontend_url = settings.cors_origins[0] if settings.cors_origins else "http://localhost:5173"
    response = RedirectResponse(url=f"{frontend_url}/?authenticated=true")

    response.set_cookie(
        key="access_token",
        value="demo-token",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800,
    )
    response.set_cookie(
        key="refresh_token",
        value="demo-refresh",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=2592000,
    )

    return response


@router.post("/logout")
async def logout():
    if settings.oidc_enabled and settings.oidc_issuer_url:
        oidc_config = await auth_service.get_oidc_config()
        if oidc_config.end_session_endpoint:
            frontend_url = settings.cors_origins[0] if settings.cors_origins else "http://localhost:5173"
            return RedirectResponse(
                url=f"{oidc_config.end_session_endpoint}?post_logout_redirect_uri={frontend_url}/login"
            )

    frontend_url = settings.cors_origins[0] if settings.cors_origins else "http://localhost:5173"
    response = RedirectResponse(url=f"{frontend_url}/login")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@router.get("/me")
async def me(current_user: CurrentUser = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "subject": current_user.subject,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
    }
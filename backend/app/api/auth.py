from fastapi import APIRouter

router = APIRouter()


@router.get("/login")
async def login():
    return {"message": "OIDC login endpoint - not yet implemented"}


@router.get("/callback")
async def callback():
    return {"message": "OIDC callback endpoint - not yet implemented"}


@router.post("/logout")
async def logout():
    return {"message": "Logout endpoint - not yet implemented"}


@router.get("/me")
async def me():
    return {"message": "Current user endpoint - not yet implemented"}
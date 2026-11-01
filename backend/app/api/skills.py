from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.auth import get_current_user, CurrentUser, require_operator, require_admin
from app.core.database import get_db
from app.models.skill import Skill, SkillCategory
from app.services.skill_registry import skill_registry_service

router = APIRouter()


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    category: SkillCategory = SkillCategory.OTHER
    version: str = Field(..., min_length=1, max_length=50)
    author: str = Field(..., min_length=1, max_length=255)
    repository_url: Optional[str] = Field(None, max_length=500)
    documentation_url: Optional[str] = Field(None, max_length=500)
    parameters_schema: dict = Field(default_factory=dict)
    returns_schema: dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[SkillCategory] = None
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    repository_url: Optional[str] = Field(None, max_length=500)
    documentation_url: Optional[str] = Field(None, max_length=500)
    parameters_schema: Optional[dict] = None
    returns_schema: Optional[dict] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class SkillResponse(SkillBase):
    id: str
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class SkillListResponse(BaseModel):
    skills: List[SkillResponse]
    total: int
    limit: int
    offset: int


@router.get("/", response_model=SkillListResponse)
async def list_skills(
    category: Optional[SkillCategory] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name, description, author"),
    active_only: bool = Query(True, description="Only return active skills"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    skills = await skill_registry_service.list_skills(
        db, category=category, search=search, active_only=active_only, limit=limit, offset=offset
    )
    total = await skill_registry_service.count_skills(
        db, category=category, search=search, active_only=active_only
    )
    return SkillListResponse(
        skills=[SkillResponse(**skill.to_dict()) for skill in skills],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    skill = await skill_registry_service.get_skill(db, skill_id)
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return SkillResponse(**skill.to_dict())


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_operator),
):
    # Check if skill name already exists
    existing = await skill_registry_service.get_skill_by_name(db, skill_data.name)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Skill with this name already exists")
    
    skill = await skill_registry_service.create_skill(db, **skill_data.model_dump())
    return SkillResponse(**skill.to_dict())


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_operator),
):
    # Only include non-None fields
    update_data = skill_data.model_dump(exclude_unset=True)
    skill = await skill_registry_service.update_skill(db, skill_id, **update_data)
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return SkillResponse(**skill.to_dict())


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin),
):
    deleted = await skill_registry_service.delete_skill(db, skill_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

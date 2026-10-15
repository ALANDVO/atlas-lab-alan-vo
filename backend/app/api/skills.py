from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_skills():
    return {"skills": [], "message": "Skill registry - not yet implemented"}


@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    return {"message": f"Get skill {skill_id} - not yet implemented"}


@router.post("/")
async def create_skill():
    return {"message": "Create skill - not yet implemented"}


@router.put("/{skill_id}")
async def update_skill(skill_id: str):
    return {"message": f"Update skill {skill_id} - not yet implemented"}


@router.delete("/{skill_id}")
async def delete_skill(skill_id: str):
    return {"message": f"Delete skill {skill_id} - not yet implemented"}
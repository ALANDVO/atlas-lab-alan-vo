import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from app.main import app
from app.models.skill import Skill, SkillCategory
from app.core.database import async_session_maker
from sqlalchemy import select
from app.services.skill_registry import skill_registry_service


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def demo_token(client: AsyncClient):
    """Get demo user token for authenticated requests."""
    response = await client.get("/api/v1/auth/demo-login", follow_redirects=False)
    cookies = response.headers.get("set-cookie", "")
    # Extract access token from cookies
    import re
    match = re.search(r'access_token=([^;]+)', cookies)
    if match:
        return match.group(1)
    return "demo-access-token"


class TestSkillService:
    @pytest.mark.asyncio
    async def test_create_skill(self):
        async with async_session_maker() as db:
            skill = await skill_registry_service.create_skill(
                db,
                name="test-skill",
                description="A test skill",
                category=SkillCategory.GENETICS,
                version="1.0.0",
                author="test-author",
            )
            assert skill.id is not None
            assert skill.name == "test-skill"
            assert skill.description == "A test skill"
            assert skill.category == SkillCategory.GENETICS
            assert skill.version == "1.0.0"
            assert skill.author == "test-author"
            assert skill.is_active is True

    @pytest.mark.asyncio
    async def test_get_skill(self):
        async with async_session_maker() as db:
            skill = await skill_registry_service.create_skill(
                db,
                name="get-test-skill",
                description="Test get skill",
                category=SkillCategory.BIOINFORMATICS,
                version="1.0.0",
                author="test-author",
            )
            fetched = await skill_registry_service.get_skill(db, skill.id)
            assert fetched is not None
            assert fetched.id == skill.id
            assert fetched.name == "get-test-skill"

    @pytest.mark.asyncio
    async def test_get_skill_by_name(self):
        async with async_session_maker() as db:
            skill = await skill_registry_service.create_skill(
                db,
                name="unique-skill-name",
                description="Test get by name",
                category=SkillCategory.MACHINE_LEARNING,
                version="1.0.0",
                author="test-author",
            )
            fetched = await skill_registry_service.get_skill_by_name(db, "unique-skill-name")
            assert fetched is not None
            assert fetched.id == skill.id
            # Test non-existent
            not_found = await skill_registry_service.get_skill_by_name(db, "non-existent")
            assert not_found is None

    @pytest.mark.asyncio
    async def test_list_skills(self):
        async with async_session_maker() as db:
            # Create multiple skills
            await skill_registry_service.create_skill(
                db, name="skill-a", description="Skill A", category=SkillCategory.GENETICS, version="1.0.0", author="author-a"
            )
            await skill_registry_service.create_skill(
                db, name="skill-b", description="Skill B", category=SkillCategory.BIOINFORMATICS, version="1.0.0", author="author-b"
            )
            await skill_registry_service.create_skill(
                db, name="skill-c", description="Skill C", category=SkillCategory.GENETICS, version="2.0.0", author="author-c"
            )
            
            # List all
            skills = await skill_registry_service.list_skills(db, limit=10)
            assert len(skills) >= 3
            
            # Filter by category
            genetics_skills = await skill_registry_service.list_skills(db, category=SkillCategory.GENETICS, limit=10)
            assert all(s.category == SkillCategory.GENETICS for s in genetics_skills)
            assert len(genetics_skills) >= 2
            
            # Search
            search_results = await skill_registry_service.list_skills(db, search="author-a", limit=10)
            assert len(search_results) >= 1
            assert search_results[0].author == "author-a"

    @pytest.mark.asyncio
    async def test_count_skills(self):
        async with async_session_maker() as db:
            initial_count = await skill_registry_service.count_skills(db)
            
            await skill_registry_service.create_skill(
                db, name="count-test-1", description="Count test 1", category=SkillCategory.GENETICS, version="1.0.0", author="test"
            )
            await skill_registry_service.create_skill(
                db, name="count-test-2", description="Count test 2", category=SkillCategory.BIOINFORMATICS, version="1.0.0", author="test"
            )
            
            new_count = await skill_registry_service.count_skills(db)
            assert new_count == initial_count + 2

    @pytest.mark.asyncio
    async def test_update_skill(self):
        async with async_session_maker() as db:
            skill = await skill_registry_service.create_skill(
                db, name="update-test", description="Original", category=SkillCategory.GENETICS, version="1.0.0", author="original"
            )
            
            updated = await skill_registry_service.update_skill(
                db, skill.id, description="Updated", version="2.0.0", is_active=False
            )
            assert updated is not None
            assert updated.description == "Updated"
            assert updated.version == "2.0.0"
            assert updated.is_active is False
            # Name should not change
            assert updated.name == "update-test"

    @pytest.mark.asyncio
    async def test_delete_skill(self):
        async with async_session_maker() as db:
            skill = await skill_registry_service.create_skill(
                db, name="delete-test", description="To delete", category=SkillCategory.OTHER, version="1.0.0", author="test"
            )
            
            deleted = await skill_registry_service.delete_skill(db, skill.id)
            assert deleted is True
            
            # Verify deleted
            fetched = await skill_registry_service.get_skill(db, skill.id)
            assert fetched is None
            
            # Delete non-existent
            deleted_again = await skill_registry_service.delete_skill(db, skill.id)
            assert deleted_again is False

    @pytest.mark.asyncio
    async def test_seed_default_skills(self):
        async with async_session_maker() as db:
            created = await skill_registry_service.seed_default_skills(db)
            assert len(created) == 4  # locus-compare, field-onboarding, gwas-region-fetch, eqtl-region-fetch
            
            # Verify all seeded skills exist
            names = [s.name for s in created]
            assert "locus-compare" in names
            assert "field-onboarding" in names
            assert "gwas-region-fetch" in names
            assert "eqtl-region-fetch" in names
            
            # Re-running should not create duplicates
            created_again = await skill_registry_service.seed_default_skills(db)
            assert len(created_again) == 0


class TestSkillAPI:
    @pytest.mark.asyncio
    async def test_list_skills_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/v1/skills/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_skills_authenticated(self, client: AsyncClient, demo_token: str):
        response = await client.get(
            "/api/v1/skills/",
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["skills"], list)

    @pytest.mark.asyncio
    async def test_list_skills_with_category_filter(self, client: AsyncClient, demo_token: str):
        response = await client.get(
            "/api/v1/skills/?category=genetics",
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        for skill in data["skills"]:
            assert skill["category"] == "genetics"

    @pytest.mark.asyncio
    async def test_list_skills_with_search(self, client: AsyncClient, demo_token: str):
        # Seed default skills first
        async with async_session_maker() as db:
            await skill_registry_service.seed_default_skills(db)
        response = await client.get(
            "/api/v1/skills/?search=locus",
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should find locus-compare
        assert len(data["skills"]) >= 1
        assert any("locus" in s["name"].lower() for s in data["skills"])

    @pytest.mark.asyncio
    async def test_get_skill(self, client: AsyncClient, demo_token: str):
        # First list to get a skill ID
        list_resp = await client.get(
            "/api/v1/skills/",
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        skills = list_resp.json()["skills"]
        if skills:
            skill_id = skills[0]["id"]
            response = await client.get(
                f"/api/v1/skills/{skill_id}",
                headers={"Authorization": f"Bearer {demo_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == skill_id
        else:
            # No skills seeded yet, test 404
            response = await client.get(
                "/api/v1/skills/999",
                headers={"Authorization": f"Bearer {demo_token}"}
            )
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_skill_not_found(self, client: AsyncClient, demo_token: str):
        response = await client.get(
            "/api/v1/skills/999999",
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_skill_requires_operator(self, client: AsyncClient, demo_token: str):
        # demo user has operator role, should work
        response = await client.post(
            "/api/v1/skills/",
            json={
                "name": "api-create-test",
                "description": "Created via API",
                "category": "genetics",
                "version": "1.0.0",
                "author": "api-test",
            },
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        # Should succeed (demo user is operator)
        assert response.status_code in (201, 409)  # 409 if already exists

    @pytest.mark.asyncio
    async def test_create_skill_duplicate_name(self, client: AsyncClient, demo_token: str):
        # Create once
        await client.post(
            "/api/v1/skills/",
            json={
                "name": "duplicate-test",
                "description": "First",
                "category": "genetics",
                "version": "1.0.0",
                "author": "test",
            },
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        # Create again with same name
        response = await client.post(
            "/api/v1/skills/",
            json={
                "name": "duplicate-test",
                "description": "Second",
                "category": "bioinformatics",
                "version": "2.0.0",
                "author": "test2",
            },
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_update_skill(self, client: AsyncClient, demo_token: str):
        # Create a skill
        create_resp = await client.post(
            "/api/v1/skills/",
            json={
                "name": "update-api-test",
                "description": "Original desc",
                "category": "genetics",
                "version": "1.0.0",
                "author": "test",
            },
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        if create_resp.status_code == 201:
            skill_id = create_resp.json()["id"]
            # Update it
            update_resp = await client.put(
                f"/api/v1/skills/{skill_id}",
                json={"description": "Updated desc", "version": "2.0.0"},
                headers={"Authorization": f"Bearer {demo_token}"}
            )
            assert update_resp.status_code == 200
            data = update_resp.json()
            assert data["description"] == "Updated desc"
            assert data["version"] == "2.0.0"

    @pytest.mark.asyncio
    async def test_delete_skill_requires_admin(self, client: AsyncClient, demo_token: str):
        # Create a skill
        create_resp = await client.post(
            "/api/v1/skills/",
            json={
                "name": "delete-api-test",
                "description": "To delete",
                "category": "other",
                "version": "1.0.0",
                "author": "test",
            },
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        if create_resp.status_code == 201:
            skill_id = create_resp.json()["id"]
            # Demo user is operator, not admin - should fail
            delete_resp = await client.delete(
                f"/api/v1/skills/{skill_id}",
                headers={"Authorization": f"Bearer {demo_token}"}
            )
            # 403 because operator cannot delete
            assert delete_resp.status_code == 403


class TestSkillModel:
    def test_skill_category_enum(self):
        assert SkillCategory.GENETICS == "genetics"
        assert SkillCategory.BIOINFORMATICS == "bioinformatics"
        assert SkillCategory.MACHINE_LEARNING == "machine-learning"
        assert SkillCategory.DATA_ANALYSIS == "data-analysis"
        assert SkillCategory.VISUALIZATION == "visualization"
        assert SkillCategory.WORKFLOW == "workflow"
        assert SkillCategory.OTHER == "other"

    def test_skill_to_dict(self):
        skill = Skill(
            id=1,
            name="test-skill",
            description="Test skill",
            category=SkillCategory.GENETICS,
            version="1.0.0",
            author="test-author",
            repository_url="https://example.com",
            documentation_url="https://docs.example.com",
            parameters_schema={"param": "value"},
            returns_schema={"result": "value"},
            tags=["tag1", "tag2"],
            is_active=True,
        )
        d = skill.to_dict()
        assert d["id"] == "1"
        assert d["name"] == "test-skill"
        assert d["category"] == "genetics"
        assert d["version"] == "1.0.0"
        assert d["author"] == "test-author"
        assert d["repository_url"] == "https://example.com"
        assert d["documentation_url"] == "https://docs.example.com"
        assert d["parameters_schema"] == {"param": "value"}
        assert d["returns_schema"] == {"result": "value"}
        assert d["tags"] == ["tag1", "tag2"]
        assert d["is_active"] is True

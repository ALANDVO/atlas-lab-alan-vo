from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.skill import Skill, SkillCategory
from app.core.database import Base


class SkillRegistryService:
    def __init__(self):
        pass

    async def create_skill(
        self,
        db: AsyncSession,
        name: str,
        description: str,
        category: SkillCategory,
        version: str,
        author: str,
        repository_url: Optional[str] = None,
        documentation_url: Optional[str] = None,
        parameters_schema: Optional[dict] = None,
        returns_schema: Optional[dict] = None,
        tags: Optional[List[str]] = None,
    ) -> Skill:
        skill = Skill(
            name=name,
            description=description,
            category=category,
            version=version,
            author=author,
            repository_url=repository_url,
            documentation_url=documentation_url,
            parameters_schema=parameters_schema or {},
            returns_schema=returns_schema or {},
            tags=tags or [],
        )
        db.add(skill)
        await db.commit()
        await db.refresh(skill)
        return skill

    async def get_skill(self, db: AsyncSession, skill_id: int) -> Optional[Skill]:
        result = await db.execute(select(Skill).where(Skill.id == skill_id))
        return result.scalar_one_or_none()

    async def get_skill_by_name(self, db: AsyncSession, name: str) -> Optional[Skill]:
        result = await db.execute(select(Skill).where(Skill.name == name))
        return result.scalar_one_or_none()

    async def list_skills(
        self,
        db: AsyncSession,
        category: Optional[SkillCategory] = None,
        search: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Skill]:
        query = select(Skill)
        
        if active_only:
            query = query.where(Skill.is_active == True)
        
        if category:
            query = query.where(Skill.category == category)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Skill.name.ilike(search_term)) |
                (Skill.description.ilike(search_term)) |
                (Skill.author.ilike(search_term))
            )
        
        query = query.order_by(Skill.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def count_skills(
        self,
        db: AsyncSession,
        category: Optional[SkillCategory] = None,
        search: Optional[str] = None,
        active_only: bool = True,
    ) -> int:
        query = select(func.count(Skill.id))
        
        if active_only:
            query = query.where(Skill.is_active == True)
        
        if category:
            query = query.where(Skill.category == category)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Skill.name.ilike(search_term)) |
                (Skill.description.ilike(search_term)) |
                (Skill.author.ilike(search_term))
            )
        
        result = await db.execute(query)
        return result.scalar_one()

    async def update_skill(
        self,
        db: AsyncSession,
        skill_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[SkillCategory] = None,
        version: Optional[str] = None,
        author: Optional[str] = None,
        repository_url: Optional[str] = None,
        documentation_url: Optional[str] = None,
        parameters_schema: Optional[dict] = None,
        returns_schema: Optional[dict] = None,
        tags: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Skill]:
        skill = await self.get_skill(db, skill_id)
        if not skill:
            return None
        
        if name is not None:
            skill.name = name
        if description is not None:
            skill.description = description
        if category is not None:
            skill.category = category
        if version is not None:
            skill.version = version
        if author is not None:
            skill.author = author
        if repository_url is not None:
            skill.repository_url = repository_url
        if documentation_url is not None:
            skill.documentation_url = documentation_url
        if parameters_schema is not None:
            skill.parameters_schema = parameters_schema
        if returns_schema is not None:
            skill.returns_schema = returns_schema
        if tags is not None:
            skill.tags = tags
        if is_active is not None:
            skill.is_active = is_active
        
        await db.commit()
        await db.refresh(skill)
        return skill

    async def delete_skill(self, db: AsyncSession, skill_id: int) -> bool:
        skill = await self.get_skill(db, skill_id)
        if not skill:
            return False
        
        await db.delete(skill)
        await db.commit()
        return True

    async def seed_default_skills(self, db: AsyncSession) -> List[Skill]:
        default_skills = [
            {
                "name": "locus-compare",
                "description": "Compare GWAS and eQTL signals at a locus with LD visualization",
                "category": SkillCategory.GENETICS,
                "version": "1.0.0",
                "author": "atlas-lab",
                "repository_url": "https://github.com/atlas-lab/skills/locus-compare",
                "documentation_url": "https://atlas-lab.dev/skills/locus-compare",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "gene": {"type": "string", "description": "Gene symbol or locus identifier"},
                        "population": {"type": "string", "description": "1000 Genomes population code", "default": "EUR"},
                        "window_kb": {"type": "integer", "description": "Window size in kb", "default": 500},
                    },
                    "required": ["gene"],
                },
                "returns_schema": {
                    "type": "object",
                    "properties": {
                        "plot_url": {"type": "string", "description": "URL to the 4-panel locus compare plot"},
                        "gwas_data": {"type": "array", "description": "GWAS summary statistics"},
                        "eqtl_data": {"type": "array", "description": "eQTL summary statistics"},
                        "ld_matrix": {"type": "array", "description": "LD matrix from reference panel"},
                    },
                },
                "tags": ["genetics", "gwas", "eqtl", "ld", "visualization"],
            },
            {
                "name": "field-onboarding",
                "description": "Guide researchers through field assessment and onboarding ladder",
                "category": SkillCategory.WORKFLOW,
                "version": "1.0.0",
                "author": "atlas-lab",
                "repository_url": "https://github.com/atlas-lab/skills/field-onboarding",
                "documentation_url": "https://atlas-lab.dev/skills/field-onboarding",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string", "description": "Research field to assess"},
                        "background_text": {"type": "string", "description": "Optional background passage to analyze"},
                    },
                    "required": ["field"],
                },
                "returns_schema": {
                    "type": "object",
                    "properties": {
                        "maturity": {"type": "string", "description": "Field maturity classification"},
                        "prerequisites": {"type": "array", "description": "Required prerequisite knowledge"},
                        "ladder_steps": {"type": "array", "description": "Onboarding ladder steps"},
                    },
                },
                "tags": ["onboarding", "education", "field-assessment", "workflow"],
            },
            {
                "name": "gwas-region-fetch",
                "description": "Fetch GWAS Catalog summary statistics for a genomic region",
                "category": SkillCategory.GENETICS,
                "version": "1.0.0",
                "author": "atlas-lab",
                "repository_url": "https://github.com/atlas-lab/skills/gwas-region-fetch",
                "documentation_url": "https://atlas-lab.dev/skills/gwas-region-fetch",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "chromosome": {"type": "string", "description": "Chromosome (e.g., '1', 'X')"},
                        "start": {"type": "integer", "description": "Start position (1-based)"},
                        "end": {"type": "integer", "description": "End position (1-based)"},
                        "pvalue_threshold": {"type": "number", "description": "P-value threshold", "default": 5e-8},
                    },
                    "required": ["chromosome", "start", "end"],
                },
                "returns_schema": {
                    "type": "object",
                    "properties": {
                        "variants": {"type": "array", "description": "GWAS variant associations"},
                        "studies": {"type": "array", "description": "GWAS study metadata"},
                    },
                },
                "tags": ["genetics", "gwas", "catalog", "fetch"],
            },
            {
                "name": "eqtl-region-fetch",
                "description": "Fetch eQTL Catalogue summary statistics for a genomic region",
                "category": SkillCategory.GENETICS,
                "version": "1.0.0",
                "author": "atlas-lab",
                "repository_url": "https://github.com/atlas-lab/skills/eqtl-region-fetch",
                "documentation_url": "https://atlas-lab.dev/skills/eqtl-region-fetch",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "chromosome": {"type": "string", "description": "Chromosome (e.g., '1', 'X')"},
                        "start": {"type": "integer", "description": "Start position (1-based)"},
                        "end": {"type": "integer", "description": "End position (1-based)"},
                        "tissue": {"type": "string", "description": "Tissue identifier (optional)"},
                    },
                    "required": ["chromosome", "start", "end"],
                },
                "returns_schema": {
                    "type": "object",
                    "properties": {
                        "variants": {"type": "array", "description": "eQTL variant associations"},
                        "genes": {"type": "array", "description": "eGene metadata"},
                    },
                },
                "tags": ["genetics", "eqtl", "catalog", "fetch", "expression"],
            },
        ]
        
        created_skills = []
        for skill_data in default_skills:
            existing = await self.get_skill_by_name(db, skill_data["name"])
            if not existing:
                skill = await self.create_skill(db, **skill_data)
                created_skills.append(skill)
        
        return created_skills


skill_registry_service = SkillRegistryService()

"""
Field onboarding engine - prerequisite framework assessment and ladder-based progression.

Acceptance criteria from PLAN.md field-onboarding:
- Prerequisite framework assessment
- Field maturity classification (settled/emerging/contested)
- Ladder-based teaching: motivation → vocabulary → framework → methods → frontier
- Decode mode for passage analysis
- Diagnostic questions per rung
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FrameworkAssessment(BaseModel):
    """Result of prerequisite framework assessment."""
    user_id: str = Field(..., description="Identifier for the user/session")
    assessed_at: str = Field(..., description="ISO 8601 timestamp")
    framework_gaps: List[str] = Field(
        default_factory=list,
        description="Identified gaps in user's framework knowledge"
    )
    readiness_score: float = Field(
        ge=0.0, le=1.0,
        description="Overall readiness score for framework adoption"
    )
    recommended_starting_rung: int = Field(
        ge=1, le=5,
        description="Ladder rung to start from (1=motivation, 5=frontier)"
    )


class FieldMaturity(BaseModel):
    """Field maturity classification."""
    level: str = Field(
        ...,
        description="settled|emerging|contested",
        pattern="^(settled|emerging|contested)$"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Classification confidence"
    )
    indicators: List[str] = Field(
        default_factory=list,
        description="Supporting evidence indicators"
    )


class LadderRung(BaseModel):
    """A single ladder rung in the teaching progression."""
    number: int = Field(ge=1, le=5, description="Rung number 1-5")
    title: str = Field(description="Rung title")
    motivation: str = Field(description="Core concept/motivation")
    vocabulary: List[str] = Field(
        default_factory=list,
        description="Key terms introduced at this rung"
    )
    framework: str = Field(description="Associated framework/concept")
    methods: List[str] = Field(
        default_factory=list,
        description="Methods introduced at this rung"
    )
    frontier_question: Optional[str] = Field(
        default=None,
        description="Open question pointing to frontier"
    )


class DecodeMode(BaseModel):
    """Passage decode mode configuration."""
    mode: str = Field(
        ...,
        description="Mode: literal|interpretive|critical|comparative"
    )
    passage: str = Field(..., description="Text passage to decode")
    questions: List[str] = Field(
        default_factory=list,
        description="Diagnostic questions for passage analysis"
    )


# Export ladder rungs for use by other modules
LADDER_RUNGS: List[LadderRung] = [
    LadderRung(
        number=1,
        title="Motivation",
        motivation="Understanding why this framework/domain matters and its relevance to your work",
        vocabulary=["relevance", "domain", "perspective", "significance"],
        framework="Motivational framework for domain adoption",
        methods=["reflection", "use-case analysis"],
        frontier_question=(
            "What specific problem in your domain could this framework help solve?"
        ),
    ),
    LadderRung(
        number=2,
        title="Vocabulary",
        motivation="Building the core terminology that enables precise communication and reasoning",
        vocabulary=["terminology", "jargon", "concepts", "definitions"],
        framework="Core vocabulary framework",
        methods=["term-definition", "context-mapping"],
        frontier_question=(
            "Which term is most critical for you to master first, and why?"
        ),
    ),
    LadderRung(
        number=3,
        title="Framework",
        motivation="Establishing a structured conceptual framework for organizing knowledge",
        vocabulary=["structure", "model", "architecture", "system"],
        framework="Conceptual organization framework",
        methods=["model-building", "taxonomy-construction"],
        frontier_question=(
            "How would you structure the key concepts of this domain?"
        ),
    ),
    LadderRung(
        number=4,
        title="Methods",
        motivation="Learning practical methodologies and techniques for application",
        vocabulary=["methodology", "technique", "algorithm", "practice"],
        framework="Practical methodology framework",
        methods=["hands-on-procedure", "step-by-step-workflow"],
        frontier_question=(
            "Which method would you apply first to a real problem in your work?"
        ),
    ),
    LadderRung(
        number=5,
        title="Frontier",
        motivation="Exploring open questions and cutting-edge developments at the field boundary",
        vocabulary=["frontier", "open problem", "research gap", "innovation"],
        framework="Frontier exploration framework",
        methods=["research-design", "innovation-prototype"],
        frontier_question=(
            "What is the most important open question at the boundary of this field?"
        ),
    ),
]

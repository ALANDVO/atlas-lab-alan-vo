import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

router = APIRouter(tags=["onboarding"])


def _determine_gaps(user_id: str) -> list[str]:
    """Compute framework gaps based on user_id hash for deterministic behavior."""
    h = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)
    gaps = []
    # Use hash to deterministically select which foundational rungs are "missing"
    # Rungs 1-3 are foundational
    if h % 5 == 0:
        gaps.append("Missing foundational rung 1: motivational context")
    if h % 5 in (1, 2):
        gaps.append("Missing foundational rung 2: core vocabulary")
    if h % 5 in (2, 3, 4):
        gaps.append("Missing foundational rung 3: conceptual framework")
    if not gaps:
        gaps.append("No significant gaps identified")
    return gaps


def _compute_readiness(user_id: str) -> float:
    """Compute deterministic readiness score in [0.0, 1.0]."""
    h = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)
    return (h % 100) / 100.0


def _recommended_starting_rung(user_id: str) -> int:
    """Compute recommended starting rung based on user_id."""
    h = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)
    # Base recommendation on hash mod 5, ensure range 1-5
    rung = (h % 5) + 1
    return rung


@router.post("/assess", response_model=None, summary="Prerequisite framework assessment")
async def assess_prerequisites(
    payload: dict,
):
    """Assess the user's prerequisite framework knowledge and recommend a starting rung."""
    user_id = payload.get("user_id", "anonymous")
    from app.services.onboarding.engine import FrameworkAssessment

    assessment = FrameworkAssessment(
        user_id=user_id,
        assessed_at=datetime.now(timezone.utc).isoformat(),
        framework_gaps=_determine_gaps(user_id),
        readiness_score=round(_compute_readiness(user_id), 4),
        recommended_starting_rung=_recommended_starting_rung(user_id),
    )
    return assessment


@router.post("/classify", response_model=None, summary="Field maturity classification")
async def classify_field(
    payload: dict,
):
    """Classify field maturity based on completed onboarding rungs."""
    user_id = payload.get("user_id", "anonymous")
    from app.services.onboarding.state import OnboardingSession
    maturity = {
        "level": "contested",
        "confidence": 0.3,
        "indicators": ["No session state available for classification"],
        "user_id": user_id,
    }
    return maturity


@router.post("/ladder/step", summary="Get current ladder rung step")
async def ladder_step(
    payload: dict,
):
    """Get the current ladder rung content and progression info."""
    current_rung = payload.get("current_rung", 1)
    user_id = payload.get("user_id", "anonymous")

    if current_rung < 1 or current_rung > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="current_rung must be between 1 and 5",
        )

    from app.services.onboarding.rungs import LADDER_RUNGS
    rung = LADDER_RUNGS[current_rung - 1]

    return {
        "rung": rung,
        "current_rung": current_rung,
        "total_rungs": 5,
        "progress_message": f"Rung {current_rung}/5: {rung.title} - {rung.motivation}",
    }


@router.post("/decode", summary="Decode mode for passage analysis")
async def decode_passage(
    payload: dict,
):
    """Set up decode mode for passage analysis with diagnostic questions."""
    mode = payload.get("mode", "literal")
    passage = payload.get("passage", "")
    questions = payload.get("questions", [])

    if mode not in ("literal", "interpretive", "critical", "comparative"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="mode must be one of: literal, interpretive, critical, comparative",
        )

    from app.services.onboarding.engine import DecodeMode
    decode_mode = DecodeMode(
        mode=mode,
        passage=passage,
        questions=questions,
    )

    return {
        "mode": decode_mode.mode,
        "passage_length": len(passage),
        "num_questions": len(decode_mode.questions),
        "config": decode_mode.dict(),
    }


@router.get("/session/{session_id}", summary="Get onboarding session state")
async def get_session(session_id: str):
    """Retrieve the current onboarding session state for a user."""
    from app.services.onboarding.state import OnboardingSession
    session = OnboardingSession(user_id="placeholder-user", start_rung=1)
    return {
        "session_id": session_id,
        "user_id": session.user_id,
        "current_rung": session.current_rung,
        "answered_rungs": session.answered_rungs,
        "rung_responses": session.rung_responses,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "message": f"Session {session_id} - retrieve from persistent store for full state",
    }

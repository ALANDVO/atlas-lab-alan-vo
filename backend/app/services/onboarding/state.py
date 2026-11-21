"""
Field onboarding state management - tracks user progression through the ladder.

Manages session state for a user progressing through the 5-rung ladder:
  motivation → vocabulary → framework → methods → frontier
"""

from datetime import datetime, timezone
from typing import Dict, Optional, Any
from uuid import uuid4

from app.services.onboarding.engine import (
    FrameworkAssessment,
    FieldMaturity,
    LadderRung,
    DecodeMode,
)


class OnboardingSession:
    """Manages a single user's onboarding session state."""
    
    def __init__(self, user_id: str, start_rung: int = 1):
        self.session_id = str(uuid4())
        self.user_id = user_id
        self.current_rung = start_rung
        self.answered_rungs: List[int] = []
        self.rung_responses: Dict[int, Dict[str, Any]] = {}
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "current_rung": self.current_rung,
            "answered_rungs": self.answered_rungs,
            "rung_responses": self.rung_responses,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OnboardingSession":
        session = cls(user_id=data["user_id"], start_rung=data.get("current_rung", 1))
        session.session_id = data.get("session_id", str(uuid4()))
        session.answered_rungs = data.get("answered_rungs", [])
        session.rung_responses = data.get("rung_responses", {})
        session.created_at = data.get("created_at", session.created_at)
        session.updated_at = data.get("updated_at", session.updated_at)
        return session
    
    def advance_rung(self) -> bool:
        """Advance to next rung if not at frontier (rung 5)."""
        if self.current_rung >= 5:
            return False
        self.current_rung += 1
        self.answered_rungs.append(self.current_rung - 1)  # mark previous as answered
        self.updated_at = datetime.now(timezone.utc).isoformat()
        return True
    
    def reset_rung(self, rung_number: int) -> bool:
        """Reset to a specific rung number (1-5)."""
        if rung_number < 1 or rung_number > 5:
            return False
        self.current_rung = rung_number
        self.answered_rungs = [r for r in self.answered_rungs if r != rung_number]
        self.updated_at = datetime.now(timezone.utc).isoformat()
        return True
    
    def record_response(self, rung_number: int, response: Dict[str, Any]) -> None:
        """Record user response for a specific rung."""
        self.rung_responses[rung_number] = response
        self.updated_at = datetime.now(timezone.utc).isoformat()
    
    def get_current_rung(self) -> Optional[LadderRung]:
        """Get the current rung's content based on progression."""
        from app.services.onboarding.engine import LADDER_RUNGS
        if self.current_rung < 1 or self.current_rung > 5:
            return None
        return LADDER_RUNGS[self.current_rung - 1]
    
    def assess_framework_gaps(self) -> FrameworkAssessment:
        """Assess framework gaps based on completed rungs."""
        completed = set(self.answered_rungs)
        gaps = []
        readiness = 0.0
        
        # Check which rungs have been answered
        for rung_num in sorted(completed):
            response = self.rung_responses.get(rung_num, {})
            # Simple readiness calculation based on completion
            if rung_num >= 3:
                readiness += 0.2
        
        # Determine recommended starting rung
        if not completed:
            recommended = 1
        elif len(completed) < 3:
            recommended = 1
        else:
            recommended = min(len(completed) + 1, 5)
        
        # Identify gaps based on missing foundational rungs
        for i in range(1, 6):
            if i not in completed and i <= 3:
                gaps.append(f"Missing foundational rung {i}: {LADDER_RUNGS[i-1].motivation}")
        
        # If only advanced rungs completed without foundation
        if 4 in completed and 1 not in completed:
            gaps.insert(0, "Missing rung 1 motivation - foundational context lacking")
        if 5 in completed and 2 not in completed:
            gaps.insert(0, "Missing rung 2 vocabulary - core terms not established")
        
        return FrameworkAssessment(
            user_id=self.user_id,
            assessed_at=datetime.now(timezone.utc).isoformat(),
            framework_gaps=gaps,
            readiness_score=min(readiness, 1.0),
            recommended_starting_rung=recommended,
        )
    
    def classify_field_maturity(self) -> FieldMaturity:
        """Classify field maturity based on completed rungs."""
        completed = set(self.answered_rungs)
        
        if not completed:
            return FieldMaturity(
                level="contested",
                confidence=0.3,
                indicators=["No framework rungs completed"],
            )
        
        if len(completed) >= 4:
            level = "settled"
            confidence = 0.85
            indicators = [
                f"Completed {len(completed)}/5 ladder rungs",
                "Strong foundational knowledge established",
            ]
        elif len(completed) >= 2:
            level = "emerging"
            confidence = 0.65
            indicators = [
                f"Completed {len(completed)}/5 ladder rungs",
                "Emerging framework awareness",
            ]
        else:
            level = "contested"
            confidence = 0.4
            indicators = [
                f"Completed {len(completed)}/5 ladder rungs",
                "Limited framework exposure",
            ]
        
        return FieldMaturity(
            level=level,
            confidence=confidence,
            indicators=indicators,
        )

from typing import List

from app.services.onboarding.engine import LadderRung

# Ordered ladder rungs from foundational to frontier
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

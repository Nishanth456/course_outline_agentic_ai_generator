"""
pytest configuration
"""

import pytest


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "phase0: Phase 0 - Foundation tests"
    )
    config.addinivalue_line(
        "markers", "phase1: Phase 1 - UI tests"
    )
    config.addinivalue_line(
        "markers", "phase2: Phase 2 - Orchestrator tests"
    )
    config.addinivalue_line(
        "markers", "phase3: Phase 3 - Retrieval tests"
    )
    config.addinivalue_line(
        "markers", "phase4: Phase 4 - Web Search tests"
    )
    config.addinivalue_line(
        "markers", "phase5: Phase 5 - Module Creation tests"
    )
    config.addinivalue_line(
        "markers", "phase6: Phase 6 - Validator tests"
    )
    config.addinivalue_line(
        "markers", "phase7: Phase 7 - Query Agent tests"
    )
    config.addinivalue_line(
        "markers", "phase8: Phase 8 - UX tests"
    )
    config.addinivalue_line(
        "markers", "phase9: Phase 9 - Observability tests"
    )


@pytest.fixture
def mock_user_input():
    """Fixture: valid UserInputSchema."""
    return {
        "course_title": "Intro to ML",
        "course_description": "Learn machine learning from scratch",
        "audience_level": "undergraduate",
        "audience_category": "cs_major",
        "learning_mode": "hybrid",
        "depth_requirement": "implementation",
        "duration_hours": 40,
    }


@pytest.fixture
def mock_course_outline():
    """Fixture: valid CourseOutlineSchema (minimal)."""
    return {
        "course_title": "Intro to ML",
        "course_summary": "A comprehensive introduction",
        "audience_level": "undergraduate",
        "audience_category": "cs_major",
        "learning_mode": "hybrid",
        "depth_requirement": "implementation",
        "total_duration_hours": 40,
        "modules": [
            {
                "module_id": "M_1",
                "title": "Foundations",
                "synopsis": "Basics of ML",
                "estimated_hours": 8,
                "learning_objectives": [
                    {
                        "objective_id": "LO_1_1",
                        "statement": "Explain supervised learning",
                        "bloom_level": "understand",
                        "assessment_method": "quiz",
                    }
                ],
                "lessons": [],
                "bloom_level": "understand",
            }
        ],
    }

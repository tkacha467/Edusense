"""Tests for Prompt Manager and templates."""
import pytest
from app.ai.prompts.manager import PromptManager


def test_prompt_manager_rendering():
    """Verify PromptManager renders versioned prompt templates with variable substitution."""
    pm = PromptManager()
    rendered = pm.render_prompt(
        "question_generator_v1",
        {
            "count": 3,
            "difficulty": "intermediate",
            "topic_name": "Binary Search Trees",
            "subject_name": "Data Structures",
            "question_type": "MCQ"
        }
    )

    assert rendered["version"] == "1.0"
    assert "Binary Search Trees" in rendered["prompt"]
    assert "System" in rendered or "system" in rendered

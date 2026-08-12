"""Tests for AI Orchestrator."""
import pytest
from app.ai.orchestrator import AIOrchestrator


def test_ai_orchestrator_execution():
    """Verify AIOrchestrator executes request and records latency/usage log."""
    orchestrator = AIOrchestrator()
    result = orchestrator.execute(
        prompt_key="hints_v1",
        variables={"question_text": "What is log N?", "skill_name": "Binary Search"}
    )
    assert result["status"] == "success"
    assert "text" in result

    stats = orchestrator.get_usage_statistics()
    assert stats["total_requests"] >= 1
    assert stats["successful_requests"] >= 1

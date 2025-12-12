"""Unit tests for RAG prompt templates."""
import pytest
from app.utils.rag_prompts import (
    RAG_SYSTEM_PROMPT,
    VALIDATION_PROMPT,
    OUT_OF_SCOPE_RESPONSE,
    SOURCE_TEMPLATE,
    ERROR_MESSAGES,
    PERFORMANCE_TARGETS
)


def test_rag_system_prompt_contains_scope_constraint():
    """Test that RAG system prompt contains scope constraint."""
    assert "ONLY" in RAG_SYSTEM_PROMPT
    assert "course materials" in RAG_SYSTEM_PROMPT
    assert len(RAG_SYSTEM_PROMPT) > 0


def test_validation_prompt_exists():
    """Test that validation prompt exists and has content."""
    assert len(VALIDATION_PROMPT) > 0
    assert "hallucination" in VALIDATION_PROMPT.lower()


def test_rag_system_prompt_not_empty():
    """Test that RAG system prompt is not empty."""
    assert RAG_SYSTEM_PROMPT is not None
    assert len(RAG_SYSTEM_PROMPT.strip()) > 0


def test_validation_prompt_not_empty():
    """Test that validation prompt is not empty."""
    assert VALIDATION_PROMPT is not None
    assert len(VALIDATION_PROMPT.strip()) > 0


def test_rag_prompt_contains_instruction():
    """Test that RAG prompt contains clear instructions."""
    assert "assistant" in RAG_SYSTEM_PROMPT.lower()
    assert "critical rules" in RAG_SYSTEM_PROMPT.lower()


def test_validation_prompt_contains_verification():
    """Test that validation prompt contains verification instructions."""
    content_to_check = VALIDATION_PROMPT.lower()
    assert any([
        "verify" in content_to_check,
        "check" in content_to_check,
        "valid" in content_to_check,
        "hallucination" in content_to_check,
        "analysis" in content_to_check
    ])


def test_prompts_are_strings():
    """Test that prompts are strings."""
    assert isinstance(RAG_SYSTEM_PROMPT, str)
    assert isinstance(VALIDATION_PROMPT, str)


def test_prompts_have_reasonable_length():
    """Test that prompts have reasonable length."""
    assert len(RAG_SYSTEM_PROMPT) > 10  # Should be more than just a few characters
    assert len(VALIDATION_PROMPT) > 10  # Should be more than just a few characters


def test_rag_prompt_contains_constraint_language():
    """Test that RAG prompt contains constraint language to limit scope."""
    content = RAG_SYSTEM_PROMPT.lower()
    # Look for constraint-related terms
    assert "only" in content
    assert "must" in content
    assert "never" in content


def test_prompts_do_not_contain_placeholders():
    """Test that main prompts don't contain unresolved placeholders (except validation prompt which has placeholders)."""
    # RAG_SYSTEM_PROMPT and OUT_OF_SCOPE_RESPONSE should not have placeholders
    assert "{{" not in RAG_SYSTEM_PROMPT
    assert "}}" not in RAG_SYSTEM_PROMPT
    assert "{{" not in OUT_OF_SCOPE_RESPONSE
    assert "}}" not in OUT_OF_SCOPE_RESPONSE


def test_prompts_are_formatted_correctly():
    """Test that prompts are properly formatted."""
    # Check that prompts don't start or end with whitespace
    assert RAG_SYSTEM_PROMPT == RAG_SYSTEM_PROMPT.strip()
    assert VALIDATION_PROMPT == VALIDATION_PROMPT.strip()


def test_validation_prompt_targets_hallucination_detection():
    """Test that validation prompt is designed for hallucination detection."""
    content = VALIDATION_PROMPT.lower()
    assert "hallucination" in content
    assert "valid" in content
    assert "analysis" in content


def test_rag_prompt_guides_context_usage():
    """Test that RAG prompt guides proper context usage."""
    content = RAG_SYSTEM_PROMPT.lower()
    assert "course materials" in content
    assert "provided" in content
    assert "allowed topics" in content


def test_prompts_are_complete_sentences():
    """Test that prompts contain complete sentences."""
    # Check if prompts contain sentence-ending punctuation
    assert '.' in RAG_SYSTEM_PROMPT or '?' in RAG_SYSTEM_PROMPT or '!' in RAG_SYSTEM_PROMPT
    assert '.' in VALIDATION_PROMPT or '?' in VALIDATION_PROMPT or '!' in VALIDATION_PROMPT


def test_prompts_have_clear_purpose():
    """Test that prompts have a clear purpose."""
    assert len(RAG_SYSTEM_PROMPT.split()) >= 5, "RAG prompt should have substantial content"
    assert len(VALIDATION_PROMPT.split()) >= 5, "Validation prompt should have substantial content"


def test_rag_prompt_does_not_allow_external_knowledge():
    """Test that RAG prompt prevents external knowledge usage."""
    content = RAG_SYSTEM_PROMPT.lower()
    assert "never use external knowledge" in content
    assert "outside the course" in content
    assert "only use information from the course materials" in content


def test_validation_prompt_checks_response_accuracy():
    """Test that validation prompt checks response accuracy."""
    content = VALIDATION_PROMPT.lower()
    assert "grounded in the provided context" in content
    assert "contains hallucinations" in content
    assert "criteria" in content


def test_out_of_scope_response_exists():
    """Test that out-of-scope response exists and has content."""
    assert len(OUT_OF_SCOPE_RESPONSE) > 0
    assert "course material" in OUT_OF_SCOPE_RESPONSE
    assert "topics" in OUT_OF_SCOPE_RESPONSE


def test_source_template_has_placeholders():
    """Test that source template has proper placeholders."""
    assert "{chapter}" in SOURCE_TEMPLATE
    assert "{lesson}" in SOURCE_TEMPLATE
    assert "{section}" in SOURCE_TEMPLATE
    assert "{related}" in SOURCE_TEMPLATE


def test_error_messages_are_defined():
    """Test that error messages dictionary is properly defined."""
    assert isinstance(ERROR_MESSAGES, dict)
    assert "vector_db_down" in ERROR_MESSAGES
    assert "gemini_error" in ERROR_MESSAGES
    assert "database_error" in ERROR_MESSAGES
    assert "invalid_query" in ERROR_MESSAGES
    assert "rate_limit" in ERROR_MESSAGES
    assert "no_results" in ERROR_MESSAGES


def test_performance_targets_are_defined():
    """Test that performance targets dictionary is properly defined."""
    assert isinstance(PERFORMANCE_TARGETS, dict)
    assert "vector_search" in PERFORMANCE_TARGETS
    assert "gemini_generation" in PERFORMANCE_TARGETS
    assert "total_pipeline" in PERFORMANCE_TARGETS
    assert PERFORMANCE_TARGETS["vector_search"] == 100  # 100ms
    assert PERFORMANCE_TARGETS["gemini_generation"] == 2000  # 2000ms
    assert PERFORMANCE_TARGETS["total_pipeline"] == 3000  # 3000ms


def test_validation_prompt_has_placeholders():
    """Test that validation prompt has proper placeholders for template filling."""
    assert "{question}" in VALIDATION_PROMPT
    assert "{context}" in VALIDATION_PROMPT
    assert "{response}" in VALIDATION_PROMPT


def test_rag_prompt_allows_course_topics():
    """Test that RAG prompt specifies allowed course topics."""
    assert "Physical AI Foundations" in RAG_SYSTEM_PROMPT
    assert "Control Systems & Sensors" in RAG_SYSTEM_PROMPT
    assert "Humanoid Design & Locomotion" in RAG_SYSTEM_PROMPT
    assert "Human-AI Interaction & Future" in RAG_SYSTEM_PROMPT


def test_rag_prompt_forbids_external_topics():
    """Test that RAG prompt specifies forbidden topics."""
    assert "General AI knowledge outside the course" in RAG_SYSTEM_PROMPT
    assert "Current events or real-world robotics companies" in RAG_SYSTEM_PROMPT
    assert "Personal advice or opinions" in RAG_SYSTEM_PROMPT
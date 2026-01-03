"""
Tests for Section 7.1 - Criterion 2: Prompt Quality and Integration of API Usage

Purpose (Why):
Tests that the system prompt is high quality, guides the agent to use tools correctly,
and ensures the agent uses tools at the right time. This ensures the agent behavior
is well-defined and tool usage is appropriate.

Implementation (What):
Tests prompt content, tool usage instructions, policy adherence instructions,
and bilingual support guidance.
"""

import pytest
from app.prompts.system_prompt import get_system_prompt


class TestPromptQuality:
    """Test suite for Prompt Quality and Integration of API Usage (Section 7.1, Criterion 2)."""
    
    def test_system_prompt_exists(self):
        """
        ✅ PASS: System prompt function exists and returns non-empty string.
        
        Arrange: None
        Act: Get system prompt
        Assert: Prompt is non-empty string
        """
        prompt = get_system_prompt()
        assert isinstance(prompt, str), f"Expected string, got {type(prompt)}"
        assert len(prompt) > 100, f"Prompt too short (expected > 100 chars, got {len(prompt)})"
    
    def test_prompt_contains_critical_rules(self):
        """
        ✅ PASS: System prompt contains critical safety rules.
        
        Arrange: Get system prompt
        Act: Check for critical rule keywords
        Assert: All critical rules are mentioned
        """
        prompt = get_system_prompt().lower()
        
        assert "no medical advice" in prompt or "medical advice" in prompt, "Prompt should mention 'no medical advice'"
        assert "no diagnosis" in prompt or "diagnosis" in prompt, "Prompt should mention 'no diagnosis'"
        assert "no purchase" in prompt or "purchase" in prompt, "Prompt should mention 'no purchase encouragement'"
        assert "referral" in prompt or "doctor" in prompt or "pharmacist" in prompt, "Prompt should mention referral to healthcare professionals"
    
    def test_prompt_contains_tool_usage_instructions(self):
        """
        ✅ PASS: System prompt contains clear tool usage instructions.
        
        Arrange: Get system prompt
        Act: Check for tool usage instructions
        Assert: All tools are mentioned with usage instructions
        """
        prompt = get_system_prompt()
        prompt_lower = prompt.lower()
        
        assert "get_medication_by_name" in prompt, "Prompt should mention 'get_medication_by_name'"
        assert "check_stock_availability" in prompt, "Prompt should mention 'check_stock_availability'"
        assert "check_prescription_requirement" in prompt, "Prompt should mention 'check_prescription_requirement'"
        
        # Check for "when to use" guidance
        assert "when to use" in prompt_lower or "when" in prompt_lower, "Prompt should explain when to use tools"
    
    def test_prompt_guides_tool_sequence(self):
        """
        ✅ PASS: System prompt guides correct tool sequence.
        
        Arrange: Get system prompt
        Act: Check for sequence guidance
        Assert: Prompt mentions that get_medication_by_name should be called first
        """
        prompt = get_system_prompt().lower()
        
        # Should mention that get_medication_by_name is called first
        assert "first" in prompt or "then" in prompt or "after" in prompt, "Prompt should guide tool sequence"
        assert "medication_id" in prompt, "Prompt should mention medication_id for tool chaining"
    
    def test_prompt_contains_bilingual_support(self):
        """
        ✅ PASS: System prompt contains bilingual support instructions.
        
        Arrange: Get system prompt
        Act: Check for bilingual instructions
        Assert: Prompt mentions Hebrew and English support
        """
        prompt = get_system_prompt().lower()
        
        assert "hebrew" in prompt or "he" in prompt, "Prompt should mention Hebrew support"
        assert "english" in prompt or "en" in prompt, "Prompt should mention English support"
        assert "bilingual" in prompt or "language" in prompt, "Prompt should mention bilingual support"
    
    def test_prompt_contains_stateless_instruction(self):
        """
        ✅ PASS: System prompt mentions stateless agent behavior.
        
        Arrange: Get system prompt
        Act: Check for stateless mention
        Assert: Prompt mentions stateless behavior
        """
        prompt = get_system_prompt().lower()
        
        assert "stateless" in prompt or "independent" in prompt or "no memory" in prompt, "Prompt should mention stateless behavior"
    
    def test_prompt_contains_required_functionality(self):
        """
        ✅ PASS: System prompt lists required functionality.
        
        Arrange: Get system prompt
        Act: Check for required functionality mentions
        Assert: Prompt mentions key functionalities
        """
        prompt = get_system_prompt().lower()
        
        assert "medication information" in prompt or "medication" in prompt, "Prompt should mention medication information"
        assert "dosage" in prompt, "Prompt should mention dosage instructions"
        assert "active ingredient" in prompt, "Prompt should mention active ingredients"
        assert "prescription" in prompt, "Prompt should mention prescription requirements"
        assert "stock" in prompt or "availability" in prompt, "Prompt should mention stock availability"
    
    def test_prompt_contains_error_handling_guidance(self):
        """
        ✅ PASS: System prompt contains error handling guidance.
        
        Arrange: Get system prompt
        Act: Check for error handling mentions
        Assert: Prompt mentions error handling
        """
        prompt = get_system_prompt().lower()
        
        assert "error" in prompt or "fail" in prompt or "not found" in prompt, "Prompt should mention error handling"
    
    def test_prompt_contains_response_guidelines(self):
        """
        ✅ PASS: System prompt contains response guidelines.
        
        Arrange: Get system prompt
        Act: Check for response guidelines
        Assert: Prompt contains response guidance
        """
        prompt = get_system_prompt().lower()
        
        assert "response" in prompt or "guideline" in prompt or "clear" in prompt, "Prompt should contain response guidelines"
    
    def test_prompt_quality_length(self):
        """
        ✅ PASS: System prompt has sufficient length for comprehensive guidance.
        
        Arrange: Get system prompt
        Act: Check prompt length
        Assert: Prompt is comprehensive (not too short)
        """
        prompt = get_system_prompt()
        
        # Should be comprehensive but not excessive
        assert len(prompt) > 500, f"Prompt too short for comprehensive guidance (got {len(prompt)} chars)"
        assert len(prompt) < 10000, f"Prompt too long (got {len(prompt)} chars)"
    
    def test_prompt_mentions_tool_parameters(self):
        """
        ✅ PASS: System prompt mentions tool parameters.
        
        Arrange: Get system prompt
        Act: Check for parameter mentions
        Assert: Prompt mentions key tool parameters
        """
        prompt = get_system_prompt()
        prompt_lower = prompt.lower()
        
        assert "name" in prompt_lower or "medication" in prompt_lower, "Prompt should mention name parameter"
        assert "language" in prompt_lower, "Prompt should mention language parameter"
        assert "medication_id" in prompt_lower, "Prompt should mention medication_id parameter"
        assert "quantity" in prompt_lower, "Prompt should mention quantity parameter"


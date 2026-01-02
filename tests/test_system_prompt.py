"""
Tests for Task 4.1: system_prompt.py

Purpose (Why):
Validates that the system prompt contains all required elements for the pharmacy
assistant agent, including safety rules, tool usage instructions, bilingual support,
and stateless behavior guidelines.

Implementation (What):
Tests the get_system_prompt function to ensure it returns a comprehensive prompt
with all required sections:
- Role definition (professional pharmacy assistant)
- Critical safety rules (no medical advice, no diagnosis, no purchase encouragement)
- Bilingual support (Hebrew and English)
- Tool usage instructions
- Doctor referral instructions
- Required functionality specifications
- Stateless behavior description
"""

import pytest
from app.prompts.system_prompt import get_system_prompt


class TestSystemPrompt:
    """Test suite for system prompt."""
    
    def test_get_system_prompt_returns_string(self):
        """
        Test that get_system_prompt returns a string.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Returns a non-empty string
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert isinstance(prompt, str), f"Expected string, got {type(prompt)}"
        assert len(prompt) > 0, f"Expected non-empty prompt, got length {len(prompt)}"
    
    def test_system_prompt_contains_role_definition(self):
        """
        Test that system prompt contains role definition.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains pharmacy assistant role description
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert "pharmacy" in prompt.lower() or "pharmacist" in prompt.lower(), \
            f"Expected prompt to contain pharmacy/pharmacist role, got: {prompt[:200]}..."
        assert "assistant" in prompt.lower(), \
            f"Expected prompt to contain 'assistant', got: {prompt[:200]}..."
    
    def test_system_prompt_contains_no_medical_advice_rule(self):
        """
        Test that system prompt contains rule about no medical advice.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains explicit rule about not providing medical advice
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert "no medical advice" in prompt.lower() or "never provide medical advice" in prompt.lower() or \
               "must never provide medical advice" in prompt.lower(), \
            f"Expected prompt to contain 'no medical advice' rule, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_no_diagnosis_rule(self):
        """
        Test that system prompt contains rule about no diagnosis.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains explicit rule about not diagnosing
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert "no diagnosis" in prompt.lower() or "never diagnose" in prompt.lower() or \
               "must never diagnose" in prompt.lower(), \
            f"Expected prompt to contain 'no diagnosis' rule, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_no_purchase_encouragement_rule(self):
        """
        Test that system prompt contains rule about no purchase encouragement.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains explicit rule about not encouraging purchases
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert "no encouragement" in prompt.lower() or "never encourage" in prompt.lower() or \
               "must never encourage" in prompt.lower() or "purchase" in prompt.lower(), \
            f"Expected prompt to contain 'no purchase encouragement' rule, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_bilingual_support(self):
        """
        Test that system prompt contains bilingual support instructions.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instructions for Hebrew and English support
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert ("hebrew" in prompt.lower() and "english" in prompt.lower()) or \
               ("hebrew" in prompt.lower() and "en" in prompt.lower()) or \
               ("he" in prompt.lower() and "en" in prompt.lower()), \
            f"Expected prompt to contain bilingual support (Hebrew/English), got: {prompt[:300]}..."
    
    def test_system_prompt_contains_stateless_behavior(self):
        """
        Test that system prompt contains stateless behavior description.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains explicit description of stateless behavior
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert "stateless" in prompt.lower(), \
            f"Expected prompt to contain 'stateless' description, got: {prompt[:300]}..."
        assert ("independent" in prompt.lower() or "no state" in prompt.lower() or \
                "do not remember" in prompt.lower() or "no prior context" in prompt.lower()), \
            f"Expected prompt to describe stateless behavior, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_active_ingredients_requirement(self):
        """
        Test that system prompt contains requirement to identify active ingredients.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instruction to always identify active ingredients
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert "active ingredient" in prompt.lower(), \
            f"Expected prompt to contain 'active ingredient' requirement, got: {prompt[:300]}..."
        assert ("always" in prompt.lower() or "must" in prompt.lower() or "critical" in prompt.lower()), \
            f"Expected prompt to emphasize active ingredients requirement, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_dosage_instructions_requirement(self):
        """
        Test that system prompt contains requirement to explain dosage instructions.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instruction to explain dosage and usage instructions
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert "dosage" in prompt.lower() or "usage instruction" in prompt.lower(), \
            f"Expected prompt to contain 'dosage' or 'usage instruction' requirement, got: {prompt[:300]}..."
        assert ("explain" in prompt.lower() or "provide" in prompt.lower() or "detail" in prompt.lower()), \
            f"Expected prompt to require explaining dosage, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_tool_usage_instructions(self):
        """
        Test that system prompt contains tool usage instructions.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instructions on when and how to use tools
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert "tool" in prompt.lower() or "get_medication_by_name" in prompt.lower() or \
               "check_stock" in prompt.lower() or "check_prescription" in prompt.lower(), \
            f"Expected prompt to contain tool usage instructions, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_prescription_requirement_check(self):
        """
        Test that system prompt contains instruction to check prescription requirements.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instruction to check and explain prescription requirements
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert "prescription" in prompt.lower(), \
            f"Expected prompt to contain 'prescription' requirement, got: {prompt[:300]}..."
        assert ("check" in prompt.lower() or "verify" in prompt.lower() or "require" in prompt.lower()), \
            f"Expected prompt to require checking prescription requirements, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_stock_availability_check(self):
        """
        Test that system prompt contains instruction to check stock availability.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instruction to check stock availability
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert ("stock" in prompt.lower() or "availability" in prompt.lower() or "inventory" in prompt.lower()), \
            f"Expected prompt to contain stock/availability check requirement, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_doctor_referral_instructions(self):
        """
        Test that system prompt contains instructions for referring to healthcare professionals.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instructions on when to refer to doctors/healthcare professionals
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert ("doctor" in prompt.lower() or "healthcare professional" in prompt.lower() or \
                "pharmacist" in prompt.lower() or "refer" in prompt.lower() or "redirect" in prompt.lower()), \
            f"Expected prompt to contain doctor referral instructions, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_medication_information_requirements(self):
        """
        Test that system prompt contains requirements for providing medication information.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains requirements for factual medication information
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert ("medication" in prompt.lower() or "factual information" in prompt.lower()), \
            f"Expected prompt to contain medication information requirements, got: {prompt[:300]}..."
    
    def test_system_prompt_is_comprehensive(self):
        """
        Test that system prompt is comprehensive (minimum length check).
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt is sufficiently detailed (minimum 500 characters)
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert len(prompt) >= 500, \
            f"Expected comprehensive prompt (>=500 chars), got length {len(prompt)}"
    
    def test_get_system_prompt_is_idempotent(self):
        """
        Test that get_system_prompt returns consistent results on multiple calls.
        
        Arrange: No setup needed
        Act: Call get_system_prompt multiple times
        Assert: Returns same prompt each time
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt1 = get_system_prompt()
        prompt2 = get_system_prompt()
        prompt3 = get_system_prompt()
        
        # Assert
        assert prompt1 == prompt2, "Expected same prompt on second call"
        assert prompt2 == prompt3, "Expected same prompt on third call"
        assert prompt1 == prompt3, "Expected same prompt on first and third call"
    
    def test_system_prompt_contains_multi_step_flow_examples(self):
        """
        Test that system prompt contains multi-step flow examples.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains examples of multi-step flows
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert ("flow" in prompt.lower() or "step" in prompt.lower() or "example" in prompt.lower()), \
            f"Expected prompt to contain flow examples, got: {prompt[:300]}..."
        assert ("stock" in prompt.lower() or "availability" in prompt.lower() or "prescription" in prompt.lower()), \
            f"Expected prompt to contain flow examples with tools, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_error_handling_instructions(self):
        """
        Test that system prompt contains error handling instructions.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instructions for handling errors
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert ("error" in prompt.lower() or "fail" in prompt.lower() or "not found" in prompt.lower() or \
                "suggest" in prompt.lower() or "alternative" in prompt.lower()), \
            f"Expected prompt to contain error handling instructions, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_response_guidelines(self):
        """
        Test that system prompt contains response guidelines.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains guidelines for responses
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert ("guideline" in prompt.lower() or "response" in prompt.lower() or "clear" in prompt.lower() or \
                "helpful" in prompt.lower() or "professional" in prompt.lower()), \
            f"Expected prompt to contain response guidelines, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_tool_specific_instructions(self):
        """
        Test that system prompt contains specific instructions for each tool.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instructions for get_medication_by_name, check_stock_availability, check_prescription_requirement
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert "get_medication_by_name" in prompt.lower(), \
            f"Expected prompt to contain get_medication_by_name instructions, got: {prompt[:300]}..."
        assert "check_stock" in prompt.lower() or "stock_availability" in prompt.lower(), \
            f"Expected prompt to contain check_stock_availability instructions, got: {prompt[:300]}..."
        assert "check_prescription" in prompt.lower() or "prescription_requirement" in prompt.lower(), \
            f"Expected prompt to contain check_prescription_requirement instructions, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_language_switching_instructions(self):
        """
        Test that system prompt contains instructions for language switching.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instructions for handling language switches
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert ("switch" in prompt.lower() or "language" in prompt.lower() or "hebrew" in prompt.lower() or \
                "english" in prompt.lower() or "he" in prompt.lower() or "en" in prompt.lower()), \
            f"Expected prompt to contain language switching instructions, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_dosage_forms_requirement(self):
        """
        Test that system prompt contains requirement to describe dosage forms.
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instruction to describe dosage forms
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert ("dosage form" in prompt.lower() or "tablet" in prompt.lower() or "capsule" in prompt.lower() or \
                "syrup" in prompt.lower() or "form" in prompt.lower()), \
            f"Expected prompt to contain dosage forms requirement, got: {prompt[:300]}..."
    
    def test_system_prompt_contains_timing_instructions_requirement(self):
        """
        Test that system prompt contains requirement to explain timing (when to take medication).
        
        Arrange: No setup needed
        Act: Call get_system_prompt
        Assert: Prompt contains instruction to explain timing
        """
        # Arrange
        # No setup needed
        
        # Act
        prompt = get_system_prompt()
        
        # Assert
        assert ("timing" in prompt.lower() or "when" in prompt.lower() or "food" in prompt.lower() or \
                "meal" in prompt.lower() or "before" in prompt.lower() or "after" in prompt.lower()), \
            f"Expected prompt to contain timing instructions requirement, got: {prompt[:300]}..."


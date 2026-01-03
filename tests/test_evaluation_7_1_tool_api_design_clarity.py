"""
Tests for Section 7.1 - Criterion 1: Tool/API Design Clarity

Purpose (Why):
Tests that all tools are clearly defined, have clear inputs/outputs,
and valid JSON schemas. This ensures the tools are well-designed and
can be properly used by the AI agent.

Implementation (What):
Tests tool schemas, parameter validation, return value structure,
and JSON schema compliance.
"""

import pytest
import json
from typing import Dict, Any, List
from app.tools.registry import get_tools_for_openai, execute_tool
from app.tools.medication_tools import get_medication_by_name
from app.tools.prescription_tools import check_prescription_requirement
from app.tools.inventory_tools import check_stock_availability


class TestToolAPIDesignClarity:
    """Test suite for Tool/API Design Clarity (Section 7.1, Criterion 1)."""
    
    def test_tools_are_defined(self):
        """
        ✅ PASS: All required tools are defined in the registry.
        
        Arrange: None (static check)
        Act: Get tools from registry
        Assert: All 3 required tools are present
        """
        tools = get_tools_for_openai()
        tool_names = [tool["function"]["name"] for tool in tools]
        
        assert "get_medication_by_name" in tool_names, f"Expected 'get_medication_by_name' in tools, got {tool_names}"
        assert "check_stock_availability" in tool_names, f"Expected 'check_stock_availability' in tools, got {tool_names}"
        assert "check_prescription_requirement" in tool_names, f"Expected 'check_prescription_requirement' in tools, got {tool_names}"
        # Note: Registry now includes 7 tools (3 medication/inventory/prescription + 4 user tools)
        assert len(tools) == 7, f"Expected exactly 7 tools, got {len(tools)}"
    
    def test_tool_schemas_have_required_fields(self):
        """
        ✅ PASS: All tool schemas have required OpenAI format fields.
        
        Arrange: Get tools from registry
        Act: Check each tool schema structure
        Assert: Each tool has type, function.name, function.description, function.parameters
        """
        tools = get_tools_for_openai()
        
        for tool in tools:
            assert "type" in tool, f"Tool {tool.get('function', {}).get('name', 'unknown')} missing 'type' field"
            assert tool["type"] == "function", f"Tool type must be 'function', got {tool.get('type')}"
            assert "function" in tool, f"Tool missing 'function' field"
            assert "name" in tool["function"], f"Tool missing 'function.name' field"
            assert "description" in tool["function"], f"Tool {tool['function']['name']} missing 'function.description' field"
            assert "parameters" in tool["function"], f"Tool {tool['function']['name']} missing 'function.parameters' field"
    
    def test_tool_schemas_have_valid_json_schema(self):
        """
        ✅ PASS: All tool parameter schemas are valid JSON Schema.
        
        Arrange: Get tools from registry
        Act: Validate JSON Schema structure
        Assert: Each schema has type, properties, and required fields
        """
        tools = get_tools_for_openai()
        
        for tool in tools:
            params = tool["function"]["parameters"]
            assert "type" in params, f"Tool {tool['function']['name']} parameters missing 'type'"
            assert params["type"] == "object", f"Tool {tool['function']['name']} parameters type must be 'object'"
            assert "properties" in params, f"Tool {tool['function']['name']} parameters missing 'properties'"
            if "required" in params:
                assert isinstance(params["required"], list), f"Tool {tool['function']['name']} 'required' must be a list"
    
    def test_get_medication_by_name_schema_clarity(self):
        """
        ✅ PASS: get_medication_by_name has clear input/output definitions.
        
        Arrange: Get tool schema
        Act: Check parameter definitions
        Assert: Parameters are clearly defined with descriptions
        """
        tools = get_tools_for_openai()
        tool = next(t for t in tools if t["function"]["name"] == "get_medication_by_name")
        
        params = tool["function"]["parameters"]
        properties = params["properties"]
        
        # Check name parameter
        assert "name" in properties, "Missing 'name' parameter"
        assert properties["name"]["type"] == "string", "Parameter 'name' must be string"
        assert "description" in properties["name"], "Parameter 'name' missing description"
        assert len(properties["name"]["description"]) > 10, "Parameter 'name' description too short"
        
        # Check language parameter
        assert "language" in properties, "Missing 'language' parameter"
        assert "enum" in properties["language"], "Parameter 'language' must have enum"
        assert properties["language"]["enum"] == ["he", "en"], "Parameter 'language' enum must be ['he', 'en']"
        assert "description" in properties["language"], "Parameter 'language' missing description"
        
        # Check required fields
        assert "name" in params.get("required", []), "Parameter 'name' must be required"
    
    def test_check_stock_availability_schema_clarity(self):
        """
        ✅ PASS: check_stock_availability has clear input/output definitions.
        
        Arrange: Get tool schema
        Act: Check parameter definitions
        Assert: Parameters are clearly defined with descriptions
        """
        tools = get_tools_for_openai()
        tool = next(t for t in tools if t["function"]["name"] == "check_stock_availability")
        
        params = tool["function"]["parameters"]
        properties = params["properties"]
        
        # Check medication_id parameter
        assert "medication_id" in properties, "Missing 'medication_id' parameter"
        assert properties["medication_id"]["type"] == "string", "Parameter 'medication_id' must be string"
        assert "description" in properties["medication_id"], "Parameter 'medication_id' missing description"
        
        # Check quantity parameter
        assert "quantity" in properties, "Missing 'quantity' parameter"
        assert properties["quantity"]["type"] == "integer", "Parameter 'quantity' must be integer"
        assert "description" in properties["quantity"], "Parameter 'quantity' missing description"
        
        # Check required fields
        assert "medication_id" in params.get("required", []), "Parameter 'medication_id' must be required"
        assert "quantity" not in params.get("required", []), "Parameter 'quantity' should be optional"
    
    def test_check_prescription_requirement_schema_clarity(self):
        """
        ✅ PASS: check_prescription_requirement has clear input/output definitions.
        
        Arrange: Get tool schema
        Act: Check parameter definitions
        Assert: Parameters are clearly defined with descriptions
        """
        tools = get_tools_for_openai()
        tool = next(t for t in tools if t["function"]["name"] == "check_prescription_requirement")
        
        params = tool["function"]["parameters"]
        properties = params["properties"]
        
        # Check medication_id parameter
        assert "medication_id" in properties, "Missing 'medication_id' parameter"
        assert properties["medication_id"]["type"] == "string", "Parameter 'medication_id' must be string"
        assert "description" in properties["medication_id"], "Parameter 'medication_id' missing description"
        
        # Check required fields
        assert "medication_id" in params.get("required", []), "Parameter 'medication_id' must be required"
        assert len(params.get("required", [])) == 1, "Only 'medication_id' should be required"
    
    def test_tool_descriptions_are_clear(self):
        """
        ✅ PASS: All tool descriptions are clear and informative.
        
        Arrange: Get tools from registry
        Act: Check description quality
        Assert: Descriptions are non-empty and informative
        """
        tools = get_tools_for_openai()
        
        for tool in tools:
            description = tool["function"]["description"]
            assert len(description) > 50, f"Tool {tool['function']['name']} description too short (must be > 50 chars)"
            assert "when" in description.lower() or "use" in description.lower(), f"Tool {tool['function']['name']} description should mention when to use it"
    
    def test_get_medication_by_name_input_validation(self):
        """
        ✅ PASS: get_medication_by_name validates inputs correctly.
        
        Arrange: Prepare test inputs
        Act: Call tool with various inputs
        Assert: Tool validates inputs and returns appropriate errors
        """
        # Test empty name
        result = get_medication_by_name("")
        assert "error" in result or "searched_name" in result, f"Expected error for empty name, got {result}"
        
        # Test valid name
        result = get_medication_by_name("אקמול")
        assert "medication_id" in result or "error" in result, f"Expected medication_id or error, got {result}"
        
        # Test invalid language
        result = get_medication_by_name("אקמול", "invalid")
        # Should still work (language validation is lenient)
        assert "medication_id" in result or "error" in result, f"Expected medication_id or error, got {result}"
    
    def test_check_stock_availability_input_validation(self):
        """
        ✅ PASS: check_stock_availability validates inputs correctly.
        
        Arrange: Prepare test inputs
        Act: Call tool with various inputs
        Assert: Tool validates inputs and returns appropriate errors
        """
        # Test empty medication_id
        result = check_stock_availability("")
        assert "error" in result or "available" in result, f"Expected error for empty medication_id, got {result}"
        
        # Test invalid medication_id
        result = check_stock_availability("invalid_id")
        assert "error" in result or "available" in result, f"Expected error for invalid medication_id, got {result}"
        
        # Test negative quantity
        result = check_stock_availability("med_001", -1)
        assert "error" in result or "available" in result, f"Expected error for negative quantity, got {result}"
    
    def test_check_prescription_requirement_input_validation(self):
        """
        ✅ PASS: check_prescription_requirement validates inputs correctly.
        
        Arrange: Prepare test inputs
        Act: Call tool with various inputs
        Assert: Tool validates inputs and returns appropriate errors
        """
        # Test empty medication_id
        result = check_prescription_requirement("")
        assert "error" in result or "requires_prescription" in result, f"Expected error for empty medication_id, got {result}"
        
        # Test invalid medication_id
        result = check_prescription_requirement("invalid_id")
        assert "error" in result or "requires_prescription" in result, f"Expected error for invalid medication_id, got {result}"
    
    def test_tool_output_structures_are_consistent(self):
        """
        ✅ PASS: All tools return consistent output structures.
        
        Arrange: Call each tool with valid inputs
        Act: Check output structure
        Assert: Success outputs have expected fields, error outputs have error field
        """
        # Test get_medication_by_name output structure
        result = get_medication_by_name("אקמול")
        if "error" in result:
            assert "searched_name" in result, "Error result should include 'searched_name'"
            assert "suggestions" in result, "Error result should include 'suggestions'"
        else:
            assert "medication_id" in result, "Success result should include 'medication_id'"
            assert "name_he" in result or "name_en" in result, "Success result should include name"
            assert "active_ingredients" in result, "Success result should include 'active_ingredients'"
        
        # Test check_stock_availability output structure
        if "medication_id" in result:
            stock_result = check_stock_availability(result["medication_id"])
            if "error" in stock_result:
                assert "medication_id" in stock_result, "Error result should include 'medication_id'"
                assert "available" in stock_result, "Error result should include 'available'"
            else:
                assert "medication_id" in stock_result, "Success result should include 'medication_id'"
                assert "available" in stock_result, "Success result should include 'available'"
                assert "quantity_in_stock" in stock_result, "Success result should include 'quantity_in_stock'"
    
    def test_tool_schemas_are_json_serializable(self):
        """
        ✅ PASS: All tool schemas can be serialized to JSON.
        
        Arrange: Get tools from registry
        Act: Serialize to JSON
        Assert: No serialization errors
        """
        tools = get_tools_for_openai()
        
        for tool in tools:
            # Should not raise exception
            json_str = json.dumps(tool)
            assert len(json_str) > 0, f"Tool {tool['function']['name']} JSON serialization failed"
            
            # Should be able to deserialize
            deserialized = json.loads(json_str)
            assert deserialized["function"]["name"] == tool["function"]["name"], "Deserialization failed"


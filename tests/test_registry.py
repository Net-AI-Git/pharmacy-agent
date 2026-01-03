"""
Tests for Task 3.4: registry.py

Purpose (Why):
Validates that tool registry correctly provides tool definitions for OpenAI API
and routes tool execution to the correct Python functions.

Implementation (What):
Tests the get_tools_for_openai and execute_tool functions with:
- Tool definitions format validation
- Tool execution routing
- Error handling for invalid tool names
- Parameter passing
"""

import pytest
from app.tools.registry import get_tools_for_openai, execute_tool


class TestRegistry:
    """Test suite for tool registry."""
    
    def test_get_tools_for_openai_returns_list(self):
        """
        Test that get_tools_for_openai returns a list.
        
        Arrange: No setup needed
        Act: Call get_tools_for_openai
        Assert: Returns a list
        """
        # Arrange
        # No setup needed
        
        # Act
        tools = get_tools_for_openai()
        
        # Assert
        assert isinstance(tools, list), f"Expected list, got {type(tools)}"
        assert len(tools) > 0, f"Expected non-empty list, got {len(tools)} tools"
    
    def test_get_tools_for_openai_returns_three_tools(self):
        """
        Test that get_tools_for_openai returns exactly 6 tools.
        
        Arrange: No setup needed
        Act: Call get_tools_for_openai
        Assert: Returns list with 6 tools (3 medication/inventory/prescription + 3 user tools)
        """
        # Arrange
        # No setup needed
        
        # Act
        tools = get_tools_for_openai()
        
        # Assert
        # Note: Registry now includes 7 tools (3 medication/inventory/prescription + 4 user tools)
        assert len(tools) == 7, f"Expected 7 tools, got {len(tools)}"
    
    def test_get_tools_for_openai_contains_medication_tool(self):
        """
        Test that tool list includes get_medication_by_name.
        
        Arrange: No setup needed
        Act: Call get_tools_for_openai
        Assert: List contains medication tool
        """
        # Arrange
        # No setup needed
        
        # Act
        tools = get_tools_for_openai()
        
        # Assert
        tool_names = [tool["function"]["name"] for tool in tools]
        assert "get_medication_by_name" in tool_names, \
            f"Expected 'get_medication_by_name' in tools, got {tool_names}"
    
    def test_get_tools_for_openai_contains_inventory_tool(self):
        """
        Test that tool list includes check_stock_availability.
        
        Arrange: No setup needed
        Act: Call get_tools_for_openai
        Assert: List contains inventory tool
        """
        # Arrange
        # No setup needed
        
        # Act
        tools = get_tools_for_openai()
        
        # Assert
        tool_names = [tool["function"]["name"] for tool in tools]
        assert "check_stock_availability" in tool_names, \
            f"Expected 'check_stock_availability' in tools, got {tool_names}"
    
    def test_get_tools_for_openai_contains_prescription_tool(self):
        """
        Test that tool list includes check_prescription_requirement.
        
        Arrange: No setup needed
        Act: Call get_tools_for_openai
        Assert: List contains prescription tool
        """
        # Arrange
        # No setup needed
        
        # Act
        tools = get_tools_for_openai()
        
        # Assert
        tool_names = [tool["function"]["name"] for tool in tools]
        assert "check_prescription_requirement" in tool_names, \
            f"Expected 'check_prescription_requirement' in tools, got {tool_names}"
    
    def test_get_tools_for_openai_tool_structure(self):
        """
        Test that each tool has correct OpenAI API structure.
        
        Arrange: No setup needed
        Act: Call get_tools_for_openai
        Assert: Each tool has type, function.name, function.description, function.parameters
        """
        # Arrange
        # No setup needed
        
        # Act
        tools = get_tools_for_openai()
        
        # Assert
        for tool in tools:
            assert "type" in tool, f"Tool missing 'type' field: {tool}"
            assert tool["type"] == "function", f"Expected type='function', got '{tool.get('type')}'"
            assert "function" in tool, f"Tool missing 'function' field: {tool}"
            assert "name" in tool["function"], f"Tool function missing 'name' field: {tool}"
            assert "description" in tool["function"], f"Tool function missing 'description' field: {tool}"
            assert "parameters" in tool["function"], f"Tool function missing 'parameters' field: {tool}"
    
    def test_get_tools_for_openai_parameters_structure(self):
        """
        Test that tool parameters have correct JSON Schema structure.
        
        Arrange: No setup needed
        Act: Call get_tools_for_openai
        Assert: Parameters have type, properties, required fields
        """
        # Arrange
        # No setup needed
        
        # Act
        tools = get_tools_for_openai()
        
        # Assert
        for tool in tools:
            params = tool["function"]["parameters"]
            assert "type" in params, f"Parameters missing 'type' field: {params}"
            assert params["type"] == "object", f"Expected parameters type='object', got '{params.get('type')}'"
            assert "properties" in params, f"Parameters missing 'properties' field: {params}"
            assert "required" in params, f"Parameters missing 'required' field: {params}"
            assert isinstance(params["required"], list), \
                f"Expected 'required' to be a list, got {type(params['required'])}"
    
    def test_execute_tool_get_medication_by_name(self):
        """
        Test executing get_medication_by_name tool.
        
        Arrange: Valid tool name and arguments
        Act: Call execute_tool with medication tool
        Assert: Returns medication search result
        """
        # Arrange
        tool_name = "get_medication_by_name"
        arguments = {"name": "Acamol", "language": "he"}
        
        # Act
        result = execute_tool(tool_name, arguments)
        
        # Assert
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        assert "error" not in result or "medication_id" in result, \
            f"Expected success or error result, got {result}"
    
    def test_execute_tool_check_stock_availability(self):
        """
        Test executing check_stock_availability tool.
        
        Arrange: Valid tool name and arguments
        Act: Call execute_tool with inventory tool
        Assert: Returns stock check result
        """
        # Arrange
        tool_name = "check_stock_availability"
        arguments = {"medication_id": "med_001", "quantity": None}
        
        # Act
        result = execute_tool(tool_name, arguments)
        
        # Assert
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        assert "error" not in result or "available" in result, \
            f"Expected success or error result, got {result}"
    
    def test_execute_tool_check_prescription_requirement(self):
        """
        Test executing check_prescription_requirement tool.
        
        Arrange: Valid tool name and arguments
        Act: Call execute_tool with prescription tool
        Assert: Returns prescription check result
        """
        # Arrange
        tool_name = "check_prescription_requirement"
        arguments = {"medication_id": "med_001"}
        
        # Act
        result = execute_tool(tool_name, arguments)
        
        # Assert
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        assert "error" not in result or "requires_prescription" in result, \
            f"Expected success or error result, got {result}"
    
    def test_execute_tool_invalid_tool_name(self):
        """
        Test error handling for invalid tool name.
        
        Arrange: Invalid tool name
        Act: Call execute_tool with invalid name
        Assert: Raises ValueError
        """
        # Arrange
        tool_name = "invalid_tool_name"
        arguments = {}
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            execute_tool(tool_name, arguments)
        
        assert "not found" in str(exc_info.value).lower() or "available" in str(exc_info.value).lower(), \
            f"Expected error message about tool not found, got '{str(exc_info.value)}'"
    
    def test_execute_tool_passes_arguments_correctly(self):
        """
        Test that execute_tool passes arguments correctly to tool function.
        
        Arrange: Tool name and specific arguments
        Act: Call execute_tool
        Assert: Tool receives and uses arguments correctly
        """
        # Arrange
        tool_name = "get_medication_by_name"
        arguments = {"name": "Aspirin", "language": None}
        
        # Act
        result = execute_tool(tool_name, arguments)
        
        # Assert
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        # If successful, should find Aspirin (med_002)
        if "error" not in result:
            assert result.get("medication_id") == "med_002" or "Aspirin" in result.get("name_he", "") or "Aspirin" in result.get("name_en", ""), \
                f"Expected to find Aspirin, got {result}"
    
    def test_get_tools_for_openai_medication_tool_parameters(self):
        """
        Test that medication tool has correct parameter schema.
        
        Arrange: No setup needed
        Act: Get tools and find medication tool
        Assert: Parameters match expected schema
        """
        # Arrange
        # No setup needed
        
        # Act
        tools = get_tools_for_openai()
        medication_tool = next(tool for tool in tools if tool["function"]["name"] == "get_medication_by_name")
        params = medication_tool["function"]["parameters"]
        
        # Assert
        assert "name" in params["properties"], "Parameters must include 'name' property"
        assert params["properties"]["name"]["type"] == "string", \
            f"Expected name type='string', got '{params['properties']['name'].get('type')}'"
        assert "name" in params["required"], "Parameters must require 'name'"
        assert "language" in params["properties"], "Parameters must include 'language' property"
    
    def test_get_tools_for_openai_inventory_tool_parameters(self):
        """
        Test that inventory tool has correct parameter schema.
        
        Arrange: No setup needed
        Act: Get tools and find inventory tool
        Assert: Parameters match expected schema
        """
        # Arrange
        # No setup needed
        
        # Act
        tools = get_tools_for_openai()
        inventory_tool = next(tool for tool in tools if tool["function"]["name"] == "check_stock_availability")
        params = inventory_tool["function"]["parameters"]
        
        # Assert
        assert "medication_id" in params["properties"], "Parameters must include 'medication_id' property"
        assert params["properties"]["medication_id"]["type"] == "string", \
            f"Expected medication_id type='string', got '{params['properties']['medication_id'].get('type')}'"
        assert "medication_id" in params["required"], "Parameters must require 'medication_id'"
        assert "quantity" in params["properties"], "Parameters must include 'quantity' property"
    
    def test_get_tools_for_openai_prescription_tool_parameters(self):
        """
        Test that prescription tool has correct parameter schema.
        
        Arrange: No setup needed
        Act: Get tools and find prescription tool
        Assert: Parameters match expected schema
        """
        # Arrange
        # No setup needed
        
        # Act
        tools = get_tools_for_openai()
        prescription_tool = next(tool for tool in tools if tool["function"]["name"] == "check_prescription_requirement")
        params = prescription_tool["function"]["parameters"]
        
        # Assert
        assert "medication_id" in params["properties"], "Parameters must include 'medication_id' property"
        assert params["properties"]["medication_id"]["type"] == "string", \
            f"Expected medication_id type='string', got '{params['properties']['medication_id'].get('type')}'"
        assert "medication_id" in params["required"], "Parameters must require 'medication_id'"
        assert len(params["required"]) == 1, \
            f"Expected exactly 1 required parameter, got {len(params['required'])}"
    
    def test_execute_tool_with_empty_arguments(self):
        """
        Test executing tool with empty arguments dictionary (edge case).
        
        Arrange: Tool name with empty arguments
        Act: Call execute_tool with empty dict
        Assert: Handles gracefully (may raise error or return result)
        """
        # Arrange
        tool_name = "get_medication_by_name"
        arguments = {}
        
        # Act & Assert
        # Should raise TypeError or ValueError for missing required arguments
        with pytest.raises((TypeError, ValueError, KeyError)):
            execute_tool(tool_name, arguments)
    
    def test_execute_tool_with_extra_arguments(self):
        """
        Test executing tool with extra unexpected arguments (edge case).
        
        Arrange: Tool name with extra arguments
        Act: Call execute_tool with extra arguments
        Assert: Filters out extra arguments and executes successfully
        """
        # Arrange
        tool_name = "check_prescription_requirement"
        arguments = {"medication_id": "med_001", "extra_param": "should_be_ignored"}
        
        # Act
        result = execute_tool(tool_name, arguments)
        
        # Assert
        # Should filter out extra_param and execute successfully
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        # Should have correct structure (extra_param was filtered out)
        if "error" not in result:
            assert "medication_id" in result, "Result should include medication_id"
            assert result["medication_id"] == "med_001", \
                f"Expected medication_id='med_001', got '{result.get('medication_id')}'"
    
    def test_execute_tool_with_wrong_argument_types(self):
        """
        Test executing tool with wrong argument types (edge case).
        
        Arrange: Tool name with wrong type arguments
        Act: Call execute_tool with wrong types
        Assert: Handles gracefully (may raise error or convert)
        """
        # Arrange
        tool_name = "check_stock_availability"
        arguments = {"medication_id": 123, "quantity": "not_a_number"}  # Wrong types
        
        # Act & Assert
        # Should either raise TypeError or handle gracefully
        # The tool may convert or reject - both are acceptable
        try:
            result = execute_tool(tool_name, arguments)
            assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        except (TypeError, ValueError):
            # Also acceptable - type validation
            pass
    
    def test_get_tools_for_openai_returns_consistent_structure(self):
        """
        Test that get_tools_for_openai returns consistent structure on multiple calls (edge case).
        
        Arrange: No setup needed
        Act: Call get_tools_for_openai multiple times
        Assert: Returns same structure each time
        """
        # Arrange
        # No setup needed
        
        # Act
        tools1 = get_tools_for_openai()
        tools2 = get_tools_for_openai()
        
        # Assert
        assert len(tools1) == len(tools2), \
            f"Expected same number of tools, got {len(tools1)} vs {len(tools2)}"
        # Note: Registry now includes 7 tools (3 medication/inventory/prescription + 4 user tools)
        assert len(tools1) == 7, f"Expected 7 tools, got {len(tools1)}"
        
        # Check that tool names are consistent
        names1 = [tool["function"]["name"] for tool in tools1]
        names2 = [tool["function"]["name"] for tool in tools2]
        assert names1 == names2, \
            f"Expected same tool names, got {names1} vs {names2}"


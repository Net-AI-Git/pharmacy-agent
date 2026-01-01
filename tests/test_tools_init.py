"""
Tests for Task 3.5: app/tools/__init__.py

Purpose (Why):
Validates that the tools module __init__.py correctly exports all required functions
and classes, enabling proper imports throughout the application.

Implementation (What):
Tests that all expected exports are available from app.tools module:
- get_medication_by_name
- MedicationSearchInput, MedicationSearchResult, MedicationSearchError
- get_tools_for_openai
- execute_tool
"""

import pytest


class TestToolsInit:
    """Test suite for tools __init__.py exports."""
    
    def test_import_get_medication_by_name(self):
        """
        Test that get_medication_by_name can be imported from app.tools.
        
        Arrange: Import statement
        Act: Import get_medication_by_name from app.tools
        Assert: Import succeeds
        """
        # Arrange
        # No setup needed
        
        # Act
        from app.tools import get_medication_by_name
        
        # Assert
        assert get_medication_by_name is not None, "get_medication_by_name could not be imported"
        assert callable(get_medication_by_name), f"Expected get_medication_by_name to be callable, got {type(get_medication_by_name)}"
    
    def test_import_get_tools_for_openai(self):
        """
        Test that get_tools_for_openai can be imported from app.tools.
        
        Arrange: Import statement
        Act: Import get_tools_for_openai from app.tools
        Assert: Import succeeds
        """
        # Arrange
        # No setup needed
        
        # Act
        from app.tools import get_tools_for_openai
        
        # Assert
        assert get_tools_for_openai is not None, "get_tools_for_openai could not be imported"
        assert callable(get_tools_for_openai), f"Expected get_tools_for_openai to be callable, got {type(get_tools_for_openai)}"
    
    def test_import_execute_tool(self):
        """
        Test that execute_tool can be imported from app.tools.
        
        Arrange: Import statement
        Act: Import execute_tool from app.tools
        Assert: Import succeeds
        """
        # Arrange
        # No setup needed
        
        # Act
        from app.tools import execute_tool
        
        # Assert
        assert execute_tool is not None, "execute_tool could not be imported"
        assert callable(execute_tool), f"Expected execute_tool to be callable, got {type(execute_tool)}"
    
    def test_import_medication_search_input(self):
        """
        Test that MedicationSearchInput can be imported from app.tools.
        
        Arrange: Import statement
        Act: Import MedicationSearchInput from app.tools
        Assert: Import succeeds
        """
        # Arrange
        # No setup needed
        
        # Act
        from app.tools import MedicationSearchInput
        
        # Assert
        assert MedicationSearchInput is not None, "MedicationSearchInput could not be imported"
    
    def test_import_medication_search_result(self):
        """
        Test that MedicationSearchResult can be imported from app.tools.
        
        Arrange: Import statement
        Act: Import MedicationSearchResult from app.tools
        Assert: Import succeeds
        """
        # Arrange
        # No setup needed
        
        # Act
        from app.tools import MedicationSearchResult
        
        # Assert
        assert MedicationSearchResult is not None, "MedicationSearchResult could not be imported"
    
    def test_import_medication_search_error(self):
        """
        Test that MedicationSearchError can be imported from app.tools.
        
        Arrange: Import statement
        Act: Import MedicationSearchError from app.tools
        Assert: Import succeeds
        """
        # Arrange
        # No setup needed
        
        # Act
        from app.tools import MedicationSearchError
        
        # Assert
        assert MedicationSearchError is not None, "MedicationSearchError could not be imported"
    
    def test_import_all_from_tools_module(self):
        """
        Test that all expected exports are available from app.tools.
        
        Arrange: Import statement
        Act: Import all expected items from app.tools
        Assert: All imports succeed
        """
        # Arrange
        # No setup needed
        
        # Act
        from app.tools import (
            get_medication_by_name,
            MedicationSearchInput,
            MedicationSearchResult,
            MedicationSearchError,
            get_tools_for_openai,
            execute_tool
        )
        
        # Assert
        assert get_medication_by_name is not None, "get_medication_by_name import failed"
        assert MedicationSearchInput is not None, "MedicationSearchInput import failed"
        assert MedicationSearchResult is not None, "MedicationSearchResult import failed"
        assert MedicationSearchError is not None, "MedicationSearchError import failed"
        assert get_tools_for_openai is not None, "get_tools_for_openai import failed"
        assert execute_tool is not None, "execute_tool import failed"
    
    def test_imported_functions_are_callable(self):
        """
        Test that imported functions are actually callable.
        
        Arrange: Import functions
        Act: Check if functions are callable
        Assert: All functions are callable
        """
        # Arrange
        from app.tools import get_medication_by_name, get_tools_for_openai, execute_tool
        
        # Act & Assert
        assert callable(get_medication_by_name), \
            f"Expected get_medication_by_name to be callable, got {type(get_medication_by_name)}"
        assert callable(get_tools_for_openai), \
            f"Expected get_tools_for_openai to be callable, got {type(get_tools_for_openai)}"
        assert callable(execute_tool), \
            f"Expected execute_tool to be callable, got {type(execute_tool)}"
    
    def test_imported_classes_can_be_instantiated(self):
        """
        Test that imported Pydantic classes can be instantiated.
        
        Arrange: Import classes
        Act: Create instances of classes
        Assert: Instances created successfully
        """
        # Arrange
        from app.tools import MedicationSearchInput, MedicationSearchResult, MedicationSearchError
        
        # Act & Assert - MedicationSearchInput
        input_instance = MedicationSearchInput(name="Test")
        assert input_instance.name == "Test", \
            f"Expected name='Test', got '{input_instance.name}'"
        
        # Act & Assert - MedicationSearchError
        error_instance = MedicationSearchError(
            error="Test error",
            searched_name="Test",
            suggestions=[]
        )
        assert error_instance.error == "Test error", \
            f"Expected error='Test error', got '{error_instance.error}'"
    
    def test_import_does_not_raise_exceptions(self):
        """
        Test that importing from app.tools does not raise exceptions.
        
        Arrange: Import statement
        Act: Import from app.tools
        Assert: No exceptions raised
        """
        # Arrange
        # No setup needed
        
        # Act & Assert
        try:
            from app.tools import (
                get_medication_by_name,
                MedicationSearchInput,
                MedicationSearchResult,
                MedicationSearchError,
                get_tools_for_openai,
                execute_tool
            )
        except Exception as e:
            pytest.fail(f"Import from app.tools raised exception: {e}")


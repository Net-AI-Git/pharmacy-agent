"""
Medication tools for the pharmacy AI agent.

Purpose (Why):
This module provides tools for medication-related operations that can be used with
OpenAI API function calling. These tools enable the AI agent to search for medications,
retrieve detailed information, and provide accurate medication data to users. The tools
are designed to support both Hebrew and English queries with fuzzy matching capabilities.

Implementation (What):
Implements plain Python functions that can be registered with OpenAI API as tools.
Uses module-level caching for the DatabaseManager to improve performance and reduce
token usage. Provides comprehensive error handling with suggestions when medications
are not found. Fuzzy matching is implemented via partial string matching in the
DatabaseManager.search_medications_by_name method.

Fuzzy Matching Explanation:
Fuzzy matching allows finding medications even with partial or slightly incorrect names.
For example, searching "Acam" will find "Acamol", and searching "paracet" will find
"Paracetamol". This is implemented using case-insensitive partial string matching
(in operator) in the database search method.
"""

import logging
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.database.db import DatabaseManager
from app.models.medication import Medication

# Configure module-level logger
logger = logging.getLogger(__name__)

# Module-level cache for DatabaseManager (reduces token usage and improves performance)
_db_manager: Optional[DatabaseManager] = None


def _get_db_manager() -> DatabaseManager:
    """
    Get or create the module-level DatabaseManager instance.
    
    Purpose (Why):
    Provides a singleton DatabaseManager instance to avoid repeated instantiation
    and maintain database state across tool calls. This reduces memory usage and
    improves performance by reusing the loaded database cache.
    
    Implementation (What):
    Uses module-level variable to cache the DatabaseManager instance. Creates a
    new instance only if one doesn't exist. This ensures the database is loaded
    once and reused for all tool calls.
    
    Returns:
        DatabaseManager instance (cached or newly created)
    """
    global _db_manager
    if _db_manager is None:
        logger.debug("Creating new DatabaseManager instance")
        _db_manager = DatabaseManager()
        _db_manager.load_db()
    return _db_manager


class MedicationSearchInput(BaseModel):
    """
    Input schema for medication search tool.
    
    Purpose (Why):
    Defines the structure and validation rules for medication search parameters.
    This ensures type safety and provides clear documentation for the LLM about
    what parameters are expected and their meanings.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for automatic validation. Uses Literal type
    for language field to restrict values to valid options. All fields include
    Field descriptions which are critical for LLM understanding.
    
    Attributes:
        name: The medication name to search for (required)
        language: Optional language filter ('he' for Hebrew, 'en' for English)
    """
    name: str = Field(description="The medication name to search for (supports partial matches and fuzzy matching)")
    language: Optional[Literal["he", "en"]] = Field(
        default=None,
        description="Optional language filter: 'he' for Hebrew, 'en' for English. If not provided, searches both languages"
    )


class MedicationSearchResult(BaseModel):
    """
    Output schema for successful medication search.
    
    Purpose (Why):
    Defines the structure of medication information returned to the agent. Ensures
    all required fields (active_ingredients, dosage_instructions) are present
    and provides a consistent format for the agent to process.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for validation and serialization. Includes
    all medication fields with Field descriptions. The medication_id is included
    for reference in subsequent tool calls.
    
    Attributes:
        medication_id: Unique identifier for the medication
        name_he: Name in Hebrew
        name_en: Name in English
        active_ingredients: List of active ingredients (required field)
        dosage_forms: Available dosage forms
        dosage_instructions: Detailed dosage instructions (required field)
        usage_instructions: Instructions on how to use the medication
        requires_prescription: Whether prescription is required
        description: General description of the medication
        available: Whether the medication is currently in stock
        quantity_in_stock: Current stock quantity
    """
    medication_id: str = Field(description="Unique identifier for the medication")
    name_he: str = Field(description="Name of the medication in Hebrew")
    name_en: str = Field(description="Name of the medication in English")
    active_ingredients: List[str] = Field(description="List of active ingredients in the medication (required field)")
    dosage_forms: List[str] = Field(description="Available dosage forms (e.g., Tablets, Capsules, Syrup)")
    dosage_instructions: str = Field(description="Detailed dosage instructions including amount and frequency (required field)")
    usage_instructions: str = Field(description="Instructions on how to use the medication, including when to take it")
    requires_prescription: bool = Field(description="Whether a prescription is required to purchase this medication")
    description: str = Field(description="General description of what the medication is used for")
    available: bool = Field(description="Whether the medication is currently available in stock")
    quantity_in_stock: int = Field(description="Current quantity of the medication in stock")


class MedicationSearchError(BaseModel):
    """
    Error schema for medication search failures.
    
    Purpose (Why):
    Provides structured error information when medication search fails. Includes
    suggestions to help users find the correct medication name, improving user
    experience and reducing frustration.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for consistent error format. Includes the
    original search query, error message, and a list of suggested medication
    names that might match what the user was looking for.
    
    Attributes:
        error: Error message describing what went wrong
        searched_name: The medication name that was searched for
        suggestions: List of suggested medication names that might match
    """
    error: str = Field(description="Error message describing why the search failed")
    searched_name: str = Field(description="The medication name that was searched for")
    suggestions: List[str] = Field(description="List of suggested medication names that might match the search query")


def _validate_search_input(name: str, language: Optional[str]) -> tuple[str, Optional[str]]:
    """
    Validate and normalize search input parameters.
    
    Purpose (Why):
    Ensures input parameters are valid before performing database search. Prevents
    invalid queries and normalizes the input for consistent processing.
    
    Implementation (What):
    Validates that name is not empty and trims whitespace. Validates language
    parameter is one of the allowed values ('he', 'en') or None. Returns normalized
    values for further processing.
    
    Args:
        name: The medication name to validate
        language: Optional language filter to validate
    
    Returns:
        Tuple of (normalized_name, validated_language)
    
    Raises:
        ValueError: If name is empty after trimming
    """
    if not name or not name.strip():
        raise ValueError("Medication name cannot be empty")
    
    normalized_name = name.strip()
    
    if language is not None and language not in ["he", "en"]:
        logger.warning(f"Invalid language parameter: {language}. Using None (search both languages)")
        language = None
    
    return normalized_name, language


def _generate_suggestions(db_manager: DatabaseManager, name: str) -> List[str]:
    """
    Generate medication name suggestions when search fails.
    
    Purpose (Why):
    Provides helpful suggestions to users when their search query doesn't match
    any medications. Improves user experience by helping them find the correct
    medication name.
    
    Implementation (What):
    Searches the database without language filter, and if still no results,
    tries with first 3 characters for partial matching. Extracts unique medication
    names (both Hebrew and English) and limits to 5 suggestions.
    
    Args:
        db_manager: DatabaseManager instance for searching
        name: The search query that failed
    
    Returns:
        List of suggested medication names (up to 5)
    """
    all_medications = db_manager.search_medications_by_name(name, None)
    
    # If still no results, try with first few characters
    if not all_medications and len(name) > 2:
        partial_name = name[:3]
        all_medications = db_manager.search_medications_by_name(partial_name, None)
    
    # Extract unique medication names for suggestions
    suggestions = []
    seen_ids = set()
    
    for med in all_medications[:5]:
        if med.medication_id not in seen_ids:
            seen_ids.add(med.medication_id)
            # Add both Hebrew and English names
            if med.name_he:
                suggestions.append(med.name_he)
            if med.name_en and med.name_en not in suggestions:
                suggestions.append(med.name_en)
    
    return suggestions[:5]


def _validate_medication_required_fields(medication: Medication, name: str) -> Optional[MedicationSearchError]:
    """
    Validate that medication has all required fields.
    
    Purpose (Why):
    Ensures medication data integrity by checking for required fields that are
    critical for safety (active_ingredients, dosage_instructions). Returns error
    if any required field is missing.
    
    Implementation (What):
    Checks if active_ingredients and dosage_instructions are present and non-empty.
    Returns MedicationSearchError if validation fails, None if validation passes.
    
    Args:
        medication: The medication to validate
        name: The original search query (for error message)
    
    Returns:
        MedicationSearchError if validation fails, None if validation passes
    """
    if not medication.active_ingredients:
        logger.error(f"Medication {medication.medication_id} missing active_ingredients (required field)")
        return MedicationSearchError(
            error="Medication data is incomplete: missing active ingredients",
            searched_name=name,
            suggestions=[]
        )
    
    if not medication.dosage_instructions:
        logger.error(f"Medication {medication.medication_id} missing dosage_instructions (required field)")
        return MedicationSearchError(
            error="Medication data is incomplete: missing dosage instructions",
            searched_name=name,
            suggestions=[]
        )
    
    return None


def _build_success_result(medication: Medication) -> MedicationSearchResult:
    """
    Build success result from medication data.
    
    Purpose (Why):
    Converts Medication model to MedicationSearchResult schema for consistent
    tool output format. Extracts all necessary fields including stock information.
    
    Implementation (What):
    Maps Medication model fields to MedicationSearchResult schema, including
    nested stock information. Returns validated Pydantic model instance.
    
    Args:
        medication: The Medication model instance to convert
    
    Returns:
        MedicationSearchResult with all medication information
    """
    return MedicationSearchResult(
        medication_id=medication.medication_id,
        name_he=medication.name_he,
        name_en=medication.name_en,
        active_ingredients=medication.active_ingredients,
        dosage_forms=medication.dosage_forms,
        dosage_instructions=medication.dosage_instructions,
        usage_instructions=medication.usage_instructions,
        requires_prescription=medication.requires_prescription,
        description=medication.description,
        available=medication.stock.available,
        quantity_in_stock=medication.stock.quantity_in_stock
    )


def _build_error_result(error_msg: str, name: str, suggestions: List[str]) -> MedicationSearchError:
    """
    Build error result with message and suggestions.
    
    Purpose (Why):
    Creates consistent error responses with helpful suggestions. Provides
    structured error information for the agent to process and present to users.
    
    Implementation (What):
    Creates MedicationSearchError instance with error message, searched name,
    and list of suggestions. Limits suggestions to 5 items.
    
    Args:
        error_msg: The error message to include
        name: The medication name that was searched
        suggestions: List of suggested medication names
    
    Returns:
        MedicationSearchError instance
    """
    return MedicationSearchError(
        error=error_msg,
        searched_name=name,
        suggestions=suggestions[:5]
    )


def _handle_no_medications_found(
    db_manager: DatabaseManager,
    normalized_name: str,
    validated_language: Optional[str]
) -> Dict[str, Any]:
    """
    Handle case when no medications are found in search.
    
    Purpose (Why):
    Provides consistent error handling when medication search returns no results.
    Generates helpful suggestions to improve user experience.
    
    Implementation (What):
    Logs warning, generates suggestions, and returns error result with suggestions.
    
    Args:
        db_manager: DatabaseManager instance for generating suggestions
        normalized_name: The normalized medication name that was searched
        validated_language: The language filter that was used
    
    Returns:
        Dictionary containing MedicationSearchError with suggestions
    """
    logger.warning(f"No medications found for name='{normalized_name}', language={validated_language}")
    suggestions = _generate_suggestions(db_manager, normalized_name)
    error_result = _build_error_result(
        error_msg=f"Medication '{normalized_name}' not found. Please check the spelling or try a different name.",
        name=normalized_name,
        suggestions=suggestions
    )
    return error_result.model_dump()


def _handle_medication_found(
    medication: Medication,
    normalized_name: str
) -> Dict[str, Any]:
    """
    Handle case when medication is found in search.
    
    Purpose (Why):
    Validates found medication and returns success result. Ensures all required
    fields are present before returning medication information.
    
    Implementation (What):
    Validates required fields, builds success result, and returns it.
    
    Args:
        medication: The Medication instance that was found
        normalized_name: The original search query (for validation error messages)
    
    Returns:
        Dictionary containing MedicationSearchResult or MedicationSearchError if validation fails
    """
    logger.info(f"Found medication: {medication.medication_id} ({medication.name_he} / {medication.name_en})")
    
    # Validate required fields
    validation_error = _validate_medication_required_fields(medication, normalized_name)
    if validation_error:
        return validation_error.model_dump()
    
    # Build and return success result
    result = _build_success_result(medication)
    logger.debug(f"Successfully retrieved medication: {medication.medication_id}")
    return result.model_dump()


def _handle_search_validation_error(error: ValueError, name: str) -> Dict[str, Any]:
    """
    Handle input validation errors during medication search.
    
    Purpose (Why):
    Provides consistent error handling for validation failures. Ensures
    structured error information is returned when input is invalid.
    
    Implementation (What):
    Logs warning and returns error result without suggestions.
    
    Args:
        error: The ValueError that occurred
        name: The medication name that was being validated
    
    Returns:
        Dictionary containing MedicationSearchError
    """
    logger.warning(f"Input validation error: {str(error)}")
    error_result = _build_error_result(
        error_msg=str(error),
        name=name or "",
        suggestions=[]
    )
    return error_result.model_dump()


def _handle_search_unexpected_error(error: Exception, name: str) -> Dict[str, Any]:
    """
    Handle unexpected errors during medication search.
    
    Purpose (Why):
    Provides consistent error handling for unexpected failures. Ensures
    structured error information is returned when system errors occur.
    
    Implementation (What):
    Logs error with full traceback and returns error result without suggestions.
    
    Args:
        error: The Exception that occurred
        name: The medication name that was being searched
    
    Returns:
        Dictionary containing MedicationSearchError
    """
    logger.error(f"Error searching for medication '{name}': {str(error)}", exc_info=True)
    error_result = _build_error_result(
        error_msg=f"An error occurred while searching for the medication: {str(error)}",
        name=name or "",
        suggestions=[]
    )
    return error_result.model_dump()


def get_medication_by_name(name: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for a medication by name with fuzzy matching support.
    
    Purpose (Why):
    This tool enables the AI agent to find medications when users provide medication
    names in natural language. It supports both Hebrew and English names, handles
    partial matches (fuzzy matching), and provides helpful suggestions when no exact
    match is found. This is essential for the agent to provide accurate medication
    information to users.
    
    Implementation (What):
    Uses DatabaseManager to search the medication database by name. Supports case-
    insensitive partial matching in both Hebrew and English. Returns complete medication
    information including required fields (active_ingredients, dosage_instructions).
    If no exact match is found, returns error with suggestions based on similar names.
    Uses module-level caching for DatabaseManager to improve performance.
    
    Args:
        name: The medication name to search for (string, case-insensitive, supports partial matches)
        language: Optional language filter ('he' for Hebrew, 'en' for English). 
                 If None, searches both languages.
    
    Returns:
        Dictionary containing either:
        - MedicationSearchResult: If medication is found (includes all medication details)
        - MedicationSearchError: If medication is not found (includes error message and suggestions)
    
    Raises:
        ValueError: If name parameter is empty or invalid
        RuntimeError: If database cannot be loaded
    
    Example Input:
        name="Acamol", language="he"
    
    Example Output (Success):
        {
            "medication_id": "med_001",
            "name_he": "Acamol",
            "name_en": "Acetaminophen",
            "active_ingredients": ["Paracetamol 500mg"],
            "dosage_forms": ["Tablets", "Capsules"],
            "dosage_instructions": "500-1000mg every 4-6 hours, maximum 4g per day",
            "usage_instructions": "Take with or after food. Can be taken up to 4 times per day as needed",
            "requires_prescription": False,
            "description": "Pain reliever and fever reducer",
            "available": True,
            "quantity_in_stock": 150
        }
    
    Example Output (Error):
        {
            "error": "Medication not found",
            "searched_name": "InvalidMed",
            "suggestions": ["Acamol", "Advil", "Aspirin"]
        }
    """
    try:
        # Validate and normalize input
        normalized_name, validated_language = _validate_search_input(name, language)
        logger.info(f"Searching for medication: name='{normalized_name}', language={validated_language}")
        
        # Get cached DatabaseManager instance
        db_manager = _get_db_manager()
        
        # Search for medications
        medications = db_manager.search_medications_by_name(normalized_name, validated_language)
        
        # Handle no results
        if not medications:
            return _handle_no_medications_found(db_manager, normalized_name, validated_language)
        
        # Handle multiple results - return the first match
        # In a production system, you might want to return all matches and let the agent choose
        medication = medications[0]
        return _handle_medication_found(medication, normalized_name)
        
    except ValueError as e:
        return _handle_search_validation_error(e, name)
        
    except Exception as e:
        return _handle_search_unexpected_error(e, name)


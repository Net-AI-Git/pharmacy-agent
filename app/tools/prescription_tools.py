"""
Prescription tools for the pharmacy AI agent.

Purpose (Why):
This module provides tools for prescription requirement checking that can be used with
OpenAI API function calling. These tools enable the AI agent to verify whether
medications require prescriptions, which is essential for compliance with pharmacy
regulations and helping customers understand prescription requirements before attempting
to purchase medications.

Implementation (What):
Implements plain Python functions that can be registered with OpenAI API as tools.
Uses module-level caching for the DatabaseManager to improve performance and reduce
token usage. Provides comprehensive error handling with safe fallback values
(requires_prescription=true) when medications are not found or errors occur. This
ensures safety by defaulting to requiring a prescription when information is uncertain.
"""

import logging
from typing import Optional, Dict, Any, Literal
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


class PrescriptionCheckInput(BaseModel):
    """
    Input schema for prescription requirement check tool.
    
    Purpose (Why):
    Defines the structure and validation rules for prescription check parameters.
    This ensures type safety and provides clear documentation for the LLM about
    what parameters are expected and their meanings.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for automatic validation. The medication_id
    is required. All fields include Field descriptions which are critical for
    LLM understanding.
    
    Attributes:
        medication_id: The unique identifier of the medication to check (required)
    """
    medication_id: str = Field(description="The unique identifier of the medication to check prescription requirements for")


class PrescriptionCheckResult(BaseModel):
    """
    Output schema for successful prescription requirement check.
    
    Purpose (Why):
    Defines the structure of prescription requirement information returned to the agent.
    Ensures all required fields (requires_prescription, prescription_type) are present
    and provides a consistent format for the agent to process.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for validation and serialization. Includes
    medication identification, prescription requirement status, and prescription type.
    The prescription_type field uses Literal type to restrict values to valid options.
    
    Attributes:
        medication_id: Unique identifier for the medication
        medication_name: Name of the medication (for display purposes)
        requires_prescription: Whether a prescription is required to purchase this medication
        prescription_type: Type of prescription requirement (not_required, prescription_required)
    """
    medication_id: str = Field(description="Unique identifier for the medication")
    medication_name: str = Field(description="Name of the medication (for display purposes)")
    requires_prescription: bool = Field(description="Whether a prescription is required to purchase this medication")
    prescription_type: Literal["not_required", "prescription_required"] = Field(
        description="Type of prescription requirement: 'not_required' for over-the-counter medications, 'prescription_required' for medications that need a prescription"
    )


class PrescriptionCheckError(BaseModel):
    """
    Error schema for prescription check failures.
    
    Purpose (Why):
    Provides structured error information when prescription check fails. Includes the
    medication ID that was searched for and a clear error message. Always sets
    requires_prescription=True as a safe default when errors occur, ensuring safety
    by defaulting to requiring a prescription when information is uncertain.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for consistent error format. Includes the
    medication ID that was searched, error message, and fallback values set to
    safe defaults (requires_prescription=True, prescription_type="prescription_required").
    
    Attributes:
        error: Error message describing what went wrong
        medication_id: The medication ID that was searched for
        requires_prescription: Fallback prescription requirement status (always True for errors, safe default)
        prescription_type: Fallback prescription type (always prescription_required for errors, safe default)
    """
    error: str = Field(description="Error message describing why the prescription check failed")
    medication_id: str = Field(description="The medication ID that was searched for")
    requires_prescription: bool = Field(description="Fallback prescription requirement status (always True for errors, safe default)")
    prescription_type: Literal["not_required", "prescription_required"] = Field(
        description="Fallback prescription type (always prescription_required for errors, safe default)"
    )


def _validate_prescription_input(medication_id: str) -> str:
    """
    Validate and normalize prescription check input parameters.
    
    Purpose (Why):
    Ensures input parameters are valid before performing database lookup. Prevents
    invalid queries and normalizes the input for consistent processing.
    
    Implementation (What):
    Validates that medication_id is not empty and trims whitespace. Returns normalized
    value for further processing.
    
    Args:
        medication_id: The medication ID to validate
    
    Returns:
        Normalized medication_id string
    
    Raises:
        ValueError: If medication_id is empty after trimming
    """
    if not medication_id or not medication_id.strip():
        raise ValueError("Medication ID cannot be empty")
    
    return medication_id.strip()


def _determine_prescription_type(requires_prescription: bool) -> Literal["not_required", "prescription_required"]:
    """
    Determine prescription type from prescription requirement status.
    
    Purpose (Why):
    Converts boolean prescription requirement to a descriptive type that provides
    more context to the agent. This helps the agent provide clearer information
    to users about prescription requirements.
    
    Implementation (What):
    Returns "not_required" if requires_prescription is False, "prescription_required"
    if True. Uses Literal type to ensure type safety.
    
    Args:
        requires_prescription: Boolean indicating if prescription is required
    
    Returns:
        Literal prescription type: "not_required" or "prescription_required"
    """
    return "prescription_required" if requires_prescription else "not_required"


def _build_success_result(medication: Medication) -> PrescriptionCheckResult:
    """
    Build success result from medication prescription data.
    
    Purpose (Why):
    Converts Medication model to PrescriptionCheckResult schema for consistent tool output
    format. Extracts prescription requirement information and determines prescription type.
    
    Implementation (What):
    Maps Medication model fields to PrescriptionCheckResult schema. Determines
    prescription_type from requires_prescription field. Returns validated Pydantic
    model instance.
    
    Args:
        medication: The Medication model instance to convert
    
    Returns:
        PrescriptionCheckResult with all prescription requirement information
    """
    # Use Hebrew name if available, otherwise English name
    medication_name = medication.name_he if medication.name_he else medication.name_en
    
    prescription_type = _determine_prescription_type(medication.requires_prescription)
    
    return PrescriptionCheckResult(
        medication_id=medication.medication_id,
        medication_name=medication_name,
        requires_prescription=medication.requires_prescription,
        prescription_type=prescription_type
    )


def _build_error_result(error_msg: str, medication_id: str) -> PrescriptionCheckError:
    """
    Build error result with message and safe fallback values.
    
    Purpose (Why):
    Creates consistent error responses with safe fallback values. Provides
    structured error information for the agent to process and present to users.
    Always sets requires_prescription=True and prescription_type="prescription_required"
    as safe defaults when errors occur. This ensures safety by defaulting to requiring
    a prescription when information is uncertain.
    
    Implementation (What):
    Creates PrescriptionCheckError instance with error message, medication ID, and
    safe fallback values (requires_prescription=True, prescription_type="prescription_required").
    This ensures the agent always has safe default values to work with.
    
    Args:
        error_msg: The error message to include
        medication_id: The medication ID that was searched
    
    Returns:
        PrescriptionCheckError instance with safe fallback values
    """
    return PrescriptionCheckError(
        error=error_msg,
        medication_id=medication_id,
        requires_prescription=True,
        prescription_type="prescription_required"
    )


def _handle_medication_not_found(medication_id: str) -> Dict[str, Any]:
    """
    Handle case when medication is not found in database.
    
    Purpose (Why):
    Provides consistent error handling when medication lookup fails. Ensures
    safe fallback values are returned to prevent unsafe medication sales.
    
    Implementation (What):
    Logs warning and returns error result with safe fallback values.
    
    Args:
        medication_id: The medication ID that was not found
    
    Returns:
        Dictionary containing PrescriptionCheckError with safe fallback values
    """
    logger.warning(f"Medication not found: {medication_id}")
    error_result = _build_error_result(
        error_msg=f"Medication not found: {medication_id}. Please verify the medication ID.",
        medication_id=medication_id
    )
    return error_result.model_dump()


def _handle_validation_error(error: ValueError, medication_id: str) -> Dict[str, Any]:
    """
    Handle input validation errors.
    
    Purpose (Why):
    Provides consistent error handling for validation failures. Ensures safe
    fallback values are returned when input is invalid.
    
    Implementation (What):
    Logs warning and returns error result with safe fallback values.
    
    Args:
        error: The ValueError that occurred
        medication_id: The medication ID that was being validated
    
    Returns:
        Dictionary containing PrescriptionCheckError with safe fallback values
    """
    logger.warning(f"Input validation error: {str(error)}")
    error_result = _build_error_result(
        error_msg=str(error),
        medication_id=medication_id or ""
    )
    return error_result.model_dump()


def _handle_unexpected_error(error: Exception, medication_id: str) -> Dict[str, Any]:
    """
    Handle unexpected errors during prescription check.
    
    Purpose (Why):
    Provides consistent error handling for unexpected failures. Ensures safe
    fallback values are returned to prevent unsafe medication sales when
    system errors occur.
    
    Implementation (What):
    Logs error with full traceback and returns error result with safe fallback values.
    
    Args:
        error: The Exception that occurred
        medication_id: The medication ID that was being checked
    
    Returns:
        Dictionary containing PrescriptionCheckError with safe fallback values
    """
    logger.error(f"Error checking prescription requirement for medication '{medication_id}': {str(error)}", exc_info=True)
    error_result = _build_error_result(
        error_msg=f"An error occurred while checking prescription requirement: {str(error)}",
        medication_id=medication_id or ""
    )
    return error_result.model_dump()


def _handle_prescription_found(medication: Medication) -> Dict[str, Any]:
    """
    Handle case when medication is found during prescription check.
    
    Purpose (Why):
    Builds and returns success result for found medication. Provides consistent
    result formatting for prescription requirement information.
    
    Implementation (What):
    Logs medication found, builds success result, and returns it.
    
    Args:
        medication: The Medication instance that was found
    
    Returns:
        Dictionary containing PrescriptionCheckResult
    """
    logger.info(f"Found medication: {medication.medication_id} ({medication.name_he} / {medication.name_en})")
    result = _build_success_result(medication)
    logger.debug(
        f"Successfully checked prescription requirement for medication: {medication.medication_id}, "
        f"requires_prescription={result.requires_prescription}, prescription_type={result.prescription_type}"
    )
    return result.model_dump()


def check_prescription_requirement(medication_id: str) -> Dict[str, Any]:
    """
    Check prescription requirement for a medication by ID.
    
    Purpose (Why):
    This tool enables the AI agent to verify whether medications require prescriptions
    when users ask about prescription requirements. It provides essential information
    for compliance with pharmacy regulations and helps customers understand what
    they need before attempting to purchase medications. This is critical for
    preventing illegal sales and ensuring patient safety.
    
    Implementation (What):
    Uses DatabaseManager to retrieve medication by ID from the database. Extracts
    prescription requirement information including requires_prescription status and
    determines prescription_type. Returns complete prescription requirement information
    if medication is found, or error with safe fallback values (requires_prescription=True,
    prescription_type="prescription_required") if not found. Uses module-level caching
    for DatabaseManager to improve performance. Implements safe fallback when errors
    occur to ensure safety by defaulting to requiring a prescription when information
    is uncertain.
    
    Args:
        medication_id: The unique identifier of the medication to check (string, required)
    
    Returns:
        Dictionary containing either:
        - PrescriptionCheckResult: If medication is found (includes prescription requirement details)
        - PrescriptionCheckError: If medication is not found or error occurs (includes error
                                  message and safe fallback values: requires_prescription=True,
                                  prescription_type="prescription_required")
    
    Raises:
        ValueError: If medication_id parameter is empty or invalid
        RuntimeError: If database cannot be loaded
    
    Example Input:
        medication_id="med_001"
    
    Example Output (Success - No Prescription Required):
        {
            "medication_id": "med_001",
            "medication_name": "Acamol",
            "requires_prescription": False,
            "prescription_type": "not_required"
        }
    
    Example Output (Success - Prescription Required):
        {
            "medication_id": "med_003",
            "medication_name": "Amoxicillin",
            "requires_prescription": True,
            "prescription_type": "prescription_required"
        }
    
    Example Output (Error):
        {
            "error": "Medication not found: med_999",
            "medication_id": "med_999",
            "requires_prescription": true,
            "prescription_type": "prescription_required"
        }
    """
    try:
        # Validate and normalize input
        normalized_id = _validate_prescription_input(medication_id)
        logger.info(f"Checking prescription requirement for medication: id='{normalized_id}'")
        
        # Get cached DatabaseManager instance
        db_manager = _get_db_manager()
        
        # Retrieve medication by ID
        medication = db_manager.get_medication_by_id(normalized_id)
        
        # Handle medication not found
        if medication is None:
            return _handle_medication_not_found(normalized_id)
        
        # Build and return success result
        return _handle_prescription_found(medication)
        
    except ValueError as e:
        return _handle_validation_error(e, medication_id)
        
    except Exception as e:
        return _handle_unexpected_error(e, medication_id)


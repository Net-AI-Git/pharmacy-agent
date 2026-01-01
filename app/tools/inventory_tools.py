"""
Inventory tools for the pharmacy AI agent.

Purpose (Why):
This module provides tools for inventory and stock-related operations that can be used with
OpenAI API function calling. These tools enable the AI agent to check medication stock
availability, verify quantities, and provide real-time inventory information to users.
This is essential for helping customers know if medications are available and in what quantities.

Implementation (What):
Implements plain Python functions that can be registered with OpenAI API as tools.
Uses module-level caching for the DatabaseManager to improve performance and reduce
token usage. Provides comprehensive error handling with safe fallback values when
medications are not found or errors occur. Validates quantity requirements against
available stock.
"""

import logging
from typing import Optional, Dict, Any
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


class StockCheckInput(BaseModel):
    """
    Input schema for stock availability check tool.
    
    Purpose (Why):
    Defines the structure and validation rules for stock check parameters.
    This ensures type safety and provides clear documentation for the LLM about
    what parameters are expected and their meanings.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for automatic validation. The medication_id
    is required, while quantity is optional. All fields include Field descriptions
    which are critical for LLM understanding.
    
    Attributes:
        medication_id: The unique identifier of the medication to check (required)
        quantity: Optional quantity to check availability for (if provided, checks if enough stock exists)
    """
    medication_id: str = Field(description="The unique identifier of the medication to check stock for")
    quantity: Optional[int] = Field(
        default=None,
        description="Optional quantity to check availability for. If provided, the tool will verify if there is enough stock to fulfill this quantity. If not provided, only checks general availability."
    )


class StockCheckResult(BaseModel):
    """
    Output schema for successful stock availability check.
    
    Purpose (Why):
    Defines the structure of stock information returned to the agent. Ensures
    all required fields (available, quantity_in_stock, last_restocked) are present
    and provides a consistent format for the agent to process.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for validation and serialization. Includes
    medication identification, availability status, current stock quantity, and
    restocking information. The sufficient_quantity field indicates if the requested
    quantity (if provided) is available.
    
    Attributes:
        medication_id: Unique identifier for the medication
        medication_name: Name of the medication (for display purposes)
        available: Whether the medication is currently available in stock
        quantity_in_stock: Current quantity of the medication in stock
        last_restocked: ISO format datetime string of when the medication was last restocked
        sufficient_quantity: Whether there is enough stock for the requested quantity (if quantity was provided)
        requested_quantity: The quantity that was requested (if provided)
    """
    medication_id: str = Field(description="Unique identifier for the medication")
    medication_name: str = Field(description="Name of the medication (for display purposes)")
    available: bool = Field(description="Whether the medication is currently available in stock")
    quantity_in_stock: int = Field(description="Current quantity of the medication in stock")
    last_restocked: str = Field(description="ISO format datetime string of when the medication was last restocked")
    sufficient_quantity: bool = Field(description="Whether there is enough stock for the requested quantity (True if quantity was not provided, or if quantity_in_stock >= requested_quantity)")
    requested_quantity: Optional[int] = Field(description="The quantity that was requested (None if not provided)")


class StockCheckError(BaseModel):
    """
    Error schema for stock check failures.
    
    Purpose (Why):
    Provides structured error information when stock check fails. Includes the
    medication ID that was searched for and a clear error message to help
    users understand what went wrong.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for consistent error format. Includes the
    medication ID that was searched, error message, and a fallback availability
    status set to False for safety.
    
    Attributes:
        error: Error message describing what went wrong
        medication_id: The medication ID that was searched for
        available: Fallback availability status (always False for errors)
    """
    error: str = Field(description="Error message describing why the stock check failed")
    medication_id: str = Field(description="The medication ID that was searched for")
    available: bool = Field(description="Fallback availability status (always False for errors, safe default)")


def _validate_stock_input(medication_id: str, quantity: Optional[int]) -> tuple[str, Optional[int]]:
    """
    Validate and normalize stock check input parameters.
    
    Purpose (Why):
    Ensures input parameters are valid before performing database lookup. Prevents
    invalid queries and normalizes the input for consistent processing.
    
    Implementation (What):
    Validates that medication_id is not empty and trims whitespace. Validates that
    quantity is positive if provided. Returns normalized values for further processing.
    
    Args:
        medication_id: The medication ID to validate
        quantity: Optional quantity to validate
    
    Returns:
        Tuple of (normalized_medication_id, validated_quantity)
    
    Raises:
        ValueError: If medication_id is empty after trimming or if quantity is negative
    """
    if not medication_id or not medication_id.strip():
        raise ValueError("Medication ID cannot be empty")
    
    normalized_id = medication_id.strip()
    
    if quantity is not None and quantity < 0:
        raise ValueError("Quantity cannot be negative")
    
    return normalized_id, quantity


def _build_success_result(medication: Medication, requested_quantity: Optional[int]) -> StockCheckResult:
    """
    Build success result from medication stock data.
    
    Purpose (Why):
    Converts Medication model to StockCheckResult schema for consistent tool output
    format. Extracts stock information and calculates if sufficient quantity is available.
    
    Implementation (What):
    Maps Medication model fields to StockCheckResult schema, including nested stock
    information. Calculates sufficient_quantity based on whether requested_quantity
    is provided and if stock is adequate. Returns validated Pydantic model instance.
    
    Args:
        medication: The Medication model instance to convert
        requested_quantity: Optional quantity that was requested
    
    Returns:
        StockCheckResult with all stock information
    """
    sufficient = True
    if requested_quantity is not None:
        sufficient = medication.stock.quantity_in_stock >= requested_quantity
    
    # Use Hebrew name if available, otherwise English name
    medication_name = medication.name_he if medication.name_he else medication.name_en
    
    return StockCheckResult(
        medication_id=medication.medication_id,
        medication_name=medication_name,
        available=medication.stock.available,
        quantity_in_stock=medication.stock.quantity_in_stock,
        last_restocked=medication.stock.last_restocked,
        sufficient_quantity=sufficient,
        requested_quantity=requested_quantity
    )


def _build_error_result(error_msg: str, medication_id: str) -> StockCheckError:
    """
    Build error result with message and fallback values.
    
    Purpose (Why):
    Creates consistent error responses with safe fallback values. Provides
    structured error information for the agent to process and present to users.
    Always sets available=False as a safe default when errors occur.
    
    Implementation (What):
    Creates StockCheckError instance with error message, medication ID, and
    available=False as fallback. This ensures the agent always has a safe default
    value to work with.
    
    Args:
        error_msg: The error message to include
        medication_id: The medication ID that was searched
    
    Returns:
        StockCheckError instance with available=False
    """
    return StockCheckError(
        error=error_msg,
        medication_id=medication_id,
        available=False
    )


def _handle_medication_not_found_stock(medication_id: str) -> Dict[str, Any]:
    """
    Handle case when medication is not found during stock check.
    
    Purpose (Why):
    Provides consistent error handling when medication lookup fails during stock check.
    Ensures safe fallback values are returned.
    
    Implementation (What):
    Logs warning and returns error result with available=False fallback.
    
    Args:
        medication_id: The medication ID that was not found
    
    Returns:
        Dictionary containing StockCheckError with available=False
    """
    logger.warning(f"Medication not found: {medication_id}")
    error_result = _build_error_result(
        error_msg=f"Medication not found: {medication_id}. Please verify the medication ID.",
        medication_id=medication_id
    )
    return error_result.model_dump()


def _handle_stock_validation_error(error: ValueError, medication_id: str) -> Dict[str, Any]:
    """
    Handle input validation errors during stock check.
    
    Purpose (Why):
    Provides consistent error handling for validation failures. Ensures safe
    fallback values are returned when input is invalid.
    
    Implementation (What):
    Logs warning and returns error result with available=False fallback.
    
    Args:
        error: The ValueError that occurred
        medication_id: The medication ID that was being validated
    
    Returns:
        Dictionary containing StockCheckError with available=False
    """
    logger.warning(f"Input validation error: {str(error)}")
    error_result = _build_error_result(
        error_msg=str(error),
        medication_id=medication_id or ""
    )
    return error_result.model_dump()


def _handle_stock_unexpected_error(error: Exception, medication_id: str) -> Dict[str, Any]:
    """
    Handle unexpected errors during stock check.
    
    Purpose (Why):
    Provides consistent error handling for unexpected failures. Ensures safe
    fallback values are returned when system errors occur.
    
    Implementation (What):
    Logs error with full traceback and returns error result with available=False fallback.
    
    Args:
        error: The Exception that occurred
        medication_id: The medication ID that was being checked
    
    Returns:
        Dictionary containing StockCheckError with available=False
    """
    logger.error(f"Error checking stock for medication '{medication_id}': {str(error)}", exc_info=True)
    error_result = _build_error_result(
        error_msg=f"An error occurred while checking stock: {str(error)}",
        medication_id=medication_id or ""
    )
    return error_result.model_dump()


def check_stock_availability(medication_id: str, quantity: Optional[int] = None) -> Dict[str, Any]:
    """
    Check stock availability for a medication by ID.
    
    Purpose (Why):
    This tool enables the AI agent to check medication stock availability when users
    ask about inventory. It verifies if medications are in stock, how many units are
    available, and whether there is sufficient quantity for a specific request. This is
    essential for providing accurate inventory information to customers and helping them
    make informed decisions about medication purchases.
    
    Implementation (What):
    Uses DatabaseManager to retrieve medication by ID from the database. Extracts stock
    information including availability, quantity, and last restocked date. If a quantity
    is provided, verifies if there is sufficient stock. Returns complete stock information
    if medication is found, or error with fallback values if not found. Uses module-level
    caching for DatabaseManager to improve performance. Implements safe fallback (available=False)
    when errors occur.
    
    Args:
        medication_id: The unique identifier of the medication to check (string, required)
        quantity: Optional quantity to check availability for (integer). If provided,
                 the tool will verify if there is enough stock to fulfill this quantity.
                 If not provided, only checks general availability.
    
    Returns:
        Dictionary containing either:
        - StockCheckResult: If medication is found (includes all stock details)
        - StockCheckError: If medication is not found or error occurs (includes error
                          message and available=False as fallback)
    
    Raises:
        ValueError: If medication_id parameter is empty or invalid, or if quantity is negative
        RuntimeError: If database cannot be loaded
    
    Example Input:
        medication_id="med_001", quantity=10
    
    Example Output (Success):
        {
            "medication_id": "med_001",
            "medication_name": "Acamol",
            "available": True,
            "quantity_in_stock": 150,
            "last_restocked": "2024-01-15T10:30:00Z",
            "sufficient_quantity": True,
            "requested_quantity": 10
        }
    
    Example Output (Error):
        {
            "error": "Medication not found: med_999",
            "medication_id": "med_999",
            "available": false
        }
    """
    try:
        # Validate and normalize input
        normalized_id, validated_quantity = _validate_stock_input(medication_id, quantity)
        logger.info(f"Checking stock for medication: id='{normalized_id}', quantity={validated_quantity}")
        
        # Get cached DatabaseManager instance
        db_manager = _get_db_manager()
        
        # Retrieve medication by ID
        medication = db_manager.get_medication_by_id(normalized_id)
        
        # Handle medication not found
        if medication is None:
            return _handle_medication_not_found_stock(normalized_id)
        
        logger.info(f"Found medication: {medication.medication_id} ({medication.name_he} / {medication.name_en})")
        
        # Build and return success result
        result = _build_success_result(medication, validated_quantity)
        logger.debug(f"Successfully checked stock for medication: {medication.medication_id}, available={result.available}, quantity={result.quantity_in_stock}")
        return result.model_dump()
        
    except ValueError as e:
        return _handle_stock_validation_error(e, medication_id)
        
    except Exception as e:
        return _handle_stock_unexpected_error(e, medication_id)


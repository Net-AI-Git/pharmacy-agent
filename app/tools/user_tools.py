"""
User tools for the pharmacy AI agent.

Purpose (Why):
This module provides tools for user-related operations that can be used with
OpenAI API function calling. These tools enable the AI agent to find users by
name or email, retrieve their prescriptions, and check for active prescriptions
for specific medications. The tools support natural language queries where users
identify themselves by name or email instead of technical IDs.

Implementation (What):
Implements plain Python functions that can be registered with OpenAI API as tools.
Uses module-level caching for the DatabaseManager to improve performance and reduce
token usage. Provides comprehensive error handling with suggestions when users are
not found. Supports case-insensitive partial matching for flexible user search.
"""

import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.database.db import DatabaseManager
from app.models.user import User
from app.models.prescription import Prescription
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


class UserSearchInput(BaseModel):
    """
    Input schema for user search tool.
    
    Purpose (Why):
    Defines the structure and validation rules for user search parameters.
    This ensures type safety and provides clear documentation for the LLM about
    what parameters are expected and their meanings.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for automatic validation. All fields include
    Field descriptions which are critical for LLM understanding.
    
    Attributes:
        name_or_email: The user name or email address to search for (required)
    """
    name_or_email: str = Field(description="The user name or email address to search for (supports partial matches and case-insensitive search)")


class UserSearchResult(BaseModel):
    """
    Output schema for successful user search.
    
    Purpose (Why):
    Defines the structure of user information returned to the agent. Ensures
    all required fields are present and provides a consistent format for the
    agent to process.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for validation and serialization. Includes
    all user fields with Field descriptions.
    
    Attributes:
        user_id: Unique identifier for the user (use this for other tool calls)
        name: Full name of the user
        email: Email address of the user
        prescriptions: List of prescription IDs associated with this user
    """
    user_id: str = Field(description="Unique identifier for the user (use this for get_user_prescriptions and check_user_prescription_for_medication)")
    name: str = Field(description="Full name of the user")
    email: str = Field(description="Email address of the user")
    prescriptions: List[str] = Field(description="List of prescription IDs associated with this user")


class UserSearchError(BaseModel):
    """
    Error schema for user search failures.
    
    Purpose (Why):
    Provides structured error information when user search fails. Includes
    suggestions to help users find the correct user name or email, improving
    user experience and reducing frustration.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for consistent error format. Includes the
    original search query, error message, and a list of suggested user names
    that might match what the user was looking for.
    
    Attributes:
        error: Error message describing what went wrong
        searched_name_or_email: The name or email that was searched for
        suggestions: List of suggested user names or emails that might match
    """
    error: str = Field(description="Error message describing why the search failed")
    searched_name_or_email: str = Field(description="The name or email that was searched for")
    suggestions: List[str] = Field(description="List of suggested user names or emails that might match the search query")


class UserPrescriptionsInput(BaseModel):
    """
    Input schema for user prescriptions retrieval tool.
    
    Purpose (Why):
    Defines the structure and validation rules for user prescriptions retrieval
    parameters. This ensures type safety and provides clear documentation for
    the LLM about what parameters are expected.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for automatic validation. All fields include
    Field descriptions which are critical for LLM understanding.
    
    Attributes:
        user_id: The unique identifier of the user to get prescriptions for (required)
    """
    user_id: str = Field(description="The unique identifier of the user to get prescriptions for. This is typically obtained from get_user_by_name_or_email.")


class PrescriptionInfo(BaseModel):
    """
    Prescription information schema for user prescriptions result.
    
    Purpose (Why):
    Provides detailed prescription information including complete medication details
    to avoid redundant tool calls. When get_user_prescriptions returns this information,
    the AI agent has all medication details (active ingredients, dosage, etc.) and
    doesn't need to call get_medication_by_name separately, reducing latency.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for validation and serialization. Includes
    all prescription fields plus complete medication information (names, active ingredients,
    dosage instructions, etc.) to prevent redundant tool calls.
    
    Attributes:
        prescription_id: Unique identifier for the prescription
        medication_id: ID of the prescribed medication
        medication_name_he: Name of the medication in Hebrew
        medication_name_en: Name of the medication in English
        active_ingredients: List of active ingredients (to avoid calling get_medication_by_name)
        dosage_forms: Available dosage forms
        dosage_instructions: Detailed dosage instructions
        usage_instructions: Instructions on how to use the medication
        description: General description of what the medication is used for
        prescribed_by: Name of the doctor who prescribed the medication
        prescription_date: ISO format datetime string of when the prescription was issued
        expiry_date: ISO format datetime string of when the prescription expires
        quantity: Quantity of medication prescribed
        refills_remaining: Number of refills remaining for this prescription
        status: Current status of the prescription (active, expired, cancelled, completed)
    """
    prescription_id: str = Field(description="Unique identifier for the prescription")
    medication_id: str = Field(description="ID of the prescribed medication")
    medication_name_he: str = Field(description="Name of the medication in Hebrew")
    medication_name_en: str = Field(description="Name of the medication in English")
    active_ingredients: List[str] = Field(default_factory=list, description="List of active ingredients in the medication")
    dosage_forms: List[str] = Field(default_factory=list, description="Available dosage forms (e.g., Tablets, Capsules, Syrup)")
    dosage_instructions: Optional[str] = Field(default=None, description="Detailed dosage instructions including amount and frequency")
    usage_instructions: Optional[str] = Field(default=None, description="Instructions on how to use the medication, including when to take it")
    description: Optional[str] = Field(default=None, description="General description of what the medication is used for")
    prescribed_by: str = Field(description="Name of the doctor who prescribed the medication")
    prescription_date: str = Field(description="ISO format datetime string of when the prescription was issued")
    expiry_date: str = Field(description="ISO format datetime string of when the prescription expires")
    quantity: int = Field(description="Quantity of medication prescribed")
    refills_remaining: int = Field(description="Number of refills remaining for this prescription")
    status: str = Field(description="Current status of the prescription (active, expired, cancelled, completed)")


class UserPrescriptionsResult(BaseModel):
    """
    Output schema for successful user prescriptions retrieval.
    
    Purpose (Why):
    Defines the structure of user prescriptions information returned to the agent.
    Ensures all required fields are present and provides a consistent format for
    the agent to process.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for validation and serialization. Includes
    user identification and list of prescription details.
    
    Attributes:
        user_id: Unique identifier for the user
        user_name: Full name of the user
        prescriptions: List of prescription information (empty list if user has no prescriptions)
    """
    user_id: str = Field(description="Unique identifier for the user")
    user_name: str = Field(description="Full name of the user")
    prescriptions: List[PrescriptionInfo] = Field(description="List of prescription information for this user (empty list if user has no prescriptions)")


class PrescriptionCheckInput(BaseModel):
    """
    Input schema for prescription check tool.
    
    Purpose (Why):
    Defines the structure and validation rules for prescription check parameters.
    This ensures type safety and provides clear documentation for the LLM about
    what parameters are expected.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for automatic validation. All fields include
    Field descriptions which are critical for LLM understanding.
    
    Attributes:
        user_id: The unique identifier of the user to check prescription for (required)
        medication_id: The unique identifier of the medication to check prescription for (required)
    """
    user_id: str = Field(description="The unique identifier of the user to check prescription for. This is typically obtained from get_user_by_name_or_email.")
    medication_id: str = Field(description="The unique identifier of the medication to check prescription for. This is typically obtained from get_medication_by_name.")


class PrescriptionCheckResult(BaseModel):
    """
    Output schema for prescription check result.
    
    Purpose (Why):
    Defines the structure of prescription check information returned to the agent.
    Provides clear indication of whether user has an active prescription for the
    specified medication.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for validation and serialization. Includes
    prescription status and optional prescription details.
    
    Attributes:
        has_active_prescription: Whether the user has an active prescription for this medication
        prescription_details: Prescription information if active prescription exists, None otherwise
    """
    has_active_prescription: bool = Field(description="Whether the user has an active prescription for this medication")
    prescription_details: Optional[PrescriptionInfo] = Field(default=None, description="Prescription information if active prescription exists, None otherwise")


def _validate_user_search_input(name_or_email: str) -> str:
    """
    Validate and normalize user search input parameters.
    
    Purpose (Why):
    Ensures input is valid before processing. Normalizes input to prevent
    unnecessary processing failures and improves user experience.
    
    Implementation (What):
    Trims whitespace and validates that input is not empty. Raises ValueError
    if input is invalid.
    
    Args:
        name_or_email: The name or email to validate
    
    Returns:
        Normalized name or email string
    
    Raises:
        ValueError: If name_or_email is empty or invalid
    """
    if not name_or_email or not name_or_email.strip():
        raise ValueError("name_or_email cannot be empty")
    
    return name_or_email.strip()


def _generate_user_suggestions(db_manager: DatabaseManager, name_or_email: str) -> List[str]:
    """
    Generate suggestions when user is not found.
    
    Purpose (Why):
    Provides helpful suggestions to users when their search doesn't match any
    users. Improves user experience by offering similar names or emails.
    
    Implementation (What):
    Searches for partial matches in user names and emails. Returns up to 5
    suggestions including both names and emails.
    
    Args:
        db_manager: DatabaseManager instance for searching
        name_or_email: The search term that didn't match
    
    Returns:
        List of suggested user names or emails (up to 5)
    """
    if len(name_or_email) < 2:
        return []
    
    # Try searching with first few characters
    partial_term = name_or_email[:3] if len(name_or_email) > 3 else name_or_email
    all_users = db_manager.search_users_by_name_or_email(partial_term)
    
    suggestions = []
    seen = set()
    
    for user in all_users[:5]:
        if user.name not in seen:
            suggestions.append(user.name)
            seen.add(user.name)
        if user.email not in seen:
            suggestions.append(user.email)
            seen.add(user.email)
    
    return suggestions[:5]


def _build_user_search_success_result(user: User) -> UserSearchResult:
    """
    Build success result from user data.
    
    Purpose (Why):
    Converts User model to UserSearchResult schema for consistent tool output
    format. Provides all user information needed for subsequent tool calls.
    
    Implementation (What):
    Maps User model fields to UserSearchResult schema. Returns validated
    Pydantic model instance.
    
    Args:
        user: The User model instance to convert
    
    Returns:
        UserSearchResult with user information
    """
    return UserSearchResult(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        prescriptions=user.prescriptions
    )


def _build_user_search_error_result(error_msg: str, name_or_email: str, suggestions: List[str]) -> UserSearchError:
    """
    Build error result with message and suggestions.
    
    Purpose (Why):
    Creates consistent error responses with helpful suggestions. Provides
    structured error information for the agent to process and present to users.
    
    Implementation (What):
    Creates UserSearchError instance with error message, searched term, and
    list of suggestions. Limits suggestions to 5 items.
    
    Args:
        error_msg: The error message to include
        name_or_email: The name or email that was searched
        suggestions: List of suggested user names or emails
    
    Returns:
        UserSearchError instance
    """
    return UserSearchError(
        error=error_msg,
        searched_name_or_email=name_or_email,
        suggestions=suggestions[:5]
    )


def get_user_by_name_or_email(name_or_email: str, authenticated_user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for a user by name or email address.
    
    Purpose (Why):
    Enables the AI agent to find users when they provide their name or email
    address instead of user_id. This supports natural language queries where
    users identify themselves by name or email, which is more user-friendly
    than requiring technical IDs. Supports case-insensitive partial matching
    for flexible search. Includes security check: if authenticated_user_id is provided,
    only returns the authenticated user's information, preventing access to other users' data.
    
    Implementation (What):
    If authenticated_user_id is provided, returns only that user's information (security).
    Otherwise, validates input, searches database using DatabaseManager.search_users_by_name_or_email,
    handles multiple results (returns first match), and provides suggestions if no
    user is found. Uses module-level caching for DatabaseManager to improve performance.
    Returns UserSearchResult if user is found, UserSearchError if not found.
    
    Args:
        name_or_email: The user name or email address to search for (case-insensitive, partial match).
            Ignored if authenticated_user_id is provided (security).
        authenticated_user_id: The authenticated user ID (from session). If provided, only returns
            this user's information, ignoring name_or_email parameter for security.
    
    Returns:
        Dictionary containing:
        - UserSearchResult: If user is found (includes user_id, name, email, prescriptions)
        - UserSearchError: If user is not found (includes error message and suggestions)
    
    Example:
        >>> result = get_user_by_name_or_email("John Doe")
        >>> if "error" in result:
        ...     print(f"Error: {result['error']}")
        ... else:
        ...     print(f"Found user: {result['user_id']}")
    """
    try:
        # Security: If user is authenticated, check if the request is about the authenticated user
        if authenticated_user_id:
            logger.info(f"User is authenticated: {authenticated_user_id}, checking if request is about authenticated user")
            db_manager = _get_db_manager()
            authenticated_user = db_manager.get_user_by_id(authenticated_user_id)
            if not authenticated_user:
                logger.warning(f"Authenticated user not found: {authenticated_user_id}")
                error_result = _build_user_search_error_result(
                    error_msg=f"Authenticated user '{authenticated_user_id}' not found in database.",
                    name_or_email=authenticated_user_id,
                    suggestions=[]
                )
                return error_result.model_dump()
            
            # Normalize the requested name/email for comparison
            normalized_input = _validate_user_search_input(name_or_email)
            
            # Check if the requested name/email matches the authenticated user
            # Compare with user's name and email (case-insensitive)
            requested_matches_authenticated = (
                normalized_input.lower() == authenticated_user.name.lower() or
                normalized_input.lower() == authenticated_user.email.lower() or
                normalized_input.lower() == authenticated_user_id.lower()
            )
            
            # Also check if the request is about "my" or "me" (common in queries like "my prescriptions")
            is_self_reference = any(phrase in normalized_input.lower() for phrase in ["my", "me", "myself", "שלי", "אני"])
            
            if not requested_matches_authenticated and not is_self_reference:
                # Request is about a different user - reject immediately without database access
                logger.warning(
                    f"Access denied: Authenticated user '{authenticated_user_id}' ({authenticated_user.name}) "
                    f"tried to access information about '{normalized_input}'"
                )
                error_result = _build_user_search_error_result(
                    error_msg="Access denied. You can only access your own information. I cannot provide information about other users.",
                    name_or_email=normalized_input,
                    suggestions=[]
                )
                return error_result.model_dump()
            
            # Request is about the authenticated user - return their information
            logger.info(f"Returning authenticated user: {authenticated_user.user_id} ({authenticated_user.name})")
            result = _build_user_search_success_result(authenticated_user)
            return result.model_dump()
        
        # If not authenticated, proceed with normal search (public information only)
        normalized_input = _validate_user_search_input(name_or_email)
        logger.info(f"Searching for user: name_or_email='{normalized_input}' (not authenticated)")
        
        db_manager = _get_db_manager()
        users = db_manager.search_users_by_name_or_email(normalized_input)
        
        if not users:
            logger.warning(f"No users found for name_or_email='{normalized_input}'")
            suggestions = _generate_user_suggestions(db_manager, normalized_input)
            error_result = _build_user_search_error_result(
                error_msg=f"User '{normalized_input}' not found. Please check the spelling or try a different name or email.",
                name_or_email=normalized_input,
                suggestions=suggestions
            )
            return error_result.model_dump()
        
        # If multiple users found, return the first one
        # In a real system, you might want to ask the user to clarify
        if len(users) > 1:
            logger.info(f"Multiple users found ({len(users)}), returning first match")
        
        user = users[0]
        logger.info(f"Found user: {user.user_id} ({user.name})")
        
        result = _build_user_search_success_result(user)
        logger.debug(f"Successfully retrieved user: {user.user_id}")
        return result.model_dump()
        
    except ValueError as e:
        logger.error(f"Invalid input for user search: {str(e)}", exc_info=True)
        error_result = _build_user_search_error_result(
            error_msg=f"Invalid input: {str(e)}",
            name_or_email=name_or_email,
            suggestions=[]
        )
        return error_result.model_dump()
    except Exception as e:
        logger.error(f"Error searching for user '{name_or_email}': {str(e)}", exc_info=True)
        error_result = _build_user_search_error_result(
            error_msg=f"An error occurred while searching for user: {str(e)}",
            name_or_email=name_or_email,
            suggestions=[]
        )
        return error_result.model_dump()


def get_user_prescriptions(user_id: str, authenticated_user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all prescriptions for a specific user.
    
    Purpose (Why):
    Enables the AI agent to retrieve all prescriptions associated with a user.
    This allows users to view their prescription history and verify prescription
    details. Provides complete prescription information including medication names
    for better user experience. Includes security check to ensure only authenticated
    users can access their own prescription information.
    
    Implementation (What):
    Validates user_id, checks authentication (authenticated_user_id must match user_id),
    retrieves prescriptions using DatabaseManager.get_prescriptions_by_user,
    enriches prescription data with medication names, and returns formatted result.
    Returns empty list if user has no prescriptions (not an error). Uses module-level
    caching for DatabaseManager to improve performance.
    
    Args:
        user_id: The unique identifier of the user to get prescriptions for
        authenticated_user_id: The authenticated user ID (from session). Must match user_id
            for security. If None, access is denied.
    
    Returns:
        Dictionary containing:
        - UserPrescriptionsResult: If user is found and authenticated (includes user_id, user_name, prescriptions list)
        - Error dictionary: If user is not found or authentication fails (includes error message)
    
    Example:
        >>> result = get_user_prescriptions("user_001", authenticated_user_id="user_001")
        >>> if "error" in result:
        ...     print(f"Error: {result['error']}")
        ... else:
        ...     print(f"User has {len(result['prescriptions'])} prescriptions")
    """
    try:
        # Security check: Only authenticated users can access their own prescriptions
        if not authenticated_user_id:
            if not user_id or not user_id.strip():
                raise ValueError("user_id cannot be empty")
            normalized_user_id = user_id.strip()
            logger.warning(f"Access denied: No authenticated user for user_id='{normalized_user_id}'")
            return {
                "error": "Authentication required. Please log in to access your prescriptions.",
                "success": False
            }
        
        # Normalize authenticated_user_id
        normalized_authenticated_user_id = authenticated_user_id.strip()
        
        # Normalize requested user_id
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")
        normalized_user_id = user_id.strip()
        
        # Security check: user_id must match authenticated_user_id
        if normalized_user_id != normalized_authenticated_user_id:
            logger.warning(
                f"Access denied: Authenticated user '{normalized_authenticated_user_id}' "
                f"tried to access user '{normalized_user_id}' prescriptions"
            )
            return {
                "error": "Access denied. You can only access your own prescription information.",
                "success": False
            }
        
        # Use authenticated_user_id (which matches user_id after validation)
        normalized_user_id = normalized_authenticated_user_id
        logger.info(f"Getting prescriptions for authenticated user: user_id='{normalized_user_id}'")
        
        db_manager = _get_db_manager()
        
        # First verify user exists
        user = db_manager.get_user_by_id(normalized_user_id)
        if not user:
            logger.warning(f"User not found: {normalized_user_id}")
            return {
                "error": f"User '{normalized_user_id}' not found",
                "success": False
            }
        
        # Get prescriptions
        prescriptions = db_manager.get_prescriptions_by_user(normalized_user_id)
        logger.info(f"Found {len(prescriptions)} prescriptions for user: {normalized_user_id}")
        
        # Enrich prescriptions with complete medication information to avoid redundant tool calls
        # This includes all medication details (active ingredients, dosage, etc.) so the AI
        # doesn't need to call get_medication_by_name separately, reducing latency
        prescription_info_list = []
        for prescription in prescriptions:
            medication = db_manager.get_medication_by_id(prescription.medication_id)
            if medication:
                prescription_info = PrescriptionInfo(
                    prescription_id=prescription.prescription_id,
                    medication_id=prescription.medication_id,
                    medication_name_he=medication.name_he,
                    medication_name_en=medication.name_en,
                    active_ingredients=medication.active_ingredients,
                    dosage_forms=medication.dosage_forms,
                    dosage_instructions=medication.dosage_instructions,
                    usage_instructions=medication.usage_instructions,
                    description=medication.description,
                    prescribed_by=prescription.prescribed_by,
                    prescription_date=prescription.prescription_date,
                    expiry_date=prescription.expiry_date,
                    quantity=prescription.quantity,
                    refills_remaining=prescription.refills_remaining,
                    status=prescription.status
                )
                prescription_info_list.append(prescription_info)
            else:
                logger.warning(f"Medication {prescription.medication_id} not found for prescription {prescription.prescription_id}")
                # Still include prescription even if medication not found
                prescription_info = PrescriptionInfo(
                    prescription_id=prescription.prescription_id,
                    medication_id=prescription.medication_id,
                    medication_name_he="Unknown",
                    medication_name_en="Unknown",
                    active_ingredients=[],
                    dosage_forms=[],
                    dosage_instructions=None,
                    usage_instructions=None,
                    description=None,
                    prescribed_by=prescription.prescribed_by,
                    prescription_date=prescription.prescription_date,
                    expiry_date=prescription.expiry_date,
                    quantity=prescription.quantity,
                    refills_remaining=prescription.refills_remaining,
                    status=prescription.status
                )
                prescription_info_list.append(prescription_info)
        
        result = UserPrescriptionsResult(
            user_id=user.user_id,
            user_name=user.name,
            prescriptions=prescription_info_list
        )
        
        logger.debug(f"Successfully retrieved {len(prescription_info_list)} prescriptions for user: {normalized_user_id}")
        return result.model_dump()
        
    except ValueError as e:
        logger.error(f"Invalid input for get_user_prescriptions: {str(e)}", exc_info=True)
        return {
            "error": f"Invalid input: {str(e)}",
            "success": False
        }
    except Exception as e:
        logger.error(f"Error getting prescriptions for user '{user_id}': {str(e)}", exc_info=True)
        return {
            "error": f"An error occurred while getting prescriptions: {str(e)}",
            "success": False
        }


def check_user_prescription_for_medication(user_id: str, medication_id: str, authenticated_user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if a user has an active prescription for a specific medication.
    
    Purpose (Why):
    Enables the AI agent to verify whether a user has an active prescription for
    a specific medication. This is essential for prescription validation before
    medication purchases and helps users understand their prescription status.
    Only returns active prescriptions (status="active"). Includes security check
    to ensure only authenticated users can access their own prescription information.
    
    Implementation (What):
    Validates inputs, checks authentication (authenticated_user_id must match user_id),
    retrieves user prescriptions, filters for active prescriptions matching the
    medication_id, and returns result. Returns has_active_prescription=false if no
    active prescription found (not an error). Uses module-level caching for
    DatabaseManager to improve performance.
    
    Args:
        user_id: The unique identifier of the user to check prescription for
        medication_id: The unique identifier of the medication to check prescription for
        authenticated_user_id: The authenticated user ID (from session). Must match user_id
            for security. If None, access is denied.
    
    Returns:
        Dictionary containing:
        - PrescriptionCheckResult: Includes has_active_prescription and optional prescription_details
        - Error dictionary: If user or medication is not found, or authentication fails (includes error message)
    
    Example:
        >>> result = check_user_prescription_for_medication("user_001", "med_003", authenticated_user_id="user_001")
        >>> if "error" in result:
        ...     print(f"Error: {result['error']}")
        ... else:
        ...     print(f"Has active prescription: {result['has_active_prescription']}")
    """
    try:
        # Security check: Only authenticated users can access their own prescriptions
        if not authenticated_user_id:
            if not user_id or not user_id.strip():
                raise ValueError("user_id cannot be empty")
            normalized_user_id = user_id.strip()
            if not medication_id or not medication_id.strip():
                raise ValueError("medication_id cannot be empty")
            normalized_medication_id = medication_id.strip()
            logger.warning(f"Access denied: No authenticated user for user_id='{normalized_user_id}'")
            return {
                "error": "Authentication required. Please log in to access your prescription information.",
                "success": False
            }
        
        # Normalize authenticated_user_id
        normalized_authenticated_user_id = authenticated_user_id.strip()
        
        # Normalize requested user_id
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")
        normalized_user_id = user_id.strip()
        
        if not medication_id or not medication_id.strip():
            raise ValueError("medication_id cannot be empty")
        
        normalized_medication_id = medication_id.strip()
        
        # Security check: user_id must match authenticated_user_id
        if normalized_user_id != normalized_authenticated_user_id:
            logger.warning(
                f"Access denied: Authenticated user '{normalized_authenticated_user_id}' "
                f"tried to access user '{normalized_user_id}' prescription"
            )
            return {
                "error": "Access denied. You can only access your own prescription information.",
                "success": False
            }
        
        # Use authenticated_user_id (which matches user_id after validation)
        normalized_user_id = normalized_authenticated_user_id
        logger.info(f"Checking prescription for authenticated user: user_id='{normalized_user_id}', medication_id='{normalized_medication_id}'")
        
        db_manager = _get_db_manager()
        
        # Verify user exists
        user = db_manager.get_user_by_id(normalized_user_id)
        if not user:
            logger.warning(f"User not found: {normalized_user_id}")
            return {
                "error": f"User '{normalized_user_id}' not found",
                "success": False
            }
        
        # Verify medication exists
        medication = db_manager.get_medication_by_id(normalized_medication_id)
        if not medication:
            logger.warning(f"Medication not found: {normalized_medication_id}")
            return {
                "error": f"Medication '{normalized_medication_id}' not found",
                "success": False
            }
        
        # Get prescriptions and filter for active ones matching medication
        prescriptions = db_manager.get_prescriptions_by_user(normalized_user_id)
        active_prescription = None
        
        for prescription in prescriptions:
            if prescription.medication_id == normalized_medication_id and prescription.status == "active":
                active_prescription = prescription
                break
        
        if active_prescription:
            logger.info(f"Found active prescription for user: {normalized_user_id}, medication: {normalized_medication_id}")
            prescription_info = PrescriptionInfo(
                prescription_id=active_prescription.prescription_id,
                medication_id=active_prescription.medication_id,
                medication_name_he=medication.name_he,
                medication_name_en=medication.name_en,
                active_ingredients=medication.active_ingredients,
                dosage_forms=medication.dosage_forms,
                dosage_instructions=medication.dosage_instructions,
                usage_instructions=medication.usage_instructions,
                description=medication.description,
                prescribed_by=active_prescription.prescribed_by,
                prescription_date=active_prescription.prescription_date,
                expiry_date=active_prescription.expiry_date,
                quantity=active_prescription.quantity,
                refills_remaining=active_prescription.refills_remaining,
                status=active_prescription.status
            )
            
            result = PrescriptionCheckResult(
                has_active_prescription=True,
                prescription_details=prescription_info
            )
        else:
            logger.info(f"No active prescription found for user: {normalized_user_id}, medication: {normalized_medication_id}")
            result = PrescriptionCheckResult(
                has_active_prescription=False,
                prescription_details=None
            )
        
        logger.debug(f"Successfully checked prescription for user: {normalized_user_id}, medication: {normalized_medication_id}")
        return result.model_dump()
        
    except ValueError as e:
        logger.error(f"Invalid input for check_user_prescription_for_medication: {str(e)}", exc_info=True)
        return {
            "error": f"Invalid input: {str(e)}",
            "success": False
        }
    except Exception as e:
        logger.error(f"Error checking prescription for user '{user_id}', medication '{medication_id}': {str(e)}", exc_info=True)
        return {
            "error": f"An error occurred while checking prescription: {str(e)}",
            "success": False
        }


class AuthenticatedUserInfoInput(BaseModel):
    """
    Input schema for authenticated user info tool.
    
    Purpose (Why):
    Defines the structure and validation rules for authenticated user info retrieval.
    This tool is the ONLY way to retrieve personal user information from the database.
    Requires username and password for authentication.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for automatic validation. All fields include
    Field descriptions which are critical for LLM understanding.
    
    Attributes:
        username: The username (name or email) used for authentication (required)
        password: The password for authentication (required)
    """
    username: str = Field(description="The username (name or email) used for authentication. Must match the authenticated user's credentials.")
    password: str = Field(description="The password for authentication. Must match the authenticated user's password.")


class AuthenticatedUserInfoResult(BaseModel):
    """
    Output schema for authenticated user info result.
    
    Purpose (Why):
    Defines the structure of authenticated user information returned to the agent.
    Includes all user information including prescriptions.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for validation and serialization. Includes
    user identification, contact information, and list of prescription details.
    
    Attributes:
        user_id: Unique identifier for the user
        name: Full name of the user
        email: Email address of the user
        prescriptions: List of prescription information (empty list if user has no prescriptions)
    """
    user_id: str = Field(description="Unique identifier for the user")
    name: str = Field(description="Full name of the user")
    email: str = Field(description="Email address of the user")
    prescriptions: List[PrescriptionInfo] = Field(description="List of prescription information for this user (empty list if user has no prescriptions)")


def get_authenticated_user_info(username: str, password: str, authenticated_username: Optional[str] = None, authenticated_password_hash: Optional[str] = None) -> Dict[str, Any]:
    """
    Get authenticated user information by username and password.
    
    Purpose (Why):
    This is the ONLY tool that retrieves personal user information from the database.
    It requires username and password authentication to ensure only the authenticated
    user can access their own information. This prevents unauthorized access to other
    users' data. Returns complete user information including prescriptions.
    
    Implementation (What):
    Validates username and password against stored authentication credentials.
    If authenticated_username and authenticated_password_hash are provided from context,
    verifies that the provided username and password match. Then authenticates the user
    and retrieves their complete information including prescriptions from the database.
    Uses module-level caching for DatabaseManager to improve performance.
    
    Args:
        username: The username (name or email) to authenticate
        password: The password to authenticate
        authenticated_username: The authenticated username from session (optional, for verification)
        authenticated_password_hash: The authenticated password hash from session (optional, for verification)
    
    Returns:
        Dictionary containing:
        - AuthenticatedUserInfoResult: If authentication succeeds (includes user_id, name, email, prescriptions)
        - Error dictionary: If authentication fails (includes error message)
    
    Example:
        >>> result = get_authenticated_user_info("John Doe", "password123", authenticated_username="John Doe", authenticated_password_hash="abc123...")
        >>> if "error" in result:
        ...     print(f"Error: {result['error']}")
        ... else:
        ...     print(f"User: {result['name']}, Prescriptions: {len(result['prescriptions'])}")
    """
    try:
        import hashlib
        
        # Validate inputs
        if not username or not username.strip():
            logger.warning("Empty username provided to get_authenticated_user_info")
            return {
                "error": "Username is required for authentication.",
                "success": False
            }
        
        if not password or not password.strip():
            logger.warning("Empty password provided to get_authenticated_user_info")
            return {
                "error": "Password is required for authentication.",
                "success": False
            }
        
        normalized_username = username.strip()
        normalized_password = password.strip()
        
        # Hash the provided password for comparison
        def hash_password(pwd: str) -> str:
            """Hash password using SHA-256 (same as in main.py)."""
            return hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        
        password_hash = hash_password(normalized_password)
        
        # If authenticated credentials are provided from context, verify they match
        if authenticated_username and authenticated_password_hash:
            # Verify username matches
            if normalized_username.lower() != authenticated_username.lower():
                logger.warning(
                    f"Username mismatch: provided '{normalized_username}' != authenticated '{authenticated_username}'"
                )
                return {
                    "error": "Authentication failed. Username does not match authenticated user.",
                    "success": False
                }
            
            # Verify password hash matches
            if password_hash != authenticated_password_hash:
                logger.warning("Password hash mismatch in get_authenticated_user_info")
                return {
                    "error": "Authentication failed. Password does not match authenticated user.",
                    "success": False
                }
        
        # Find user by username/email
        db_manager = _get_db_manager()
        users = db_manager.search_users_by_name_or_email(normalized_username)
        
        if not users:
            logger.warning(f"User not found for username: {normalized_username}")
            return {
                "error": f"User '{normalized_username}' not found. Please check your username and try again.",
                "success": False
            }
        
        # Get the first matching user (in a real system, you might want to handle multiple matches)
        user = users[0]
        
        # Verify password against user's stored password hash
        if user.password_hash:
            if password_hash != user.password_hash:
                logger.warning(f"Password verification failed for user: {user.user_id}")
                return {
                    "error": "Authentication failed. Incorrect password.",
                    "success": False
                }
        else:
            # If no password hash exists, allow access (backward compatibility)
            # In production, this should require password setup
            logger.info(f"User {user.user_id} has no password hash, allowing access (backward compatibility)")
        
        # Get prescriptions for the user
        prescriptions = db_manager.get_prescriptions_by_user(user.user_id)
        logger.info(f"Found {len(prescriptions)} prescriptions for authenticated user: {user.user_id}")
        
        # Enrich prescriptions with complete medication information to avoid redundant tool calls
        # This includes all medication details (active ingredients, dosage, etc.) so the AI
        # doesn't need to call get_medication_by_name separately, reducing latency
        prescription_info_list = []
        for prescription in prescriptions:
            medication = db_manager.get_medication_by_id(prescription.medication_id)
            if medication:
                prescription_info = PrescriptionInfo(
                    prescription_id=prescription.prescription_id,
                    medication_id=prescription.medication_id,
                    medication_name_he=medication.name_he,
                    medication_name_en=medication.name_en,
                    active_ingredients=medication.active_ingredients,
                    dosage_forms=medication.dosage_forms,
                    dosage_instructions=medication.dosage_instructions,
                    usage_instructions=medication.usage_instructions,
                    description=medication.description,
                    prescribed_by=prescription.prescribed_by,
                    prescription_date=prescription.prescription_date,
                    expiry_date=prescription.expiry_date,
                    quantity=prescription.quantity,
                    refills_remaining=prescription.refills_remaining,
                    status=prescription.status
                )
                prescription_info_list.append(prescription_info)
            else:
                logger.warning(f"Medication {prescription.medication_id} not found for prescription {prescription.prescription_id}")
                # Still include prescription even if medication not found
                prescription_info = PrescriptionInfo(
                    prescription_id=prescription.prescription_id,
                    medication_id=prescription.medication_id,
                    medication_name_he="Unknown",
                    medication_name_en="Unknown",
                    active_ingredients=[],
                    dosage_forms=[],
                    dosage_instructions=None,
                    usage_instructions=None,
                    description=None,
                    prescribed_by=prescription.prescribed_by,
                    prescription_date=prescription.prescription_date,
                    expiry_date=prescription.expiry_date,
                    quantity=prescription.quantity,
                    refills_remaining=prescription.refills_remaining,
                    status=prescription.status
                )
                prescription_info_list.append(prescription_info)
        
        result = AuthenticatedUserInfoResult(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            prescriptions=prescription_info_list
        )
        
        logger.info(f"Successfully retrieved authenticated user info: {user.user_id} ({user.name})")
        return result.model_dump()
        
    except ValueError as e:
        logger.error(f"Invalid input for get_authenticated_user_info: {str(e)}", exc_info=True)
        return {
            "error": f"Invalid input: {str(e)}",
            "success": False
        }
    except Exception as e:
        logger.error(f"Error getting authenticated user info: {str(e)}", exc_info=True)
        return {
            "error": f"An error occurred while retrieving user information: {str(e)}",
            "success": False
        }

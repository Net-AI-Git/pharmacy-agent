"""
Tool registry for OpenAI function calling.

Purpose (Why):
This module provides the interface between the Python tool functions and OpenAI API.
It converts Python functions into JSON Schema format that OpenAI API understands,
and provides execution routing for tool calls.

Implementation (What):
Defines tool schemas in OpenAI format (JSON Schema) and maps tool names to their
corresponding Python functions. The get_tools_for_openai() function returns the
schemas that are sent to OpenAI API, and execute_tool() routes tool calls to the
correct Python function.
"""

import inspect
import logging
from typing import Dict, Any, List, Callable, Optional
from app.tools.medication_tools import get_medication_by_name
from app.tools.inventory_tools import check_stock_availability
from app.tools.prescription_tools import check_prescription_requirement
from app.tools.user_tools import get_user_by_name_or_email, get_user_prescriptions, check_user_prescription_for_medication, get_authenticated_user_info
from app.security.rate_limiter import RateLimiter
from app.security.audit_logger import AuditLogger
from app.security.correlation import generate_correlation_id

# Configure module-level logger
logger = logging.getLogger(__name__)

# Module-level rate limiter instance
_rate_limiter = RateLimiter()

# Module-level audit logger instance
_audit_logger = AuditLogger()

# Registry mapping tool names to their Python functions
_TOOL_FUNCTIONS: Dict[str, Callable] = {
    "get_medication_by_name": get_medication_by_name,
    "check_stock_availability": check_stock_availability,
    "check_prescription_requirement": check_prescription_requirement,
    "get_user_by_name_or_email": get_user_by_name_or_email,
    "get_user_prescriptions": get_user_prescriptions,
    "check_user_prescription_for_medication": check_user_prescription_for_medication,
    "get_authenticated_user_info": get_authenticated_user_info,
}


def get_tools_for_openai() -> List[Dict[str, Any]]:
    """
    Get tool definitions in OpenAI API format.
    
    Purpose (Why):
    Returns tool definitions in JSON Schema format that OpenAI API understands.
    This is what the LLM "sees" - it receives these schemas to understand what
    tools are available and when to use them.
    
    Implementation (What):
    Returns a list of tool definitions, each containing:
    - type: "function" (OpenAI function calling type)
    - function.name: The tool name
    - function.description: What the tool does (from docstring)
    - function.parameters: JSON Schema describing the parameters
    
    Returns:
        List of tool definitions in OpenAI format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_medication_by_name",
                "description": (
                    "Search for a medication by name with fuzzy matching support. "
                    "This tool enables the AI agent to find medications when users provide "
                    "medication names in natural language. It supports both Hebrew and English "
                    "names, handles partial matches (fuzzy matching), and provides helpful "
                    "suggestions when no exact match is found. Returns basic medication "
                    "information including medication_id, names, active ingredients, dosage forms, "
                    "dosage instructions, usage instructions, and description. "
                    "Does NOT return stock availability or prescription requirements - use "
                    "check_stock_availability and check_prescription_requirement for those."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": (
                                "The medication name to search for. "
                                "Supports partial matches and fuzzy matching. "
                                "Case-insensitive. Examples: 'Acamol', 'paracet', 'אקמול'"
                            )
                        },
                        "language": {
                            "type": "string",
                            "enum": ["he", "en"],
                            "description": (
                                "Optional language filter: 'he' for Hebrew, 'en' for English. "
                                "If not provided, searches both languages. "
                                "Use 'he' when the user asks in Hebrew, 'en' when in English."
                            )
                        }
                    },
                    "required": ["name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_stock_availability",
                "description": (
                    "Check stock availability for a medication by ID. "
                    "This tool enables the AI agent to check medication stock availability when users "
                    "ask about inventory. It verifies if medications are in stock, how many units are "
                    "available, and whether there is sufficient quantity for a specific request. "
                    "Returns complete stock information including availability status, quantity in stock, "
                    "last restocked date, and whether sufficient quantity is available for the requested amount."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "medication_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the medication to check stock for. "
                                "This is typically obtained from a previous medication search. "
                                "Example: 'med_001'"
                            )
                        },
                        "quantity": {
                            "type": "integer",
                            "description": (
                                "Optional quantity to check availability for. "
                                "If provided, the tool will verify if there is enough stock to fulfill this quantity. "
                                "If not provided, only checks general availability. "
                                "Must be a positive integer. Example: 10"
                            )
                        }
                    },
                    "required": ["medication_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_prescription_requirement",
                "description": (
                    "Check prescription requirement for a medication by ID. "
                    "This tool enables the AI agent to verify whether medications require prescriptions "
                    "when users ask about prescription requirements. It provides essential information "
                    "for compliance with pharmacy regulations and helps customers understand what they "
                    "need before attempting to purchase medications. Returns prescription requirement "
                    "information including whether a prescription is required and the prescription type "
                    "(not_required or prescription_required). Uses safe fallback values (requires_prescription=True) "
                    "when medication is not found or errors occur to ensure safety."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "medication_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the medication to check prescription requirements for. "
                                "This is typically obtained from a previous medication search. "
                                "Example: 'med_001'"
                            )
                        }
                    },
                    "required": ["medication_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_by_name_or_email",
                "description": (
                    "Search for a user by name or email address with case-insensitive partial matching support. "
                    "This tool enables the AI agent to find users when they provide their name or email "
                    "address instead of user_id. It supports natural language queries where users identify "
                    "themselves by name or email, which is more user-friendly than requiring technical IDs. "
                    "Returns user information including user_id (required for other user tools), name, email, "
                    "and list of prescription IDs. If multiple users match, returns the first match. "
                    "If no user is found, returns error with suggestions of similar names or emails."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name_or_email": {
                            "type": "string",
                            "description": (
                                "The user name or email address to search for. "
                                "Supports partial matches and case-insensitive search. "
                                "Examples: 'John Doe', 'john.doe@example.com', 'john'"
                            )
                        }
                    },
                    "required": ["name_or_email"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_prescriptions",
                "description": (
                    "Get all prescriptions for a specific user by user_id. "
                    "This tool enables the AI agent to retrieve all prescriptions associated with a user. "
                    "This allows users to view their prescription history and verify prescription details. "
                    "Returns complete prescription information including medication names (Hebrew and English), "
                    "prescription dates, expiry dates, quantities, refills remaining, and status. "
                    "Returns empty list if user has no prescriptions (this is not an error). "
                    "The user_id is typically obtained from get_user_by_name_or_email."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the user to get prescriptions for. "
                                "This is typically obtained from get_user_by_name_or_email. "
                                "Example: 'user_001'"
                            )
                        }
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_user_prescription_for_medication",
                "description": (
                    "Check if a user has an active prescription for a specific medication. "
                    "This tool enables the AI agent to verify whether a user has an active prescription "
                    "for a specific medication. This is essential for prescription validation before "
                    "medication purchases and helps users understand their prescription status. "
                    "Only returns active prescriptions (status='active'). Returns has_active_prescription=false "
                    "if no active prescription found (this is not an error). "
                    "The user_id is typically obtained from get_user_by_name_or_email, and medication_id "
                    "is typically obtained from get_medication_by_name."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the user to check prescription for. "
                                "This is typically obtained from get_user_by_name_or_email. "
                                "Example: 'user_001'"
                            )
                        },
                        "medication_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the medication to check prescription for. "
                                "This is typically obtained from get_medication_by_name. "
                                "Example: 'med_001'"
                            )
                        }
                    },
                    "required": ["user_id", "medication_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_authenticated_user_info",
                "description": (
                    "Get authenticated user information by username and password. "
                    "This is the ONLY tool that retrieves personal user information from the database. "
                    "It requires username and password authentication to ensure only the authenticated "
                    "user can access their own information. This prevents unauthorized access to other "
                    "users' data. Returns complete user information including user_id, name, email, "
                    "and all prescriptions with full details. Use this tool when the user asks about "
                    "'my prescriptions', 'my medical record', or 'my information'. "
                    "IMPORTANT: This tool requires the authenticated user's username and password from the session. "
                    "Never use this tool to access information about other users."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": (
                                "The username (name or email) used for authentication. "
                                "Must match the authenticated user's credentials from the session. "
                                "Example: 'John Doe' or 'john.doe@example.com'"
                            )
                        },
                        "password": {
                            "type": "string",
                            "description": (
                                "The password for authentication. "
                                "Must match the authenticated user's password from the session."
                            )
                        }
                    },
                    "required": ["username", "password"]
                }
            }
        }
    ]


def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    agent_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute a tool by name with given arguments.
    
    Purpose (Why):
    Routes tool calls from OpenAI API to the correct Python function. When OpenAI
    decides to call a tool, it sends the tool name and arguments, and this function
    executes the corresponding Python function. Includes rate limiting to prevent
    resource exhaustion and infinite loops. Provides comprehensive auditing for
    complete traceability of tool executions.
    
    Implementation (What):
    First checks rate limits to ensure the tool call is allowed. If rate limit is
    exceeded, returns an error response instead of executing the tool. If allowed,
    generates or uses provided correlation ID for audit logging, logs tool call start,
    looks up the tool function in the registry, calls it with the provided arguments,
    records the call for rate limit tracking, logs tool call completion, and returns
    the result. Handles errors gracefully and provides clear error messages for rate
    limit violations. All operations are logged for audit trail.
    
    Args:
        tool_name: Name of the tool to execute (must match a key in _TOOL_FUNCTIONS)
        arguments: Dictionary of arguments to pass to the tool function
        agent_id: Optional identifier for the agent/session making the call.
            Used for rate limit tracking and audit logging. Defaults to "default" for
            stateless agents. Can be session ID or user ID in future implementations.
        correlation_id: Optional correlation ID for request tracking. If not provided,
            generates a new one. Used to link all operations in a single request/conversation.
        context: Optional dictionary with additional context information for audit logging.
            Can include user message, conversation history, or other relevant context.
    
    Returns:
        Dictionary containing the tool execution result. If rate limit is exceeded,
        returns error dictionary with "error" and "success" fields.
    
    Raises:
        ValueError: If tool_name is not found in registry
        Exception: Any exception raised by the tool function (except rate limit errors)
    
    Example:
        >>> result = execute_tool("get_medication_by_name", {"name": "Acamol"})
        >>> if not result.get("success", True):
        ...     print(f"Error: {result.get('error')}")
    """
    if tool_name not in _TOOL_FUNCTIONS:
        error_msg = f"Tool '{tool_name}' not found in registry. Available tools: {list(_TOOL_FUNCTIONS.keys())}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Use default agent_id if not provided (for stateless agents)
    effective_agent_id = agent_id if agent_id is not None else "default"
    
    # Generate or use provided correlation ID
    effective_correlation_id = correlation_id if correlation_id is not None else generate_correlation_id()
    
    # Check rate limit before executing
    allowed, error_message = _rate_limiter.check_rate_limit(tool_name, effective_agent_id, effective_correlation_id)
    if not allowed:
        error_result = {
            "error": error_message,
            "success": False,
            "tool_name": tool_name,
            "rate_limit_exceeded": True
        }
        logger.warning(
            f"Rate limit exceeded for tool '{tool_name}' by agent '{effective_agent_id}': {error_message}"
        )
        
        # Log rate limit error to audit log
        _audit_logger.log_tool_call(
            correlation_id=effective_correlation_id,
            tool_name=tool_name,
            agent_id=effective_agent_id,
            arguments=arguments,
            result=error_result,
            context=context,
            status="error"
        )
        
        return error_result
    
    tool_function = _TOOL_FUNCTIONS[tool_name]
    logger.info(f"Executing tool: {tool_name} with arguments: {arguments} (agent_id: {effective_agent_id})")
    
    # Filter arguments to only include parameters that the function accepts
    # This prevents TypeError when extra arguments are provided
    try:
        sig = inspect.signature(tool_function)
        valid_params = set(sig.parameters.keys())
        filtered_arguments = {k: v for k, v in arguments.items() if k in valid_params}
        
        # For user tools, add authenticated_user_id from context if available
        user_tools = ["get_user_by_name_or_email", "get_user_prescriptions", "check_user_prescription_for_medication"]
        if tool_name in user_tools and context and "authenticated_user_id" in context:
            authenticated_user_id = context.get("authenticated_user_id")
            if "authenticated_user_id" in valid_params:
                filtered_arguments["authenticated_user_id"] = authenticated_user_id
                logger.debug(f"Added authenticated_user_id to {tool_name}: {authenticated_user_id}")
        
        # For get_authenticated_user_info, add authenticated_username, authenticated_password, and authenticated_password_hash from context if available
        if tool_name == "get_authenticated_user_info" and context:
            if "authenticated_username" in context and "authenticated_username" in valid_params:
                filtered_arguments["authenticated_username"] = context.get("authenticated_username")
                logger.debug(f"Added authenticated_username to {tool_name}")
            # If password is not provided by LLM, use it from context
            if "password" not in filtered_arguments and "authenticated_password" in context and "password" in valid_params:
                filtered_arguments["password"] = context.get("authenticated_password")
                logger.debug(f"Added authenticated_password from context to {tool_name}")
            if "authenticated_password_hash" in context and "authenticated_password_hash" in valid_params:
                filtered_arguments["authenticated_password_hash"] = context.get("authenticated_password_hash")
                logger.debug(f"Added authenticated_password_hash to {tool_name}")
        
        # Log if any arguments were filtered out
        if len(filtered_arguments) < len(arguments):
            filtered_out = set(arguments.keys()) - set(filtered_arguments.keys())
            logger.warning(f"Filtered out unexpected arguments for {tool_name}: {filtered_out}")
        
        # Execute the tool
        result = tool_function(**filtered_arguments)
        
        # Record the call for rate limit tracking (after successful execution)
        _rate_limiter.record_call(tool_name, effective_agent_id, effective_correlation_id)
        
        # Determine status based on result content, not just execution success
        # Check if result contains an error field or success=False
        if isinstance(result, dict):
            has_error = "error" in result or result.get("success") is False
            status = "error" if has_error else "success"
        else:
            # If result is not a dict, assume success (tool executed without exception)
            status = "success"
        
        # Log tool execution to audit log with appropriate status
        _audit_logger.log_tool_call(
            correlation_id=effective_correlation_id,
            tool_name=tool_name,
            agent_id=effective_agent_id,
            arguments=filtered_arguments,
            result=result,
            context=context,
            status=status
        )
        
        if status == "success":
            logger.debug(f"Tool {tool_name} executed successfully")
        else:
            logger.debug(f"Tool {tool_name} executed but returned error result")
        
        return result
    except Exception as e:
        error_result = {
            "error": str(e),
            "success": False,
            "tool_name": tool_name
        }
        
        logger.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
        
        # Log error to audit log
        _audit_logger.log_tool_call(
            correlation_id=effective_correlation_id,
            tool_name=tool_name,
            agent_id=effective_agent_id,
            arguments=filtered_arguments if 'filtered_arguments' in locals() else arguments,
            result=error_result,
            context=context,
            status="error"
        )
        
        raise


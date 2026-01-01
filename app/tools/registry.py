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
from typing import Dict, Any, List, Callable
from app.tools.medication_tools import get_medication_by_name
from app.tools.inventory_tools import check_stock_availability
from app.tools.prescription_tools import check_prescription_requirement

# Configure module-level logger
logger = logging.getLogger(__name__)

# Registry mapping tool names to their Python functions
_TOOL_FUNCTIONS: Dict[str, Callable] = {
    "get_medication_by_name": get_medication_by_name,
    "check_stock_availability": check_stock_availability,
    "check_prescription_requirement": check_prescription_requirement,
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
                    "suggestions when no exact match is found. Returns complete medication "
                    "information including active ingredients, dosage instructions, stock availability, "
                    "and prescription requirements."
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
        }
    ]


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool by name with given arguments.
    
    Purpose (Why):
    Routes tool calls from OpenAI API to the correct Python function. When OpenAI
    decides to call a tool, it sends the tool name and arguments, and this function
    executes the corresponding Python function.
    
    Implementation (What):
    Looks up the tool function in the registry, calls it with the provided arguments,
    and returns the result. Handles errors gracefully.
    
    Args:
        tool_name: Name of the tool to execute (must match a key in _TOOL_FUNCTIONS)
        arguments: Dictionary of arguments to pass to the tool function
    
    Returns:
        Dictionary containing the tool execution result
    
    Raises:
        ValueError: If tool_name is not found in registry
        Exception: Any exception raised by the tool function
    """
    if tool_name not in _TOOL_FUNCTIONS:
        error_msg = f"Tool '{tool_name}' not found in registry. Available tools: {list(_TOOL_FUNCTIONS.keys())}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    tool_function = _TOOL_FUNCTIONS[tool_name]
    logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")
    
    # Filter arguments to only include parameters that the function accepts
    # This prevents TypeError when extra arguments are provided
    try:
        sig = inspect.signature(tool_function)
        valid_params = set(sig.parameters.keys())
        filtered_arguments = {k: v for k, v in arguments.items() if k in valid_params}
        
        # Log if any arguments were filtered out
        if len(filtered_arguments) < len(arguments):
            filtered_out = set(arguments.keys()) - set(filtered_arguments.keys())
            logger.warning(f"Filtered out unexpected arguments for {tool_name}: {filtered_out}")
        
        result = tool_function(**filtered_arguments)
        logger.debug(f"Tool {tool_name} executed successfully")
        return result
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
        raise


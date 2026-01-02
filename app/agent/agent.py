"""
Pharmacy Agent for OpenAI API integration.

Purpose (Why):
This module implements the core PharmacyAgent class that integrates with OpenAI API
to provide conversational AI capabilities for the pharmacy assistant. The agent handles
function calling, message processing, and maintains stateless behavior as required
by the pharmacy assistant specifications. It serves as the bridge between user queries
and the pharmacy tools (medication search, stock checking, prescription verification).

Implementation (What):
Implements a stateless agent that processes user messages through OpenAI API with
function calling support. The agent handles tool calls in a loop until the conversation
is complete, executing tools and feeding results back to the model. Uses OpenAI API
directly (not Langchain) as per project requirements. Maintains conversation history
only within a single session, ensuring stateless behavior between different sessions.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from app.prompts.system_prompt import get_system_prompt
from app.tools.registry import get_tools_for_openai, execute_tool

# Load environment variables
load_dotenv()

# Configure module-level logger
logger = logging.getLogger(__name__)


class PharmacyAgent:
    """
    Pharmacy AI Agent for processing user queries with OpenAI API.
    
    Purpose (Why):
    This class provides the main interface for the pharmacy assistant AI agent.
    It processes user messages, handles function calling for pharmacy tools,
    and maintains stateless behavior. The agent is designed to provide accurate
    medication information while strictly adhering to safety policies (no medical
    advice, no diagnosis, no purchase encouragement).
    
    Implementation (What):
    Uses OpenAI API directly with function calling capabilities. Processes messages
    by sending them to OpenAI API along with conversation history and available tools.
    When OpenAI requests tool calls, executes them and feeds results back to the model
    in a loop until the conversation is complete. Maintains stateless design - each
    conversation session is independent with no state preservation between sessions.
    
    Attributes:
        client: OpenAI API client instance
        system_prompt: System prompt defining agent behavior and policies
        tools: List of tool definitions in OpenAI format
        model: OpenAI model name to use (default: "gpt-5")
    """
    
    def __init__(self, model: str = "gpt-5"):
        """
        Initialize the PharmacyAgent.
        
        Purpose (Why):
        Sets up the OpenAI client, loads system prompt, and prepares tools for
        function calling. Validates that required environment variables are present
        and initializes all components needed for agent operation.
        
        Implementation (What):
        Loads OpenAI API key from environment, creates OpenAI client, retrieves
        system prompt and tools. The agent is stateless - no state is maintained
        between different agent instances or conversation sessions.
        
        Args:
            model: OpenAI model name to use (default: "gpt-5")
                This can be configured via environment variable or parameter.
        
        Raises:
            ValueError: If OPENAI_API_KEY is not found in environment
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            error_msg = "OPENAI_API_KEY not found in environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = get_system_prompt()
        self.tools = get_tools_for_openai()
        self.model = model
        
        logger.info(f"PharmacyAgent initialized with model: {model}")
        logger.debug(f"Loaded {len(self.tools)} tools for function calling")
    
    def _build_messages(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Build message list for OpenAI API from user message and history.
        
        Purpose (Why):
        Constructs the message format required by OpenAI API, including system
        prompt, conversation history, and the current user message. This ensures
        proper context is maintained within a single conversation session.
        
        Implementation (What):
        Creates a list of message dictionaries in OpenAI format. Starts with
        system message, adds conversation history if provided, and appends the
        current user message. History is only maintained within a single session
        to maintain stateless behavior between sessions.
        
        Args:
            user_message: The current user message to process
            conversation_history: Optional list of previous messages in the
                current conversation session. Format: [{"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}, ...]
        
        Returns:
            List of message dictionaries in OpenAI API format
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _process_tool_calls(
        self,
        tool_calls: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Process tool calls from OpenAI API and execute them.
        
        Purpose (Why):
        Executes tool calls requested by OpenAI API and formats the results
        for feeding back to the model. This enables the agent to use pharmacy
        tools (medication search, stock checking, prescription verification)
        to provide accurate information to users.
        
        Implementation (What):
        Iterates through tool calls, executes each tool using the registry,
        and creates tool message responses. Handles errors gracefully and
        logs all tool executions for debugging and auditing. Works with both
        OpenAI API object structure and dictionary structure for flexibility.
        
        Args:
            tool_calls: List of tool call objects from OpenAI API response.
                Each object has: id, type, function (with name and arguments)
        
        Returns:
            List of tool message dictionaries to send back to OpenAI API
        """
        tool_messages = []
        
        for tool_call in tool_calls:
            # Handle both object and dict structures
            if hasattr(tool_call, 'id'):
                # OpenAI API object structure
                tool_id = tool_call.id
                function = tool_call.function
                tool_name = function.name if hasattr(function, 'name') else None
                arguments_str = function.arguments if hasattr(function, 'arguments') else "{}"
            else:
                # Dictionary structure (for testing/compatibility)
                tool_id = tool_call.get("id")
                function = tool_call.get("function", {})
                tool_name = function.get("name") if isinstance(function, dict) else getattr(function, "name", None)
                arguments_str = function.get("arguments", "{}") if isinstance(function, dict) else getattr(function, "arguments", "{}")
            
            if not tool_name:
                logger.warning(f"Tool call missing name: {tool_call}")
                continue
            
            logger.info(f"Processing tool call: {tool_name} with ID: {tool_id}")
            logger.debug(f"Tool arguments: {arguments_str}")
            
            try:
                # Parse arguments (OpenAI sends as JSON string)
                arguments = json.loads(arguments_str)
                
                # Execute the tool
                result = execute_tool(tool_name, arguments)
                
                # Format result as JSON string for OpenAI
                result_str = json.dumps(result, ensure_ascii=False)
                
                # Create tool message response
                tool_message = {
                    "role": "tool",
                    "content": result_str,
                    "tool_call_id": tool_id
                }
                tool_messages.append(tool_message)
                
                logger.debug(f"Tool {tool_name} executed successfully")
                
            except Exception as e:
                error_msg = f"Error executing tool {tool_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                
                # Send error back to model
                error_result = {"error": error_msg, "success": False}
                tool_message = {
                    "role": "tool",
                    "content": json.dumps(error_result, ensure_ascii=False),
                    "tool_call_id": tool_id
                }
                tool_messages.append(tool_message)
        
        return tool_messages
    
    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Process a user message and return agent response.
        
        Purpose (Why):
        Main entry point for processing user queries. Handles the complete
        conversation flow including function calling in a loop until the
        conversation is complete. This method orchestrates the interaction
        between OpenAI API and pharmacy tools to provide accurate responses.
        
        Implementation (What):
        Sends user message to OpenAI API with conversation history and tools.
        If OpenAI requests tool calls, executes them and feeds results back
        to the model. Repeats this process until OpenAI returns a final
        response without tool calls. Maintains stateless behavior - history
        is only used within the current session.
        
        Args:
            user_message: The user's message to process
            conversation_history: Optional list of previous messages in the
                current conversation session. Format: [{"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}, ...]
                Note: This is session-level history only. The agent is stateless
                between different sessions.
        
        Returns:
            String containing the agent's response to the user
        
        Raises:
            Exception: If OpenAI API call fails or other errors occur
        """
        if not user_message or not user_message.strip():
            logger.warning("Empty user message received")
            return "I'm here to help! Please ask me about medications, stock availability, or prescription requirements."
        
        messages = self._build_messages(user_message, conversation_history)
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        logger.info("Processing user message")
        logger.debug(f"Message: {user_message[:100]}...")
        
        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"OpenAI API call iteration: {iteration}")
            
            try:
                # Call OpenAI API with tools
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto"  # Let model decide when to use tools
                )
                
                assistant_message = response.choices[0].message
                
                # Build assistant message dict (handle None content and tool_calls)
                assistant_msg_dict = {
                    "role": "assistant",
                    "content": assistant_message.content if assistant_message.content else None
                }
                
                # Check if model wants to call tools
                if assistant_message.tool_calls:
                    # Add tool_calls to assistant message dict
                    tool_calls_list = []
                    for tc in assistant_message.tool_calls:
                        tool_call_dict = {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        tool_calls_list.append(tool_call_dict)
                    assistant_msg_dict["tool_calls"] = tool_calls_list
                    
                    # Add assistant message to conversation history (needed for tool calling loop)
                    messages.append(assistant_msg_dict)
                    
                    logger.info(f"Model requested {len(assistant_message.tool_calls)} tool calls")
                    tool_messages = self._process_tool_calls(assistant_message.tool_calls)
                    messages.extend(tool_messages)
                    # Continue loop to get model's response to tool results
                    continue
                
                # No tool calls - we have final response
                # Don't add assistant message to messages since we're returning (stateless behavior)
                final_response = assistant_message.content or ""
                logger.info("Received final response from model")
                return final_response
                
            except Exception as e:
                error_msg = f"Error in OpenAI API call: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise Exception(f"Failed to process message: {error_msg}") from e
        
        # If we exit loop, we hit max iterations
        logger.warning(f"Reached max iterations ({max_iterations}) in tool calling loop")
        return "I apologize, but I encountered an issue processing your request. Please try again or rephrase your question."


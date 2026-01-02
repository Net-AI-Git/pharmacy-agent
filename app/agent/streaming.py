"""
Streaming Agent for OpenAI API integration with real-time text streaming.

Purpose (Why):
This module implements the StreamingAgent class that provides real-time text streaming
capabilities for the pharmacy assistant. Streaming enables users to see responses as they
are generated, improving user experience and perceived responsiveness. The agent handles
function calling during streaming, pausing stream execution when tools are needed and
resuming after tool results are processed.

Implementation (What):
Implements a stateless streaming agent that processes user messages through OpenAI API
with streaming support. The agent yields response chunks in real-time while handling
tool calls seamlessly. When OpenAI requests tool calls during streaming, the agent
pauses streaming, executes tools, and continues streaming with tool results. Uses OpenAI
API directly (not Langchain) as per project requirements. Maintains conversation history
only within a single session, ensuring stateless behavior between different sessions.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Generator
from openai import OpenAI
from dotenv import load_dotenv
from app.prompts.system_prompt import get_system_prompt
from app.tools.registry import get_tools_for_openai, execute_tool

# Load environment variables
load_dotenv()

# Configure module-level logger
logger = logging.getLogger(__name__)


class StreamingAgent:
    """
    Streaming Pharmacy AI Agent for processing user queries with real-time streaming.
    
    Purpose (Why):
    This class provides the main interface for the pharmacy assistant AI agent with
    streaming capabilities. It processes user messages, streams responses in real-time,
    handles function calling for pharmacy tools during streaming, and maintains stateless
    behavior. The agent is designed to provide accurate medication information while
    strictly adhering to safety policies (no medical advice, no diagnosis, no purchase
    encouragement). Streaming improves user experience by showing responses as they are
    generated rather than waiting for complete responses.
    
    Implementation (What):
    Uses OpenAI API directly with streaming and function calling capabilities. Processes
    messages by sending them to OpenAI API with stream=True, yielding response chunks
    as they arrive. When OpenAI requests tool calls during streaming, the agent collects
    all tool calls, pauses streaming, executes tools, and continues streaming with
    tool results. Maintains stateless design - each conversation session is independent
    with no state preservation between sessions.
    
    Attributes:
        client: OpenAI API client instance
        system_prompt: System prompt defining agent behavior and policies
        tools: List of tool definitions in OpenAI format
        model: OpenAI model name to use (default: "gpt-5")
    """
    
    def __init__(self, model: str = "gpt-5"):
        """
        Initialize the StreamingAgent.
        
        Purpose (Why):
        Sets up the OpenAI client, loads system prompt, and prepares tools for
        function calling. Validates that required environment variables are present
        and initializes all components needed for streaming agent operation.
        
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
        
        logger.info(f"StreamingAgent initialized with model: {model}")
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
        to provide accurate information to users during streaming.
        
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
    
    def stream_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Generator[str, None, None]:
        """
        Stream agent response in real-time as a generator.
        
        Purpose (Why):
        Provides real-time streaming of agent responses, improving user experience
        by showing text as it is generated rather than waiting for complete responses.
        Handles function calling seamlessly during streaming by pausing stream execution,
        executing tools, and continuing streaming with tool results.
        
        Implementation (What):
        Sends user message to OpenAI API with stream=True, yielding response chunks
        as they arrive. When OpenAI requests tool calls during streaming, collects
        all tool calls from the stream, pauses streaming, executes tools, and continues
        streaming with tool results. Repeats this process until OpenAI returns a final
        response without tool calls. Maintains stateless behavior - history is only
        used within the current session.
        
        Args:
            user_message: The user's message to process
            conversation_history: Optional list of previous messages in the
                current conversation session. Format: [{"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}, ...]
                Note: This is session-level history only. The agent is stateless
                between different sessions.
        
        Yields:
            String chunks containing parts of the agent's response. Each yield is a
            piece of text that should be displayed to the user in real-time.
        
        Raises:
            Exception: If OpenAI API call fails or other errors occur
        
        Example:
            >>> agent = StreamingAgent()
            >>> for chunk in agent.stream_response("Tell me about Acamol"):
            ...     print(chunk, end="", flush=True)
        """
        if not user_message or not user_message.strip():
            logger.warning("Empty user message received")
            yield "I'm here to help! Please ask me about medications, stock availability, or prescription requirements."
            return
        
        messages = self._build_messages(user_message, conversation_history)
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        logger.info("Processing user message with streaming")
        logger.debug(f"Message: {user_message[:100]}...")
        
        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"OpenAI API streaming call iteration: {iteration}")
            
            try:
                # Call OpenAI API with streaming enabled
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",  # Let model decide when to use tools
                    stream=True  # Enable streaming
                )
                
                # Collect response chunks and tool calls
                accumulated_content = ""
                tool_calls_collected = []
                finish_reason = None
                
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    
                    # Check for finish reason
                    if chunk.choices[0].finish_reason:
                        finish_reason = chunk.choices[0].finish_reason
                    
                    # Handle text content
                    if delta.content:
                        accumulated_content += delta.content
                        # Yield text chunk immediately for real-time display
                        yield delta.content
                    
                    # Handle tool calls (collect them as they arrive)
                    if delta.tool_calls:
                        for tool_call_delta in delta.tool_calls:
                            # Initialize tool call structure if needed
                            index = tool_call_delta.index
                            while len(tool_calls_collected) <= index:
                                tool_calls_collected.append({
                                    "id": "",
                                    "type": "function",
                                    "function": {
                                        "name": "",
                                        "arguments": ""
                                    }
                                })
                            
                            # Update tool call with delta information
                            if tool_call_delta.id:
                                tool_calls_collected[index]["id"] = tool_call_delta.id
                            if tool_call_delta.function:
                                if tool_call_delta.function.name:
                                    tool_calls_collected[index]["function"]["name"] = tool_call_delta.function.name
                                if tool_call_delta.function.arguments:
                                    tool_calls_collected[index]["function"]["arguments"] += tool_call_delta.function.arguments
                
                # After stream completes, check if we need to handle tool calls
                if finish_reason == "tool_calls" and tool_calls_collected:
                    # Add accumulated content to assistant message if any
                    if accumulated_content:
                        assistant_msg_dict = {
                            "role": "assistant",
                            "content": accumulated_content
                        }
                    else:
                        assistant_msg_dict = {
                            "role": "assistant",
                            "content": None
                        }
                    
                    # Add tool_calls to assistant message
                    assistant_msg_dict["tool_calls"] = tool_calls_collected
                    messages.append(assistant_msg_dict)
                    
                    logger.info(f"Model requested {len(tool_calls_collected)} tool calls during streaming")
                    
                    # Execute tools
                    tool_messages = self._process_tool_calls(tool_calls_collected)
                    messages.extend(tool_messages)
                    
                    # Continue loop to get model's response to tool results (with streaming)
                    continue
                
                # No tool calls - we have final response
                # If we already yielded content, we're done
                # If no content was yielded but finish_reason is "stop", we're also done
                if finish_reason == "stop" or (not tool_calls_collected and accumulated_content):
                    logger.info("Streaming completed with final response")
                    return
                
                # If we reach here and no content was yielded, something unexpected happened
                if not accumulated_content and not tool_calls_collected:
                    logger.warning("Stream completed with no content and no tool calls")
                    yield "I apologize, but I encountered an issue processing your request. Please try again or rephrase your question."
                    return
                
            except Exception as e:
                error_msg = f"Error in OpenAI API streaming call: {str(e)}"
                logger.error(error_msg, exc_info=True)
                yield f"I apologize, but I encountered an error: {error_msg}. Please try again."
                return
        
        # If we exit loop, we hit max iterations
        logger.warning(f"Reached max iterations ({max_iterations}) in streaming tool calling loop")
        yield "I apologize, but I encountered an issue processing your request. Please try again or rephrase your question."


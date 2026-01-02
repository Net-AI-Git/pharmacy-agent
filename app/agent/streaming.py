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
import concurrent.futures
from typing import List, Dict, Any, Optional, Generator
from openai import OpenAI
from dotenv import load_dotenv
from app.prompts.system_prompt import get_system_prompt
from app.tools.registry import get_tools_for_openai, execute_tool
from app.security.audit_logger import AuditLogger
from app.security.correlation import generate_correlation_id

# Load environment variables
load_dotenv()

# Configure module-level logger
logger = logging.getLogger(__name__)

# Module-level audit logger instance
_audit_logger = AuditLogger()


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
    
    def _process_single_tool_call(
        self,
        tool_call: Any,
        correlation_id: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single tool call and return structured result.
        
        Purpose (Why):
        Extracts tool call information, executes the tool, and formats the result
        for parallel execution. This helper function enables concurrent tool execution
        by isolating the processing logic for each tool call, allowing multiple tools
        to run simultaneously without interfering with each other.
        
        Implementation (What):
        Handles both OpenAI API object structure and dictionary structure for flexibility.
        Parses tool call arguments, executes the tool via execute_tool(), and formats
        the result as JSON string. Catches exceptions and returns error results to
        ensure that one tool's failure doesn't prevent other tools from completing.
        Returns None if tool call is invalid (missing name).
        
        Args:
            tool_call: Tool call object from OpenAI API (can be object or dict)
            correlation_id: Unique identifier for the request/conversation.
                Used for audit logging to link all operations.
            agent_id: Identifier for the agent/session. Used for audit logging.
            context: Optional dictionary with additional context for audit logging.
        
        Returns:
            Dictionary with keys:
                - tool_call_id: The tool call ID for matching results
                - result: JSON string containing tool execution result
                - success: Boolean indicating execution success
            Returns None if tool call is invalid (missing name).
        
        Raises:
            None. All exceptions are caught and returned as error results in the
            returned dictionary. This ensures error isolation during parallel execution.
        """
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
            return None
        
        logger.info(f"Processing tool call: {tool_name} with ID: {tool_id}")
        logger.debug(f"Tool arguments: {arguments_str}")
        
        try:
            # Parse arguments (OpenAI sends as JSON string)
            arguments = json.loads(arguments_str)
            
            # Execute the tool with correlation ID for audit logging
            result = execute_tool(
                tool_name=tool_name,
                arguments=arguments,
                agent_id=agent_id,
                correlation_id=correlation_id,
                context=context
            )
            
            # Format result as JSON string for OpenAI
            result_str = json.dumps(result, ensure_ascii=False)
            
            logger.debug(f"Tool {tool_name} executed successfully")
            
            return {
                "tool_call_id": tool_id,
                "result": result_str,
                "success": True
            }
            
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Format error result as JSON string
            error_result = {"error": error_msg, "success": False}
            result_str = json.dumps(error_result, ensure_ascii=False)
            
            return {
                "tool_call_id": tool_id,
                "result": result_str,
                "success": False
            }
    
    def _process_tool_calls(
        self,
        tool_calls: List[Any],
        correlation_id: str,
        agent_id: str = "default",
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process tool calls from OpenAI API and execute them in parallel.
        
        Purpose (Why):
        Executes tool calls requested by OpenAI API and formats the results
        for feeding back to the model. This enables the agent to use pharmacy
        tools (medication search, stock checking, prescription verification)
        to provide accurate information to users during streaming. All tool
        executions are logged for audit trail using correlation ID. Independent
        tools are executed in parallel to improve performance, reducing total
        execution time when multiple tools are requested simultaneously.
        
        Implementation (What):
        Uses ThreadPoolExecutor to execute independent tool calls in parallel,
        significantly reducing execution time when multiple tools are requested.
        Each tool call is processed by _process_single_tool_call() helper function
        which handles execution, error handling, and result formatting. Results
        are collected and ordered by tool_call_id to preserve the original order
        expected by OpenAI API. All tool executions are logged for audit trail
        with correlation ID. Works with both OpenAI API object structure and
        dictionary structure for flexibility.
        
        Args:
            tool_calls: List of tool call objects from OpenAI API response.
                Each object has: id, type, function (with name and arguments)
            correlation_id: Unique identifier for the request/conversation.
                Used for audit logging to link all operations.
            agent_id: Identifier for the agent/session. Used for audit logging.
            context: Optional dictionary with additional context for audit logging.
        
        Returns:
            List of tool message dictionaries to send back to OpenAI API,
            preserving the original order of tool calls. Each dictionary contains:
            - role: "tool" (string)
            - content: JSON string containing tool execution result
            - tool_call_id: The tool call ID for matching with original request
        
        Raises:
            None. All exceptions from individual tool executions are caught and
            returned as error messages in the tool_messages list. This ensures
            that one tool's failure does not prevent other tools from completing.
        """
        if not tool_calls:
            logger.debug("No tool calls to process")
            return []
        
        logger.info(f"Processing {len(tool_calls)} tool call(s) in parallel")
        
        # Execute tools in parallel using ThreadPoolExecutor
        # This is safe because tools are independent and don't share mutable state
        # RateLimiter and AuditLogger are thread-safe with locks
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tool calls for parallel execution
            future_to_tool = {
                executor.submit(
                    self._process_single_tool_call,
                    tool_call,
                    correlation_id,
                    agent_id,
                    context
                ): tool_call
                for tool_call in tool_calls
            }
            
            # Collect results as they complete
            results = []
            for future in concurrent.futures.as_completed(future_to_tool):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    # Handle unexpected exceptions from executor
                    logger.error(f"Unexpected error in tool execution: {str(e)}", exc_info=True)
                    # Try to get tool_id from the original tool_call for error message
                    tool_call = future_to_tool[future]
                    tool_id = tool_call.id if hasattr(tool_call, 'id') else tool_call.get("id", "unknown")
                    error_result = {
                        "tool_call_id": tool_id,
                        "result": json.dumps({"error": str(e), "success": False}, ensure_ascii=False),
                        "success": False
                    }
                    results.append(error_result)
        
        # Build tool messages preserving original order
        # Map results by tool_call_id for efficient lookup
        tool_id_to_result = {r["tool_call_id"]: r for r in results}
        tool_messages = []
        
        # Iterate through original tool_calls to preserve order
        for tool_call in tool_calls:
            tool_id = tool_call.id if hasattr(tool_call, 'id') else tool_call.get("id")
            if tool_id and tool_id in tool_id_to_result:
                result_data = tool_id_to_result[tool_id]
                tool_message = {
                    "role": "tool",
                    "content": result_data["result"],
                    "tool_call_id": tool_id
                }
                tool_messages.append(tool_message)
            else:
                # Handle case where tool call was invalid or failed to process
                logger.warning(f"Tool call result not found for ID: {tool_id}")
                error_result = {
                    "error": "Tool execution failed or tool call was invalid",
                    "success": False
                }
                tool_message = {
                    "role": "tool",
                    "content": json.dumps(error_result, ensure_ascii=False),
                    "tool_call_id": tool_id or "unknown"
                }
                tool_messages.append(tool_message)
        
        logger.info(f"Completed processing {len(tool_messages)} tool call(s)")
        return tool_messages
    
    def stream_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        agent_id: Optional[str] = None,
        include_tool_calls: bool = False
    ) -> Generator[str, None, None]:
        """
        Stream agent response in real-time as a generator.
        
        Purpose (Why):
        Provides real-time streaming of agent responses, improving user experience
        by showing text as it is generated rather than waiting for complete responses.
        Handles function calling seamlessly during streaming by pausing stream execution,
        executing tools, and continuing streaming with tool results. All operations
        are logged with correlation ID for complete audit trail.
        
        Implementation (What):
        Generates a correlation ID for the request and logs message receipt. Sends user
        message to OpenAI API with stream=True, yielding response chunks as they
        arrive. When OpenAI requests tool calls during streaming, collects all tool
        calls from the stream, pauses streaming, executes tools with correlation ID,
        and continues streaming with tool results. Repeats this process until OpenAI
        returns a final response without tool calls. Logs response generation completion.
        Maintains stateless behavior - history is only used within the current session.
        
        Args:
            user_message: The user's message to process
            conversation_history: Optional list of previous messages in the
                current conversation session. Format: [{"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}, ...]
                Note: This is session-level history only. The agent is stateless
                between different sessions.
            agent_id: Optional identifier for the agent/session. Used for audit logging.
                Defaults to "default" for stateless agents.
            include_tool_calls: If True, yields special JSON markers for tool calls
                that can be captured by the UI layer. If False, only yields text chunks (default).
                When True, tool call information is embedded in the stream as special markers
                that can be extracted and displayed separately in the UI.
        
        Yields:
            String chunks containing parts of the agent's response. Each yield is a
            piece of text that should be displayed to the user in real-time. When
            include_tool_calls=True, may yield special JSON markers for tool calls
            in the format [TOOL_CALL_START]{...}[/TOOL_CALL_START] and
            [TOOL_CALL_RESULT]{...}[/TOOL_CALL_RESULT] that can be extracted and
            displayed separately in the UI.
        
        Raises:
            Exception: If OpenAI API call fails or other errors occur
        
        Example:
            >>> agent = StreamingAgent()
            >>> for chunk in agent.stream_response("Tell me about Acamol"):
            ...     print(chunk, end="", flush=True)
        """
        # Generate correlation ID for this request
        correlation_id = generate_correlation_id()
        effective_agent_id = agent_id if agent_id is not None else "default"
        
        # Log message receipt
        _audit_logger.log_agent_action(
            correlation_id=correlation_id,
            agent_id=effective_agent_id,
            action="message_received",
            details={"message": user_message[:500]},  # Limit message length in logs
            status="success"
        )
        
        if not user_message or not user_message.strip():
            logger.warning("Empty user message received")
            _audit_logger.log_agent_action(
                correlation_id=correlation_id,
                agent_id=effective_agent_id,
                action="empty_message_handled",
                details={},
                status="success"
            )
            yield "I'm here to help! Please ask me about medications, stock availability, or prescription requirements."
            return
        
        messages = self._build_messages(user_message, conversation_history)
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        logger.info(f"Processing user message with streaming (correlation_id: {correlation_id})")
        logger.debug(f"Message: {user_message[:100]}...")
        
        # Build context for audit logging
        context = {
            "user_message": user_message[:500],  # Limit message length
            "conversation_history_length": len(conversation_history) if conversation_history else 0
        }
        
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
                    # Check if tool_calls exists and is iterable (not just truthy Mock)
                    if delta.tool_calls:
                        try:
                            # Try to iterate to verify it's actually iterable
                            # This will raise TypeError if tool_calls is not iterable (e.g., Mock object)
                            iter(delta.tool_calls)
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
                        except (TypeError, AttributeError):
                            # tool_calls is not iterable (e.g., Mock object that's not configured as iterable)
                            # Skip tool call processing for this chunk
                            pass
                
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
                    
                    # If include_tool_calls is True, yield tool call information before execution
                    # This allows the UI to display tool calls as they happen
                    if include_tool_calls:
                        for tool_call in tool_calls_collected:
                            tool_call_info = {
                                "type": "tool_call_start",
                                "tool_name": tool_call.get("function", {}).get("name", ""),
                                "tool_id": tool_call.get("id", ""),
                                "arguments": json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                            }
                            yield f"\n\n[TOOL_CALL_START]{json.dumps(tool_call_info, ensure_ascii=False)}[/TOOL_CALL_START]\n\n"
                    
                    # Execute tools with correlation ID for audit logging
                    tool_messages = self._process_tool_calls(
                        tool_calls_collected,
                        correlation_id=correlation_id,
                        agent_id=effective_agent_id,
                        context=context
                    )
                    
                    # If include_tool_calls is True, yield tool call results after execution
                    if include_tool_calls:
                        for tool_call, tool_message in zip(tool_calls_collected, tool_messages):
                            tool_result_info = {
                                "type": "tool_call_result",
                                "tool_name": tool_call.get("function", {}).get("name", ""),
                                "tool_id": tool_call.get("id", ""),
                                "result": json.loads(tool_message.get("content", "{}")),
                                "success": json.loads(tool_message.get("content", "{}")).get("success", True)
                            }
                            yield f"\n\n[TOOL_CALL_RESULT]{json.dumps(tool_result_info, ensure_ascii=False)}[/TOOL_CALL_RESULT]\n\n"
                    
                    messages.extend(tool_messages)
                    
                    # Continue loop to get model's response to tool results (with streaming)
                    continue
                
                # No tool calls - we have final response
                # If we already yielded content, we're done
                # If no content was yielded but finish_reason is "stop", check if we need to yield error
                if finish_reason == "stop":
                    if accumulated_content:
                        # We already yielded content, we're done
                        logger.info("Streaming completed with final response")
                        _audit_logger.log_agent_action(
                            correlation_id=correlation_id,
                            agent_id=effective_agent_id,
                            action="response_generated",
                            details={"response_length": len(accumulated_content)},
                            status="success"
                        )
                        return
                    elif not tool_calls_collected:
                        # No content and no tool calls - yield error message
                        logger.warning("Stream completed with no content and no tool calls")
                        _audit_logger.log_agent_action(
                            correlation_id=correlation_id,
                            agent_id=effective_agent_id,
                            action="response_generation_failed",
                            details={"reason": "no_content_no_tool_calls"},
                            status="error"
                        )
                        yield "I apologize, but I encountered an issue processing your request. Please try again or rephrase your question."
                        return
                    else:
                        # Should not happen, but handle gracefully
                        logger.info("Streaming completed with final response")
                        _audit_logger.log_agent_action(
                            correlation_id=correlation_id,
                            agent_id=effective_agent_id,
                            action="response_generated",
                            details={"response_length": 0},
                            status="success"
                        )
                        return
                elif not tool_calls_collected and accumulated_content:
                    # We have content and no tool calls - we're done
                    logger.info("Streaming completed with final response")
                    _audit_logger.log_agent_action(
                        correlation_id=correlation_id,
                        agent_id=effective_agent_id,
                        action="response_generated",
                        details={"response_length": len(accumulated_content)},
                        status="success"
                    )
                    return
                
                # If we reach here and no content was yielded, something unexpected happened
                if not accumulated_content and not tool_calls_collected:
                    logger.warning("Stream completed with no content and no tool calls")
                    _audit_logger.log_agent_action(
                        correlation_id=correlation_id,
                        agent_id=effective_agent_id,
                        action="response_generation_failed",
                        details={"reason": "unexpected_state"},
                        status="error"
                    )
                    yield "I apologize, but I encountered an issue processing your request. Please try again or rephrase your question."
                    return
                
            except Exception as e:
                error_msg = f"Error in OpenAI API streaming call: {str(e)}"
                logger.error(error_msg, exc_info=True)
                _audit_logger.log_agent_action(
                    correlation_id=correlation_id,
                    agent_id=effective_agent_id,
                    action="error_handled",
                    details={"error": str(e), "error_type": type(e).__name__},
                    status="error"
                )
                yield f"I apologize, but I encountered an error: {error_msg}. Please try again."
                return
        
        # If we exit loop, we hit max iterations
        logger.warning(f"Reached max iterations ({max_iterations}) in streaming tool calling loop")
        _audit_logger.log_agent_action(
            correlation_id=correlation_id,
            agent_id=effective_agent_id,
            action="max_iterations_reached",
            details={"max_iterations": max_iterations},
            status="error"
        )
        yield "I apologize, but I encountered an issue processing your request. Please try again or rephrase your question."


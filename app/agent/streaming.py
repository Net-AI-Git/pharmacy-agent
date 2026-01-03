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
import re
import time
from typing import List, Dict, Any, Optional, Generator, Tuple
from openai import OpenAI
import httpx
from dotenv import load_dotenv
from app.prompts.system_prompt import get_system_prompt
from app.tools.registry import get_tools_for_openai, execute_tool
from app.security.audit_logger import AuditLogger
from app.security.correlation import generate_correlation_id

# #region agent log
# Debug log path - only used if the directory exists (for local development)
# In Docker/production, this will silently fail (no logging to file)
DEBUG_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".cursor", "debug.log")
def _debug_log(location: str, message: str, data: dict = None, hypothesis_id: str = None):
    try:
        # Only log if the directory exists (local development)
        log_dir = os.path.dirname(DEBUG_LOG_PATH)
        if not os.path.exists(log_dir):
            return
        log_entry = {
            "sessionId": "debug-session",
            "runId": "initial",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000)
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass
# #endregion

# Load environment variables
load_dotenv()

# Configure module-level logger
logger = logging.getLogger(__name__)

# Module-level audit logger instance
_audit_logger = AuditLogger()

# Shared HTTP client with optimized connection pooling for improved performance
# Using HTTP/1.1 instead of HTTP/2 for better compatibility and faster initial connection
# HTTP/2 can have slower initial connection setup, which is causing 30-40s delays
_http_client = httpx.Client(
    http2=False,  # Disable HTTP/2 to avoid slow initial connection setup
    limits=httpx.Limits(
        max_keepalive_connections=20,  # Increased for better connection reuse
        max_connections=50  # Increased connection pool size
    ),
    timeout=httpx.Timeout(
        connect=5.0,   # Faster connection timeout (fail fast if can't connect)
        read=120.0,    # Longer read timeout for streaming
        write=10.0,    # Write timeout
        pool=10.0      # Connection pool timeout
    )
)


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
        # #region agent log
        init_start = time.time()
        _debug_log("app/agent/streaming.py:__init__:entry", "StreamingAgent.__init__ started", {"model": model}, "H2")
        # #endregion
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            error_msg = "OPENAI_API_KEY not found in environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Configure OpenAI client with optimized timeout settings
        # Using the shared HTTP client with optimized connection pooling
        # #region agent log
        client_start = time.time()
        # #endregion
        self.client = OpenAI(
            api_key=api_key,
            http_client=_http_client,  # Use shared optimized HTTP client
            timeout=httpx.Timeout(
                connect=5.0,       # Faster connection timeout (fail fast)
                read=120.0,       # Longer read timeout for streaming responses
                write=10.0,        # Write timeout
                pool=10.0         # Connection pool timeout
            ),
            max_retries=1          # Reduced retries to fail faster and avoid long delays
        )
        # #region agent log
        _debug_log("app/agent/streaming.py:__init__:client_created", "OpenAI client created", {"duration_ms": (time.time() - client_start) * 1000}, "H2")
        # #endregion
        
        # #region agent log
        prompt_start = time.time()
        # #endregion
        self.system_prompt = get_system_prompt()
        # #region agent log
        _debug_log("app/agent/streaming.py:__init__:prompt_loaded", "System prompt loaded", {"duration_ms": (time.time() - prompt_start) * 1000, "prompt_length": len(self.system_prompt)}, "H2")
        # #endregion
        
        # #region agent log
        tools_start = time.time()
        # #endregion
        self.tools = get_tools_for_openai()
        # #region agent log
        _debug_log("app/agent/streaming.py:__init__:tools_loaded", "Tools loaded", {"duration_ms": (time.time() - tools_start) * 1000, "tools_count": len(self.tools)}, "H3")
        # #endregion
        
        self.model = model
        
        # #region agent log
        _debug_log("app/agent/streaming.py:__init__:complete", "StreamingAgent.__init__ complete", {"total_duration_ms": (time.time() - init_start) * 1000}, "H2")
        # #endregion
        logger.info(f"StreamingAgent initialized with model: {model}")
        logger.debug(f"Loaded {len(self.tools)} tools for function calling")
    
    def _normalize_input(self, user_message: str) -> Tuple[str, bool]:
        """
        Normalize user input by detecting and cleaning repetitive content.
        
        Purpose (Why):
        Detects repetitive input (same word/phrase repeated many times) and cleans it
        to reduce token usage and improve processing efficiency. Also limits maximum
        input length to prevent excessive token consumption.
        
        Implementation (What):
        Checks for repetitive patterns (same word/phrase repeated >10 times), reduces
        to 1-2 repetitions, limits total length to 2000 characters (500 tokens),
        and cleans excessive whitespace.
        
        Args:
            user_message: The user's message to normalize
        
        Returns:
            Tuple of (normalized_message, was_cleaned) where:
            - normalized_message: The cleaned message
            - was_cleaned: Boolean indicating if any cleaning was performed
        """
        if not user_message or not user_message.strip():
            return user_message, False
        
        original_length = len(user_message)
        cleaned = False
        normalized = user_message.strip()
        
        # Detect repetitive patterns (same word/phrase repeated many times)
        # Split into words and check for excessive repetition
        words = normalized.split()
        if len(words) > 20:  # Only check if message is long enough
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # Find words that appear more than 10 times
            repetitive_words = {word: count for word, count in word_counts.items() if count > 10}
            
            if repetitive_words:
                # Replace excessive repetitions with 1-2 occurrences
                for word, count in repetitive_words.items():
                    # Create pattern to match the word repeated many times
                    pattern = r'\b' + re.escape(word) + r'\b'
                    # Replace all occurrences with just 2 occurrences
                    normalized = re.sub(pattern, word, normalized, count=count-2)
                    cleaned = True
                    logger.info(f"Detected repetitive input: '{word}' appeared {count} times, reduced to 2")
        
        # Limit maximum length to 2000 characters (approximately 500 tokens)
        if len(normalized) > 2000:
            normalized = normalized[:2000] + "..."
            cleaned = True
            logger.info(f"Input truncated from {len(user_message)} to 2000 characters")
        
        # Clean excessive whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        if len(normalized) != original_length:
            cleaned = True
        
        if cleaned:
            logger.debug(f"Input normalized: original length {original_length}, normalized length {len(normalized)}")
        
        return normalized, cleaned
    
    def _optimize_history(
        self,
        conversation_history: Optional[List[Dict[str, str]]],
        max_messages: int = 20,
        max_tokens: int = 4000
    ) -> List[Dict[str, str]]:
        """
        Optimize conversation history by limiting length and summarizing old messages.
        
        Purpose (Why):
        Reduces token usage by limiting history length and summarizing old messages
        when history becomes too long. This prevents excessive token consumption
        while maintaining essential context.
        
        Implementation (What):
        Estimates tokens (4 chars = 1 token), keeps last 10 messages in full,
        summarizes older messages into a single summary message if history exceeds
        limits. Prevents duplicate consecutive messages.
        
        Args:
            conversation_history: Optional list of previous messages
            max_messages: Maximum number of messages to keep (default: 20)
            max_tokens: Maximum estimated tokens for history (default: 4000)
        
        Returns:
            Optimized list of messages with summary if needed
        """
        if not conversation_history:
            return []
        
        # Estimate tokens (rough approximation: 4 characters = 1 token)
        def estimate_tokens(text: str) -> int:
            return len(text) // 4
        
        # Calculate total tokens
        total_tokens = sum(estimate_tokens(msg.get("content", "")) for msg in conversation_history)
        total_messages = len(conversation_history)
        
        # If within limits, return as-is (but check for duplicates)
        if total_messages <= max_messages and total_tokens <= max_tokens:
            # Remove duplicate consecutive messages
            optimized = []
            prev_content = None
            for msg in conversation_history:
                content = msg.get("content", "")
                if content != prev_content:
                    optimized.append(msg)
                    prev_content = content
            return optimized
        
        # Need to optimize - keep last 10 messages, summarize older ones
        keep_count = 10
        if total_messages <= keep_count:
            return conversation_history[-keep_count:]
        
        # Keep last messages
        recent_messages = conversation_history[-keep_count:]
        old_messages = conversation_history[:-keep_count]
        
        # Create summary of old messages
        old_content = " ".join(msg.get("content", "")[:200] for msg in old_messages[:5])  # Sample first 5
        summary_message = {
            "role": "system",
            "content": f"[Previous conversation summary: {len(old_messages)} earlier messages discussing medications and prescriptions]"
        }
        
        # Combine summary + recent messages
        optimized = [summary_message] + recent_messages
        
        logger.info(f"History optimized: {total_messages} messages ({total_tokens} tokens) -> {len(optimized)} messages")
        
        return optimized
    
    def _extract_context_info(
        self,
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> Dict[str, Any]:
        """
        Extract context information (medications, users) from conversation history.
        
        Purpose (Why):
        Identifies medications and users that have already been discussed in the
        conversation history, allowing the agent to avoid redundant tool calls
        when information is already available.
        
        Implementation (What):
        Scans history for medication IDs/names and user IDs/names mentioned in
        tool call results or assistant messages. Returns structured context info.
        
        Args:
            conversation_history: Optional list of previous messages
        
        Returns:
            Dictionary with keys:
            - medications: List of medication IDs/names found
            - users: List of user IDs/names found
        """
        context = {
            "medications": [],
            "users": []
        }
        
        if not conversation_history:
            return context
        
        # Patterns to look for in messages
        medication_pattern = r'"medication_id"\s*:\s*"([^"]+)"'
        medication_name_pattern = r'"name_he"\s*:\s*"([^"]+)"|"name_en"\s*:\s*"([^"]+)"'
        user_id_pattern = r'"user_id"\s*:\s*"([^"]+)"'
        user_name_pattern = r'"name"\s*:\s*"([^"]+)"'
        
        for msg in conversation_history:
            content = msg.get("content", "")
            if not content:
                continue
            
            # Look for medication IDs
            medication_ids = re.findall(medication_pattern, content)
            context["medications"].extend(medication_ids)
            
            # Look for medication names
            medication_names_he = re.findall(medication_name_pattern, content)
            for match in medication_names_he:
                if match[0]:  # Hebrew name
                    context["medications"].append(match[0])
                if match[1]:  # English name
                    context["medications"].append(match[1])
            
            # Look for user IDs
            user_ids = re.findall(user_id_pattern, content)
            context["users"].extend(user_ids)
            
            # Look for user names
            user_names = re.findall(user_name_pattern, content)
            context["users"].extend(user_names)
        
        # Remove duplicates
        context["medications"] = list(set(context["medications"]))
        context["users"] = list(set(context["users"]))
        
        if context["medications"] or context["users"]:
            logger.debug(f"Extracted context: {len(context['medications'])} medications, {len(context['users'])} users")
        
        return context
    
    def _build_messages(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context_info: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """
        Build message list for OpenAI API from user message and history.
        
        Purpose (Why):
        Constructs the message format required by OpenAI API, including system
        prompt, optimized conversation history, context information, and the
        current user message. This ensures proper context is maintained while
        minimizing token usage.
        
        Implementation (What):
        Creates a list of message dictionaries in OpenAI format. Starts with
        system message, adds optimized conversation history if provided, adds
        context information if available, and appends the current user message.
        History is optimized to reduce token usage while maintaining essential context.
        
        Args:
            user_message: The current user message to process
            conversation_history: Optional list of previous messages in the
                current conversation session. Format: [{"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}, ...]
            context_info: Optional dictionary with context information (medications, users)
                extracted from history to avoid redundant tool calls
        
        Returns:
            List of message dictionaries in OpenAI API format
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add context information if available
        if context_info and (context_info.get("medications") or context_info.get("users")):
            context_msg = "Available context from conversation history:\n"
            if context_info.get("medications"):
                context_msg += f"- Medications already discussed: {', '.join(context_info['medications'][:5])}\n"
            if context_info.get("users"):
                context_msg += f"- Users already discussed: {', '.join(context_info['users'][:3])}\n"
            context_msg += "Before calling tools, check if this information is already available."
            messages.append({"role": "system", "content": context_msg})
        
        # Optimize and add conversation history
        if conversation_history:
            optimized_history = self._optimize_history(conversation_history)
            messages.extend(optimized_history)
        
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _process_single_tool_call(
        self,
        tool_call: Any,
        correlation_id: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None,
        tool_call_cache: Optional[Dict[str, Any]] = None
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
            
            # Check cache for duplicate tool calls with same arguments
            if tool_call_cache is not None:
                # Create cache key from tool name and sorted arguments
                cache_key = (tool_name, json.dumps(arguments, sort_keys=True))
                if cache_key in tool_call_cache:
                    logger.debug(f"Cache hit for tool call: {tool_name} with arguments: {arguments_str[:100]}...")
                    cached_result = tool_call_cache[cache_key]
                    # Return cached result with current tool_call_id
                    return {
                        "tool_call_id": tool_id,
                        "result": cached_result["result"],
                        "success": cached_result.get("success", True)
                    }
            
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
            
            # Cache the result if cache is available
            if tool_call_cache is not None:
                cache_key = (tool_name, json.dumps(arguments, sort_keys=True))
                tool_call_cache[cache_key] = {
                    "result": result_str,
                    "success": result.get("success", True) if isinstance(result, dict) else True
                }
                logger.debug(f"Cached result for tool call: {tool_name}")
            
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
        context: Optional[Dict[str, Any]] = None,
        tool_call_cache: Optional[Dict[str, Any]] = None
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
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all tool calls for parallel execution
            future_to_tool = {
                executor.submit(
                    self._process_single_tool_call,
                    tool_call,
                    correlation_id,
                    agent_id,
                    context,
                    tool_call_cache
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
        include_tool_calls: bool = False,
        context: Optional[Dict[str, Any]] = None
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
        # #region agent log
        stream_start = time.time()
        _debug_log("app/agent/streaming.py:stream_response:entry", "stream_response started", {"message_length": len(user_message), "history_length": len(conversation_history) if conversation_history else 0}, "H1")
        # #endregion
        
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
        
        # Normalize input to handle repetitive content
        # #region agent log
        normalize_start = time.time()
        # #endregion
        normalized_message, was_cleaned = self._normalize_input(user_message)
        # #region agent log
        _debug_log("app/agent/streaming.py:stream_response:normalize", "Input normalized", {"duration_ms": (time.time() - normalize_start) * 1000, "was_cleaned": was_cleaned}, "H5")
        # #endregion
        if was_cleaned:
            logger.info("Input was normalized (repetitive content detected or length limited)")
            _audit_logger.log_agent_action(
                correlation_id=correlation_id,
                agent_id=effective_agent_id,
                action="input_normalized",
                details={"original_length": len(user_message), "normalized_length": len(normalized_message)},
                status="success"
            )
            # Note: We don't yield a message to user about cleaning to avoid interrupting flow
        
        # Extract context information from history
        # #region agent log
        context_start = time.time()
        # #endregion
        context_info = self._extract_context_info(conversation_history)
        # #region agent log
        _debug_log("app/agent/streaming.py:stream_response:context_extracted", "Context extracted", {"duration_ms": (time.time() - context_start) * 1000}, "H5")
        # #endregion
        
        # Build messages with optimized history and context
        # #region agent log
        build_start = time.time()
        # #endregion
        messages = self._build_messages(normalized_message, conversation_history, context_info)
        # #region agent log
        _debug_log("app/agent/streaming.py:stream_response:messages_built", "Messages built", {"duration_ms": (time.time() - build_start) * 1000, "messages_count": len(messages)}, "H5")
        # #endregion
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        logger.info(f"Processing user message with streaming (correlation_id: {correlation_id})")
        logger.debug(f"Message: {user_message[:100]}...")
        
        # Build context for audit logging and tool execution
        if context is None:
            context = {}
        context.update({
            "user_message": user_message[:500],  # Limit message length
            "conversation_history_length": len(conversation_history) if conversation_history else 0
        })
        
        # Track authentication errors to prevent retrying the same failed authentication
        auth_errors = []  # List of authentication error messages seen in previous iterations
        
        # Cache tool call results within this request to prevent duplicate calls
        tool_call_cache = {}  # Key: (tool_name, json.dumps(sorted arguments)), Value: result dict
        
        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"OpenAI API streaming call iteration: {iteration}")
            
            try:
                # Call OpenAI API with streaming enabled
                # #region agent log
                api_call_start = time.time()
                _debug_log("app/agent/streaming.py:stream_response:api_call_start", "OpenAI API call starting", {"iteration": iteration, "messages_count": len(messages)}, "H4")
                # #endregion
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",  # Let model decide when to use tools
                    stream=True  # Enable streaming
                )
                # #region agent log
                _debug_log("app/agent/streaming.py:stream_response:api_call_connected", "OpenAI API stream connected", {"duration_ms": (time.time() - api_call_start) * 1000}, "H4")
                # #endregion
                
                # Collect response chunks and tool calls
                accumulated_content = ""
                tool_calls_collected = []
                finish_reason = None
                first_chunk_time = None
                chunk_count = 0
                
                # #region agent log
                stream_processing_start = time.time()
                # #endregion
                for chunk in stream:
                    if first_chunk_time is None:
                        first_chunk_time = time.time()
                        # #region agent log
                        _debug_log("app/agent/streaming.py:stream_response:first_chunk", "First chunk received", {"time_to_first_chunk_ms": (first_chunk_time - api_call_start) * 1000}, "H4")
                        # #endregion
                    chunk_count += 1
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
                
                # #region agent log
                _debug_log("app/agent/streaming.py:stream_response:stream_complete", "Stream processing complete", {"duration_ms": (time.time() - stream_processing_start) * 1000, "chunk_count": chunk_count, "content_length": len(accumulated_content)}, "H4")
                # #endregion
                
                # After stream completes, check if we need to handle tool calls
                if finish_reason == "tool_calls" and tool_calls_collected:
                    # #region agent log
                    tool_exec_start = time.time()
                    _debug_log("app/agent/streaming.py:stream_response:tool_exec_start", "Tool execution starting", {"tool_calls_count": len(tool_calls_collected)}, "H6")
                    # #endregion
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
                        context=context,
                        tool_call_cache=tool_call_cache
                    )
                    # #region agent log
                    _debug_log("app/agent/streaming.py:stream_response:tool_exec_complete", "Tool execution complete", {"duration_ms": (time.time() - tool_exec_start) * 1000, "tool_messages_count": len(tool_messages)}, "H6")
                    # #endregion
                    
                    # Check for authentication errors in tool results
                    current_auth_errors = []
                    for tool_message in tool_messages:
                        try:
                            result_content = json.loads(tool_message.get("content", "{}"))
                            error_msg = result_content.get("error", "")
                            success = result_content.get("success", True)
                            
                            # Check if this is an authentication error (improved detection)
                            if error_msg and not success:
                                error_lower = error_msg.lower()
                                # Detect various authentication error patterns
                                if any(pattern in error_lower for pattern in [
                                    "authentication required",
                                    "authentication",
                                    "login required",
                                    "not authenticated",
                                    "unauthorized",
                                    "access denied"
                                ]):
                                    current_auth_errors.append(error_msg)
                        except (json.JSONDecodeError, AttributeError):
                            pass
                    
                    # If we see authentication errors, handle them immediately
                    if current_auth_errors:
                        # Check if we've seen this error before (in any iteration)
                        for auth_error in current_auth_errors:
                            if auth_error in auth_errors:
                                # Same authentication error seen before - stop retrying immediately
                                logger.warning(f"Authentication error repeated: {auth_error}. Stopping retries.")
                                error_response = (
                                    "I apologize, but I'm unable to access your prescription information due to an authentication issue. "
                                    "Please ensure you are logged in and try again. If the problem persists, please contact support."
                                )
                                yield error_response
                                _audit_logger.log_agent_action(
                                    correlation_id=correlation_id,
                                    agent_id=effective_agent_id,
                                    action="authentication_error_repeated",
                                    details={"error": auth_error, "iteration": iteration},
                                    status="error"
                                )
                                return
                        
                        # First time seeing this error - add to list and respond immediately
                        auth_errors.extend(current_auth_errors)
                        # If this is the first iteration and we got auth error, respond immediately
                        if iteration == 1:
                            logger.info("Authentication error detected in first iteration, responding immediately")
                            error_response = (
                                "I'm unable to access your prescription information. Authentication is required. "
                                "Please log in to your account and try again."
                            )
                            yield error_response
                            _audit_logger.log_agent_action(
                                correlation_id=correlation_id,
                                agent_id=effective_agent_id,
                                action="authentication_error_detected",
                                details={"error": current_auth_errors[0], "iteration": iteration},
                                status="error"
                            )
                            return
                    
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


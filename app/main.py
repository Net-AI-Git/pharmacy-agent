"""
Main entry point for the Pharmacy AI Agent application.

Purpose (Why):
This module serves as the application entry point for the Pharmacy AI Assistant.
It initializes the Gradio user interface and the StreamingAgent, providing the
main interface for users to interact with the pharmacy assistant. The module
sets up the necessary components for the chat interface, streaming responses,
and tool call visualization as required by the project specifications.

Implementation (What):
Imports Gradio for the UI framework and StreamingAgent for the AI agent
functionality. Creates an instance of StreamingAgent and a Gradio ChatInterface
with streaming support. The chat interface handles user messages, converts
conversation history formats, and streams agent responses in real-time. The
module follows the project requirements: uses OpenAI API directly (not Langchain),
supports streaming, maintains stateless behavior, and supports both Hebrew and English.
"""

import logging
import json
import re
import os
from typing import Optional, List, Dict, Generator, Tuple, Any
import gradio as gr
from app.agent import StreamingAgent

# Configure module-level logger
logger = logging.getLogger(__name__)

# #region agent log
DEBUG_LOG_PATH = r"c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log"
def _debug_log(location: str, message: str, data: dict = None, hypothesis_id: str = None):
    try:
        log_entry = {
            "sessionId": "debug-session",
            "runId": "initial",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(__import__("time").time() * 1000)
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass
# #endregion


def initialize_agent(model: Optional[str] = None) -> StreamingAgent:
    """
    Initialize and return a StreamingAgent instance.
    
    Purpose (Why):
    Creates a StreamingAgent instance for processing user queries with real-time
    streaming capabilities. This function encapsulates agent initialization logic,
    making it easier to configure the agent with different models or settings
    if needed in the future. The agent is stateless and supports both Hebrew
    and English as required by the project specifications.
    
    Implementation (What):
    Creates a new StreamingAgent instance with the specified model (or default
    "gpt-5"). The agent is initialized with OpenAI API client, system prompt,
    and tools for function calling. All initialization errors are logged and
    re-raised to ensure proper error handling at the application level.
    
    Args:
        model: Optional OpenAI model name to use. If None, defaults to "gpt-5"
            as configured in StreamingAgent.__init__(). This allows flexibility
            to use different models for different environments (dev vs prod).
    
    Returns:
        StreamingAgent: Initialized agent instance ready to process user queries
            with streaming support and tool calling capabilities.
    
    Raises:
        ValueError: If OPENAI_API_KEY is not found in environment variables.
            This is raised by StreamingAgent.__init__() and propagated here.
        Exception: Any other errors during agent initialization are logged and
            re-raised for proper error handling.
    
    Example:
        >>> agent = initialize_agent()
        >>> # Use agent.stream_response() to process user messages
    """
    try:
        model_name = model or "gpt-5"
        logger.info(f"Initializing StreamingAgent with model: {model_name}")
        agent = StreamingAgent(model=model_name)
        logger.info("StreamingAgent initialized successfully")
        return agent
    except Exception as e:
        error_msg = f"Failed to initialize StreamingAgent: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise


# Initialize the agent instance at module level
# This follows the module-level caching pattern from agentic-logic-and-tools
# The agent instance is created once and reused across all requests
# This reduces initialization overhead and maintains consistency
_agent_instance: Optional[StreamingAgent] = None


def get_agent_instance() -> StreamingAgent:
    """
    Get or create the shared StreamingAgent instance.
    
    Purpose (Why):
    Provides singleton-like access to the StreamingAgent, ensuring all parts
    of the application use the same agent instance. This follows the module-level
    caching pattern recommended in agentic-logic-and-tools.md, reducing token
    usage and improving performance by reusing the same agent instance across
    requests. The agent is stateless, so sharing an instance is safe.
    
    Implementation (What):
    Creates a StreamingAgent instance on first call and returns the same
    instance on subsequent calls. This ensures consistency and reduces
    initialization overhead. The instance is stored at module level for
    availability between calls.
    
    Returns:
        StreamingAgent: The shared StreamingAgent instance. Creates a new
        instance on first call and returns the same instance on subsequent calls.
    
    Raises:
        ValueError: If OPENAI_API_KEY is not found in environment variables.
        Exception: Any other errors during agent initialization.
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = initialize_agent()
    return _agent_instance


# Initialize agent when module is imported
# This ensures the agent is ready when the Gradio interface is created
# #region agent log
_debug_log("app/main.py:119", "Starting agent initialization", {}, "H2")
# #endregion
try:
    agent = get_agent_instance()
    logger.info("Main application: StreamingAgent instance created and ready")
    # #region agent log
    _debug_log("app/main.py:122", "Agent initialized successfully", {"agent_is_none": agent is None}, "H2")
    # #endregion
except Exception as e:
    logger.error(f"Main application: Failed to initialize agent: {str(e)}", exc_info=True)
    # Set agent to None so the application can handle the error gracefully
    agent = None
    # #region agent log
    _debug_log("app/main.py:125", "Agent initialization failed", {"error": str(e), "error_type": type(e).__name__}, "H2")
    # #endregion


def convert_gradio_history_to_dict_format(
    gradio_history: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    Convert Gradio 6.0 chat history format (dict) to agent message format.
    
    Gradio 6.0 uses list of dicts with 'role' and 'content' keys.
    """
    if not gradio_history:
        return []
    
    agent_messages = []
    for msg in gradio_history:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            role = msg["role"]
            content = msg.get("content", "")
            if content and content.strip():
                agent_messages.append({"role": role, "content": content})
    
    return agent_messages


def convert_dict_history_to_gradio_format(
    history: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    Convert agent message format to Gradio 6.0 format.
    
    Returns list of dicts with 'role' and 'content' keys.
    """
    if not history:
        return []
    
    gradio_messages = []
    for msg in history:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            gradio_messages.append({
                "role": msg["role"],
                "content": str(msg.get("content", ""))
            })
    
    return gradio_messages


def convert_gradio_history_to_agent_format(
    gradio_history: List[Tuple[str, str]]
) -> List[Dict[str, str]]:
    """
    Convert Gradio chat history format to agent message format.
    
    Purpose (Why):
    Gradio ChatInterface uses a list of tuples (user_message, assistant_message)
    for chat history, while the StreamingAgent expects a list of dictionaries
    with "role" and "content" keys. This function bridges the format gap,
    enabling proper conversation history management within a single session.
    The agent is stateless, so history is only maintained within the current
    conversation session.
    
    Implementation (What):
    Iterates through Gradio history tuples and converts each pair to two
    message dictionaries: one for user role and one for assistant role.
    Returns an empty list if history is None or empty. Handles edge cases
    where messages might be empty strings.
    
    Args:
        gradio_history: List of tuples from Gradio ChatInterface.
            Each tuple is (user_message: str, assistant_message: str).
            Can be None or empty list.
    
    Returns:
        List of message dictionaries in OpenAI API format:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
        Returns empty list if input is None or empty.
    
    Example:
        >>> history = [("Hello", "Hi there!"), ("How are you?", "I'm doing well.")]
        >>> agent_format = convert_gradio_history_to_agent_format(history)
        >>> # Returns: [
        >>> #     {"role": "user", "content": "Hello"},
        >>> #     {"role": "assistant", "content": "Hi there!"},
        >>> #     {"role": "user", "content": "How are you?"},
        >>> #     {"role": "assistant", "content": "I'm doing well."}
        >>> # ]
    """
    if not gradio_history:
        return []
    
    agent_messages = []
    for user_msg, assistant_msg in gradio_history:
        if user_msg and user_msg.strip():
            agent_messages.append({"role": "user", "content": user_msg})
        if assistant_msg and assistant_msg.strip():
            agent_messages.append({"role": "assistant", "content": assistant_msg})
    
    return agent_messages


def chat_fn(
    message: str,
    history: List[Tuple[str, str]]
) -> Generator[Tuple[str, str], None, None]:
    """
    Handle chat messages with streaming support and tool call display.
    
    Purpose (Why):
    Processes user messages through the StreamingAgent and yields response
    chunks in real-time for display in the Gradio chat interface. This function
    enables real-time streaming of agent responses, improving user experience
    by showing text as it is generated. Additionally, extracts and displays
    tool call information (name, parameters, results) as required by the
    project specifications. Handles conversation history conversion and error
    cases gracefully, ensuring the UI remains responsive even when errors occur.
    The agent is stateless, so history is only maintained within the current
    conversation session.
    
    Implementation (What):
    Converts Gradio history format to agent message format, retrieves the
    agent instance, and calls stream_response() with include_tool_calls=True
    to get a generator of response chunks. Extracts tool call information
    from special markers in the stream and yields both text chunks and tool
    call information separately. Handles cases where agent is None (initialization
    failure) or when errors occur during streaming. All errors are logged and
    user-friendly error messages are yielded instead of raising exceptions.
    
    Args:
        message: The user's message to process. Can be empty string.
        history: List of tuples from Gradio ChatInterface representing
            conversation history. Each tuple is (user_message, assistant_message).
            History is only maintained within the current session (stateless agent).
    
    Yields:
        Tuples of (response_text, tool_calls_json) where:
        - response_text: String chunks containing parts of the agent's response.
            Each chunk is yielded immediately as it arrives from the streaming agent,
            enabling real-time display in the UI. Chunks may be small (single words
            or characters) or larger (sentences), depending on the streaming behavior
            of the OpenAI API. Empty strings are yielded when only tool call information
            is available.
        - tool_calls_json: JSON string containing tool call information, or empty string.
            Updated whenever tool calls are executed, allowing real-time display of
            tool execution information. The JSON contains tool name, parameters, results,
            and success status.
        Each yield immediately updates the UI, providing true streaming behavior where
        text appears incrementally as it is generated. In case of errors, yields error
        messages instead of raising exceptions.
    
    Raises:
        None. All exceptions are caught and logged, with user-friendly error
        messages yielded instead.
    
    Example:
        >>> for response, tool_calls in chat_fn("Tell me about Acamol", []):
        ...     print(response, end="", flush=True)
        ...     if tool_calls:
        ...         print(f"\nTool calls: {tool_calls}")
    """
    if not message or not message.strip():
        logger.warning("Empty message received in chat_fn")
        yield ("I'm here to help! Please ask me about medications, stock availability, or prescription requirements.", "")
        return
    
    if agent is None:
        error_msg = "Agent is not initialized. Please check your configuration and try again."
        logger.error(error_msg)
        yield (error_msg, "")
        return
    
    try:
        # Convert Gradio history format to agent message format
        conversation_history = convert_gradio_history_to_agent_format(history)
        
        logger.info(f"Processing chat message: {message[:100]}...")
        logger.debug(f"Conversation history length: {len(conversation_history)}")
        
        # Collect tool calls for display
        tool_calls_list = []
        accumulated_text = ""
        
        # Stream response chunks from agent with tool call information
        for chunk in agent.stream_response(
            user_message=message,
            conversation_history=conversation_history if conversation_history else None,
            include_tool_calls=True
        ):
            # Check if chunk contains tool call markers
            tool_call_start_match = re.search(r'\[TOOL_CALL_START\](.*?)\[/TOOL_CALL_START\]', chunk, re.DOTALL)
            tool_call_result_match = re.search(r'\[TOOL_CALL_RESULT\](.*?)\[/TOOL_CALL_RESULT\]', chunk, re.DOTALL)
            
            if tool_call_start_match:
                # Extract tool call start information
                try:
                    tool_call_info = json.loads(tool_call_start_match.group(1))
                    tool_calls_list.append(tool_call_info)
                    logger.debug(f"Tool call started: {tool_call_info.get('tool_name')}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse tool call start info: {e}")
                # Remove marker from text
                chunk = re.sub(r'\[TOOL_CALL_START\].*?\[/TOOL_CALL_START\]', '', chunk, flags=re.DOTALL)
            
            if tool_call_result_match:
                # Extract tool call result information
                try:
                    tool_result_info = json.loads(tool_call_result_match.group(1))
                    # Update the corresponding tool call with result
                    for tool_call in tool_calls_list:
                        if tool_call.get("tool_id") == tool_result_info.get("tool_id"):
                            tool_call["result"] = tool_result_info.get("result")
                            tool_call["success"] = tool_result_info.get("success", True)
                            break
                    logger.debug(f"Tool call completed: {tool_result_info.get('tool_name')}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse tool call result info: {e}")
                # Remove marker from text
                chunk = re.sub(r'\[TOOL_CALL_RESULT\].*?\[/TOOL_CALL_RESULT\]', '', chunk, flags=re.DOTALL)
            
            # Yield text chunk and tool calls (even if chunk is empty, to ensure streaming works)
            # This ensures that every chunk from the agent is passed through for real-time display
            accumulated_text += chunk
            tool_calls_json = json.dumps(tool_calls_list, ensure_ascii=False, indent=2) if tool_calls_list else ""
            yield (chunk, tool_calls_json)
        
        # Yield final tool calls update if any remain (even if no more text chunks)
        # This ensures tool calls are displayed even if they arrive after text streaming completes
        if tool_calls_list and not accumulated_text:
            tool_calls_json = json.dumps(tool_calls_list, ensure_ascii=False, indent=2)
            yield ("", tool_calls_json)
        
        logger.info("Chat message processed successfully")
        
    except Exception as e:
        error_msg = f"I apologize, but I encountered an error processing your request. Please try again."
        logger.error(f"Error in chat_fn: {str(e)}", exc_info=True)
        yield (error_msg, "")


def create_chat_interface() -> gr.Blocks:
    """
    Create and configure the Gradio interface for the Pharmacy AI Assistant.
    
    Purpose (Why):
    Sets up the main user interface for interacting with the Pharmacy AI Assistant.
    Configures a custom Blocks interface with appropriate title, description, and
    components to provide a professional, user-friendly experience. The interface
    supports streaming responses, bilingual interactions (Hebrew and English), and
    displays tool calls as required by the project specifications (section 5.3).
    
    Implementation (What):
    Creates a custom Gradio Blocks interface with a Chatbot component for the
    conversation and a JSON component for displaying tool calls. Uses the chat_fn
    function for handling messages, which yields both text chunks and tool call
    information. The interface is designed to be professional and clean, following
    UI best practices. Tool calls are displayed in a separate JSON component below
    the chat interface, showing tool name, parameters, and results.
    
    Returns:
        gr.Blocks: Configured Gradio Blocks instance ready to be launched.
            The interface includes a Chatbot for conversation and a JSON component
            for tool call display, with streaming support and professional styling.
    
    Raises:
        None. All errors are handled gracefully during interface creation.
    
    Example:
        >>> app = create_chat_interface()
        >>> app.launch(server_name="0.0.0.0", server_port=7860)
    """
    logger.info("Creating Gradio interface with tool call display")
    
    with gr.Blocks(title="Pharmacy AI Assistant", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
            # Pharmacy AI Assistant
            
            Welcome to the Pharmacy AI Assistant! I can help you with:
            - Medication information and active ingredients
            - Dosage and usage instructions
            - Stock availability
            - Prescription requirements
            
            **Please note:** I provide factual information only. For medical advice, please consult with a healthcare professional.
            
            ---
            
            # עוזר רוקח AI
            
            ברוכים הבאים! אני יכול לעזור עם:
            - מידע על תרופות ורכיבים פעילים
            - הוראות מינון ושימוש
            - זמינות במלאי
            - דרישות מרשם
            
            **שימו לב:** אני מספק מידע עובדתי בלבד. לייעוץ רפואי, יש להתייעץ עם איש מקצוע.
            """
        )
        
        chatbot = gr.Chatbot(
            label="Conversation",
            height=500
        )
        
        tool_calls_display = gr.JSON(
            label="Tool Calls",
            visible=True,
            show_label=True
        )
        
        msg = gr.Textbox(
            label="Message",
            placeholder="Type your message here... (Type your message here... / הקלד את ההודעה שלך כאן...)",
            show_label=False,
            scale=9
        )
        
        submit_btn = gr.Button("Send", variant="primary", scale=1)
        clear_btn = gr.Button("Clear", scale=1)
        
        def respond(message: str, history: List[Dict[str, str]]) -> Generator[Tuple[List[Dict[str, str]], Any], None, None]:
            """
            Handle user message and update chat history with tool calls (streaming).
            
            Purpose (Why):
            Processes user messages through chat_fn and updates the chat history
            with both the response text and tool call information in real-time.
            This enables the UI to display tool calls separately while maintaining
            the conversation flow in the chatbot component. Supports streaming for
            real-time response display, ensuring users see text as it is generated
            chunk by chunk rather than waiting for the complete response. This improves
            user experience and perceived responsiveness of the application.
            
            Implementation (What):
            This is a generator function that yields updates in real-time. Calls chat_fn
            to get streaming response chunks and tool call information. Accumulates text
            chunks and tool call data, updating the chat history in real-time for streaming
            effect. Each yield immediately updates the UI, providing true streaming behavior
            where text appears incrementally as it is generated. Gradio automatically detects
            generator functions and enables streaming support, displaying updates as they arrive.
            
            Args:
                message: The user's message to process. Can be empty string.
                history: Current chat history as list of tuples. Each tuple is
                    (user_message, assistant_message). History is maintained within
                    the current session only (stateless agent).
        
            Yields:
                Tuples of (updated_history, tool_calls_data) where:
                - updated_history: Chat history with new user message and assistant response.
                    The assistant response is updated incrementally as chunks arrive,
                    enabling real-time streaming display in the chatbot component.
                - tool_calls_data: Dict or list containing tool call information (for gr.JSON).
                    Updated whenever tool calls are executed, allowing real-time display
                    of tool execution information.
            
            Raises:
                None. All exceptions are caught and logged, with user-friendly error
                messages displayed instead of raising exceptions.
            
            Example:
                >>> # This function is called by Gradio when user submits a message
                >>> # Gradio automatically detects it's a generator and enables streaming
                >>> for history, tool_calls in respond("Tell me about Acamol", []):
                ...     # Each yield updates the UI immediately
                ...     pass
            """
            try:
                # #region agent log
                _debug_log("app/main.py:respond:entry", "respond function called", {"message": message[:50] if message else "", "message_type": str(type(message)), "history_length": len(history) if history else 0, "history_type": str(type(history)), "history_sample": str(history[:2]) if history else "[]", "first_entry_type": str(type(history[0])) if history and len(history) > 0 else "N/A"}, "H1")
                # #endregion
                if not message or not message.strip():
                    # #region agent log
                    _debug_log("app/main.py:respond:empty", "Empty message detected", {"history_type": str(type(history or [])), "will_yield_empty_dict": True}, "H1")
                    # #endregion
                    # Ensure history is a valid list of dicts
                    valid_history = []
                    if history:
                        for entry in history:
                            if isinstance(entry, dict) and "role" in entry and "content" in entry:
                                valid_history.append({
                                    "role": str(entry["role"]),
                                    "content": str(entry.get("content", ""))
                                })
                    yield (valid_history, {})
                    return
                
                # Validate history format - Gradio 6.0 uses list of dicts
                if history is not None and not isinstance(history, list):
                    # #region agent log
                    _debug_log("app/main.py:respond:invalid_history", "Invalid history type", {"history_type": str(type(history))}, "H1")
                    # #endregion
                    history = []
                
                # Clean and validate existing history entries - convert to dict format
                history = history or []
                cleaned_history = []
                for entry in history:
                    if isinstance(entry, dict) and "role" in entry and "content" in entry:
                        cleaned_history.append({
                            "role": str(entry["role"]),
                            "content": str(entry.get("content", ""))
                        })
                    elif isinstance(entry, tuple) and len(entry) == 2:
                        # Legacy tuple format - convert to dict
                        user_msg = str(entry[0]) if entry[0] is not None else ""
                        assistant_msg = str(entry[1]) if entry[1] is not None else ""
                        if user_msg:
                            cleaned_history.append({"role": "user", "content": user_msg})
                        if assistant_msg:
                            cleaned_history.append({"role": "assistant", "content": assistant_msg})
                    else:
                        # #region agent log
                        _debug_log("app/main.py:respond:invalid_history_entry_initial", "Invalid history entry in initial history", {"entry": str(entry), "entry_type": str(type(entry))}, "H1")
                        # #endregion
                original_history = cleaned_history.copy()  # Make a copy to avoid mutations
                # #region agent log
                _debug_log("app/main.py:respond:before_append", "Before processing", {"original_history_length": len(original_history), "history_type": str(type(original_history)), "message_type": str(type(message)), "original_history_sample": str(original_history[:2]) if original_history else "[]"}, "H2")
                # #endregion
                
                # Collect response and tool calls
                response_text = ""
                tool_calls_data = {}  # Initialize as empty dict (gr.JSON requires dict or list, not None)
                
                # Convert original_history to tuple format for chat_fn (legacy format)
                # Group consecutive user/assistant messages into tuples
                tuple_history = []
                i = 0
                while i < len(original_history):
                    msg = original_history[i]
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        user_content = msg.get("content", "")
                        assistant_content = ""
                        # Look for next assistant message
                        if i + 1 < len(original_history):
                            next_msg = original_history[i + 1]
                            if isinstance(next_msg, dict) and next_msg.get("role") == "assistant":
                                assistant_content = next_msg.get("content", "")
                                i += 2  # Skip both user and assistant
                            else:
                                i += 1  # Only skip user
                        else:
                            i += 1
                        tuple_history.append((user_content, assistant_content))
                    else:
                        i += 1
                
                # Stream response chunks in real-time
                # Each yield updates the UI immediately, providing true streaming experience
                for chunk, tool_calls_json in chat_fn(message, tuple_history):
                    # Accumulate text chunks for complete response
                    response_text += chunk
                    
                    # Parse tool calls JSON if present
                    if tool_calls_json:
                        # #region agent log
                        _debug_log("app/main.py:respond:tool_calls_json", "Tool calls JSON received", {"tool_calls_json_length": len(tool_calls_json), "tool_calls_json_preview": tool_calls_json[:100]}, "H3")
                        # #endregion
                        try:
                            # Parse JSON string to dict/list for gr.JSON component
                            tool_calls_data = json.loads(tool_calls_json)
                            # Validate that it's a dict or list
                            if not isinstance(tool_calls_data, (dict, list)):
                                # #region agent log
                                _debug_log("app/main.py:respond:invalid_tool_calls_type", "Invalid tool_calls_data type", {"tool_calls_data_type": str(type(tool_calls_data))}, "H3")
                                # #endregion
                                tool_calls_data = {}
                            # #region agent log
                            _debug_log("app/main.py:respond:tool_calls_parsed", "Tool calls parsed successfully", {"tool_calls_data_type": str(type(tool_calls_data)), "is_none": tool_calls_data is None}, "H3")
                            # #endregion
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse tool calls JSON: {tool_calls_json}")
                            # #region agent log
                            _debug_log("app/main.py:respond:json_parse_error", "JSON parse error", {"error": str(e), "tool_calls_json_preview": tool_calls_json[:100]}, "H3")
                            # #endregion
                            tool_calls_data = {}
                    
                    # Update history in real-time for streaming effect
                    # This ensures the chatbot displays text as it arrives, chunk by chunk
                    # Build history from original_history + current user message + streaming assistant response
                    # IMPORTANT: Always use original_history, never use the history parameter that Gradio passes back
                    updated_history = []
                    # Add all previous messages from original history (make copies to avoid mutations)
                    for msg in original_history:
                        if isinstance(msg, dict) and "role" in msg and "content" in msg:
                            updated_history.append({
                                "role": str(msg["role"]),
                                "content": str(msg.get("content", ""))
                            })
                    # Add current user message (only once)
                    updated_history.append({"role": "user", "content": message})
                    # Add/update assistant response (this will be updated on each yield)
                    updated_history.append({"role": "assistant", "content": response_text if response_text else ""})
                    # #region agent log
                    _debug_log("app/main.py:respond:history_built", "History built for yield", {"original_history_length": len(original_history), "updated_history_length": len(updated_history), "response_text_length": len(response_text)}, "H4")
                    # #endregion
                    # Ensure tool_calls_data is never None (gr.JSON requires dict or list, not None)
                    if tool_calls_data is None:
                        tool_calls_data = {}
                    # Ensure tool_calls_data is dict or list (not other types)
                    if not isinstance(tool_calls_data, (dict, list)):
                        # #region agent log
                        _debug_log("app/main.py:respond:invalid_tool_calls_before_yield", "Invalid tool_calls_data type before yield", {"tool_calls_data_type": str(type(tool_calls_data))}, "H4")
                        # #endregion
                        tool_calls_data = {}
                    # #region agent log
                    _debug_log("app/main.py:respond:before_yield", "Before yielding", {"history_length": len(updated_history), "history_type": str(type(updated_history)), "tool_calls_data_type": str(type(tool_calls_data)), "tool_calls_data_is_none": tool_calls_data is None, "response_text_length": len(response_text)}, "H4")
                    # #endregion
                    yield updated_history, tool_calls_data
                
                # Final update to ensure complete response is displayed
                # This handles edge cases where final chunks might not trigger UI update
                if response_text:
                    # Build final history from original_history + current user message + final assistant response
                    final_history = []
                    # Add all previous messages from original history
                    for msg in original_history:
                        if isinstance(msg, dict) and "role" in msg and "content" in msg:
                            final_history.append({
                                "role": str(msg["role"]),
                                "content": str(msg.get("content", ""))
                            })
                    # Add current user message
                    final_history.append({"role": "user", "content": message})
                    # Add final assistant response
                    final_history.append({"role": "assistant", "content": response_text})
                    # Ensure tool_calls_data is never None (gr.JSON requires dict or list, not None)
                    if tool_calls_data is None:
                        tool_calls_data = {}
                    # Ensure tool_calls_data is dict or list (not other types)
                    if not isinstance(tool_calls_data, (dict, list)):
                        # #region agent log
                        _debug_log("app/main.py:respond:invalid_tool_calls_final", "Invalid tool_calls_data type in final yield", {"tool_calls_data_type": str(type(tool_calls_data))}, "H4")
                        # #endregion
                        tool_calls_data = {}
                    # #region agent log
                    _debug_log("app/main.py:respond:final_yield", "Final yield", {"history_length": len(final_history), "tool_calls_data_type": str(type(tool_calls_data)), "tool_calls_data_is_none": tool_calls_data is None}, "H4")
                    # #endregion
                    yield final_history, tool_calls_data
            except Exception as e:
                # #region agent log
                _debug_log("app/main.py:respond:exception", "Exception in respond function", {"error": str(e), "error_type": str(type(e))}, "H1")
                # #endregion
                logger.error(f"Error in respond function: {str(e)}", exc_info=True)
                # Return error state with valid types - ensure history format is correct (dict format)
                error_history = []
                if history:
                    for entry in history:
                        if isinstance(entry, dict) and "role" in entry and "content" in entry:
                            error_history.append({
                                "role": str(entry["role"]),
                                "content": str(entry.get("content", ""))
                            })
                        elif isinstance(entry, tuple) and len(entry) == 2:
                            # Legacy format - convert to dict
                            user_msg = str(entry[0]) if entry[0] is not None else ""
                            assistant_msg = str(entry[1]) if entry[1] is not None else ""
                            if user_msg:
                                error_history.append({"role": "user", "content": user_msg})
                            if assistant_msg:
                                error_history.append({"role": "assistant", "content": assistant_msg})
                yield error_history, {}
        
        def clear_chat() -> Tuple[List[Dict[str, str]], dict]:
            """Clear chat history and tool calls display."""
            # #region agent log
            _debug_log("app/main.py:clear_chat", "clear_chat called", {"will_return_empty_dict": True}, "H5")
            # #endregion
            return [], {}
        
        # Connect components with streaming support
        # Gradio automatically detects generators and enables streaming
        # The respond function yields updates in real-time, updating the UI chunk by chunk
        # #region agent log
        _debug_log("app/main.py:connect_components", "Connecting Gradio components", {"msg_type": str(type(msg)), "chatbot_type": str(type(chatbot)), "tool_calls_display_type": str(type(tool_calls_display))}, "H5")
        # #endregion
        msg.submit(
            respond,
            inputs=[msg, chatbot],
            outputs=[chatbot, tool_calls_display]
        ).then(
            lambda: "",  # Clear message box after submission
            outputs=msg
        )
        
        submit_btn.click(
            respond,
            inputs=[msg, chatbot],
            outputs=[chatbot, tool_calls_display]
        ).then(
            lambda: "",  # Clear message box after submission
            outputs=msg
        )
        
        clear_btn.click(
            clear_chat,
            inputs=None,
            outputs=[chatbot, tool_calls_display]
        )
        
        # Examples
        gr.Examples(
            examples=[
                "Tell me about Acamol",
                "Is Tylenol available in stock?",
                "תספר לי על אקמול",
                "האם יש לכם אקמול במלאי?",
                "Does Acamol require a prescription?"
            ],
            inputs=msg
        )
    
    logger.info("Gradio interface created successfully with tool call display")
    return app


# Create the chat interface at module level
# This follows the module-level caching pattern from agentic-logic-and-tools
# The interface is created once and reused, reducing initialization overhead
# #region agent log
_debug_log("app/main.py:536", "Starting Gradio app creation", {"agent_is_none": agent is None}, "H3")
# #endregion
try:
    app = create_chat_interface()
    logger.info("Main application: Gradio ChatInterface created and ready")
    # #region agent log
    _debug_log("app/main.py:538", "Gradio app created successfully", {"app_is_none": app is None}, "H3")
    # #endregion
except Exception as e:
    logger.error(f"Main application: Failed to create ChatInterface: {str(e)}", exc_info=True)
    app = None
    # #region agent log
    _debug_log("app/main.py:541", "Gradio app creation failed", {"error": str(e), "error_type": type(e).__name__}, "H3")
    # #endregion


def main() -> None:
    """
    Main entry point for launching the Pharmacy AI Assistant application.
    
    Purpose (Why):
    Launches the Gradio web interface for the Pharmacy AI Assistant, making
    it accessible to users via web browser. This function serves as the
    application entry point when running the module directly. Configures
    the server to listen on all interfaces (0.0.0.0) for Docker compatibility
    and sets the port to 7860 as specified in the project requirements.
    
    Implementation (What):
    Checks if the app was created successfully, then launches it with
    server_name="0.0.0.0" (for Docker compatibility) and server_port=7860.
    If app creation failed, logs an error and exits. The function blocks
    until the server is stopped.
    
    Returns:
        None. The function blocks until the server is stopped.
    
    Raises:
        None. All errors are logged and handled gracefully.
    
    Example:
        >>> if __name__ == "__main__":
        ...     main()
    """
    # #region agent log
    _debug_log("app/main.py:571", "main() function called", {}, "H1")
    # #endregion
    if app is None:
        logger.error("Cannot launch application: ChatInterface was not created")
        # #region agent log
        _debug_log("app/main.py:573", "App is None, cannot launch", {}, "H1")
        # #endregion
        return
    
    logger.info("Launching Pharmacy AI Assistant application")
    logger.info("Server will be available at http://0.0.0.0:7860")
    # #region agent log
    _debug_log("app/main.py:578", "About to call app.launch()", {"server_name": "0.0.0.0", "server_port": 7860}, "H1")
    # #endregion
    
    try:
        # #region agent log
        _debug_log("app/main.py:625", "Calling app.launch() - this is a blocking call", {"server_name": "0.0.0.0", "server_port": 7860}, "H1")
        # #endregion
        result = app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )
        # #region agent log
        _debug_log("app/main.py:631", "app.launch() returned (should not happen - blocking call)", {"result": str(result)}, "H1")
        # #endregion
    except Exception as e:
        # #region agent log
        _debug_log("app/main.py:582", "app.launch() failed", {"error": str(e), "error_type": type(e).__name__}, "H4")
        # #endregion
        logger.error(f"Failed to launch app: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # #region agent log
    _debug_log("app/main.py:585", "__main__ block executed, calling main()", {}, "H1")
    # #endregion
    main()


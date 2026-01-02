"""
Agent Wrapper for Performance Testing.

Purpose (Why):
Provides TracedStreamingAgent class that wraps StreamingAgent to capture
all interactions including API calls, chunks, tool executions, and thinking/reasoning
for performance testing and analysis.

Implementation (What):
Extends StreamingAgent functionality by intercepting stream_response calls,
capturing all data during execution, and storing it in a structured trace format.
Supports seed and temperature parameters for reproducible testing.
"""

import json
import time
import logging
import sys
from typing import List, Dict, Any, Optional, Generator
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.agent.streaming import StreamingAgent
from app.tools.registry import execute_tool
from app.security.correlation import generate_correlation_id

# Configure module-level logger
logger = logging.getLogger(__name__)


class TracedStreamingAgent:
    """
    Wrapper for StreamingAgent that captures all interactions for testing.
    
    Purpose (Why):
    This class wraps StreamingAgent to capture comprehensive trace data including
    all API calls, response chunks, tool executions, thinking/reasoning, and timing
    information. This enables reproducible performance testing and detailed analysis
    of agent behavior.
    
    Implementation (What):
    Extends StreamingAgent by overriding stream_response to intercept and capture
    all data. Maintains a trace structure that records every API call, chunk, tool
    execution, and timing information. Supports seed and temperature parameters
    for reproducible testing.
    
    Attributes:
        agent: Underlying StreamingAgent instance
        seed: Seed value for reproducible API calls (None if not set)
        temperature: Temperature value for API calls (None if not set)
        trace: Current trace data structure
    """
    
    def __init__(
        self,
        model: str = "gpt-5",
        seed: Optional[int] = None,
        temperature: Optional[float] = None
    ):
        """
        Initialize TracedStreamingAgent.
        
        Purpose (Why):
        Creates a wrapped StreamingAgent instance with optional seed and temperature
        parameters for reproducible testing.
        
        Implementation (What):
        Initializes underlying StreamingAgent and stores seed/temperature parameters
        for use in API calls.
        
        Args:
            model: OpenAI model name to use (default: "gpt-5")
            seed: Optional seed value for reproducible responses
            temperature: Optional temperature value (0 for deterministic)
        """
        self.agent = StreamingAgent(model=model)
        self.seed = seed
        self.temperature = temperature
        self.trace = {
            "iterations": [],
            "start_time": None,
            "end_time": None,
            "correlation_id": None
        }
        
        logger.info(f"TracedStreamingAgent initialized with model: {model}, seed: {seed}, temperature: {temperature}")
    
    def stream_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Generator[str, None, None]:
        """
        Stream agent response while capturing all trace data.
        
        Purpose (Why):
        Intercepts stream_response calls to capture all interactions including
        API calls, chunks, tool executions, and thinking/reasoning for analysis.
        
        Implementation (What):
        Overrides stream_response to intercept API calls, add seed/temperature
        parameters, capture all chunks and tool calls, and store everything in
        trace structure. Yields chunks normally while capturing data in background.
        
        Args:
            user_message: The user's message to process
            conversation_history: Optional conversation history
            
        Yields:
            String chunks containing parts of the agent's response
        """
        # Generate correlation ID for this request
        correlation_id = generate_correlation_id()
        
        self.trace = {
            "iterations": [],
            "start_time": time.time(),
            "end_time": None,
            "correlation_id": correlation_id
        }
        
        logger.debug(f"Generated correlation ID for test: {correlation_id}")
        
        if not user_message or not user_message.strip():
            logger.warning("Empty user message received")
            yield "I'm here to help! Please ask me about medications, stock availability, or prescription requirements."
            self.trace["end_time"] = time.time()
            return
        
        messages = self.agent._build_messages(user_message, conversation_history)
        max_iterations = 10
        iteration = 0
        all_chunks = []  # Collect all chunks for final response
        
        logger.info("Processing user message with tracing")
        logger.debug(f"Message: {user_message[:100]}...")
        
        while iteration < max_iterations:
            iteration += 1
            iteration_start_time = time.time()
            logger.debug(f"OpenAI API streaming call iteration: {iteration}")
            
            iteration_data = {
                "iteration": iteration,
                "api_call": {
                    "messages": messages.copy(),  # Store messages sent
                    "parameters": {},  # Will be updated after building api_params
                    "chunks": [],
                    "accumulated_content": "",
                    "tool_calls_collected": [],
                    "final_finish_reason": None
                },
                "tool_executions": [],
                "iteration_time": 0.0
            }
            
            try:
                # Prepare API call parameters
                api_params = {
                    "model": self.agent.model,
                    "messages": messages,
                    "tools": self.agent.tools,
                    "tool_choice": "auto",
                    "stream": True
                }
                
                # Add seed if provided
                if self.seed is not None:
                    api_params["seed"] = self.seed
                
                # Add temperature if provided and not 0 (some models don't support temperature=0)
                # If temperature is 0, we don't send it (use model default)
                if self.temperature is not None and self.temperature != 0:
                    api_params["temperature"] = self.temperature
                
                # Update iteration_data with actual parameters sent to API
                # This ensures we only record parameters that were actually sent
                iteration_data["api_call"]["parameters"] = {
                    "model": api_params["model"],
                    "stream": api_params["stream"],
                    "tool_choice": api_params["tool_choice"]
                }
                if "seed" in api_params:
                    iteration_data["api_call"]["parameters"]["seed"] = api_params["seed"]
                if "temperature" in api_params:
                    iteration_data["api_call"]["parameters"]["temperature"] = api_params["temperature"]
                
                # #region agent log
                api_call_start_time = time.time()
                # #endregion
                
                # Call OpenAI API with streaming enabled
                stream = self.agent.client.chat.completions.create(**api_params)
                
                # #region agent log
                api_call_return_time = time.time()
                api_call_overhead = api_call_return_time - api_call_start_time
                with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"agent_wrapper.py:193","message":"API call overhead","data":{"iteration":iteration,"api_call_overhead":api_call_overhead,"messages_count":len(messages)},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                
                # Collect response chunks and tool calls
                accumulated_content = ""
                tool_calls_collected = []
                finish_reason = None
                chunks_in_iteration = []
                
                # #region agent log
                chunk_start_time = time.time()
                first_chunk_time = None
                last_chunk_time = None
                chunk_count = 0
                total_chunk_delay = 0.0
                # #endregion
                
                for chunk in stream:
                    # #region agent log
                    chunk_receive_time = time.time()
                    if first_chunk_time is None:
                        first_chunk_time = chunk_receive_time
                        time_to_first_chunk = first_chunk_time - chunk_start_time
                        with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"agent_wrapper.py:201","message":"Time to first chunk","data":{"iteration":iteration,"time_to_first_chunk":time_to_first_chunk,"user_message":user_message[:100]},"timestamp":int(time.time()*1000)}) + '\n')
                    if last_chunk_time is not None:
                        delay_between_chunks = chunk_receive_time - last_chunk_time
                        total_chunk_delay += delay_between_chunks
                    last_chunk_time = chunk_receive_time
                    chunk_count += 1
                    # #endregion
                    
                    delta = chunk.choices[0].delta
                    chunk_data = {
                        "content": None,
                        "finish_reason": None,
                        "thinking": None,
                        "reasoning": None
                    }
                    
                    # Check for finish reason
                    if chunk.choices[0].finish_reason:
                        finish_reason = chunk.choices[0].finish_reason
                        chunk_data["finish_reason"] = finish_reason
                    
                    # Handle text content
                    if delta.content:
                        accumulated_content += delta.content
                        chunk_data["content"] = delta.content
                        chunks_in_iteration.append(delta.content)
                        # Yield text chunk immediately for real-time display
                        yield delta.content
                    
                    # Capture thinking/reasoning if available
                    if hasattr(delta, 'thinking') and delta.thinking:
                        chunk_data["thinking"] = delta.thinking
                    if hasattr(delta, 'reasoning') and delta.reasoning:
                        chunk_data["reasoning"] = delta.reasoning
                    
                    # Handle tool calls (collect them as they arrive)
                    if delta.tool_calls:
                        try:
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
                            # tool_calls is not iterable (e.g., Mock object)
                            pass
                    
                    # Store chunk data if it has any content
                    if chunk_data["content"] or chunk_data["thinking"] or chunk_data["reasoning"] or chunk_data["finish_reason"]:
                        iteration_data["api_call"]["chunks"].append(chunk_data)
                
                # Store accumulated data
                iteration_data["api_call"]["accumulated_content"] = accumulated_content
                iteration_data["api_call"]["tool_calls_collected"] = tool_calls_collected
                iteration_data["api_call"]["final_finish_reason"] = finish_reason
                all_chunks.extend(chunks_in_iteration)
                
                # #region agent log
                stream_end_time = time.time()
                stream_duration = stream_end_time - chunk_start_time
                avg_chunk_delay = total_chunk_delay / max(chunk_count - 1, 1) if chunk_count > 1 else 0
                with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"agent_wrapper.py:262","message":"Stream timing analysis","data":{"iteration":iteration,"chunk_count":chunk_count,"stream_duration":stream_duration,"total_chunk_delay":total_chunk_delay,"avg_chunk_delay":avg_chunk_delay,"accumulated_content_length":len(accumulated_content)},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                
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
                    
                    # #region agent log
                    # Check if previous tool results already contain the information
                    previous_tool_results = []
                    for msg in messages:
                        if msg.get("role") == "tool":
                            previous_tool_results.append(msg.get("content", ""))
                    # Also check all previous iterations for tool results
                    all_previous_tool_names = []
                    for prev_iteration in self.trace.get("iterations", []):
                        for prev_tool in prev_iteration.get("tool_executions", []):
                            all_previous_tool_names.append(prev_tool.get("tool_name", ""))
                    with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"agent_wrapper.py:286","message":"Tool call decision analysis","data":{"iteration":iteration,"requested_tools":[tc.get("function",{}).get("name","") for tc in tool_calls_collected],"previous_tool_results_count":len(previous_tool_results),"all_previous_tool_names":all_previous_tool_names,"accumulated_content":accumulated_content[:200]},"timestamp":int(time.time()*1000)}) + '\n')
                    # #endregion
                    
                    # Execute tools and capture execution data
                    tool_messages = []
                    for tool_call in tool_calls_collected:
                        tool_exec_start = time.time()
                        tool_id = tool_call.get("id")
                        function = tool_call.get("function", {})
                        tool_name = function.get("name") if isinstance(function, dict) else getattr(function, "name", None)
                        arguments_str = function.get("arguments", "{}") if isinstance(function, dict) else getattr(function, "arguments", "{}")
                        
                        if not tool_name:
                            continue
                        
                        try:
                            # Parse arguments
                            arguments = json.loads(arguments_str)
                            
                            # #region agent log
                            # Check if information already exists from previous tool calls (check all previous iterations)
                            info_already_available = False
                            if tool_name == "check_prescription_requirement":
                                # Check if get_medication_by_name was already called in any previous iteration
                                for prev_iteration in self.trace.get("iterations", []):
                                    for prev_tool in prev_iteration.get("tool_executions", []):
                                        if prev_tool.get("tool_name") == "get_medication_by_name":
                                            result = prev_tool.get("result", {})
                                            if isinstance(result, dict) and "requires_prescription" in result:
                                                info_already_available = True
                                                with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                                                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"agent_wrapper.py:343","message":"Redundant tool call detected","data":{"tool_name":tool_name,"medication_id":arguments.get("medication_id",""),"requires_prescription_already_available":result.get("requires_prescription"),"found_in_iteration":prev_iteration.get("iteration"),"user_message":user_message[:100]},"timestamp":int(time.time()*1000)}) + '\n')
                                                break
                                    if info_already_available:
                                        break
                            elif tool_name == "check_stock_availability":
                                # Check if get_medication_by_name was already called in any previous iteration
                                for prev_iteration in self.trace.get("iterations", []):
                                    for prev_tool in prev_iteration.get("tool_executions", []):
                                        if prev_tool.get("tool_name") == "get_medication_by_name":
                                            result = prev_tool.get("result", {})
                                            if isinstance(result, dict) and "available" in result and "quantity_in_stock" in result:
                                                info_already_available = True
                                                with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                                                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"agent_wrapper.py:353","message":"Redundant tool call detected","data":{"tool_name":tool_name,"medication_id":arguments.get("medication_id",""),"stock_info_already_available":True,"found_in_iteration":prev_iteration.get("iteration"),"user_message":user_message[:100]},"timestamp":int(time.time()*1000)}) + '\n')
                                                break
                                    if info_already_available:
                                        break
                            # #endregion
                            
                            # Build context for audit logging
                            context = {
                                "test_trace": True,
                                "iteration": iteration,
                                "tool_call_id": tool_id
                            }
                            
                            # Execute the tool with correlation ID for audit logging
                            tool_result = execute_tool(
                                tool_name=tool_name,
                                arguments=arguments,
                                agent_id="test_agent",
                                correlation_id=correlation_id,
                                context=context
                            )
                            
                            tool_exec_time = time.time() - tool_exec_start
                            
                            # #region agent log
                            with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"agent_wrapper.py:320","message":"Tool execution completed","data":{"tool_name":tool_name,"execution_time":tool_exec_time,"iteration":iteration,"info_already_available":info_already_available},"timestamp":int(time.time()*1000)}) + '\n')
                            # #endregion
                            
                            # Store tool execution data
                            iteration_data["tool_executions"].append({
                                "tool_name": tool_name,
                                "arguments": arguments,
                                "result": tool_result,
                                "execution_time": tool_exec_time,
                                "tool_call_id": tool_id,
                                "correlation_id": correlation_id
                            })
                            
                            # Format result as JSON string for OpenAI
                            result_str = json.dumps(tool_result, ensure_ascii=False)
                            
                            # Create tool message response
                            tool_message = {
                                "role": "tool",
                                "content": result_str,
                                "tool_call_id": tool_id
                            }
                            tool_messages.append(tool_message)
                            
                            logger.debug(f"Tool {tool_name} executed successfully in {tool_exec_time:.3f}s")
                            
                        except Exception as e:
                            error_msg = f"Error executing tool {tool_name}: {str(e)}"
                            logger.error(error_msg, exc_info=True)
                            
                            tool_exec_time = time.time() - tool_exec_start
                            iteration_data["tool_executions"].append({
                                "tool_name": tool_name,
                                "arguments": json.loads(arguments_str) if arguments_str else {},
                                "result": {"error": error_msg, "success": False},
                                "execution_time": tool_exec_time,
                                "tool_call_id": tool_id,
                                "correlation_id": correlation_id
                            })
                            
                            # Send error back to model
                            error_result = {"error": error_msg, "success": False}
                            tool_message = {
                                "role": "tool",
                                "content": json.dumps(error_result, ensure_ascii=False),
                                "tool_call_id": tool_id
                            }
                            tool_messages.append(tool_message)
                    
                    messages.extend(tool_messages)
                    iteration_data["iteration_time"] = time.time() - iteration_start_time
                    
                    # #region agent log
                    with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"agent_wrapper.py:369","message":"Iteration completed with tool calls","data":{"iteration":iteration,"iteration_time":iteration_data["iteration_time"],"stream_duration":stream_duration,"tool_count":len(tool_calls_collected)},"timestamp":int(time.time()*1000)}) + '\n')
                    # #endregion
                    
                    self.trace["iterations"].append(iteration_data)
                    # Continue loop to get model's response to tool results
                    continue
                
                # No tool calls - we have final response
                if finish_reason == "stop":
                    if accumulated_content:
                        iteration_data["iteration_time"] = time.time() - iteration_start_time
                        
                        # #region agent log
                        with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"agent_wrapper.py:375","message":"Final response iteration completed","data":{"iteration":iteration,"iteration_time":iteration_data["iteration_time"],"stream_duration":stream_duration,"response_length":len(accumulated_content),"chunk_count":chunk_count},"timestamp":int(time.time()*1000)}) + '\n')
                        # #endregion
                        
                        self.trace["iterations"].append(iteration_data)
                        self.trace["end_time"] = time.time()
                        logger.info("Streaming completed with final response")
                        return
                    elif not tool_calls_collected:
                        iteration_data["iteration_time"] = time.time() - iteration_start_time
                        self.trace["iterations"].append(iteration_data)
                        self.trace["end_time"] = time.time()
                        logger.warning("Stream completed with no content and no tool calls")
                        yield "I apologize, but I encountered an issue processing your request. Please try again or rephrase your question."
                        return
                    else:
                        iteration_data["iteration_time"] = time.time() - iteration_start_time
                        self.trace["iterations"].append(iteration_data)
                        self.trace["end_time"] = time.time()
                        logger.info("Streaming completed with final response")
                        return
                elif not tool_calls_collected and accumulated_content:
                    iteration_data["iteration_time"] = time.time() - iteration_start_time
                    self.trace["iterations"].append(iteration_data)
                    self.trace["end_time"] = time.time()
                    logger.info("Streaming completed with final response")
                    return
                
                # If we reach here and no content was yielded, something unexpected happened
                if not accumulated_content and not tool_calls_collected:
                    iteration_data["iteration_time"] = time.time() - iteration_start_time
                    self.trace["iterations"].append(iteration_data)
                    self.trace["end_time"] = time.time()
                    logger.warning("Stream completed with no content and no tool calls")
                    yield "I apologize, but I encountered an issue processing your request. Please try again or rephrase your question."
                    return
                
            except Exception as e:
                error_msg = f"Error in OpenAI API streaming call: {str(e)}"
                logger.error(error_msg, exc_info=True)
                iteration_data["iteration_time"] = time.time() - iteration_start_time
                iteration_data["api_call"]["error"] = error_msg
                self.trace["iterations"].append(iteration_data)
                self.trace["end_time"] = time.time()
                yield f"I apologize, but I encountered an error: {error_msg}. Please try again."
                return
        
        # If we exit loop, we hit max iterations
        self.trace["end_time"] = time.time()
        logger.warning(f"Reached max iterations ({max_iterations}) in streaming tool calling loop")
        yield "I apologize, but I encountered an issue processing your request. Please try again or rephrase your question."
    
    def get_trace(self) -> Dict[str, Any]:
        """
        Get the captured trace data.
        
        Purpose (Why):
        Returns the complete trace data structure containing all captured
        interactions for analysis and reporting.
        
        Implementation (What):
        Returns the trace dictionary with all iterations, API calls, tool
        executions, and timing information.
        
        Returns:
            Dictionary containing complete trace data
        """
        return self.trace.copy()


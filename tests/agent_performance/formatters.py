"""
Formatters for Agent Performance Test Results.

Purpose (Why):
Provides formatting functions to convert test result data into human-readable
and machine-readable formats (Markdown and JSON) for analysis and review.

Implementation (What):
Formats test results into structured JSON with proper indentation and readable
Markdown with sections for input, processing details, output, and statistics.
"""

import json
from datetime import datetime
from typing import Dict, Any


def format_json(result_data: Dict[str, Any]) -> str:
    """
    Format test result data as pretty JSON.
    
    Purpose (Why):
    Converts test result dictionary into formatted JSON string for storage
    and machine processing.
    
    Implementation (What):
    Serializes dictionary to JSON with indentation, ensures Unicode characters
    are preserved (ensure_ascii=False), and sorts keys for consistency.
    
    Args:
        result_data: Complete test result data dictionary
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(
        result_data,
        indent=2,
        ensure_ascii=False,
        sort_keys=False  # Keep original order
    )


def format_markdown(result_data: Dict[str, Any]) -> str:
    """
    Format test result data as readable Markdown.
    
    Purpose (Why):
    Converts test result dictionary into human-readable Markdown format
    for easy review and analysis of agent performance.
    
    Implementation (What):
    Creates structured Markdown with sections for test metadata, input,
    detailed processing information (iterations, API calls, chunks, tool calls),
    output, and statistics.
    
    Args:
        result_data: Complete test result data dictionary
        
    Returns:
        Formatted Markdown string
    """
    lines = []
    
    # Header
    test_name = result_data.get("test_name", "Unknown Test")
    timestamp = result_data.get("timestamp", "")
    agent_type = result_data.get("agent_type", "streaming")
    
    # Parse timestamp for display
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        display_time = timestamp
    
    lines.append(f"# Test: {test_name}")
    lines.append(f"**Date:** {display_time}  ")
    lines.append(f"**Agent Type:** {agent_type}")
    
    # Add correlation ID if available
    correlation_id = result_data.get("correlation_id")
    if correlation_id:
        lines.append(f"**Correlation ID:** `{correlation_id}`")
    
    lines.append("")
    
    # Input Section
    input_data = result_data.get("input", {})
    lines.append("## Input")
    lines.append(f"- **User Message:** \"{input_data.get('user_message', '')}\"")
    
    params = input_data.get("parameters", {})
    lines.append(f"- **Model:** {params.get('model', 'N/A')}")
    if params.get("seed") is not None:
        lines.append(f"- **Seed:** {params.get('seed')}")
    if params.get("temperature") is not None:
        lines.append(f"- **Temperature:** {params.get('temperature')}")
    
    if input_data.get("conversation_history"):
        lines.append(f"- **Conversation History:** {len(input_data['conversation_history'])} messages")
    else:
        lines.append("- **Conversation History:** None")
    
    lines.append("")
    
    # Processing Section
    processing = result_data.get("processing", {})
    iterations = processing.get("iterations", [])
    
    lines.append("## Processing")
    lines.append("")
    
    for iter_data in iterations:
        iteration_num = iter_data.get("iteration", 0)
        lines.append(f"### Iteration {iteration_num}")
        lines.append("")
        
        # API Call Information
        api_call = iter_data.get("api_call", {})
        lines.append(f"**API Call #{iteration_num}**")
        
        # Messages sent
        messages = api_call.get("messages", [])
        if messages:
            lines.append("- **Messages Sent:**")
            for msg in messages[:3]:  # Show first 3 messages
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if role == "system":
                    content_preview = content[:50] + "..." if len(content) > 50 else content
                    lines.append(f"  - System: {content_preview}")
                elif role == "user":
                    lines.append(f"  - User: \"{content}\"")
                elif role == "assistant":
                    content_preview = content[:50] + "..." if len(content) > 50 else content
                    lines.append(f"  - Assistant: {content_preview}")
            if len(messages) > 3:
                lines.append(f"  - ... and {len(messages) - 3} more messages")
        
        # Parameters
        api_params = api_call.get("parameters", {})
        lines.append("- **Parameters:**")
        lines.append(f"  - Model: {api_params.get('model', 'N/A')}")
        if api_params.get("seed") is not None:
            lines.append(f"  - Seed: {api_params.get('seed')}")
        if api_params.get("temperature") is not None:
            lines.append(f"  - Temperature: {api_params.get('temperature')}")
        lines.append(f"  - Stream: {api_params.get('stream', False)}")
        
        # Stream Chunks
        chunks = api_call.get("chunks", [])
        if chunks:
            lines.append("- **Stream Chunks:**")
            for i, chunk in enumerate(chunks[:10], 1):  # Show first 10 chunks
                content = chunk.get("content", "")
                finish_reason = chunk.get("finish_reason")
                thinking = chunk.get("thinking") or chunk.get("reasoning")
                
                chunk_info = f"  - Chunk {i}:"
                if content:
                    content_preview = content[:30] + "..." if len(content) > 30 else content
                    chunk_info += f" Content: \"{content_preview}\""
                if thinking:
                    thinking_preview = thinking[:30] + "..." if len(thinking) > 30 else thinking
                    chunk_info += f", Thinking: \"{thinking_preview}\""
                if finish_reason:
                    chunk_info += f", Finish Reason: `{finish_reason}`"
                
                lines.append(chunk_info)
            
            if len(chunks) > 10:
                lines.append(f"  - ... and {len(chunks) - 10} more chunks")
        
        # Model Response Summary
        accumulated = api_call.get("accumulated_content", "")
        tool_calls = api_call.get("tool_calls_collected", [])
        finish_reason = api_call.get("final_finish_reason")
        
        lines.append("- **Model Response:**")
        if accumulated:
            acc_preview = accumulated[:100] + "..." if len(accumulated) > 100 else accumulated
            lines.append(f"  - Accumulated Content: \"{acc_preview}\"")
        if tool_calls:
            lines.append(f"  - Tool Calls: {len(tool_calls)}")
            for tc in tool_calls[:3]:  # Show first 3 tool calls
                func = tc.get("function", {})
                tool_name = func.get("name", "unknown")
                tool_id = tc.get("id", "unknown")
                args = func.get("arguments", "{}")
                args_preview = args[:50] + "..." if len(args) > 50 else args
                lines.append(f"    - Tool: `{tool_name}`")
                lines.append(f"      - ID: `{tool_id}`")
                lines.append(f"      - Arguments: `{args_preview}`")
            if len(tool_calls) > 3:
                lines.append(f"    - ... and {len(tool_calls) - 3} more tool calls")
        if finish_reason:
            lines.append(f"  - Finish Reason: `{finish_reason}`")
        
        lines.append("")
        
        # Tool Executions
        tool_executions = iter_data.get("tool_executions", [])
        if tool_executions:
            for i, tool_exec in enumerate(tool_executions, 1):
                lines.append(f"**Tool Execution #{i}**")
                tool_name = tool_exec.get("tool_name", "unknown")
                arguments = tool_exec.get("arguments", {})
                result = tool_exec.get("result", {})
                exec_time = tool_exec.get("execution_time", 0)
                tool_correlation_id = tool_exec.get("correlation_id")
                
                lines.append(f"- Tool: `{tool_name}`")
                lines.append(f"- Arguments: `{json.dumps(arguments, ensure_ascii=False)}`")
                
                # Result preview
                result_str = json.dumps(result, ensure_ascii=False)
                result_preview = result_str[:100] + "..." if len(result_str) > 100 else result_str
                lines.append(f"- Result: `{result_preview}`")
                lines.append(f"- Execution Time: {exec_time:.3f}s")
                if tool_correlation_id:
                    lines.append(f"- Correlation ID: `{tool_correlation_id}`")
                lines.append("")
        
        # Iteration time
        iter_time = iter_data.get("iteration_time", 0)
        if iter_time > 0:
            lines.append(f"*Iteration Time: {iter_time:.3f}s*")
            lines.append("")
    
    # Output Section
    output = result_data.get("output", {})
    final_response = output.get("final_response", "")
    all_chunks = output.get("all_chunks", [])
    
    lines.append("## Output")
    if final_response:
        # Truncate if too long
        response_preview = final_response[:500] + "..." if len(final_response) > 500 else final_response
        lines.append(f"**Final Response:** \"{response_preview}\"")
    else:
        lines.append("**Final Response:** (empty)")
    
    if all_chunks:
        lines.append("")
        lines.append(f"**All Chunks:** {len(all_chunks)} chunks")
        if len(all_chunks) <= 10:
            for i, chunk in enumerate(all_chunks, 1):
                chunk_preview = chunk[:50] + "..." if len(chunk) > 50 else chunk
                lines.append(f"- Chunk {i}: \"{chunk_preview}\"")
        else:
            for i, chunk in enumerate(all_chunks[:5], 1):
                chunk_preview = chunk[:50] + "..." if len(chunk) > 50 else chunk
                lines.append(f"- Chunk {i}: \"{chunk_preview}\"")
            lines.append(f"- ... and {len(all_chunks) - 5} more chunks")
    
    lines.append("")
    
    # Statistics Section
    stats = output.get("statistics", {})
    lines.append("## Statistics")
    lines.append(f"- Total API Calls: {stats.get('total_api_calls', 0)}")
    lines.append(f"- Total Tool Calls: {stats.get('total_tool_calls', 0)}")
    lines.append(f"- Total Chunks: {stats.get('total_chunks', 0)}")
    lines.append(f"- Total Time: {stats.get('total_time', 0):.3f}s")
    
    tools_used = stats.get("tools_used", [])
    if tools_used:
        lines.append(f"- Tools Used: {', '.join(tools_used)}")
    else:
        lines.append("- Tools Used: (none)")
    
    return "\n".join(lines)


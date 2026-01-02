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
import os
# #region agent log
# #endregion


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
            for msg in messages:  # Show all messages
                role = msg.get("role", "unknown")
                content = msg.get("content")  # Get content (may be None)
                if content is None:
                    content = ""  # Normalize None to empty string
                # #region agent log
                with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"formatters.py:129","message":"Processing message","data":{"role":role,"content_is_none_original":msg.get("content") is None,"content_type":type(content).__name__,"has_content_key":"content" in msg},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                # #endregion
                if role == "system":
                    # #region agent log
                    with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"formatters.py:134","message":"Before system content check","data":{"content_is_none":content is None,"content_length":len(content) if content else 0},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                    # #endregion
                    # Show only first line of system message content
                    first_line = content.split('\n')[0] if content else ""
                    lines.append(f"  - System: {first_line}")
                elif role == "user":
                    lines.append(f"  - User: \"{content}\"")
                elif role == "assistant":
                    # #region agent log
                    with open(r'c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"formatters.py:141","message":"Before assistant content check","data":{"content_is_none":content is None,"content_length":len(content) if content else 0},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                    # #endregion
                    # Show full assistant message content, including tool_calls if present
                    assistant_line = f"  - Assistant: {content}" if content else "  - Assistant: "
                    if msg.get("tool_calls"):
                        tool_calls_info = []
                        for tc in msg.get("tool_calls", []):
                            func = tc.get("function", {}) if isinstance(tc, dict) else getattr(tc, "function", {})
                            tool_name = func.get("name", "unknown") if isinstance(func, dict) else getattr(func, "name", "unknown")
                            tool_calls_info.append(tool_name)
                        assistant_line += f" [Tool Calls: {', '.join(tool_calls_info)}]"
                    lines.append(assistant_line)
                elif role == "tool":
                    tool_call_id = msg.get("tool_call_id", "unknown")
                    tool_result = msg.get("content", "")
                    tool_result_preview = tool_result[:200] + "..." if len(tool_result) > 200 else tool_result
                    lines.append(f"  - Tool (ID: {tool_call_id}): {tool_result_preview}")
        
        # Parameters
        api_params = api_call.get("parameters", {})
        lines.append("- **Parameters:**")
        lines.append(f"  - Model: {api_params.get('model', 'N/A')}")
        if api_params.get("seed") is not None:
            lines.append(f"  - Seed: {api_params.get('seed')}")
        if api_params.get("temperature") is not None:
            lines.append(f"  - Temperature: {api_params.get('temperature')}")
        lines.append(f"  - Stream: {api_params.get('stream', False)}")
        
        # Collect all reasoning/thinking from chunks before tool calls
        chunks = api_call.get("chunks", [])
        all_reasoning = []
        all_thinking = []
        
        if chunks:
            for chunk in chunks:
                thinking = chunk.get("thinking")
                reasoning = chunk.get("reasoning")
                if thinking:
                    all_thinking.append(thinking)
                if reasoning:
                    all_reasoning.append(reasoning)
        
        # Show reasoning/thinking if available (before tool calls)
        if all_reasoning or all_thinking:
            lines.append("- **Reasoning/Thinking:**")
            if all_reasoning:
                # Combine all reasoning chunks
                full_reasoning = " ".join(all_reasoning)
                lines.append(f"  - Reasoning: {full_reasoning}")
            if all_thinking:
                # Combine all thinking chunks
                full_thinking = " ".join(all_thinking)
                lines.append(f"  - Thinking: {full_thinking}")
        
        # Stream Chunks (simplified - just show count and key info)
        if chunks:
            lines.append("- **Stream Chunks:**")
            chunks_with_content = sum(1 for c in chunks if c.get("content"))
            chunks_with_reasoning = sum(1 for c in chunks if c.get("reasoning") or c.get("thinking"))
            lines.append(f"  - Total Chunks: {len(chunks)}")
            if chunks_with_content > 0:
                lines.append(f"  - Chunks with Content: {chunks_with_content}")
            if chunks_with_reasoning > 0:
                lines.append(f"  - Chunks with Reasoning/Thinking: {chunks_with_reasoning}")
        
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
    
    lines.append("")
    
    # Evaluation Section
    evaluation = result_data.get("evaluation", {})
    if evaluation:
        lines.append("## Evaluation")
        lines.append("")
        
        # Token Usage
        token_usage = evaluation.get("token_usage", {})
        if token_usage:
            lines.append("### Token Usage")
            lines.append(f"- Total Input Tokens: {token_usage.get('total_input_tokens', 0):,}")
            lines.append(f"- Total Output Tokens: {token_usage.get('total_output_tokens', 0):,}")
            lines.append(f"- Total Tokens: {token_usage.get('total_tokens', 0):,}")
            lines.append(f"- Average Input Tokens per Call: {token_usage.get('average_input_tokens_per_call', 0):.1f}")
            lines.append(f"- Average Output Tokens per Call: {token_usage.get('average_output_tokens_per_call', 0):.1f}")
            lines.append(f"- System Prompt Tokens: {token_usage.get('system_prompt_tokens', 0):,}")
            lines.append("")
        
        # Cost Estimation
        cost_estimation = evaluation.get("cost_estimation", {})
        if cost_estimation:
            lines.append("### Cost Estimation")
            lines.append(f"- Total Estimated Cost: ${cost_estimation.get('total_cost_usd', 0):.6f}")
            lines.append(f"- Input Cost: ${cost_estimation.get('input_cost_usd', 0):.6f}")
            lines.append(f"- Output Cost: ${cost_estimation.get('output_cost_usd', 0):.6f}")
            lines.append(f"- Model: {cost_estimation.get('model', 'N/A')}")
            lines.append("")
        
        # Duplicate Calls
        dup_api = evaluation.get("duplicate_api_calls", [])
        dup_tools = evaluation.get("duplicate_tool_calls", [])
        redundant_info = evaluation.get("redundant_information", [])
        
        if dup_api or dup_tools or redundant_info:
            lines.append("### Duplicate & Redundant Calls")
            
            if dup_api:
                lines.append(f"- **Duplicate API Calls:** {len(dup_api)}")
                for dup in dup_api[:3]:
                    iterations_str = ", ".join(map(str, dup.get("iterations", [])))
                    lines.append(f"  - Pattern appears {dup.get('occurrences', 0)} times in iterations: {iterations_str}")
            
            if dup_tools:
                lines.append(f"- **Duplicate Tool Calls:** {len(dup_tools)}")
                for dup in dup_tools[:3]:
                    tool_name = dup.get("tool_name", "unknown")
                    iterations_str = ", ".join(map(str, dup.get("iterations", [])))
                    redundant = " (redundant)" if dup.get("is_redundant") else ""
                    lines.append(f"  - `{tool_name}` called {dup.get('occurrences', 0)} times{redundant} in iterations: {iterations_str}")
            
            if redundant_info:
                lines.append(f"- **Redundant Information Cases:** {len(redundant_info)}")
                for case in redundant_info[:3]:
                    tool_name = case.get("tool_name", "unknown")
                    iteration = case.get("iteration", 0)
                    severity = case.get("severity", "unknown")
                    lines.append(f"  - `{tool_name}` in iteration {iteration} ({severity} severity)")
            
            lines.append("")
        
        # Efficiency Analysis
        efficiency_analysis = evaluation.get("efficiency_analysis", {})
        if efficiency_analysis:
            issues = efficiency_analysis.get("issues", [])
            if issues:
                lines.append("### Efficiency Issues")
                for issue in issues[:5]:
                    issue_type = issue.get("type", "unknown")
                    severity = issue.get("severity", "unknown")
                    description = issue.get("description", "")
                    lines.append(f"- **{issue_type}** ({severity}): {description}")
                if len(issues) > 5:
                    lines.append(f"- ... and {len(issues) - 5} more issues")
                lines.append("")
        
        # Efficiency Score
        efficiency_score = evaluation.get("efficiency_score", 0)
        lines.append(f"### Efficiency Score: **{efficiency_score}/100**")
        
        if efficiency_score >= 80:
            lines.append("  - Status: Excellent")
        elif efficiency_score >= 60:
            lines.append("  - Status: Good")
        elif efficiency_score >= 40:
            lines.append("  - Status: Fair")
        else:
            lines.append("  - Status: Needs Improvement")
        
        lines.append("")
        
        # Recommendations
        recommendations = evaluation.get("recommendations", [])
        if recommendations:
            lines.append("### Recommendations")
            for rec in recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        # Summary
        summary = evaluation.get("summary", {})
        if summary:
            lines.append("### Summary")
            lines.append(f"- Total Duplicate API Calls: {summary.get('total_duplicate_api_calls', 0)}")
            lines.append(f"- Total Duplicate Tool Calls: {summary.get('total_duplicate_tool_calls', 0)}")
            lines.append(f"- Total Redundant Information Cases: {summary.get('total_redundant_information_cases', 0)}")
            lines.append(f"- Total Inefficiency Issues: {summary.get('total_inefficiency_issues', 0)}")
            lines.append(f"- Estimated Cost: ${summary.get('estimated_cost_usd', 0):.6f}")
            lines.append(f"- Total Tokens: {summary.get('total_tokens', 0):,}")
            lines.append(f"- Efficiency Score: {summary.get('efficiency_score', 0)}/100")
            lines.append("")
    
    return "\n".join(lines)


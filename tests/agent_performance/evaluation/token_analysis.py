"""
Token Analysis for Agent Performance Testing.

Purpose (Why):
Provides token counting and analysis capabilities to track token usage across
API calls, enabling cost estimation and efficiency analysis.

Implementation (What):
Uses tiktoken library for accurate token counting, supports multiple models,
and calculates detailed token usage statistics per API call and overall.
"""

import logging
from typing import Dict, Any, Optional

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available, using fallback token estimation")

# Configure module-level logger
logger = logging.getLogger(__name__)


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text using tiktoken.
    
    Purpose (Why):
    Provides accurate token counting for cost estimation and analysis.
    Uses tiktoken for precise counting based on model encoding.
    
    Implementation (What):
    Attempts to use tiktoken for accurate counting. Falls back to rough
    estimation (1 token ≈ 4 characters) if tiktoken is not available.
    
    Args:
        text: Text to count tokens for
        model: Model name to use for encoding (default: "gpt-4")
        
    Returns:
        Number of tokens in the text
    """
    if not text:
        return 0
    
    if TIKTOKEN_AVAILABLE:
        try:
            # Map model names to tiktoken encodings
            encoding_map = {
                "gpt-4": "cl100k_base",
                "gpt-4-turbo": "cl100k_base",
                "gpt-3.5-turbo": "cl100k_base",
                "gpt-5": "cl100k_base",  # Assuming same encoding
            }
            
            encoding_name = encoding_map.get(model, "cl100k_base")
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Error using tiktoken, falling back to estimation: {e}")
    
    # Fallback: rough estimation (1 token ≈ 4 characters)
    return len(text) // 4


def analyze_token_usage(result_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze token usage across all API calls.
    
    Purpose (Why):
    Calculates comprehensive token usage statistics to understand cost
    and efficiency of agent interactions.
    
    Implementation (What):
    Iterates through all iterations, counts tokens for system prompts,
    messages, and output content. Calculates totals and averages.
    
    Args:
        result_data: Complete test result data dictionary
        
    Returns:
        Dictionary with token usage statistics including:
        - total_input_tokens: Sum of all input tokens
        - total_output_tokens: Sum of all output tokens
        - total_tokens: Total tokens used
        - average_input_tokens_per_call: Average input tokens per API call
        - average_output_tokens_per_call: Average output tokens per API call
        - system_prompt_tokens: Tokens in system prompt (first iteration)
        - message_tokens: Tokens in user/assistant/tool messages
        - per_iteration_breakdown: Token breakdown per iteration
    """
    iterations = result_data.get("processing", {}).get("iterations", [])
    model = result_data.get("input", {}).get("parameters", {}).get("model", "gpt-4")
    
    if not iterations:
        return {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "average_input_tokens_per_call": 0,
            "average_output_tokens_per_call": 0,
            "system_prompt_tokens": 0,
            "message_tokens": 0,
            "per_iteration_breakdown": []
        }
    
    total_input_tokens = 0
    total_output_tokens = 0
    system_prompt_tokens = 0
    per_iteration = []
    
    # Get system prompt from first iteration
    first_iter = iterations[0]
    first_messages = first_iter.get("api_call", {}).get("messages", [])
    system_msg = next((m for m in first_messages if m.get("role") == "system"), None)
    if system_msg:
        system_content = system_msg.get("content", "") or ""
        system_prompt_tokens = count_tokens(system_content, model)
    
    # Analyze each iteration
    for iter_data in iterations:
        api_call = iter_data.get("api_call", {})
        messages = api_call.get("messages", [])
        
        # Count input tokens for this iteration
        iteration_input_tokens = 0
        
        # Count system prompt (only once, but included in first iteration)
        if iter_data.get("iteration") == 1:
            iteration_input_tokens += system_prompt_tokens
        
        # Count message tokens
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "") or ""
            
            if role == "system" and iter_data.get("iteration") == 1:
                # Already counted above
                continue
            elif role in ["user", "assistant", "tool"]:
                msg_tokens = count_tokens(content, model)
                iteration_input_tokens += msg_tokens
        
        # Count output tokens
        accumulated = api_call.get("accumulated_content", "") or ""
        iteration_output_tokens = count_tokens(accumulated, model)
        
        total_input_tokens += iteration_input_tokens
        total_output_tokens += iteration_output_tokens
        
        per_iteration.append({
            "iteration": iter_data.get("iteration", 0),
            "input_tokens": iteration_input_tokens,
            "output_tokens": iteration_output_tokens,
            "total_tokens": iteration_input_tokens + iteration_output_tokens
        })
    
    # Calculate message tokens (excluding system prompt)
    message_tokens = total_input_tokens - system_prompt_tokens
    
    # Calculate averages
    num_iterations = len(iterations)
    avg_input_tokens = total_input_tokens / num_iterations if num_iterations > 0 else 0
    avg_output_tokens = total_output_tokens / num_iterations if num_iterations > 0 else 0
    
    return {
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "average_input_tokens_per_call": round(avg_input_tokens, 2),
        "average_output_tokens_per_call": round(avg_output_tokens, 2),
        "system_prompt_tokens": system_prompt_tokens,
        "message_tokens": message_tokens,
        "per_iteration_breakdown": per_iteration
    }


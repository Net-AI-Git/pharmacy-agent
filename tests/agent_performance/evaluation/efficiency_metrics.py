"""
Efficiency Metrics for Agent Performance Testing.

Purpose (Why):
Provides efficiency analysis and scoring to identify optimization opportunities
and measure overall agent performance efficiency.

Implementation (What):
Analyzes various efficiency factors including system prompt size, conversation
history, repeated messages, and calculates an overall efficiency score.
"""

import hashlib
import logging
from typing import Dict, Any, List

from tests.agent_performance.evaluation.token_analysis import count_tokens

# Configure module-level logger
logger = logging.getLogger(__name__)


def analyze_efficiency(result_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze efficiency of agent usage.
    
    Purpose (Why):
    Identifies inefficiency patterns and provides recommendations for
    optimization to reduce costs and improve performance.
    
    Implementation (What):
    Checks system prompt size, conversation history length, repeated messages,
    and other efficiency factors.
    
    Args:
        result_data: Complete test result data dictionary
        
    Returns:
        Dictionary with efficiency analysis:
        - issues: List of efficiency issues found
        - recommendations: List of optimization recommendations
        - total_issues: Total number of issues
    """
    iterations = result_data.get("processing", {}).get("iterations", [])
    input_data = result_data.get("input", {})
    issues = []
    recommendations = []
    
    if not iterations:
        return {
            "issues": [],
            "recommendations": [],
            "total_issues": 0
        }
    
    # Check system prompt size
    first_iter = iterations[0]
    messages = first_iter.get("api_call", {}).get("messages", [])
    system_msg = next((m for m in messages if m.get("role") == "system"), None)
    
    if system_msg:
        system_content = system_msg.get("content", "") or ""
        model = result_data.get("input", {}).get("parameters", {}).get("model", "gpt-4")
        system_tokens = count_tokens(system_content, model)
        
        if system_tokens > 2500:
            issues.append({
                "type": "large_system_prompt",
                "tokens": system_tokens,
                "severity": "critical",
                "description": f"System prompt is {system_tokens} tokens"
            })
            recommendations.append(
                f"System prompt is {system_tokens} tokens. Consider reducing to <2000 tokens "
                "to improve efficiency and reduce costs."
            )
        elif system_tokens > 2000:
            issues.append({
                "type": "large_system_prompt",
                "tokens": system_tokens,
                "severity": "high",
                "description": f"System prompt is {system_tokens} tokens"
            })
            recommendations.append(
                f"System prompt is {system_tokens} tokens. Consider reducing to <2000 tokens "
                "to improve efficiency and reduce costs."
            )
        elif system_tokens > 1500:
            issues.append({
                "type": "large_system_prompt",
                "tokens": system_tokens,
                "severity": "medium",
                "description": f"System prompt is {system_tokens} tokens"
            })
    
    # Check for repeated messages
    message_hashes = []
    for iter_data in iterations:
        api_call = iter_data.get("api_call", {})
        messages = api_call.get("messages", [])
        
        for msg in messages:
            role = msg.get("role", "")
            if role in ["user", "assistant"]:
                content = msg.get("content", "") or ""
                if content:
                    msg_hash = hashlib.md5(content.encode()).hexdigest()
                    if msg_hash in message_hashes:
                        issues.append({
                            "type": "repeated_message",
                            "content_preview": content[:100],
                            "severity": "low",
                            "description": "Message content repeated across iterations"
                        })
                    message_hashes.append(msg_hash)
    
    # Check conversation history length
    conv_history = input_data.get("conversation_history", [])
    if conv_history and len(conv_history) > 10:
        issues.append({
            "type": "long_conversation_history",
            "message_count": len(conv_history),
            "severity": "medium",
            "description": f"Conversation history has {len(conv_history)} messages"
        })
        recommendations.append(
            f"Conversation history has {len(conv_history)} messages. "
            "Consider summarizing or truncating old messages to reduce token usage."
        )
    
    # Check for excessive iterations
    if len(iterations) > 5:
        issues.append({
            "type": "excessive_iterations",
            "iteration_count": len(iterations),
            "severity": "medium",
            "description": f"Test required {len(iterations)} iterations"
        })
        recommendations.append(
            f"Test required {len(iterations)} iterations. Consider optimizing "
            "tool usage or system prompt to reduce iteration count."
        )
    
    return {
        "issues": issues,
        "recommendations": recommendations,
        "total_issues": len(issues)
    }


def calculate_efficiency_score(
    result_data: Dict[str, Any],
    evaluation: Dict[str, Any]
) -> float:
    """
    Calculate overall efficiency score (0-100).
    
    Purpose (Why):
    Provides a single metric to quickly assess agent efficiency, making it
    easy to compare different runs and track improvements.
    
    Implementation (What):
    Starts at 100 and applies penalties for various inefficiency factors:
    - Duplicate API calls
    - Duplicate tool calls
    - Excessive token usage
    - Efficiency issues
    
    Args:
        result_data: Complete test result data dictionary
        evaluation: Complete evaluation dictionary with all metrics
        
    Returns:
        Efficiency score from 0 to 100 (higher is better)
    """
    score = 100.0
    
    # Penalize duplicate API calls
    duplicate_api = evaluation.get("duplicate_api_calls", [])
    for dup in duplicate_api:
        occurrences = dup.get("occurrences", 1)
        if occurrences > 1:
            # Penalty: 5 points per duplicate occurrence
            score -= min((occurrences - 1) * 5, 20)
    
    # Penalize duplicate tool calls
    duplicate_tools = evaluation.get("duplicate_tool_calls", [])
    for dup in duplicate_tools:
        occurrences = dup.get("occurrences", 1)
        is_redundant = dup.get("is_redundant", False)
        if occurrences > 1:
            # Higher penalty for redundant calls (same result)
            penalty = 8 if is_redundant else 5
            score -= min((occurrences - 1) * penalty, 15)
    
    # Penalize excessive token usage
    token_usage = evaluation.get("token_usage", {})
    total_tokens = token_usage.get("total_tokens", 0)
    
    if total_tokens > 20000:
        # Penalty for very high token usage
        excess = total_tokens - 20000
        score -= min(excess / 1000, 30)
    elif total_tokens > 10000:
        # Smaller penalty for moderate excess
        excess = total_tokens - 10000
        score -= min(excess / 2000, 20)
    
    # Penalize efficiency issues
    efficiency_analysis = evaluation.get("efficiency_analysis", {})
    issues = efficiency_analysis.get("issues", [])
    
    for issue in issues:
        severity = issue.get("severity", "low")
        if severity == "critical":
            score -= 25
        elif severity == "high":
            score -= 15
        elif severity == "medium":
            score -= 8
        else:  # low
            score -= 2
        
        # Additional penalty for large_system_prompt
        if issue.get("type") == "large_system_prompt":
            tokens = issue.get("tokens", 0)
            if tokens > 2500:
                score -= 10  # Additional penalty on top of critical
            elif tokens > 2000:
                score -= 5   # Additional penalty on top of high
    
    # Penalize if system prompt is too large relative to input
    system_prompt_tokens = token_usage.get("system_prompt_tokens", 0)
    total_input_tokens = token_usage.get("total_input_tokens", 0)
    if total_input_tokens > 0 and system_prompt_tokens > 0:
        system_prompt_ratio = system_prompt_tokens / total_input_tokens
        if system_prompt_ratio > 0.75:
            score -= 10  # System prompt too heavy relative to input
        elif system_prompt_ratio > 0.60:
            score -= 5
    
    # Bonus for efficient usage (low token count, few iterations)
    stats = result_data.get("output", {}).get("statistics", {})
    total_api_calls = stats.get("total_api_calls", 0)
    
    if total_api_calls <= 2 and total_tokens < 5000:
        score += 5  # Bonus for very efficient runs
    
    # Ensure score is within bounds
    return max(0.0, min(100.0, round(score, 1)))


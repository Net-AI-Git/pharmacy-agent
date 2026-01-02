"""
Cost Estimation for Agent Performance Testing.

Purpose (Why):
Provides cost estimation capabilities based on token usage, enabling
budget planning and cost optimization analysis.

Implementation (What):
Calculates estimated costs based on model-specific pricing for input
and output tokens. Supports multiple models with configurable pricing.
"""

from typing import Dict, Any


# Pricing as of 2024 (per 1K tokens)
# Update these values as pricing changes
MODEL_PRICING = {
    "gpt-4": {
        "input": 0.03,  # $0.03 per 1K input tokens
        "output": 0.06  # $0.06 per 1K output tokens
    },
    "gpt-4-turbo": {
        "input": 0.01,  # $0.01 per 1K input tokens
        "output": 0.03  # $0.03 per 1K output tokens
    },
    "gpt-3.5-turbo": {
        "input": 0.0015,  # $0.0015 per 1K input tokens
        "output": 0.002   # $0.002 per 1K output tokens
    },
    "gpt-5": {
        "input": 0.01,  # Estimated - update when available
        "output": 0.03  # Estimated - update when available
    }
}


def estimate_cost(input_tokens: int, output_tokens: int, model: str = "gpt-4") -> float:
    """
    Estimate cost in USD based on token usage.
    
    Purpose (Why):
    Calculates estimated cost for API calls to help with budget planning
    and cost optimization.
    
    Implementation (What):
    Uses model-specific pricing to calculate cost for input and output
    tokens separately, then sums them.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name to use for pricing
        
    Returns:
        Estimated cost in USD (rounded to 6 decimal places)
    """
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4"])
    
    input_cost = (input_tokens / 1000.0) * pricing["input"]
    output_cost = (output_tokens / 1000.0) * pricing["output"]
    
    total_cost = input_cost + output_cost
    return round(total_cost, 6)


def calculate_total_cost(result_data: Dict[str, Any], token_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate total cost for a test result.
    
    Purpose (Why):
    Provides comprehensive cost breakdown for the entire test run,
    including per-iteration costs.
    
    Implementation (What):
    Uses token analysis data to calculate costs per iteration and total.
    
    Args:
        result_data: Complete test result data dictionary
        token_analysis: Token analysis results from analyze_token_usage
        
    Returns:
        Dictionary with cost breakdown:
        - total_cost_usd: Total estimated cost
        - input_cost_usd: Cost for input tokens
        - output_cost_usd: Cost for output tokens
        - per_iteration_costs: List of costs per iteration
    """
    model = result_data.get("input", {}).get("parameters", {}).get("model", "gpt-4")
    
    total_input_tokens = token_analysis.get("total_input_tokens", 0)
    total_output_tokens = token_analysis.get("total_output_tokens", 0)
    
    total_cost = estimate_cost(total_input_tokens, total_output_tokens, model)
    input_cost = estimate_cost(total_input_tokens, 0, model)
    output_cost = estimate_cost(0, total_output_tokens, model)
    
    # Calculate per-iteration costs
    per_iteration_costs = []
    for iter_breakdown in token_analysis.get("per_iteration_breakdown", []):
        iter_input = iter_breakdown.get("input_tokens", 0)
        iter_output = iter_breakdown.get("output_tokens", 0)
        iter_cost = estimate_cost(iter_input, iter_output, model)
        per_iteration_costs.append({
            "iteration": iter_breakdown.get("iteration", 0),
            "cost_usd": iter_cost,
            "input_tokens": iter_input,
            "output_tokens": iter_output
        })
    
    return {
        "total_cost_usd": total_cost,
        "input_cost_usd": input_cost,
        "output_cost_usd": output_cost,
        "model": model,
        "per_iteration_costs": per_iteration_costs
    }


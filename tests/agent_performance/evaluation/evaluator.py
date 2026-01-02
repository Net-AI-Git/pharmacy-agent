"""
Main Evaluator for Agent Performance Testing.

Purpose (Why):
Provides comprehensive evaluation of test results by combining all analysis
modules into a single unified evaluation report.

Implementation (What):
Orchestrates all evaluation modules (token analysis, duplicate detection,
efficiency metrics, cost estimation) and combines results into a complete
evaluation dictionary.
"""

import logging
from typing import Dict, Any

from tests.agent_performance.evaluation.token_analysis import analyze_token_usage
from tests.agent_performance.evaluation.duplicate_detection import (
    detect_duplicate_api_calls,
    detect_duplicate_tool_calls,
    detect_redundant_information
)
from tests.agent_performance.evaluation.efficiency_metrics import (
    analyze_efficiency,
    calculate_efficiency_score
)
from tests.agent_performance.evaluation.cost_estimation import calculate_total_cost

# Configure module-level logger
logger = logging.getLogger(__name__)


def evaluate_test_result(result_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive evaluation of a test result.
    
    Purpose (Why):
    Provides complete evaluation of test results including token usage,
    duplicate detection, efficiency analysis, and cost estimation. This
    enables comprehensive performance analysis and optimization.
    
    Implementation (What):
    Calls all evaluation modules in sequence, combines results, calculates
    efficiency score, and generates summary and recommendations.
    
    Args:
        result_data: Complete test result data dictionary
        
    Returns:
        Complete evaluation dictionary with:
        - token_usage: Token analysis results
        - duplicate_api_calls: List of duplicate API calls
        - duplicate_tool_calls: List of duplicate tool calls
        - redundant_information: List of redundant information cases
        - efficiency_analysis: Efficiency analysis results
        - efficiency_score: Overall efficiency score (0-100)
        - cost_estimation: Cost estimation results
        - summary: Summary of key metrics
        - recommendations: List of optimization recommendations
    """
    logger.debug("Starting comprehensive evaluation")
    
    # Token analysis
    logger.debug("Analyzing token usage")
    token_usage = analyze_token_usage(result_data)
    
    # Duplicate detection
    logger.debug("Detecting duplicate calls")
    duplicate_api_calls = detect_duplicate_api_calls(result_data)
    duplicate_tool_calls = detect_duplicate_tool_calls(result_data)
    redundant_information = detect_redundant_information(result_data)
    
    # Efficiency analysis
    logger.debug("Analyzing efficiency")
    efficiency_analysis = analyze_efficiency(result_data)
    
    # Cost estimation
    logger.debug("Estimating costs")
    cost_estimation = calculate_total_cost(result_data, token_usage)
    
    # Build initial evaluation (without score, as we need it for calculation)
    evaluation = {
        "token_usage": token_usage,
        "duplicate_api_calls": duplicate_api_calls,
        "duplicate_tool_calls": duplicate_tool_calls,
        "redundant_information": redundant_information,
        "efficiency_analysis": efficiency_analysis,
        "cost_estimation": cost_estimation
    }
    
    # Calculate efficiency score (needs the evaluation dict)
    logger.debug("Calculating efficiency score")
    efficiency_score = calculate_efficiency_score(result_data, evaluation)
    evaluation["efficiency_score"] = efficiency_score
    
    # Build summary
    summary = {
        "total_duplicate_api_calls": len(duplicate_api_calls),
        "total_duplicate_tool_calls": len(duplicate_tool_calls),
        "total_redundant_information_cases": len(redundant_information),
        "total_inefficiency_issues": efficiency_analysis.get("total_issues", 0),
        "estimated_cost_usd": cost_estimation.get("total_cost_usd", 0),
        "total_tokens": token_usage.get("total_tokens", 0),
        "efficiency_score": efficiency_score
    }
    evaluation["summary"] = summary
    
    # Collect recommendations
    recommendations = []
    
    # From efficiency analysis
    recommendations.extend(efficiency_analysis.get("recommendations", []))
    
    # From duplicate calls
    if duplicate_api_calls:
        recommendations.append(
            f"Found {len(duplicate_api_calls)} duplicate API call patterns. "
            "Consider optimizing to reduce redundant API calls."
        )
    
    if duplicate_tool_calls:
        redundant_count = sum(1 for d in duplicate_tool_calls if d.get("is_redundant"))
        if redundant_count > 0:
            recommendations.append(
                f"Found {redundant_count} redundant tool calls with identical results. "
                "Consider caching or reusing previous results."
            )
    
    # From redundant information
    if redundant_information:
        recommendations.append(
            f"Found {len(redundant_information)} cases of redundant information retrieval. "
            "Consider reusing information from previous tool calls."
        )
    
    # Token usage recommendations
    total_tokens = token_usage.get("total_tokens", 0)
    if total_tokens > 15000:
        recommendations.append(
            f"High token usage ({total_tokens:,} tokens). Consider optimizing "
            "system prompt or reducing conversation history."
        )
    
    evaluation["recommendations"] = recommendations
    
    logger.debug(f"Evaluation complete. Efficiency score: {efficiency_score}")
    
    return evaluation


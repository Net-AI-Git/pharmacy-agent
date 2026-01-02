"""
Evaluation module for agent performance testing.

Purpose (Why):
Provides comprehensive evaluation capabilities for agent performance tests,
including token analysis, duplicate detection, efficiency metrics, run comparison,
and cost estimation.

Implementation (What):
Exports main evaluation function and sub-modules for detailed analysis of
test results.
"""

from tests.agent_performance.evaluation.evaluator import evaluate_test_result
from tests.agent_performance.evaluation.token_analysis import analyze_token_usage, count_tokens
from tests.agent_performance.evaluation.duplicate_detection import (
    detect_duplicate_api_calls,
    detect_duplicate_tool_calls,
    detect_redundant_information
)
from tests.agent_performance.evaluation.efficiency_metrics import (
    analyze_efficiency,
    calculate_efficiency_score
)
from tests.agent_performance.evaluation.cost_estimation import estimate_cost, calculate_total_cost
from tests.agent_performance.evaluation.run_comparison import (
    find_previous_runs,
    compare_runs,
    compare_with_audit_logs
)

__all__ = [
    'evaluate_test_result',
    'analyze_token_usage',
    'count_tokens',
    'detect_duplicate_api_calls',
    'detect_duplicate_tool_calls',
    'detect_redundant_information',
    'analyze_efficiency',
    'calculate_efficiency_score',
    'estimate_cost',
    'calculate_total_cost',
    'find_previous_runs',
    'compare_runs',
    'compare_with_audit_logs'
]


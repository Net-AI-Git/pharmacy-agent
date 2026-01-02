"""
Run Comparison Report Generator for Agent Performance Testing.

Purpose (Why):
Generates comprehensive comparison reports between the current test run and
previous runs, enabling developers to track performance trends, identify
regressions, and measure improvements over time.

Implementation (What):
Compares all tests from the current run with their previous executions,
aggregates comparison data, and generates a unified Markdown report showing
trends, significant changes, and overall performance direction.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from tests.agent_performance.evaluation.run_comparison import (
    find_previous_runs,
    compare_runs
)

# Configure module-level logger
logger = logging.getLogger(__name__)


def _format_percent_change(percent: float) -> str:
    """
    Format percent change with appropriate sign and color indicator.
    
    Purpose (Why):
    Provides clear visual indication of whether changes are positive or negative,
    making trends easier to identify at a glance.
    
    Implementation (What):
    Formats percentage with +/- sign and adds emoji indicators for quick visual
    assessment of improvement vs regression.
    
    Args:
        percent: Percentage change value
        
    Returns:
        Formatted string with sign and indicator
    """
    if percent > 0:
        return f"+{percent:.1f}% ⬆️"
    elif percent < 0:
        return f"{percent:.1f}% ⬇️"
    else:
        return "0% ➡️"


def _format_trend_indicator(trend: str) -> str:
    """
    Format trend indicator with appropriate emoji.
    
    Purpose (Why):
    Provides visual indication of trend direction for quick assessment.
    
    Implementation (What):
    Maps trend strings to emoji indicators for clear visual representation.
    
    Args:
        trend: Trend string ("improving", "declining", "stable")
        
    Returns:
        Formatted string with emoji indicator
    """
    trend_map = {
        "improving": "📈",
        "declining": "📉",
        "stable": "➡️"
    }
    emoji = trend_map.get(trend, "")
    return f"{emoji} {trend}" if emoji else trend


def _generate_test_comparison_section(
    test_name: str,
    current_result: Dict[str, Any],
    comparison_data: Dict[str, Any]
) -> List[str]:
    """
    Generate Markdown section for a single test comparison.
    
    Purpose (Why):
    Creates detailed comparison section for each test, showing how current
    performance compares to previous runs with clear metrics and trends.
    
    Implementation (What):
    Formats comparison data into structured Markdown with tables and indicators
    for easy reading and analysis.
    
    Args:
        test_name: Name of the test
        current_result: Current test result dictionary
        comparison_data: Comparison results from compare_runs()
        
    Returns:
        List of Markdown lines for this test section
    """
    lines = []
    lines.append(f"### {test_name}")
    lines.append("")
    
    comparisons = comparison_data.get("comparisons", [])
    trends = comparison_data.get("trends", {})
    significant_changes = comparison_data.get("significant_changes", [])
    
    if not comparisons:
        lines.append("*No previous runs found for comparison.*")
        lines.append("")
        return lines
    
    # Current metrics
    current_stats = current_result.get("output", {}).get("statistics", {})
    current_eval = current_result.get("evaluation", {})
    current_summary = current_eval.get("summary", {}) if current_eval else {}
    
    lines.append("**Current Run Metrics:**")
    lines.append(f"- API Calls: {current_stats.get('total_api_calls', 0)}")
    lines.append(f"- Tool Calls: {current_stats.get('total_tool_calls', 0)}")
    lines.append(f"- Time: {current_stats.get('total_time', 0):.3f}s")
    if current_summary:
        lines.append(f"- Total Tokens: {current_summary.get('total_tokens', 0):,}")
        lines.append(f"- Efficiency Score: {current_summary.get('efficiency_score', 0)}/100")
        lines.append(f"- Estimated Cost: ${current_summary.get('estimated_cost_usd', 0):.6f}")
    lines.append("")
    
    # Comparison table with most recent previous run
    if comparisons:
        latest = comparisons[0]
        lines.append("**Comparison with Most Recent Previous Run:**")
        lines.append(f"*Previous Run: {latest.get('run_name', 'unknown')}*")
        lines.append("")
        lines.append("| Metric | Current | Previous | Change | Trend |")
        lines.append("|--------|---------|----------|--------|-------|")
        
        differences = latest.get("differences", {})
        for metric, diff_data in differences.items():
            current_val = diff_data.get("current", 0)
            prev_val = diff_data.get("previous", 0)
            change = diff_data.get("difference", 0)
            percent = diff_data.get("percent_change", 0)
            
            # Format values based on metric type
            if metric == "time":
                current_str = f"{current_val:.3f}s"
                prev_str = f"{prev_val:.3f}s"
                change_str = f"{change:+.3f}s"
            elif metric == "efficiency_score":
                current_str = f"{current_val:.1f}/100"
                prev_str = f"{prev_val:.1f}/100"
                change_str = f"{change:+.1f}"
            elif metric == "tokens":
                current_str = f"{int(current_val):,}"
                prev_str = f"{int(prev_val):,}"
                change_str = f"{int(change):+,}"
            else:
                current_str = str(int(current_val))
                prev_str = str(int(prev_val))
                change_str = f"{int(change):+}"
            
            trend = trends.get(metric, "stable")
            trend_str = _format_trend_indicator(trend)
            percent_str = _format_percent_change(percent)
            
            lines.append(f"| {metric.replace('_', ' ').title()} | {current_str} | {prev_str} | {change_str} ({percent_str}) | {trend_str} |")
        
        lines.append("")
    
    # Significant changes
    if significant_changes:
        lines.append("**⚠️ Significant Changes (>20%):**")
        for change in significant_changes[:5]:
            metric = change.get("metric", "unknown")
            direction = change.get("direction", "unknown")
            percent = change.get("percent_change", 0)
            run_name = change.get("run", "unknown")
            
            direction_emoji = "✅" if direction == "improvement" else "❌"
            lines.append(f"- {direction_emoji} **{metric.replace('_', ' ').title()}**: {_format_percent_change(percent)} compared to {run_name} ({direction})")
        lines.append("")
    
    return lines


def generate_run_comparison_report(
    current_results: List[Dict[str, Any]],
    run_directory: str,
    results_dir: str = "tests/agent_performance/results"
) -> str:
    """
    Generate comprehensive comparison report for the current test run.
    
    Purpose (Why):
    Creates a unified comparison report showing how all tests in the current
    run compare to their previous executions, enabling quick assessment of
    overall performance trends and identifying which tests improved or regressed.
    
    Implementation (What):
    For each test in the current run, finds previous executions, performs
    comparison, and aggregates results into a single Markdown report. Saves
    the report to the current run directory, overwriting any previous comparison.
    
    Args:
        current_results: List of current test result dictionaries
        run_directory: Path to current run directory
        results_dir: Base directory containing all run directories
        
    Returns:
        Path to the generated comparison report file
        
    Raises:
        IOError: If unable to write the comparison report file
    """
    logger.info("Generating run comparison report")
    
    report_lines = []
    report_lines.append("# Run Comparison Report")
    report_lines.append("")
    
    # Header information
    run_dir_path = Path(run_directory)
    run_name = run_dir_path.name
    report_lines.append(f"**Current Run:** `{run_name}`")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    if not current_results:
        report_lines.append("*No test results available for comparison.*")
        report_path = run_dir_path / "run_comparison.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
        logger.info(f"Comparison report saved: {report_path}")
        return str(report_path)
    
    # Overall summary
    report_lines.append("## Overall Summary")
    report_lines.append("")
    
    successful_tests = [r for r in current_results if r.get("status") == "success"]
    report_lines.append(f"**Tests Run:** {len(successful_tests)}")
    report_lines.append("")
    
    # Individual test comparisons
    report_lines.append("## Test-by-Test Comparison")
    report_lines.append("")
    
    for result in successful_tests:
        test_name = result.get("test_name", "unknown")
        result_data = result.get("result_data")
        
        if not result_data:
            logger.warning(f"No result data for test: {test_name}")
            continue
        
        # Find previous runs for this test
        previous_runs = find_previous_runs(
            test_name=test_name,
            results_dir=results_dir,
            limit=5
        )
        
        if not previous_runs:
            report_lines.append(f"### {test_name}")
            report_lines.append("")
            report_lines.append("*No previous runs found for comparison.*")
            report_lines.append("")
            continue
        
        # Compare with previous runs
        comparison_data = compare_runs(result_data, previous_runs)
        
        # Generate section for this test
        test_section = _generate_test_comparison_section(
            test_name=test_name,
            current_result=result_data,
            comparison_data=comparison_data
        )
        report_lines.extend(test_section)
    
    # Aggregate trends
    report_lines.append("## Aggregate Trends")
    report_lines.append("")
    
    all_trends = {}
    for result in successful_tests:
        test_name = result.get("test_name", "unknown")
        result_data = result.get("result_data")
        
        if not result_data:
            continue
        
        previous_runs = find_previous_runs(
            test_name=test_name,
            results_dir=results_dir,
            limit=1  # Only need most recent for trends
        )
        
        if previous_runs:
            comparison_data = compare_runs(result_data, previous_runs)
            trends = comparison_data.get("trends", {})
            
            for metric, trend in trends.items():
                if metric not in all_trends:
                    all_trends[metric] = {"improving": 0, "declining": 0, "stable": 0}
                all_trends[metric][trend] = all_trends[metric].get(trend, 0) + 1
    
    if all_trends:
        report_lines.append("| Metric | Improving | Declining | Stable |")
        report_lines.append("|--------|-----------|-----------|--------|")
        for metric, counts in all_trends.items():
            improving = counts.get("improving", 0)
            declining = counts.get("declining", 0)
            stable = counts.get("stable", 0)
            report_lines.append(f"| {metric.replace('_', ' ').title()} | {improving} | {declining} | {stable} |")
        report_lines.append("")
    
    # Write report
    report_path = run_dir_path / "run_comparison.md"
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
        logger.info(f"Comparison report saved: {report_path}")
        return str(report_path)
    except Exception as e:
        logger.error(f"Error writing comparison report: {e}", exc_info=True)
        raise IOError(f"Failed to write comparison report: {e}") from e


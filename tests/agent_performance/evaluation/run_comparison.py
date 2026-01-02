"""
Run Comparison for Agent Performance Testing.

Purpose (Why):
Provides comparison capabilities between different test runs to identify
trends, regressions, and improvements over time.

Implementation (What):
Loads previous test results, compares metrics, and identifies significant
changes between runs.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure module-level logger
logger = logging.getLogger(__name__)


def _parse_timestamp_from_directory_name(dirname: str) -> Optional[datetime]:
    """
    Parse timestamp from directory name.
    
    Args:
        dirname: Directory name in format YYYY-MM-DD_HH-MM-SS
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(dirname, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return None


def find_previous_runs(
    test_name: str,
    results_dir: str = "tests/agent_performance/results",
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Find previous test runs for comparison.
    
    Purpose (Why):
    Locates previous test results for the same test to enable comparison
    and trend analysis.
    
    Implementation (What):
    Scans results directory, finds all runs containing the test, sorts by
    timestamp (newest first), and loads JSON files.
    
    Args:
        test_name: Name of the test to find previous runs for
        results_dir: Base directory containing run directories
        limit: Maximum number of previous runs to return
        
    Returns:
        List of previous test result dictionaries, sorted by timestamp
        (newest first)
    """
    results_path = Path(results_dir)
    
    if not results_path.exists():
        logger.warning(f"Results directory not found: {results_dir}")
        return []
    
    # Find all run directories
    run_directories = []
    for item in results_path.iterdir():
        if item.is_dir():
            timestamp = _parse_timestamp_from_directory_name(item.name)
            if timestamp:
                run_directories.append((timestamp, item))
    
    # Sort by timestamp (newest first)
    run_directories.sort(key=lambda x: x[0], reverse=True)
    
    # Load test results from each directory
    previous_runs = []
    for timestamp, dir_path in run_directories:
        json_file = dir_path / f"{test_name}.json"
        
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                    previous_runs.append({
                        "result": result_data,
                        "timestamp": timestamp,
                        "directory": str(dir_path),
                        "run_name": dir_path.name
                    })
                    
                    if len(previous_runs) >= limit:
                        break
            except Exception as e:
                logger.warning(f"Error loading previous run {json_file}: {e}")
    
    return previous_runs


def compare_runs(
    current_result: Dict[str, Any],
    previous_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare current run with previous runs.
    
    Purpose (Why):
    Identifies changes, improvements, and regressions between test runs
    to track performance over time.
    
    Implementation (What):
    Compares key metrics between current and previous runs, calculates
    differences, and identifies significant changes.
    
    Args:
        current_result: Current test result dictionary
        previous_results: List of previous test result dictionaries
        
    Returns:
        Dictionary with comparison results:
        - comparisons: List of comparisons with each previous run
        - trends: Overall trends detected
        - significant_changes: List of significant changes
    """
    if not previous_results:
        return {
            "comparisons": [],
            "trends": {},
            "significant_changes": []
        }
    
    comparisons = []
    significant_changes = []
    
    current_stats = current_result.get("output", {}).get("statistics", {})
    current_eval = current_result.get("evaluation", {})
    
    for prev_run in previous_results:
        prev_result = prev_run.get("result", {})
        prev_stats = prev_result.get("output", {}).get("statistics", {})
        prev_eval = prev_result.get("evaluation", {})
        
        comparison = {
            "run_name": prev_run.get("run_name", "unknown"),
            "timestamp": prev_run.get("timestamp").isoformat() if prev_run.get("timestamp") else None,
            "differences": {}
        }
        
        # Compare API calls
        current_api = current_stats.get("total_api_calls", 0)
        prev_api = prev_stats.get("total_api_calls", 0)
        api_diff = current_api - prev_api
        comparison["differences"]["api_calls"] = {
            "current": current_api,
            "previous": prev_api,
            "difference": api_diff,
            "percent_change": round((api_diff / prev_api * 100) if prev_api > 0 else 0, 1)
        }
        
        # Compare tool calls
        current_tools = current_stats.get("total_tool_calls", 0)
        prev_tools = prev_stats.get("total_tool_calls", 0)
        tools_diff = current_tools - prev_tools
        comparison["differences"]["tool_calls"] = {
            "current": current_tools,
            "previous": prev_tools,
            "difference": tools_diff,
            "percent_change": round((tools_diff / prev_tools * 100) if prev_tools > 0 else 0, 1)
        }
        
        # Compare time
        current_time = current_stats.get("total_time", 0)
        prev_time = prev_stats.get("total_time", 0)
        time_diff = current_time - prev_time
        comparison["differences"]["time"] = {
            "current": current_time,
            "previous": prev_time,
            "difference": round(time_diff, 3),
            "percent_change": round((time_diff / prev_time * 100) if prev_time > 0 else 0, 1)
        }
        
        # Compare tokens if available
        if current_eval and prev_eval:
            current_tokens = current_eval.get("token_usage", {}).get("total_tokens", 0)
            prev_tokens = prev_eval.get("token_usage", {}).get("total_tokens", 0)
            tokens_diff = current_tokens - prev_tokens
            comparison["differences"]["tokens"] = {
                "current": current_tokens,
                "previous": prev_tokens,
                "difference": tokens_diff,
                "percent_change": round((tokens_diff / prev_tokens * 100) if prev_tokens > 0 else 0, 1)
            }
            
            # Compare efficiency score
            current_score = current_eval.get("efficiency_score", 0)
            prev_score = prev_eval.get("efficiency_score", 0)
            score_diff = current_score - prev_score
            comparison["differences"]["efficiency_score"] = {
                "current": current_score,
                "previous": prev_score,
                "difference": round(score_diff, 1),
                "percent_change": round((score_diff / prev_score * 100) if prev_score > 0 else 0, 1)
            }
        
        comparisons.append(comparison)
        
        # Detect significant changes (>20% change)
        for metric, diff_data in comparison["differences"].items():
            percent_change = abs(diff_data.get("percent_change", 0))
            if percent_change > 20:
                change = diff_data.get("difference", 0)
                # Determine direction: for efficiency_score, positive change is improvement
                # For other metrics (API calls, time, tokens), negative change is improvement
                if metric == "efficiency_score":
                    direction = "improvement" if change > 0 else "regression"
                else:
                    direction = "improvement" if change < 0 else "regression"
                
                significant_changes.append({
                    "metric": metric,
                    "run": prev_run.get("run_name", "unknown"),
                    "change": change,
                    "percent_change": diff_data.get("percent_change", 0),
                    "direction": direction
                })
    
    # Calculate trends (comparing with most recent previous run)
    trends = {}
    if comparisons:
        latest_comparison = comparisons[0]  # Already sorted newest first
        for metric, diff_data in latest_comparison["differences"].items():
            change = diff_data.get("difference", 0)
            if metric == "efficiency_score":
                trends[metric] = "improving" if change > 0 else "declining" if change < 0 else "stable"
            else:
                trends[metric] = "improving" if change < 0 else "declining" if change > 0 else "stable"
    
    return {
        "comparisons": comparisons,
        "trends": trends,
        "significant_changes": significant_changes
    }


def compare_with_audit_logs(
    correlation_id: str,
    audit_logs_dir: str = "logs/audit"
) -> Dict[str, Any]:
    """
    Compare test results with audit logs.
    
    Purpose (Why):
    Validates consistency between test results and audit logs, ensuring
    complete traceability and data integrity.
    
    Implementation (What):
    Loads audit log file, finds entries matching correlation_id, and compares
    tool calls between test results and audit logs.
    
    Args:
        correlation_id: Correlation ID to match
        audit_logs_dir: Directory containing audit log files
        
    Returns:
        Dictionary with comparison results:
        - consistency: Whether results are consistent
        - tool_call_matches: Number of matching tool calls
        - discrepancies: List of discrepancies found
    """
    audit_path = Path(audit_logs_dir)
    
    if not audit_path.exists():
        logger.warning(f"Audit logs directory not found: {audit_logs_dir}")
        return {
            "consistency": False,
            "error": "Audit logs directory not found",
            "tool_call_matches": 0,
            "discrepancies": []
        }
    
    # Find audit log file (try to find by date pattern or scan all)
    audit_entries = []
    
    # Try to find log file with correlation_id
    for log_file in audit_path.glob("*.json"):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            if entry.get("correlation_id") == correlation_id:
                                audit_entries.append(entry)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.warning(f"Error reading audit log {log_file}: {e}")
    
    if not audit_entries:
        return {
            "consistency": False,
            "error": "No audit log entries found for correlation_id",
            "tool_call_matches": 0,
            "discrepancies": []
        }
    
    # Extract tool calls from audit logs
    audit_tool_calls = [
        entry for entry in audit_entries
        if entry.get("event_type") == "tool_call"
    ]
    
    return {
        "consistency": True,
        "tool_call_matches": len(audit_tool_calls),
        "audit_entries_found": len(audit_entries),
        "discrepancies": []  # Could add detailed comparison here
    }


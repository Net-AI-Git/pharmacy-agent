"""
Result Manager for Agent Performance Testing.

Purpose (Why):
Manages test result files, organizing them by run session in separate directories,
and maintaining rotation to keep only the 5 most recent run directories.

Implementation (What):
Provides functions to save test results in run-specific directories (one directory
per test run session), clean up old run directories keeping only the 5 most recent,
and retrieve latest results for analysis.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

# Configure module-level logger
logger = logging.getLogger(__name__)


def _generate_run_directory_name() -> str:
    """
    Generate timestamped directory name for a test run session.
    
    Purpose (Why):
    Creates consistent, sortable directory names with timestamps for test run sessions.
    
    Implementation (What):
    Formats directory name as YYYY-MM-DD_HH-MM-SS
    
    Returns:
        Directory name string
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _parse_timestamp_from_directory_name(dirname: str) -> Optional[datetime]:
    """
    Parse timestamp from directory name.
    
    Purpose (Why):
    Extracts timestamp from directory name for sorting and comparison.
    
    Implementation (What):
    Parses directory name pattern YYYY-MM-DD_HH-MM-SS
    
    Args:
        dirname: Directory name to parse
        
    Returns:
        Datetime object or None if pattern doesn't match
    """
    try:
        return datetime.strptime(dirname, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return None


def get_or_create_run_directory(
    results_dir: str = "tests/agent_performance/results"
) -> Tuple[str, str]:
    """
    Get or create a run directory for the current test session.
    
    Purpose (Why):
    Creates a single directory for all tests in the current run session,
    ensuring all results from one run are grouped together.
    
    Implementation (What):
    Generates a timestamped directory name, creates it if needed, and
    performs cleanup to keep only 5 most recent run directories.
    
    Args:
        results_dir: Base directory for results
        
    Returns:
        Tuple of (run_directory_path, run_directory_name)
    """
    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)
    
    # Generate run directory name
    run_dir_name = _generate_run_directory_name()
    run_dir_path = results_path / run_dir_name
    run_dir_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Using run directory: {run_dir_name}")
    
    # Cleanup old run directories before creating new one
    cleanup_old_run_directories(results_dir=results_dir, keep_count=5)
    
    return str(run_dir_path), run_dir_name


def save_test_result(
    test_name: str,
    result_data: dict,
    run_directory: str
) -> Tuple[str, str]:
    """
    Save test result to JSON and Markdown files in the run directory.
    
    Purpose (Why):
    Persists test results in both machine-readable (JSON) and human-readable
    (Markdown) formats within the current run directory.
    
    Implementation (What):
    Saves JSON and Markdown files with simple test name (no timestamp in filename
    since timestamp is in directory name).
    
    Args:
        test_name: Name of the test
        result_data: Complete test result data dictionary
        run_directory: Directory path for the current run session
        
    Returns:
        Tuple of (json_path, md_path) for saved files
    """
    run_dir_path = Path(run_directory)
    run_dir_path.mkdir(parents=True, exist_ok=True)
    
    # Simple filenames (timestamp is in directory name)
    json_filename = f"{test_name}.json"
    md_filename = f"{test_name}.md"
    
    json_path = run_dir_path / json_filename
    md_path = run_dir_path / md_filename
    
    logger.info(f"Saving test result: {test_name} -> {json_path.name}, {md_path.name}")
    
    return str(json_path), str(md_path)


def cleanup_old_run_directories(
    keep_count: int = 5,
    results_dir: str = "tests/agent_performance/results"
) -> int:
    """
    Remove old run directories, keeping only the most recent ones.
    
    Purpose (Why):
    Prevents accumulation of too many result directories by maintaining only
    the most recent run sessions.
    
    Implementation (What):
    Finds all run directories (directories matching timestamp pattern),
    sorts by timestamp, and deletes directories beyond the keep_count limit.
    
    Args:
        keep_count: Number of run directories to keep
        results_dir: Base directory containing run directories
        
    Returns:
        Number of directories deleted
    """
    results_path = Path(results_dir)
    
    if not results_path.exists():
        return 0
    
    # Find all directories that match timestamp pattern
    run_directories = []
    for item in results_path.iterdir():
        if item.is_dir():
            timestamp = _parse_timestamp_from_directory_name(item.name)
            if timestamp:
                run_directories.append((timestamp, item))
    
    # Sort by timestamp (newest first)
    run_directories.sort(key=lambda x: x[0], reverse=True)
    
    # Delete directories beyond keep_count
    deleted_count = 0
    
    for timestamp, dir_path in run_directories[keep_count:]:
        try:
            shutil.rmtree(dir_path)
            deleted_count += 1
            logger.info(f"Deleted old run directory: {dir_path.name}")
        except Exception as e:
            logger.error(f"Error deleting directory {dir_path}: {e}")
    
    if deleted_count > 0:
        logger.info(f"Cleaned up {deleted_count} old run directories, kept {min(len(run_directories), keep_count)} most recent")
    
    return deleted_count


def get_latest_run_directories(
    count: int = 5,
    results_dir: str = "tests/agent_performance/results"
) -> List[str]:
    """
    Get paths to the most recent run directories.
    
    Purpose (Why):
    Provides a way to retrieve the most recent test run directories for analysis.
    
    Implementation (What):
    Finds all run directories, sorts by timestamp, and returns paths to
    the most recent ones.
    
    Args:
        count: Number of run directories to return
        results_dir: Base directory containing run directories
        
    Returns:
        List of run directory paths (newest first)
    """
    results_path = Path(results_dir)
    
    if not results_path.exists():
        return []
    
    # Find all directories that match timestamp pattern
    run_directories = []
    for item in results_path.iterdir():
        if item.is_dir():
            timestamp = _parse_timestamp_from_directory_name(item.name)
            if timestamp:
                run_directories.append((timestamp, item))
    
    # Sort by timestamp (newest first)
    run_directories.sort(key=lambda x: x[0], reverse=True)
    
    # Return paths for most recent directories
    return [str(dir_path) for _, dir_path in run_directories[:count]]


def get_latest_results(
    test_name: str,
    count: int = 5,
    results_dir: str = "tests/agent_performance/results"
) -> List[Tuple[str, str]]:
    """
    Get paths to the most recent result files for a test across all runs.
    
    Purpose (Why):
    Provides a way to retrieve the most recent test results for a specific test
    across all run directories.
    
    Implementation (What):
    Finds all run directories, looks for test result files in each, sorts by
    run directory timestamp, and returns paths to the most recent JSON/MD pairs.
    
    Args:
        test_name: Name of the test
        count: Number of result pairs to return
        results_dir: Base directory containing run directories
        
    Returns:
        List of tuples (json_path, md_path) for latest results
    """
    results_path = Path(results_dir)
    
    if not results_path.exists():
        return []
    
    # Get all run directories sorted by timestamp
    run_dirs = get_latest_run_directories(count=count * 2, results_dir=results_dir)  # Get more to ensure we find enough
    
    result_pairs = []
    for run_dir in run_dirs:
        run_dir_path = Path(run_dir)
        json_file = run_dir_path / f"{test_name}.json"
        md_file = run_dir_path / f"{test_name}.md"
        
        if json_file.exists() and md_file.exists():
            result_pairs.append((str(json_file), str(md_file)))
            if len(result_pairs) >= count:
                break
    
    return result_pairs

"""
Main script for running agent performance tests.

Purpose (Why):
Provides command-line interface to run performance tests on StreamingAgent,
capturing all interactions and saving results for analysis.

Implementation (What):
Loads test configurations, runs tests using TracedStreamingAgent, formats
results, saves them to files, and provides summary output. Supports command-line
arguments for test selection and output directory configuration.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.agent_performance.test_runner import load_test_config, run_single_test, list_available_tests
from tests.agent_performance.result_manager import get_or_create_run_directory, save_test_result
from tests.agent_performance.formatters import format_json, format_markdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to run performance tests.
    
    Purpose (Why):
    Orchestrates the test execution process: loading configurations, running
    tests, formatting results, saving files, and providing summary.
    
    Implementation (What):
    Parses command-line arguments, loads test configurations, runs each test,
    formats results as JSON and Markdown, saves to files, and prints summary.
    """
    parser = argparse.ArgumentParser(
        description="Run agent performance tests with comprehensive tracing"
    )
    parser.add_argument(
        "--test",
        type=str,
        help="Run a specific test by name (without .json extension)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available test configurations"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="tests/agent_performance/results",
        help="Directory to save test results (default: tests/agent_performance/results)"
    )
    parser.add_argument(
        "--config-dir",
        type=str,
        default="tests/agent_performance/test_configs",
        help="Directory containing test configurations (default: tests/agent_performance/test_configs)"
    )
    
    args = parser.parse_args()
    
    # List available tests if requested
    if args.list:
        tests = list_available_tests(args.config_dir)
        if tests:
            print("Available tests:")
            for test in tests:
                print(f"  - {test}")
        else:
            print("No test configurations found.")
        return
    
    # Determine which tests to run
    config_dir = Path(args.config_dir)
    
    if not config_dir.exists():
        logger.error(f"Test configs directory not found: {config_dir}")
        sys.exit(1)
    
    if args.test:
        # Run specific test
        test_config_path = config_dir / f"{args.test}.json"
        if not test_config_path.exists():
            logger.error(f"Test configuration not found: {test_config_path}")
            sys.exit(1)
        test_configs = [test_config_path]
    else:
        # Run all tests
        test_configs = list(config_dir.glob("*.json"))
        if not test_configs:
            logger.warning(f"No test configurations found in {config_dir}")
            sys.exit(0)
    
    # Create run directory for this test session
    run_dir_path, run_dir_name = get_or_create_run_directory(results_dir=args.output_dir)
    logger.info(f"Test run session: {run_dir_name}")
    
    # Run tests
    results_summary = []
    
    for config_path in test_configs:
        try:
            logger.info(f"Loading test configuration: {config_path.name}")
            test_config = load_test_config(str(config_path))
            
            logger.info(f"Running test: {test_config['test_name']}")
            result_data = run_single_test(test_config)
            
            # Format results
            json_content = format_json(result_data)
            md_content = format_markdown(result_data)
            
            # Save results in the run directory
            json_path, md_path = save_test_result(
                result_data["test_name"],
                result_data,
                run_directory=run_dir_path
            )
            
            # Write files
            Path(json_path).parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(json_content)
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"Results saved: {json_path}, {md_path}")
            
            # Add to summary
            stats = result_data["output"]["statistics"]
            results_summary.append({
                "test_name": result_data["test_name"],
                "status": "success",
                "api_calls": stats.get("total_api_calls", 0),
                "tool_calls": stats.get("total_tool_calls", 0),
                "time": stats.get("total_time", 0),
                "json_path": json_path,
                "md_path": md_path
            })
            
        except Exception as e:
            logger.error(f"Error running test {config_path.name}: {e}", exc_info=True)
            results_summary.append({
                "test_name": config_path.stem,
                "status": "error",
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Execution Summary")
    print("=" * 60)
    print(f"Run Directory: {run_dir_name}")
    print(f"Results Location: {run_dir_path}")
    print("=" * 60)
    
    for summary in results_summary:
        if summary["status"] == "success":
            print(f"\n✓ {summary['test_name']}")
            print(f"  API Calls: {summary['api_calls']}")
            print(f"  Tool Calls: {summary['tool_calls']}")
            print(f"  Time: {summary['time']:.3f}s")
            print(f"  Results: {summary['json_path']}")
        else:
            print(f"\n✗ {summary['test_name']}")
            print(f"  Error: {summary.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    
    # Exit with error code if any tests failed
    failed_tests = [s for s in results_summary if s["status"] == "error"]
    if failed_tests:
        sys.exit(1)


if __name__ == "__main__":
    main()


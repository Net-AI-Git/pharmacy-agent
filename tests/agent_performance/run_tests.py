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
from tests.agent_performance.comparison_report import generate_run_comparison_report
from app.security.audit_logger import get_audit_logger

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
        "--flow",
        type=str,
        choices=["flow1_stock_availability", "flow2_prescription", "flow3_information", "flow4_policy_adherence", "flow5_user_prescriptions", "all"],
        help="Run all tests for a specific flow (flow1_stock_availability, flow2_prescription, flow3_information, flow4_policy_adherence, flow5_user_prescriptions) or 'all' for all flows"
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
    
    # Start a new audit log run for this test session
    audit_logger = get_audit_logger()
    audit_logger.start_new_run()
    
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
    elif args.flow:
        # Run tests for a specific flow
        if args.flow == "all":
            # Run all flow tests (flow1, flow2, flow3, flow4, flow5)
            test_configs = list(config_dir.glob("flow*.json"))
        elif args.flow == "flow1_stock_availability":
            # Flow 1: Stock Availability - match flow1_stock_*
            test_configs = list(config_dir.glob("flow1_stock*.json"))
        elif args.flow == "flow2_prescription":
            # Flow 2: Prescription - match flow2_prescription_*
            test_configs = list(config_dir.glob("flow2_prescription*.json"))
        elif args.flow == "flow3_information":
            # Flow 3: Information - match flow3_information_*
            test_configs = list(config_dir.glob("flow3_information*.json"))
        elif args.flow == "flow4_policy_adherence":
            # Flow 4: Policy Adherence - match flow4_policy_adherence_*
            test_configs = list(config_dir.glob("flow4_policy_adherence*.json"))
        elif args.flow == "flow5_user_prescriptions":
            # Flow 5: User Prescriptions - match flow5_user_prescriptions_*
            test_configs = list(config_dir.glob("flow5_user_prescriptions*.json"))
        else:
            logger.error(f"Unknown flow: {args.flow}")
            sys.exit(1)
        
        if not test_configs:
            logger.warning(f"No test configurations found for flow: {args.flow} in {config_dir}")
            sys.exit(0)
        
        # Sort tests for consistent execution order
        test_configs.sort()
        logger.info(f"Found {len(test_configs)} tests for flow: {args.flow}")
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
    current_results = []  # Store full results for comparison
    
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
            evaluation = result_data.get("evaluation", {})
            eval_summary = evaluation.get("summary", {})
            
            summary_entry = {
                "test_name": result_data["test_name"],
                "status": "success",
                "api_calls": stats.get("total_api_calls", 0),
                "tool_calls": stats.get("total_tool_calls", 0),
                "time": stats.get("total_time", 0),
                "efficiency_score": eval_summary.get("efficiency_score", 0),
                "estimated_cost": eval_summary.get("estimated_cost_usd", 0),
                "total_tokens": eval_summary.get("total_tokens", 0),
                "json_path": json_path,
                "md_path": md_path
            }
            results_summary.append(summary_entry)
            
            # Store full result for comparison
            current_results.append({
                "test_name": result_data["test_name"],
                "status": "success",
                "result_data": result_data
            })
            
        except Exception as e:
            logger.error(f"Error running test {config_path.name}: {e}", exc_info=True)
            results_summary.append({
                "test_name": config_path.stem,
                "status": "error",
                "error": str(e)
            })
            current_results.append({
                "test_name": config_path.stem,
                "status": "error",
                "error": str(e)
            })
    
    # Group results by flow for better analysis
    flow_groups = {}
    for summary in results_summary:
        test_name = summary.get("test_name", "")
        # Extract flow from test name
        if test_name.startswith("flow1_"):
            flow = "Flow 1: Stock Availability"
        elif test_name.startswith("flow2_"):
            flow = "Flow 2: Prescription"
        elif test_name.startswith("flow3_"):
            flow = "Flow 3: Information"
        elif test_name.startswith("flow4_"):
            flow = "Flow 4: Policy Adherence"
        elif test_name.startswith("flow5_"):
            flow = "Flow 5: User Prescriptions"
        else:
            flow = "Other Tests"
        
        if flow not in flow_groups:
            flow_groups[flow] = []
        flow_groups[flow].append(summary)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Execution Summary")
    print("=" * 60)
    print(f"Run Directory: {run_dir_name}")
    print(f"Results Location: {run_dir_path}")
    if args.flow:
        print(f"Flow Filter: {args.flow}")
    print("=" * 60)
    
    # Print summary by flow
    for flow_name, flow_tests in sorted(flow_groups.items()):
        print(f"\n{flow_name} ({len(flow_tests)} tests):")
        print("-" * 60)
        
        success_count = sum(1 for t in flow_tests if t["status"] == "success")
        error_count = len(flow_tests) - success_count
        
        for summary in flow_tests:
            if summary["status"] == "success":
                print(f"  ✓ {summary['test_name']}")
                print(f"    API Calls: {summary['api_calls']}")
                print(f"    Tool Calls: {summary['tool_calls']}")
                print(f"    Time: {summary['time']:.3f}s")
                if summary.get("efficiency_score") is not None:
                    print(f"    Efficiency Score: {summary['efficiency_score']}/100")
                if summary.get("estimated_cost") is not None:
                    print(f"    Estimated Cost: ${summary['estimated_cost']:.6f}")
                if summary.get("total_tokens") is not None:
                    print(f"    Total Tokens: {summary['total_tokens']:,}")
            else:
                print(f"  ✗ {summary['test_name']}")
                print(f"    Error: {summary.get('error', 'Unknown error')}")
        
        print(f"\n  Flow Summary: {success_count} passed, {error_count} failed")
    
    # Overall summary
    total_tests = len(results_summary)
    total_success = sum(1 for s in results_summary if s["status"] == "success")
    total_errors = total_tests - total_success
    
    print("\n" + "=" * 60)
    print(f"Overall Summary: {total_success}/{total_tests} tests passed")
    if total_errors > 0:
        print(f"⚠️  {total_errors} test(s) failed")
    print("=" * 60)
    
    # Generate comparison report
    try:
        logger.info("Generating comparison report")
        comparison_report_path = generate_run_comparison_report(
            current_results=current_results,
            run_directory=run_dir_path,
            results_dir=args.output_dir
        )
        print(f"\n📊 Comparison Report: {comparison_report_path}")
        logger.info(f"Comparison report generated: {comparison_report_path}")
    except Exception as e:
        logger.warning(f"Error generating comparison report: {e}", exc_info=True)
        print(f"\n⚠️  Warning: Could not generate comparison report: {e}")
    
    print("\n" + "=" * 60)
    
    # Exit with error code if any tests failed
    failed_tests = [s for s in results_summary if s["status"] == "error"]
    if failed_tests:
        sys.exit(1)


if __name__ == "__main__":
    main()


"""
Test Runner for Agent Performance Testing.

Purpose (Why):
Provides functions to run individual performance tests on StreamingAgent,
loading test configurations and executing them with comprehensive tracing.

Implementation (What):
Loads test configurations from JSON files, creates TracedStreamingAgent instances,
runs tests, and collects all trace data including API calls, chunks, tool executions,
and thinking/reasoning for analysis.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.agent_performance.agent_wrapper import TracedStreamingAgent
from tests.agent_performance.evaluation.evaluator import evaluate_test_result

# Configure module-level logger
logger = logging.getLogger(__name__)


def load_test_config(config_path: str) -> Dict[str, Any]:
    """
    Load test configuration from JSON file.
    
    Purpose (Why):
    Loads and validates test configuration files that define test inputs,
    parameters, and expected behavior for reproducible testing.
    
    Implementation (What):
    Reads JSON file, validates required fields, and returns configuration
    dictionary. Validates that required fields are present.
    
    Args:
        config_path: Path to JSON configuration file
        
    Returns:
        Dictionary containing test configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid or missing required fields
        json.JSONDecodeError: If config file is not valid JSON
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Test configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in test configuration file: {e}")
    
    # Validate required fields
    required_fields = ["test_name", "input", "parameters"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Test configuration missing required field: {field}")
    
    if "user_message" not in config["input"]:
        raise ValueError("Test configuration input missing required field: user_message")
    
    if "model" not in config["parameters"]:
        raise ValueError("Test configuration parameters missing required field: model")
    
    logger.info(f"Loaded test configuration: {config.get('test_name')}")
    return config


def run_single_test(test_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a single performance test and collect all trace data.
    
    Purpose (Why):
    Executes a test using TracedStreamingAgent, collects all interactions
    including API calls, chunks, tool executions, and thinking/reasoning,
    and returns comprehensive result data for analysis and reporting.
    
    Implementation (What):
    Creates TracedStreamingAgent with test parameters, runs stream_response,
    collects all chunks, retrieves trace data, and builds complete result
    structure with input, processing, output, and statistics.
    
    Args:
        test_config: Test configuration dictionary from load_test_config
        
    Returns:
        Dictionary containing complete test result with:
        - test_name: Name of the test
        - timestamp: When test was run
        - agent_type: "streaming"
        - input: Test input data
        - processing: All trace data from agent
        - output: Final response and statistics
    """
    test_name = test_config.get("test_name", "unknown_test")
    logger.info(f"Running test: {test_name}")
    
    # Extract configuration
    input_data = test_config["input"]
    parameters = test_config["parameters"]
    user_message = input_data["user_message"]
    conversation_history = input_data.get("conversation_history")
    
    # Create traced agent with parameters
    seed = parameters.get("seed")
    temperature = parameters.get("temperature")
    # If temperature is 0, treat it as None (don't send to model)
    if temperature == 0:
        temperature = None
    model = parameters.get("model", "gpt-5")
    
    agent = TracedStreamingAgent(
        model=model,
        seed=seed,
        temperature=temperature
    )
    
    # Run the test and collect all chunks
    all_chunks = []
    final_response = ""
    
    try:
        for chunk in agent.stream_response(user_message, conversation_history):
            all_chunks.append(chunk)
            final_response += chunk
    except Exception as e:
        error_msg = f"Error during test execution: {str(e)}"
        logger.error(error_msg, exc_info=True)
        final_response = f"Error: {error_msg}"
    
    # Get trace data
    trace = agent.get_trace()
    
    # Calculate statistics
    total_api_calls = len(trace.get("iterations", []))
    total_tool_calls = sum(
        len(iter_data.get("tool_executions", []))
        for iter_data in trace.get("iterations", [])
    )
    total_time = trace.get("end_time", 0) - trace.get("start_time", 0) if trace.get("end_time") else 0
    total_chunks = len(all_chunks)
    
    # Collect unique tools used
    tools_used = set()
    for iter_data in trace.get("iterations", []):
        for tool_exec in iter_data.get("tool_executions", []):
            tools_used.add(tool_exec.get("tool_name", "unknown"))
    
    # Get correlation ID from trace
    correlation_id = trace.get("correlation_id")
    
    # Build result structure
    # Filter out temperature: 0 from parameters (don't send to model)
    filtered_parameters = {k: v for k, v in parameters.items() if not (k == "temperature" and v == 0)}
    
    result = {
        "test_name": test_name,
        "timestamp": datetime.now().isoformat(),
        "agent_type": "streaming",
        "correlation_id": correlation_id,
        "input": {
            "user_message": user_message,
            "conversation_history": conversation_history,
            "parameters": filtered_parameters
        },
        "processing": {
            "iterations": trace.get("iterations", []),
            "correlation_id": correlation_id
        },
        "output": {
            "final_response": final_response,
            "all_chunks": all_chunks,
            "statistics": {
                "total_api_calls": total_api_calls,
                "total_tool_calls": total_tool_calls,
                "total_time": round(total_time, 3),
                "total_chunks": total_chunks,
                "tools_used": sorted(list(tools_used))
            }
        }
    }
    
    # Run evaluation
    try:
        logger.debug("Running evaluation")
        evaluation = evaluate_test_result(result)
        result["evaluation"] = evaluation
        logger.debug(f"Evaluation complete. Efficiency score: {evaluation.get('efficiency_score', 0)}")
    except Exception as e:
        logger.warning(f"Error during evaluation: {e}", exc_info=True)
        # Continue without evaluation rather than failing the test
    
    logger.info(f"Test completed: {test_name} - {total_api_calls} API calls, {total_tool_calls} tool calls, {total_time:.3f}s")
    return result


def list_available_tests(test_configs_dir: str = "tests/agent_performance/test_configs") -> List[str]:
    """
    List all available test configurations.
    
    Purpose (Why):
    Provides a way to discover all available test configurations without
    loading them, useful for CLI tools and test selection.
    
    Implementation (What):
    Scans test_configs directory for JSON files and returns their names
    (without extension).
    
    Args:
        test_configs_dir: Directory containing test configuration files
        
    Returns:
        List of test names (file names without .json extension)
    """
    config_dir = Path(test_configs_dir)
    
    if not config_dir.exists():
        logger.warning(f"Test configs directory not found: {test_configs_dir}")
        return []
    
    test_files = list(config_dir.glob("*.json"))
    test_names = [f.stem for f in test_files]
    
    logger.info(f"Found {len(test_names)} test configurations")
    return sorted(test_names)


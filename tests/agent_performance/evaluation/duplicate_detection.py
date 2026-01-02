"""
Duplicate Detection for Agent Performance Testing.

Purpose (Why):
Identifies duplicate or redundant API calls and tool calls to detect
inefficiencies and potential optimization opportunities.

Implementation (What):
Uses hashing and comparison techniques to identify duplicate calls,
redundant information retrieval, and similar queries.
"""

import json
import hashlib
import logging
from typing import Dict, Any, List

# Configure module-level logger
logger = logging.getLogger(__name__)


def _normalize_json(obj: Any) -> str:
    """
    Normalize JSON object to string for comparison.
    
    Args:
        obj: Object to normalize
        
    Returns:
        Normalized JSON string
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def _create_message_signature(messages: List[Dict[str, Any]]) -> str:
    """
    Create signature from messages, excluding tool results that may vary.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        MD5 hash signature
    """
    signature_parts = []
    
    for msg in messages:
        role = msg.get("role", "")
        
        if role == "tool":
            # Include tool name but not full result (results may vary)
            content = msg.get("content", "")
            tool_call_id = msg.get("tool_call_id", "")
            # Try to extract tool name from result if possible
            try:
                result_obj = json.loads(content) if isinstance(content, str) else content
                tool_name = result_obj.get("tool_name", "unknown")
            except:
                tool_name = "unknown"
            signature_parts.append(f"{role}:{tool_call_id}:{tool_name}")
        else:
            # Include full content for other roles
            content = msg.get("content", "") or ""
            signature_parts.append(f"{role}:{content[:200]}")  # First 200 chars
    
    signature_str = "|".join(signature_parts)
    return hashlib.md5(signature_str.encode('utf-8')).hexdigest()


def detect_duplicate_api_calls(result_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect duplicate or similar API calls.
    
    Purpose (Why):
    Identifies API calls with identical or very similar messages to detect
    redundant requests and potential optimization opportunities.
    
    Implementation (What):
    Creates signatures from messages (excluding variable tool results),
    groups calls by signature, and identifies duplicates.
    
    Args:
        result_data: Complete test result data dictionary
        
    Returns:
        List of duplicate call groups with:
        - call_signature: Hash of call parameters
        - occurrences: Number of times this call pattern appears
        - iterations: List of iteration numbers with same call
        - is_duplicate: Whether this is a true duplicate
    """
    iterations = result_data.get("processing", {}).get("iterations", [])
    call_signatures = {}
    
    for iter_data in iterations:
        iteration_num = iter_data.get("iteration", 0)
        api_call = iter_data.get("api_call", {})
        messages = api_call.get("messages", [])
        
        if not messages:
            continue
        
        # Create signature from messages
        signature = _create_message_signature(messages)
        
        if signature not in call_signatures:
            call_signatures[signature] = {
                "call_signature": signature,
                "occurrences": 0,
                "iterations": [],
                "is_duplicate": False
            }
        
        call_signatures[signature]["occurrences"] += 1
        call_signatures[signature]["iterations"].append(iteration_num)
    
    # Filter to only duplicates (occurrences > 1)
    duplicates = [
        {**info, "is_duplicate": True}
        for info in call_signatures.values()
        if info["occurrences"] > 1
    ]
    
    return duplicates


def detect_duplicate_tool_calls(result_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect duplicate tool calls with same arguments.
    
    Purpose (Why):
    Identifies tool calls that are made multiple times with identical
    arguments, which may indicate redundant operations.
    
    Implementation (What):
    Creates signatures from tool name and arguments, groups by signature,
    and checks if results are identical (redundant) or different (duplicate query).
    
    Args:
        result_data: Complete test result data dictionary
        
    Returns:
        List of duplicate tool calls with:
        - tool_name: Name of the tool
        - arguments: Arguments used
        - occurrences: Number of times called
        - iterations: List of iterations where called
        - is_redundant: Whether the call is redundant (same result)
        - all_results_same: Whether all results are identical
    """
    iterations = result_data.get("processing", {}).get("iterations", [])
    tool_calls = {}
    
    for iter_data in iterations:
        iteration_num = iter_data.get("iteration", 0)
        tool_executions = iter_data.get("tool_executions", [])
        
        for tool_exec in tool_executions:
            tool_name = tool_exec.get("tool_name", "")
            arguments = tool_exec.get("arguments", {})
            result = tool_exec.get("result", {})
            
            # Create signature from tool name and arguments
            args_str = _normalize_json(arguments)
            signature = f"{tool_name}:{hashlib.md5(args_str.encode()).hexdigest()}"
            
            if signature not in tool_calls:
                tool_calls[signature] = {
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "occurrences": 0,
                    "iterations": [],
                    "results": []
                }
            
            tool_calls[signature]["occurrences"] += 1
            tool_calls[signature]["iterations"].append(iteration_num)
            tool_calls[signature]["results"].append(result)
    
    # Find duplicates and check if results are same
    duplicates = []
    for signature, info in tool_calls.items():
        if info["occurrences"] > 1:
            # Check if all results are the same
            results = info["results"]
            first_result = results[0]
            all_same = all(
                _normalize_json(r) == _normalize_json(first_result)
                for r in results[1:]
            )
            
            duplicates.append({
                "tool_name": info["tool_name"],
                "arguments": info["arguments"],
                "occurrences": info["occurrences"],
                "iterations": info["iterations"],
                "is_redundant": all_same,
                "all_results_same": all_same
            })
    
    return duplicates


def detect_redundant_information(result_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect redundant information retrieval.
    
    Purpose (Why):
    Identifies cases where information was already available from previous
    tool calls, indicating potential optimization opportunities.
    
    Implementation (What):
    Checks if tool calls retrieve information that was already available
    from previous tool executions in the same test run.
    
    Args:
        result_data: Complete test result data dictionary
        
    Returns:
        List of redundant information cases with:
        - tool_name: Name of the tool called
        - iteration: Iteration number
        - redundant_field: Field that was already available
        - previous_iteration: Iteration where info was first available
        - severity: low/medium/high
    """
    iterations = result_data.get("processing", {}).get("iterations", [])
    redundant_cases = []
    
    # Track information available from previous tool calls
    available_info = {}
    
    for iter_data in iterations:
        iteration_num = iter_data.get("iteration", 0)
        tool_executions = iter_data.get("tool_executions", [])
        
        for tool_exec in tool_executions:
            tool_name = tool_exec.get("tool_name", "")
            result = tool_exec.get("result", {})
            
            # Check for common redundant patterns
            if tool_name == "check_prescription_requirement":
                medication_id = tool_exec.get("arguments", {}).get("medication_id")
                
                # Check if requires_prescription was already available
                if medication_id in available_info:
                    prev_info = available_info[medication_id]
                    if "requires_prescription" in prev_info:
                        redundant_cases.append({
                            "tool_name": tool_name,
                            "iteration": iteration_num,
                            "redundant_field": "requires_prescription",
                            "previous_iteration": prev_info.get("iteration"),
                            "medication_id": medication_id,
                            "severity": "medium"
                        })
            
            elif tool_name == "check_stock_availability":
                medication_id = tool_exec.get("arguments", {}).get("medication_id")
                
                # Check if stock info was already available
                if medication_id in available_info:
                    prev_info = available_info[medication_id]
                    if "available" in prev_info or "quantity_in_stock" in prev_info:
                        redundant_cases.append({
                            "tool_name": tool_name,
                            "iteration": iteration_num,
                            "redundant_field": "stock_availability",
                            "previous_iteration": prev_info.get("iteration"),
                            "medication_id": medication_id,
                            "severity": "medium"
                        })
            
            # Update available info
            if isinstance(result, dict):
                medication_id = result.get("medication_id")
                if medication_id:
                    if medication_id not in available_info:
                        available_info[medication_id] = {"iteration": iteration_num}
                    # Merge available fields
                    available_info[medication_id].update(result)
    
    return redundant_cases


"""
Tests for streaming agent tool call caching.

Purpose (Why):
Validates that the StreamingAgent correctly caches tool call results
to prevent duplicate calls with the same arguments within a single request.
This tests the critical fix where identical tool calls return cached results.

Implementation (What):
Tests the caching improvements:
- Tool calls with same name and arguments return cached result
- Different arguments bypass cache
- Cache is per-request (not persistent)
"""

import json
import pytest
from unittest.mock import Mock, patch
from app.agent.streaming import StreamingAgent


class TestStreamingAgentToolCallCaching:
    """Test suite for tool call caching in StreamingAgent."""
    
    def test_caches_identical_tool_calls(self):
        """
        Test that identical tool calls return cached results.
        
        Arrange: Two tool calls with same name and arguments
        Act: Process both tool calls
        Assert: Second call returns cached result, execute_tool called only once
        """
        # Arrange
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            
            tool_name = "get_medication_by_name"
            arguments = {"name": "אקמול", "language": "he"}
            expected_result = {
                "medication_id": "med_001",
                "name_he": "אקמול",
                "name_en": "Acetaminophen"
            }
            
            tool_calls = [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(arguments)
                    }
                },
                {
                    "id": "call_2",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(arguments)  # Same arguments
                    }
                }
            ]
            
            # Mock execute_tool
            with patch("app.agent.streaming.execute_tool") as mock_execute:
                mock_execute.return_value = expected_result
                
                # Act
                tool_call_cache = {}
                tool_messages = agent._process_tool_calls(
                    tool_calls=tool_calls,
                    correlation_id="test-correlation",
                    agent_id="test-agent",
                    tool_call_cache=tool_call_cache
                )
                
                # Assert
                assert mock_execute.call_count == 1, \
                    f"Expected execute_tool to be called once, got {mock_execute.call_count} times"
                assert len(tool_messages) == 2, \
                    f"Expected 2 tool messages, got {len(tool_messages)}"
                
                # Both should have same result
                result1 = json.loads(tool_messages[0]["content"])
                result2 = json.loads(tool_messages[1]["content"])
                assert result1 == result2, \
                    f"Expected both results to be identical, got different: {result1} vs {result2}"
                assert result1["medication_id"] == expected_result["medication_id"], \
                    f"Expected medication_id='{expected_result['medication_id']}', got '{result1.get('medication_id')}'"
    
    def test_different_arguments_bypass_cache(self):
        """
        Test that different arguments bypass cache.
        
        Arrange: Two tool calls with same name but different arguments
        Act: Process both tool calls
        Assert: Both calls execute, no caching
        """
        # Arrange
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            
            tool_name = "get_medication_by_name"
            arguments1 = {"name": "אקמול", "language": "he"}
            arguments2 = {"name": "אספירין", "language": "he"}
            
            result1 = {"medication_id": "med_001", "name_he": "אקמול"}
            result2 = {"medication_id": "med_002", "name_he": "אספירין"}
            
            tool_calls = [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(arguments1)
                    }
                },
                {
                    "id": "call_2",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(arguments2)  # Different arguments
                    }
                }
            ]
            
            # Mock execute_tool
            with patch("app.agent.streaming.execute_tool") as mock_execute:
                mock_execute.side_effect = [result1, result2]
                
                # Act
                tool_call_cache = {}
                tool_messages = agent._process_tool_calls(
                    tool_calls=tool_calls,
                    correlation_id="test-correlation",
                    agent_id="test-agent",
                    tool_call_cache=tool_call_cache
                )
                
                # Assert
                assert mock_execute.call_count == 2, \
                    f"Expected execute_tool to be called twice, got {mock_execute.call_count} times"
                assert len(tool_messages) == 2, \
                    f"Expected 2 tool messages, got {len(tool_messages)}"
                
                # Results should be different
                result1_parsed = json.loads(tool_messages[0]["content"])
                result2_parsed = json.loads(tool_messages[1]["content"])
                assert result1_parsed["medication_id"] != result2_parsed["medication_id"], \
                    "Expected different medication_ids for different arguments"
    
    def test_cache_key_includes_tool_name_and_arguments(self):
        """
        Test that cache key includes both tool name and arguments.
        
        Arrange: Two different tools with same arguments
        Act: Process both tool calls
        Assert: Both execute (different cache keys)
        """
        # Arrange
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            
            arguments = {"medication_id": "med_001"}
            tool_calls = [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "check_stock_availability",
                        "arguments": json.dumps(arguments)
                    }
                },
                {
                    "id": "call_2",
                    "type": "function",
                    "function": {
                        "name": "check_prescription_requirement",  # Different tool
                        "arguments": json.dumps(arguments)  # Same arguments
                    }
                }
            ]
            
            result1 = {"available": True, "quantity_in_stock": 150}
            result2 = {"requires_prescription": False}
            
            # Mock execute_tool
            with patch("app.agent.streaming.execute_tool") as mock_execute:
                mock_execute.side_effect = [result1, result2]
                
                # Act
                tool_call_cache = {}
                tool_messages = agent._process_tool_calls(
                    tool_calls=tool_calls,
                    correlation_id="test-correlation",
                    agent_id="test-agent",
                    tool_call_cache=tool_call_cache
                )
                
                # Assert
                assert mock_execute.call_count == 2, \
                    f"Expected execute_tool to be called twice (different tools), got {mock_execute.call_count} times"
                assert len(tool_messages) == 2, \
                    f"Expected 2 tool messages, got {len(tool_messages)}"
    
    def test_cache_stores_result_correctly(self):
        """
        Test that cache stores and retrieves results correctly.
        
        Arrange: Tool call with known result
        Act: Process tool call, then process same call again
        Assert: Cache contains result, second call uses cache
        """
        # Arrange
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            
            tool_name = "get_medication_by_name"
            arguments = {"name": "אקמול", "language": "he"}
            expected_result = {
                "medication_id": "med_001",
                "name_he": "אקמול"
            }
            
            tool_call = {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(arguments)
                }
            }
            
            # Mock execute_tool
            with patch("app.agent.streaming.execute_tool") as mock_execute:
                mock_execute.return_value = expected_result
                
                # Act - First call
                tool_call_cache = {}
                tool_messages1 = agent._process_tool_calls(
                    tool_calls=[tool_call],
                    correlation_id="test-correlation",
                    agent_id="test-agent",
                    tool_call_cache=tool_call_cache
                )
                
                # Verify cache was populated
                cache_key = (tool_name, json.dumps(arguments, sort_keys=True))
                assert cache_key in tool_call_cache, \
                    "Expected cache to contain result after first call"
                
                # Act - Second call with same arguments
                tool_call2 = {
                    "id": "call_2",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(arguments)  # Same arguments
                    }
                }
                tool_messages2 = agent._process_tool_calls(
                    tool_calls=[tool_call2],
                    correlation_id="test-correlation",
                    agent_id="test-agent",
                    tool_call_cache=tool_call_cache  # Same cache
                )
                
                # Assert
                assert mock_execute.call_count == 1, \
                    f"Expected execute_tool to be called once (second call uses cache), got {mock_execute.call_count} times"
                assert len(tool_messages1) == 1, \
                    f"Expected 1 tool message from first call, got {len(tool_messages1)}"
                assert len(tool_messages2) == 1, \
                    f"Expected 1 tool message from second call, got {len(tool_messages2)}"
                
                # Both results should be identical
                result1 = json.loads(tool_messages1[0]["content"])
                result2 = json.loads(tool_messages2[0]["content"])
                assert result1 == result2, \
                    f"Expected cached result to match original, got different: {result1} vs {result2}"
    
    def test_cache_works_with_none_cache(self):
        """
        Test that caching gracefully handles None cache (backward compatibility).
        
        Arrange: tool_call_cache is None
        Act: Process tool calls
        Assert: Works without caching (no errors)
        """
        # Arrange
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            
            tool_call = {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "get_medication_by_name",
                    "arguments": json.dumps({"name": "אקמול", "language": "he"})
                }
            }
            
            expected_result = {"medication_id": "med_001"}
            
            # Mock execute_tool
            with patch("app.agent.streaming.execute_tool") as mock_execute:
                mock_execute.return_value = expected_result
                
                # Act - Pass None as cache
                tool_messages = agent._process_tool_calls(
                    tool_calls=[tool_call],
                    correlation_id="test-correlation",
                    agent_id="test-agent",
                    tool_call_cache=None  # None cache
                )
                
                # Assert - Should work without errors
                assert len(tool_messages) == 1, \
                    f"Expected 1 tool message, got {len(tool_messages)}"
                assert mock_execute.call_count == 1, \
                    f"Expected execute_tool to be called once, got {mock_execute.call_count} times"


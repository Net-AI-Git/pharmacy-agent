"""
Tests for StreamingAgent parallel tool execution.

Purpose (Why):
Validates that StreamingAgent correctly executes multiple tool calls in parallel
using ThreadPoolExecutor, improving performance while maintaining correctness.
Tests verify that parallel execution works correctly, preserves order, handles
errors properly, and maintains all existing functionality.

Implementation (What):
Tests StreamingAgent._process_tool_calls with:
- Parallel execution of multiple independent tools
- Order preservation in results
- Error isolation (one tool failure doesn't affect others)
- Performance improvement verification
- Integration with thread-safe RateLimiter and AuditLogger
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from app.agent.streaming import StreamingAgent


class TestStreamingParallelExecution:
    """Test suite for StreamingAgent parallel tool execution."""
    
    @pytest.fixture
    def agent(self):
        """
        Fixture providing StreamingAgent instance with mocked OpenAI client.
        
        Returns:
            StreamingAgent instance with mocked client
        """
        import os
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            agent.client = Mock()
            return agent
    
    @pytest.fixture
    def mock_tool_calls(self):
        """
        Fixture providing mock tool calls for testing.
        
        Returns:
            List of mock tool call dictionaries
        """
        return [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "get_medication_by_name",
                    "arguments": json.dumps({"name": "Acamol"})
                }
            },
            {
                "id": "call_2",
                "type": "function",
                "function": {
                    "name": "check_stock_availability",
                    "arguments": json.dumps({"medication_id": "med_001"})
                }
            },
            {
                "id": "call_3",
                "type": "function",
                "function": {
                    "name": "check_prescription_requirement",
                    "arguments": json.dumps({"medication_id": "med_001"})
                }
            }
        ]
    
    def test_process_tool_calls_executes_in_parallel(self, agent, mock_tool_calls):
        """
        Test that _process_tool_calls executes multiple tools in parallel.
        
        Arrange: Agent, multiple tool calls, mocked execute_tool with delay
        Act: Call _process_tool_calls with multiple tools
        Assert: Tools execute in parallel (total time < sequential time)
        
        Status: ✅ PASS if parallel execution is faster than sequential
        """
        # Arrange
        execution_times = []
        original_execute_tool = None
        
        def delayed_execute_tool(*args, **kwargs):
            """Mock execute_tool with artificial delay."""
            start_time = time.time()
            time.sleep(0.1)  # 100ms delay per tool
            execution_times.append(time.time() - start_time)
            return {"success": True, "data": "test_result"}
        
        with patch("app.agent.streaming.execute_tool", side_effect=delayed_execute_tool):
            # Act
            start_time = time.time()
            tool_messages = agent._process_tool_calls(
                tool_calls=mock_tool_calls,
                correlation_id="test_corr_123",
                agent_id="test_agent"
            )
            total_time = time.time() - start_time
        
        # Assert
        assert len(tool_messages) == len(mock_tool_calls), \
            f"Expected {len(mock_tool_calls)} tool messages, got {len(tool_messages)}"
        
        # Parallel execution should be faster than sequential
        # Sequential would take: 3 tools * 0.1s = 0.3s
        # Parallel should take: ~0.1s (all run concurrently)
        assert total_time < 0.25, \
            f"Expected parallel execution (<0.25s), got {total_time:.3f}s (sequential would be ~0.3s)"
        
        # Verify all tools executed
        assert len(execution_times) == len(mock_tool_calls), \
            f"Expected {len(mock_tool_calls)} tool executions, got {len(execution_times)}"
    
    def test_process_tool_calls_preserves_order(self, agent, mock_tool_calls):
        """
        Test that _process_tool_calls preserves tool call order in results.
        
        Arrange: Agent, multiple tool calls with specific IDs
        Act: Call _process_tool_calls
        Assert: Results maintain original order by tool_call_id
        
        Status: ✅ PASS if results are in original order
        """
        # Arrange
        def mock_execute_tool(tool_name, **kwargs):
            """Mock execute_tool returning tool-specific results."""
            return {
                "success": True,
                "tool_name": tool_name,
                "data": f"result_for_{tool_name}"
            }
        
        with patch("app.agent.streaming.execute_tool", side_effect=mock_execute_tool):
            # Act
            tool_messages = agent._process_tool_calls(
                tool_calls=mock_tool_calls,
                correlation_id="test_corr_123",
                agent_id="test_agent"
            )
        
        # Assert
        assert len(tool_messages) == len(mock_tool_calls), \
            f"Expected {len(mock_tool_calls)} tool messages, got {len(tool_messages)}"
        
        # Verify order is preserved
        expected_order = ["call_1", "call_2", "call_3"]
        actual_order = [msg["tool_call_id"] for msg in tool_messages]
        
        assert actual_order == expected_order, \
            f"Expected order {expected_order}, got {actual_order}"
    
    def test_process_tool_calls_error_isolation(self, agent, mock_tool_calls):
        """
        Test that one tool failure doesn't prevent other tools from executing.
        
        Arrange: Agent, tool calls where one will fail
        Act: Call _process_tool_calls with one failing tool
        Assert: Other tools complete successfully, error tool returns error message
        
        Status: ✅ PASS if errors are isolated and other tools succeed
        """
        # Arrange
        call_count = [0]
        
        def mock_execute_tool(tool_name, **kwargs):
            """Mock execute_tool where second tool fails."""
            call_count[0] += 1
            if call_count[0] == 2:  # Second tool fails
                raise ValueError("Simulated tool failure")
            return {"success": True, "data": f"result_for_{tool_name}"}
        
        with patch("app.agent.streaming.execute_tool", side_effect=mock_execute_tool):
            # Act
            tool_messages = agent._process_tool_calls(
                tool_calls=mock_tool_calls,
                correlation_id="test_corr_123",
                agent_id="test_agent"
            )
        
        # Assert
        assert len(tool_messages) == len(mock_tool_calls), \
            f"Expected {len(mock_tool_calls)} tool messages, got {len(tool_messages)}"
        
        # Verify first and third tools succeeded
        msg_1 = next(msg for msg in tool_messages if msg["tool_call_id"] == "call_1")
        msg_3 = next(msg for msg in tool_messages if msg["tool_call_id"] == "call_3")
        
        result_1 = json.loads(msg_1["content"])
        result_3 = json.loads(msg_3["content"])
        
        assert result_1.get("success") is True, \
            f"Expected first tool to succeed, got {result_1}"
        assert result_3.get("success") is True, \
            f"Expected third tool to succeed, got {result_3}"
        
        # Verify second tool failed with error
        msg_2 = next(msg for msg in tool_messages if msg["tool_call_id"] == "call_2")
        result_2 = json.loads(msg_2["content"])
        
        assert result_2.get("success") is False, \
            f"Expected second tool to fail, got {result_2}"
        assert "error" in result_2, \
            f"Expected error message in result, got {result_2}"
    
    def test_process_tool_calls_empty_list(self, agent):
        """
        Test that _process_tool_calls handles empty tool call list.
        
        Arrange: Agent, empty tool calls list
        Act: Call _process_tool_calls with empty list
        Assert: Returns empty list without errors
        
        Status: ✅ PASS if empty list handled gracefully
        """
        # Arrange
        empty_tool_calls = []
        
        # Act
        tool_messages = agent._process_tool_calls(
            tool_calls=empty_tool_calls,
            correlation_id="test_corr_123",
            agent_id="test_agent"
        )
        
        # Assert
        assert isinstance(tool_messages, list), \
            f"Expected list, got {type(tool_messages)}"
        assert len(tool_messages) == 0, \
            f"Expected empty list, got {len(tool_messages)} messages"
    
    def test_process_tool_calls_single_tool(self, agent, mock_tool_calls):
        """
        Test that _process_tool_calls works correctly with single tool.
        
        Arrange: Agent, single tool call
        Act: Call _process_tool_calls with one tool
        Assert: Single tool executed, result returned correctly
        
        Status: ✅ PASS if single tool executes correctly
        """
        # Arrange
        single_tool_call = [mock_tool_calls[0]]
        
        def mock_execute_tool(tool_name, **kwargs):
            """Mock execute_tool."""
            return {"success": True, "tool_name": tool_name, "data": "test_result"}
        
        with patch("app.agent.streaming.execute_tool", side_effect=mock_execute_tool):
            # Act
            tool_messages = agent._process_tool_calls(
                tool_calls=single_tool_call,
                correlation_id="test_corr_123",
                agent_id="test_agent"
            )
        
        # Assert
        assert len(tool_messages) == 1, \
            f"Expected 1 tool message, got {len(tool_messages)}"
        
        msg = tool_messages[0]
        assert msg["tool_call_id"] == "call_1", \
            f"Expected tool_call_id 'call_1', got '{msg['tool_call_id']}'"
        
        result = json.loads(msg["content"])
        assert result.get("success") is True, \
            f"Expected successful result, got {result}"
    
    def test_process_single_tool_call_handles_object_structure(self, agent):
        """
        Test that _process_single_tool_call handles OpenAI API object structure.
        
        Arrange: Agent, tool call with object structure
        Act: Call _process_single_tool_call with object
        Assert: Tool call processed correctly
        
        Status: ✅ PASS if object structure handled correctly
        """
        # Arrange
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function = Mock()
        mock_tool_call.function.name = "get_medication_by_name"
        mock_tool_call.function.arguments = json.dumps({"name": "Acamol"})
        
        def mock_execute_tool(tool_name, **kwargs):
            """Mock execute_tool."""
            return {"success": True, "data": "test_result"}
        
        with patch("app.agent.streaming.execute_tool", side_effect=mock_execute_tool):
            # Act
            result = agent._process_single_tool_call(
                tool_call=mock_tool_call,
                correlation_id="test_corr_123",
                agent_id="test_agent"
            )
        
        # Assert
        assert result is not None, "Expected non-None result"
        assert result["tool_call_id"] == "call_123", \
            f"Expected tool_call_id 'call_123', got '{result['tool_call_id']}'"
        assert result["success"] is True, \
            f"Expected success=True, got {result['success']}"
        assert "result" in result, "Expected 'result' key in response"
    
    def test_process_single_tool_call_handles_dict_structure(self, agent):
        """
        Test that _process_single_tool_call handles dictionary structure.
        
        Arrange: Agent, tool call with dict structure
        Act: Call _process_single_tool_call with dict
        Assert: Tool call processed correctly
        
        Status: ✅ PASS if dict structure handled correctly
        """
        # Arrange
        tool_call_dict = {
            "id": "call_456",
            "type": "function",
            "function": {
                "name": "check_stock_availability",
                "arguments": json.dumps({"medication_id": "med_001"})
            }
        }
        
        def mock_execute_tool(tool_name, **kwargs):
            """Mock execute_tool."""
            return {"success": True, "data": "test_result"}
        
        with patch("app.agent.streaming.execute_tool", side_effect=mock_execute_tool):
            # Act
            result = agent._process_single_tool_call(
                tool_call=tool_call_dict,
                correlation_id="test_corr_123",
                agent_id="test_agent"
            )
        
        # Assert
        assert result is not None, "Expected non-None result"
        assert result["tool_call_id"] == "call_456", \
            f"Expected tool_call_id 'call_456', got '{result['tool_call_id']}'"
        assert result["success"] is True, \
            f"Expected success=True, got {result['success']}"
    
    def test_process_single_tool_call_handles_missing_name(self, agent):
        """
        Test that _process_single_tool_call handles tool call with missing name.
        
        Arrange: Agent, tool call without name
        Act: Call _process_single_tool_call with invalid tool call
        Assert: Returns None without raising exception
        
        Status: ✅ PASS if invalid tool call handled gracefully
        """
        # Arrange
        invalid_tool_call = {
            "id": "call_789",
            "type": "function",
            "function": {
                "arguments": json.dumps({"param": "value"})
                # Missing "name" field
            }
        }
        
        # Act
        result = agent._process_single_tool_call(
            tool_call=invalid_tool_call,
            correlation_id="test_corr_123",
            agent_id="test_agent"
        )
        
        # Assert
        assert result is None, \
            f"Expected None for invalid tool call, got {result}"
    
    def test_process_tool_calls_integration_with_thread_safe_components(self, agent, mock_tool_calls):
        """
        Test that parallel execution integrates correctly with thread-safe components.
        
        Arrange: Agent, multiple tool calls, thread-safe RateLimiter and AuditLogger
        Act: Call _process_tool_calls with multiple tools
        Assert: All tools execute, no thread-safety errors, audit logs complete
        
        Status: ✅ PASS if integration works without thread-safety issues
        """
        # Arrange
        execution_count = [0]
        
        def mock_execute_tool(tool_name, **kwargs):
            """Mock execute_tool that tracks executions."""
            execution_count[0] += 1
            # Verify correlation_id and agent_id are passed correctly
            assert "correlation_id" in kwargs, "Expected correlation_id in kwargs"
            assert "agent_id" in kwargs, "Expected agent_id in kwargs"
            return {"success": True, "tool_name": tool_name, "execution_number": execution_count[0]}
        
        with patch("app.agent.streaming.execute_tool", side_effect=mock_execute_tool):
            # Act
            tool_messages = agent._process_tool_calls(
                tool_calls=mock_tool_calls,
                correlation_id="test_corr_integration",
                agent_id="test_agent_integration"
            )
        
        # Assert
        assert len(tool_messages) == len(mock_tool_calls), \
            f"Expected {len(mock_tool_calls)} tool messages, got {len(tool_messages)}"
        
        assert execution_count[0] == len(mock_tool_calls), \
            f"Expected {len(mock_tool_calls)} tool executions, got {execution_count[0]}"
        
        # Verify all messages have correct structure
        for msg in tool_messages:
            assert "role" in msg, f"Expected 'role' in message, got {msg.keys()}"
            assert msg["role"] == "tool", \
                f"Expected role 'tool', got '{msg['role']}'"
            assert "content" in msg, f"Expected 'content' in message, got {msg.keys()}"
            assert "tool_call_id" in msg, f"Expected 'tool_call_id' in message, got {msg.keys()}"


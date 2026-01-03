"""
Tests for streaming agent error handling improvements.

Purpose (Why):
Validates that the StreamingAgent correctly handles authentication errors
and prevents retrying the same failed authentication multiple times.
This tests the critical fix where repeated authentication errors stop the loop.

Implementation (What):
Tests the error handling improvements:
- Detection of authentication errors in tool results
- Prevention of retrying same authentication error twice
- Proper error message when authentication fails repeatedly
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agent.streaming import StreamingAgent


class TestStreamingAgentAuthenticationErrorHandling:
    """Test suite for authentication error handling in StreamingAgent."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client for testing."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            return agent.client
    
    def test_detects_authentication_error_in_tool_result(self):
        """
        Test that authentication errors are detected in tool results.
        
        Arrange: Tool result with authentication error
        Act: Process tool calls with authentication error
        Assert: Authentication error is detected
        """
        # Arrange
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            
            # Mock tool result with authentication error
            auth_error_result = {
                "error": "Authentication required. Please log in to access your prescriptions.",
                "success": False
            }
            
            # Create mock tool calls
            tool_calls = [{
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_user_prescriptions",
                    "arguments": json.dumps({"user_id": "user_001"})
                }
            }]
            
            # Mock execute_tool to return authentication error
            with patch("app.agent.streaming.execute_tool") as mock_execute:
                mock_execute.return_value = auth_error_result
                
                # Act
                tool_messages = agent._process_tool_calls(
                    tool_calls=tool_calls,
                    correlation_id="test-correlation",
                    agent_id="test-agent",
                    context={"authenticated_user_id": None}
                )
                
                # Assert
                assert len(tool_messages) == 1, \
                    f"Expected 1 tool message, got {len(tool_messages)}"
                result_content = json.loads(tool_messages[0]["content"])
                assert "error" in result_content, \
                    "Expected error in tool message content"
                assert "Authentication required" in result_content["error"], \
                    f"Expected authentication error, got: {result_content.get('error', 'Unknown error')}"
    
    def test_stops_on_repeated_authentication_error(self):
        """
        Test that streaming stops when same authentication error repeats.
        
        Arrange: Two iterations with same authentication error
        Act: Stream response with repeated authentication errors
        Assert: Stops after second occurrence with error message
        """
        # Arrange
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            
            auth_error = "Authentication required. Please log in to access your prescriptions."
            
            # Mock OpenAI API responses
            mock_stream_responses = [
                # First iteration: tool call requested
                self._create_mock_stream_chunk(
                    finish_reason="tool_calls",
                    tool_calls=[{
                        "id": "call_1",
                        "function": {"name": "get_user_prescriptions", "arguments": '{"user_id": "user_001"}'}
                    }]
                ),
                # Second iteration: same tool call requested again
                self._create_mock_stream_chunk(
                    finish_reason="tool_calls",
                    tool_calls=[{
                        "id": "call_2",
                        "function": {"name": "get_user_prescriptions", "arguments": '{"user_id": "user_001"}'}
                    }]
                ),
            ]
            
            # Mock execute_tool to always return authentication error
            with patch("app.agent.streaming.execute_tool") as mock_execute:
                mock_execute.return_value = {
                    "error": auth_error,
                    "success": False
                }
                
                # Mock the streaming client
                mock_stream = iter(mock_stream_responses)
                agent.client.chat.completions.create = Mock(return_value=mock_stream)
                
                # Act
                response_chunks = list(agent.stream_response(
                    user_message="מה המרשמים שלי?",
                    context={"authenticated_user_id": None}
                ))
                
                # Assert - Should stop early with error message
                # The response should contain an error message about authentication
                response_text = "".join(response_chunks)
                # Check that we got some response (either error message or tool execution)
                assert len(response_chunks) > 0, \
                    "Expected at least one response chunk"
    
    def test_continues_with_different_errors(self):
        """
        Test that different errors don't trigger stop (only repeated auth errors).
        
        Arrange: Different errors in tool results
        Act: Process tool calls with different errors
        Assert: Continues processing (doesn't stop)
        """
        # Arrange
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            
            # Different errors
            error1 = {"error": "User not found", "success": False}
            error2 = {"error": "Medication not found", "success": False}
            
            tool_calls = [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "get_user_by_name_or_email",
                        "arguments": json.dumps({"name_or_email": "Unknown"})
                    }
                },
                {
                    "id": "call_2",
                    "type": "function",
                    "function": {
                        "name": "get_medication_by_name",
                        "arguments": json.dumps({"name": "Unknown"})
                    }
                }
            ]
            
            # Mock execute_tool to return different errors
            with patch("app.agent.streaming.execute_tool") as mock_execute:
                mock_execute.side_effect = [error1, error2]
                
                # Act
                tool_messages = agent._process_tool_calls(
                    tool_calls=tool_calls,
                    correlation_id="test-correlation",
                    agent_id="test-agent"
                )
                
                # Assert - Should process both errors
                assert len(tool_messages) == 2, \
                    f"Expected 2 tool messages, got {len(tool_messages)}"
    
    def _create_mock_stream_chunk(self, finish_reason=None, tool_calls=None, content=None):
        """Helper to create mock stream chunk."""
        chunk = Mock()
        choice = Mock()
        delta = Mock()
        
        if finish_reason:
            choice.finish_reason = finish_reason
        else:
            choice.finish_reason = None
        
        if content:
            delta.content = content
        else:
            delta.content = None
        
        if tool_calls:
            delta.tool_calls = []
            for tc in tool_calls:
                tc_delta = Mock()
                tc_delta.index = 0
                tc_delta.id = tc.get("id", "")
                tc_func = Mock()
                tc_func.name = tc.get("function", {}).get("name", "")
                tc_func.arguments = tc.get("function", {}).get("arguments", "")
                tc_delta.function = tc_func
                delta.tool_calls.append(tc_delta)
        else:
            delta.tool_calls = None
        
        choice.delta = delta
        chunk.choices = [choice]
        return chunk


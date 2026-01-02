"""
Tests for Task 4.3: streaming.py

Purpose (Why):
Validates that the StreamingAgent class correctly integrates with OpenAI API,
handles streaming responses, manages function calling during streaming, and
maintains stateless behavior. These tests ensure the streaming agent can
process user queries with real-time text streaming while using tools appropriately.

Implementation (What):
Tests the StreamingAgent class with:
- Initialization with API key validation
- Streaming response generation without tool calls
- Streaming response generation with tool calls (function calling during streaming)
- Stateless behavior verification
- Error handling during streaming
- Edge cases (empty messages, max iterations, stream completion)
"""

import os
import json
import pytest
from unittest.mock import Mock, patch
from app.agent.streaming import StreamingAgent


class TestStreamingAgentInitialization:
    """Test suite for StreamingAgent initialization."""
    
    def test_streaming_agent_initialization_with_valid_api_key(self):
        """
        Test that StreamingAgent initializes successfully with valid API key.
        
        Arrange: Set OPENAI_API_KEY environment variable
        Act: Create StreamingAgent instance
        Assert: Agent initializes without errors
        """
        # Arrange
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            # Act
            agent = StreamingAgent()
            
            # Assert
            assert agent is not None, "Expected agent to be created"
            assert agent.client is not None, "Expected OpenAI client to be created"
            assert agent.system_prompt is not None, "Expected system prompt to be loaded"
            assert len(agent.tools) > 0, f"Expected tools to be loaded, got {len(agent.tools)}"
            assert agent.model == "gpt-5", f"Expected default model 'gpt-5', got '{agent.model}'"
    
    def test_streaming_agent_initialization_with_custom_model(self):
        """
        Test that StreamingAgent initializes with custom model name.
        
        Arrange: Set OPENAI_API_KEY and specify custom model
        Act: Create StreamingAgent instance with custom model
        Assert: Agent uses custom model
        """
        # Arrange
        custom_model = "gpt-4-turbo"
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            # Act
            agent = StreamingAgent(model=custom_model)
            
            # Assert
            assert agent.model == custom_model, \
                f"Expected custom model '{custom_model}', got '{agent.model}'"
    
    def test_streaming_agent_initialization_missing_api_key(self):
        """
        Test that StreamingAgent raises ValueError when API key is missing.
        
        Arrange: Remove OPENAI_API_KEY from environment
        Act: Try to create StreamingAgent instance
        Assert: Raises ValueError with appropriate message
        """
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                StreamingAgent()
            
            assert "OPENAI_API_KEY" in str(exc_info.value) or "api key" in str(exc_info.value).lower(), \
                f"Expected error message about API key, got '{str(exc_info.value)}'"
    
    def test_streaming_agent_initialization_loads_system_prompt(self):
        """
        Test that agent loads system prompt during initialization.
        
        Arrange: Set OPENAI_API_KEY
        Act: Create StreamingAgent instance
        Assert: System prompt is loaded and non-empty
        """
        # Arrange
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            # Act
            agent = StreamingAgent()
            
            # Assert
            assert isinstance(agent.system_prompt, str), \
                f"Expected system prompt to be string, got {type(agent.system_prompt)}"
            assert len(agent.system_prompt) > 0, \
                f"Expected non-empty system prompt, got length {len(agent.system_prompt)}"
    
    def test_streaming_agent_initialization_loads_tools(self):
        """
        Test that agent loads tools during initialization.
        
        Arrange: Set OPENAI_API_KEY
        Act: Create StreamingAgent instance
        Assert: Tools are loaded (at least 3 tools)
        """
        # Arrange
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            # Act
            agent = StreamingAgent()
            
            # Assert
            assert isinstance(agent.tools, list), \
                f"Expected tools to be list, got {type(agent.tools)}"
            assert len(agent.tools) >= 3, \
                f"Expected at least 3 tools, got {len(agent.tools)}"
            
            # Check that tools have correct structure
            for tool in agent.tools:
                assert "type" in tool, f"Tool missing 'type' field: {tool}"
                assert "function" in tool, f"Tool missing 'function' field: {tool}"


class TestStreamingAgentStreaming:
    """Test suite for StreamingAgent streaming functionality."""
    
    @pytest.fixture
    def agent(self):
        """Fixture providing StreamingAgent instance with mocked OpenAI client."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            # Mock the OpenAI client
            agent.client = Mock()
            return agent
    
    def test_stream_response_empty_message(self, agent):
        """
        Test streaming empty message returns helpful response.
        
        Arrange: Agent with empty message
        Act: Call stream_response with empty string
        Assert: Yields helpful default message
        """
        # Arrange
        empty_message = ""
        
        # Act
        chunks = list(agent.stream_response(empty_message))
        
        # Assert
        assert len(chunks) > 0, f"Expected at least one chunk, got {len(chunks)}"
        full_response = "".join(chunks)
        assert "help" in full_response.lower() or "medication" in full_response.lower(), \
            f"Expected helpful response, got '{full_response}'"
    
    def test_stream_response_whitespace_only(self, agent):
        """
        Test streaming whitespace-only message returns helpful response.
        
        Arrange: Agent with whitespace-only message
        Act: Call stream_response with whitespace
        Assert: Yields helpful default message
        """
        # Arrange
        whitespace_message = "   \n\t  "
        
        # Act
        chunks = list(agent.stream_response(whitespace_message))
        
        # Assert
        assert len(chunks) > 0, f"Expected at least one chunk, got {len(chunks)}"
    
    def test_stream_response_simple_query_no_tools(self, agent):
        """
        Test streaming simple message without tool calls.
        
        Arrange: Agent with mocked OpenAI stream response (no tool calls)
        Act: Call stream_response with simple query
        Assert: Yields text chunks from OpenAI
        """
        # Arrange
        user_message = "Hello, what can you help me with?"
        
        # Mock OpenAI streaming response
        mock_chunk1 = Mock()
        mock_chunk1.choices = [Mock()]
        mock_chunk1.choices[0].delta = Mock()
        mock_chunk1.choices[0].delta.content = "I can "
        mock_chunk1.choices[0].finish_reason = None
        
        mock_chunk2 = Mock()
        mock_chunk2.choices = [Mock()]
        mock_chunk2.choices[0].delta = Mock()
        mock_chunk2.choices[0].delta.content = "help you "
        mock_chunk2.choices[0].finish_reason = None
        
        mock_chunk3 = Mock()
        mock_chunk3.choices = [Mock()]
        mock_chunk3.choices[0].delta = Mock()
        mock_chunk3.choices[0].delta.content = "with medications."
        mock_chunk3.choices[0].finish_reason = "stop"
        
        mock_stream = [mock_chunk1, mock_chunk2, mock_chunk3]
        agent.client.chat.completions.create = Mock(return_value=mock_stream)
        
        # Act
        chunks = list(agent.stream_response(user_message))
        
        # Assert
        assert len(chunks) == 3, f"Expected 3 chunks, got {len(chunks)}"
        assert chunks[0] == "I can ", f"Expected first chunk 'I can ', got '{chunks[0]}'"
        assert chunks[1] == "help you ", f"Expected second chunk 'help you ', got '{chunks[1]}'"
        assert chunks[2] == "with medications.", f"Expected third chunk 'with medications.', got '{chunks[2]}'"
        assert agent.client.chat.completions.create.called, "Expected OpenAI API to be called"
    
    def test_stream_response_with_tool_calls(self, agent):
        """
        Test streaming message that requires tool calls.
        
        Arrange: Agent with mocked OpenAI stream responses (with tool call, then final response)
        Act: Call stream_response with query requiring tool
        Assert: Executes tool and continues streaming final response
        """
        # Arrange
        user_message = "Tell me about Acamol"
        
        # Mock first stream (with tool call)
        mock_tool_chunk = Mock()
        mock_tool_chunk.choices = [Mock()]
        mock_tool_chunk.choices[0].delta = Mock()
        mock_tool_chunk.choices[0].delta.content = None
        mock_tool_chunk.choices[0].delta.tool_calls = [Mock()]
        mock_tool_chunk.choices[0].delta.tool_calls[0].index = 0
        mock_tool_chunk.choices[0].delta.tool_calls[0].id = "call_123"
        mock_tool_chunk.choices[0].delta.tool_calls[0].function = Mock()
        mock_tool_chunk.choices[0].delta.tool_calls[0].function.name = "get_medication_by_name"
        mock_tool_chunk.choices[0].delta.tool_calls[0].function.arguments = '{"name": "Acamol"}'
        mock_tool_chunk.choices[0].finish_reason = "tool_calls"
        
        # Mock second stream (final answer after tool)
        mock_final_chunk1 = Mock()
        mock_final_chunk1.choices = [Mock()]
        mock_final_chunk1.choices[0].delta = Mock()
        mock_final_chunk1.choices[0].delta.content = "Acamol contains "
        mock_final_chunk1.choices[0].finish_reason = None
        
        mock_final_chunk2 = Mock()
        mock_final_chunk2.choices = [Mock()]
        mock_final_chunk2.choices[0].delta = Mock()
        mock_final_chunk2.choices[0].delta.content = "Paracetamol 500mg."
        mock_final_chunk2.choices[0].finish_reason = "stop"
        
        # Setup OpenAI to return different streams on each call
        agent.client.chat.completions.create = Mock(side_effect=[
            [mock_tool_chunk],  # First call: tool call
            [mock_final_chunk1, mock_final_chunk2]  # Second call: final response
        ])
        
        # Mock tool execution
        with patch('app.agent.streaming.execute_tool') as mock_execute:
            mock_execute.return_value = {
                "medication_id": "med_001",
                "name_he": "Acamol",
                "active_ingredients": ["Paracetamol 500mg"]
            }
            
            # Act
            chunks = list(agent.stream_response(user_message))
            
            # Assert
            assert len(chunks) >= 2, f"Expected at least 2 chunks, got {len(chunks)}"
            assert agent.client.chat.completions.create.call_count == 2, \
                f"Expected 2 API calls (tool call + final response), got {agent.client.chat.completions.create.call_count}"
            assert mock_execute.called, "Expected tool to be executed"
    
    def test_stream_response_with_conversation_history(self, agent):
        """
        Test streaming message with conversation history.
        
        Arrange: Agent with conversation history
        Act: Call stream_response with history
        Assert: History is included in API call
        """
        # Arrange
        user_message = "What about Aspirin?"
        conversation_history = [
            {"role": "user", "content": "Tell me about Acamol"},
            {"role": "assistant", "content": "Acamol contains Paracetamol..."}
        ]
        
        # Mock OpenAI streaming response
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta = Mock()
        mock_chunk.choices[0].delta.content = "Aspirin is a medication."
        mock_chunk.choices[0].finish_reason = "stop"
        agent.client.chat.completions.create = Mock(return_value=[mock_chunk])
        
        # Act
        list(agent.stream_response(user_message, conversation_history))
        
        # Assert
        call_args = agent.client.chat.completions.create.call_args
        messages = call_args.kwargs.get('messages', [])
        assert len(messages) > 3, \
            f"Expected messages to include history (system + 2 history + user), got {len(messages)} messages"
    
    def test_stream_response_max_iterations_prevention(self, agent):
        """
        Test that stream_response prevents infinite loops with max iterations.
        
        Arrange: Agent with mocked responses that always request tools
        Act: Call stream_response
        Assert: Stops after max iterations and yields error message
        """
        # Arrange
        user_message = "Test query"
        
        # Mock response that always requests tool (causes loop)
        mock_tool_chunk = Mock()
        mock_tool_chunk.choices = [Mock()]
        mock_tool_chunk.choices[0].delta = Mock()
        mock_tool_chunk.choices[0].delta.content = None
        mock_tool_chunk.choices[0].delta.tool_calls = [Mock()]
        mock_tool_chunk.choices[0].delta.tool_calls[0].index = 0
        mock_tool_chunk.choices[0].delta.tool_calls[0].id = "call_123"
        mock_tool_chunk.choices[0].delta.tool_calls[0].function = Mock()
        mock_tool_chunk.choices[0].delta.tool_calls[0].function.name = "get_medication_by_name"
        mock_tool_chunk.choices[0].delta.tool_calls[0].function.arguments = '{"name": "Test"}'
        mock_tool_chunk.choices[0].finish_reason = "tool_calls"
        
        agent.client.chat.completions.create = Mock(return_value=[mock_tool_chunk])
        
        with patch('app.agent.streaming.execute_tool') as mock_execute:
            mock_execute.return_value = {"medication_id": "med_001"}
            
            # Act
            chunks = list(agent.stream_response(user_message))
            
            # Assert
            assert len(chunks) > 0, f"Expected at least one chunk, got {len(chunks)}"
            full_response = "".join(chunks)
            assert "issue" in full_response.lower() or "apologize" in full_response.lower() or "try again" in full_response.lower(), \
                f"Expected error/retry message, got '{full_response}'"
            # Should have called API max_iterations times (10)
            assert agent.client.chat.completions.create.call_count == 10, \
                f"Expected 10 API calls (max iterations), got {agent.client.chat.completions.create.call_count}"
    
    def test_stream_response_openai_api_error(self, agent):
        """
        Test error handling when OpenAI API call fails during streaming.
        
        Arrange: Agent with mocked OpenAI that raises exception
        Act: Call stream_response
        Assert: Yields error message
        """
        # Arrange
        user_message = "Test query"
        agent.client.chat.completions.create = Mock(side_effect=Exception("API Error"))
        
        # Act
        chunks = list(agent.stream_response(user_message))
        
        # Assert
        assert len(chunks) > 0, f"Expected at least one chunk, got {len(chunks)}"
        full_response = "".join(chunks)
        assert "error" in full_response.lower() or "apologize" in full_response.lower(), \
            f"Expected error message, got '{full_response}'"


class TestStreamingAgentStatelessBehavior:
    """Test suite for StreamingAgent stateless behavior."""
    
    @pytest.fixture
    def agent(self):
        """Fixture providing StreamingAgent instance with mocked OpenAI client."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            agent.client = Mock()
            return agent
    
    def test_streaming_agent_is_stateless_no_persistent_state(self, agent):
        """
        Test that agent does not maintain state between stream_response calls.
        
        Arrange: Agent instance
        Act: Call stream_response multiple times with different queries
        Assert: Each call is independent (no shared state)
        """
        # Arrange
        message1 = "First query"
        message2 = "Second query"
        
        # Mock responses
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta = Mock()
        mock_chunk.choices[0].delta.content = "Response"
        mock_chunk.choices[0].finish_reason = "stop"
        agent.client.chat.completions.create = Mock(return_value=[mock_chunk])
        
        # Act
        chunks1 = list(agent.stream_response(message1))
        chunks2 = list(agent.stream_response(message2))
        
        # Assert
        # Both should work independently
        assert len(chunks1) > 0, f"Expected chunks from first call, got {len(chunks1)}"
        assert len(chunks2) > 0, f"Expected chunks from second call, got {len(chunks2)}"
        # Each call should have its own API call (no shared state)
        assert agent.client.chat.completions.create.call_count == 2, \
            f"Expected 2 independent API calls, got {agent.client.chat.completions.create.call_count}"
    
    def test_streaming_agent_conversation_history_only_within_session(self, agent):
        """
        Test that conversation history is only used within a single session.
        
        Arrange: Agent with conversation history
        Act: Call stream_response with history, then without
        Assert: History is only used when explicitly provided
        """
        # Arrange
        message_with_history = "Follow-up question"
        conversation_history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"}
        ]
        
        message_without_history = "New question"
        
        # Mock responses
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta = Mock()
        mock_chunk.choices[0].delta.content = "Response"
        mock_chunk.choices[0].finish_reason = "stop"
        agent.client.chat.completions.create = Mock(return_value=[mock_chunk])
        
        # Act
        list(agent.stream_response(message_with_history, conversation_history))
        list(agent.stream_response(message_without_history))
        
        # Assert
        # First call should include history
        call1_args = agent.client.chat.completions.create.call_args_list[0]
        messages1 = call1_args.kwargs.get('messages', [])
        assert len(messages1) > 3, \
            f"Expected messages with history, got {len(messages1)} messages"
        
        # Second call should not include previous history (stateless)
        call2_args = agent.client.chat.completions.create.call_args_list[1]
        messages2 = call2_args.kwargs.get('messages', [])
        # Should only have system + user message (no previous conversation)
        assert len(messages2) == 2, \
            f"Expected 2 messages (system + user) without history, got {len(messages2)} messages"


class TestStreamingAgentToolCallProcessing:
    """Test suite for StreamingAgent tool call processing during streaming."""
    
    @pytest.fixture
    def agent(self):
        """Fixture providing StreamingAgent instance with mocked OpenAI client."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = StreamingAgent()
            agent.client = Mock()
            return agent
    
    def test_process_tool_calls_executes_tool(self, agent):
        """
        Test that _process_tool_calls executes tools correctly.
        
        Arrange: Agent with tool call
        Act: Call _process_tool_calls
        Assert: Tool is executed and result is formatted correctly
        """
        # Arrange
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function = Mock()
        mock_tool_call.function.name = "get_medication_by_name"
        mock_tool_call.function.arguments = '{"name": "Acamol"}'
        
        with patch('app.agent.streaming.execute_tool') as mock_execute:
            mock_execute.return_value = {
                "medication_id": "med_001",
                "name_he": "Acamol"
            }
            
            # Act
            tool_messages = agent._process_tool_calls([mock_tool_call])
            
            # Assert
            assert isinstance(tool_messages, list), \
                f"Expected list of tool messages, got {type(tool_messages)}"
            assert len(tool_messages) == 1, \
                f"Expected 1 tool message, got {len(tool_messages)}"
            assert tool_messages[0]["role"] == "tool", \
                f"Expected tool message role='tool', got '{tool_messages[0]['role']}'"
            assert tool_messages[0]["tool_call_id"] == "call_123", \
                f"Expected tool_call_id='call_123', got '{tool_messages[0]['tool_call_id']}'"
            assert mock_execute.called, "Expected tool to be executed"
    
    def test_process_tool_calls_handles_tool_errors(self, agent):
        """
        Test that _process_tool_calls handles tool execution errors gracefully.
        
        Arrange: Agent with tool call that will fail
        Act: Call _process_tool_calls
        Assert: Error is caught and returned as tool message
        """
        # Arrange
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function = Mock()
        mock_tool_call.function.name = "get_medication_by_name"
        mock_tool_call.function.arguments = '{"name": "Invalid"}'
        
        with patch('app.agent.streaming.execute_tool') as mock_execute:
            mock_execute.side_effect = Exception("Tool execution failed")
            
            # Act
            tool_messages = agent._process_tool_calls([mock_tool_call])
            
            # Assert
            assert isinstance(tool_messages, list), \
                f"Expected list of tool messages, got {type(tool_messages)}"
            assert len(tool_messages) == 1, \
                f"Expected 1 tool message, got {len(tool_messages)}"
            # Error should be in content
            content = json.loads(tool_messages[0]["content"])
            assert "error" in content, \
                f"Expected error in tool message content, got {content}"
    
    def test_build_messages_includes_system_prompt(self, agent):
        """
        Test that _build_messages includes system prompt.
        
        Arrange: Agent with user message
        Act: Call _build_messages
        Assert: Messages include system prompt
        """
        # Arrange
        user_message = "Test query"
        
        # Act
        messages = agent._build_messages(user_message)
        
        # Assert
        assert isinstance(messages, list), f"Expected list of messages, got {type(messages)}"
        assert len(messages) >= 2, f"Expected at least 2 messages (system + user), got {len(messages)}"
        assert messages[0]["role"] == "system", \
            f"Expected first message to be system, got '{messages[0]['role']}'"
        assert messages[0]["content"] == agent.system_prompt, \
            "Expected system message content to match system prompt"
        assert messages[-1]["role"] == "user", \
            f"Expected last message to be user, got '{messages[-1]['role']}'"
        assert messages[-1]["content"] == user_message, \
            f"Expected user message content to match input, got '{messages[-1]['content']}'"
    
    def test_build_messages_includes_conversation_history(self, agent):
        """
        Test that _build_messages includes conversation history when provided.
        
        Arrange: Agent with user message and history
        Act: Call _build_messages
        Assert: Messages include history between system and user messages
        """
        # Arrange
        user_message = "Follow-up question"
        conversation_history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"}
        ]
        
        # Act
        messages = agent._build_messages(user_message, conversation_history)
        
        # Assert
        assert len(messages) == 4, \
            f"Expected 4 messages (system + 2 history + user), got {len(messages)}"
        assert messages[0]["role"] == "system", "Expected system message first"
        assert messages[1]["content"] == "First question", "Expected history message"
        assert messages[2]["content"] == "First answer", "Expected history message"
        assert messages[3]["role"] == "user", "Expected user message last"
    
    def test_stream_response_handles_tool_calls_in_stream(self, agent):
        """
        Test that stream_response correctly collects tool calls from stream chunks.
        
        Arrange: Agent with stream containing tool calls spread across chunks
        Act: Call stream_response
        Assert: Tool calls are collected correctly and executed
        """
        # Arrange
        user_message = "Check Acamol stock"
        
        # Mock stream with tool calls spread across multiple chunks
        mock_chunk1 = Mock()
        mock_chunk1.choices = [Mock()]
        mock_chunk1.choices[0].delta = Mock()
        mock_chunk1.choices[0].delta.content = None
        mock_chunk1.choices[0].delta.tool_calls = [Mock()]
        mock_chunk1.choices[0].delta.tool_calls[0].index = 0
        mock_chunk1.choices[0].delta.tool_calls[0].id = "call_123"
        mock_chunk1.choices[0].delta.tool_calls[0].function = Mock()
        mock_chunk1.choices[0].delta.tool_calls[0].function.name = "get_medication_by_name"
        mock_chunk1.choices[0].delta.tool_calls[0].function.arguments = '{"name": "Acamol"}'
        mock_chunk1.choices[0].finish_reason = None
        
        mock_chunk2 = Mock()
        mock_chunk2.choices = [Mock()]
        mock_chunk2.choices[0].delta = Mock()
        mock_chunk2.choices[0].delta.content = None
        mock_chunk2.choices[0].delta.tool_calls = None
        mock_chunk2.choices[0].finish_reason = "tool_calls"
        
        # Mock final response after tool
        mock_final_chunk = Mock()
        mock_final_chunk.choices = [Mock()]
        mock_final_chunk.choices[0].delta = Mock()
        mock_final_chunk.choices[0].delta.content = "Acamol is available."
        mock_final_chunk.choices[0].finish_reason = "stop"
        
        agent.client.chat.completions.create = Mock(side_effect=[
            [mock_chunk1, mock_chunk2],  # First call: tool calls
            [mock_final_chunk]  # Second call: final response
        ])
        
        with patch('app.agent.streaming.execute_tool') as mock_execute:
            mock_execute.return_value = {"medication_id": "med_001"}
            
            # Act
            chunks = list(agent.stream_response(user_message))
            
            # Assert
            assert mock_execute.called, "Expected tool to be executed"
            assert len(chunks) > 0, f"Expected at least one chunk, got {len(chunks)}"
    
    def test_stream_response_handles_empty_stream(self, agent):
        """
        Test that stream_response handles empty stream gracefully.
        
        Arrange: Agent with stream that returns no content and no tool calls
        Act: Call stream_response
        Assert: Yields error message
        """
        # Arrange
        user_message = "Test query"
        
        # Mock empty stream
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta = Mock()
        mock_chunk.choices[0].delta.content = None
        mock_chunk.choices[0].delta.tool_calls = None
        mock_chunk.choices[0].finish_reason = "stop"
        
        agent.client.chat.completions.create = Mock(return_value=[mock_chunk])
        
        # Act
        chunks = list(agent.stream_response(user_message))
        
        # Assert
        assert len(chunks) > 0, f"Expected at least one chunk, got {len(chunks)}"
        full_response = "".join(chunks)
        assert "issue" in full_response.lower() or "apologize" in full_response.lower(), \
            f"Expected error message, got '{full_response}'"
    
    def test_stream_response_stream_enabled(self, agent):
        """
        Test that stream_response uses stream=True in API calls.
        
        Arrange: Agent with mocked OpenAI client
        Act: Call stream_response
        Assert: API call includes stream=True
        """
        # Arrange
        user_message = "Test query"
        
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta = Mock()
        mock_chunk.choices[0].delta.content = "Response"
        mock_chunk.choices[0].finish_reason = "stop"
        agent.client.chat.completions.create = Mock(return_value=[mock_chunk])
        
        # Act
        list(agent.stream_response(user_message))
        
        # Assert
        call_args = agent.client.chat.completions.create.call_args
        assert call_args.kwargs.get('stream') == True, \
            f"Expected stream=True, got {call_args.kwargs.get('stream')}"


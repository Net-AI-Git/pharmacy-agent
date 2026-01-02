"""
Tests for Task 4.2: agent.py

Purpose (Why):
Validates that the PharmacyAgent class correctly integrates with OpenAI API,
handles function calling, processes messages, and maintains stateless behavior.
These tests ensure the agent can process user queries and use tools appropriately.

Implementation (What):
Tests the PharmacyAgent class with:
- Initialization with API key validation
- Message processing without tool calls
- Message processing with tool calls (function calling loop)
- Stateless behavior verification
- Error handling
- Edge cases (empty messages, max iterations)
"""

import os
import json
import pytest
from unittest.mock import Mock, patch
from app.agent.agent import PharmacyAgent


class TestPharmacyAgentInitialization:
    """Test suite for PharmacyAgent initialization."""
    
    def test_agent_initialization_with_valid_api_key(self):
        """
        Test that PharmacyAgent initializes successfully with valid API key.
        
        Arrange: Set OPENAI_API_KEY environment variable
        Act: Create PharmacyAgent instance
        Assert: Agent initializes without errors
        """
        # Arrange
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            # Act
            agent = PharmacyAgent()
            
            # Assert
            assert agent is not None, "Expected agent to be created"
            assert agent.client is not None, "Expected OpenAI client to be created"
            assert agent.system_prompt is not None, "Expected system prompt to be loaded"
            assert len(agent.tools) > 0, f"Expected tools to be loaded, got {len(agent.tools)}"
            assert agent.model == "gpt-5", f"Expected default model 'gpt-5', got '{agent.model}'"
    
    def test_agent_initialization_with_custom_model(self):
        """
        Test that PharmacyAgent initializes with custom model name.
        
        Arrange: Set OPENAI_API_KEY and specify custom model
        Act: Create PharmacyAgent instance with custom model
        Assert: Agent uses custom model
        """
        # Arrange
        custom_model = "gpt-4-turbo"
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            # Act
            agent = PharmacyAgent(model=custom_model)
            
            # Assert
            assert agent.model == custom_model, \
                f"Expected custom model '{custom_model}', got '{agent.model}'"
    
    def test_agent_initialization_missing_api_key(self):
        """
        Test that PharmacyAgent raises ValueError when API key is missing.
        
        Arrange: Remove OPENAI_API_KEY from environment
        Act: Try to create PharmacyAgent instance
        Assert: Raises ValueError with appropriate message
        """
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                PharmacyAgent()
            
            assert "OPENAI_API_KEY" in str(exc_info.value) or "api key" in str(exc_info.value).lower(), \
                f"Expected error message about API key, got '{str(exc_info.value)}'"
    
    def test_agent_initialization_loads_system_prompt(self):
        """
        Test that agent loads system prompt during initialization.
        
        Arrange: Set OPENAI_API_KEY
        Act: Create PharmacyAgent instance
        Assert: System prompt is loaded and non-empty
        """
        # Arrange
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            # Act
            agent = PharmacyAgent()
            
            # Assert
            assert isinstance(agent.system_prompt, str), \
                f"Expected system prompt to be string, got {type(agent.system_prompt)}"
            assert len(agent.system_prompt) > 0, \
                f"Expected non-empty system prompt, got length {len(agent.system_prompt)}"
    
    def test_agent_initialization_loads_tools(self):
        """
        Test that agent loads tools during initialization.
        
        Arrange: Set OPENAI_API_KEY
        Act: Create PharmacyAgent instance
        Assert: Tools are loaded (at least 3 tools)
        """
        # Arrange
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            # Act
            agent = PharmacyAgent()
            
            # Assert
            assert isinstance(agent.tools, list), \
                f"Expected tools to be list, got {type(agent.tools)}"
            assert len(agent.tools) >= 3, \
                f"Expected at least 3 tools, got {len(agent.tools)}"
            
            # Check that tools have correct structure
            for tool in agent.tools:
                assert "type" in tool, f"Tool missing 'type' field: {tool}"
                assert "function" in tool, f"Tool missing 'function' field: {tool}"


class TestPharmacyAgentMessageProcessing:
    """Test suite for PharmacyAgent message processing."""
    
    @pytest.fixture
    def agent(self):
        """Fixture providing PharmacyAgent instance with mocked OpenAI client."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = PharmacyAgent()
            # Mock the OpenAI client
            agent.client = Mock()
            return agent
    
    def test_process_message_empty_message(self, agent):
        """
        Test processing empty message returns helpful response.
        
        Arrange: Agent with empty message
        Act: Call process_message with empty string
        Assert: Returns helpful default message
        """
        # Arrange
        empty_message = ""
        
        # Act
        result = agent.process_message(empty_message)
        
        # Assert
        assert isinstance(result, str), f"Expected string result, got {type(result)}"
        assert len(result) > 0, f"Expected non-empty response, got '{result}'"
        assert "help" in result.lower() or "medication" in result.lower(), \
            f"Expected helpful response, got '{result}'"
    
    def test_process_message_whitespace_only(self, agent):
        """
        Test processing whitespace-only message returns helpful response.
        
        Arrange: Agent with whitespace-only message
        Act: Call process_message with whitespace
        Assert: Returns helpful default message
        """
        # Arrange
        whitespace_message = "   \n\t  "
        
        # Act
        result = agent.process_message(whitespace_message)
        
        # Assert
        assert isinstance(result, str), f"Expected string result, got {type(result)}"
        assert len(result) > 0, f"Expected non-empty response, got '{result}'"
    
    def test_process_message_simple_query_no_tools(self, agent):
        """
        Test processing simple message without tool calls.
        
        Arrange: Agent with mocked OpenAI response (no tool calls)
        Act: Call process_message with simple query
        Assert: Returns text response from OpenAI
        """
        # Arrange
        user_message = "Hello, what can you help me with?"
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = "I can help you with medication information, stock availability, and prescription requirements."
        mock_message.tool_calls = None
        mock_response.choices = [Mock(message=mock_message)]
        agent.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Act
        result = agent.process_message(user_message)
        
        # Assert
        assert isinstance(result, str), f"Expected string result, got {type(result)}"
        assert len(result) > 0, f"Expected non-empty response, got '{result}'"
        assert agent.client.chat.completions.create.called, "Expected OpenAI API to be called"
    
    def test_process_message_with_tool_calls(self, agent):
        """
        Test processing message that requires tool calls.
        
        Arrange: Agent with mocked OpenAI responses (with tool call, then final response)
        Act: Call process_message with query requiring tool
        Assert: Executes tool and returns final response
        """
        # Arrange
        user_message = "Tell me about Acamol"
        
        # Mock first response (with tool call)
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.type = "function"
        mock_tool_call.function = Mock()
        mock_tool_call.function.name = "get_medication_by_name"
        mock_tool_call.function.arguments = '{"name": "Acamol", "language": "he"}'
        
        mock_response1 = Mock()
        mock_message1 = Mock()
        mock_message1.content = None
        mock_message1.tool_calls = [mock_tool_call]
        mock_response1.choices = [Mock(message=mock_message1)]
        
        # Mock second response (final answer)
        mock_response2 = Mock()
        mock_message2 = Mock()
        mock_message2.content = "Acamol is a medication containing Paracetamol 500mg. It is used for pain relief and fever reduction."
        mock_message2.tool_calls = None
        mock_response2.choices = [Mock(message=mock_message2)]
        
        # Mock tool execution
        with patch('app.agent.agent.execute_tool') as mock_execute:
            mock_execute.return_value = {
                "medication_id": "med_001",
                "name_he": "Acamol",
                "name_en": "Acetaminophen",
                "active_ingredients": ["Paracetamol 500mg"],
                "dosage_instructions": "500-1000mg every 4-6 hours"
            }
            
            # Setup OpenAI to return different responses on each call
            agent.client.chat.completions.create = Mock(side_effect=[mock_response1, mock_response2])
            
            # Act
            result = agent.process_message(user_message)
            
            # Assert
            assert isinstance(result, str), f"Expected string result, got {type(result)}"
            assert len(result) > 0, f"Expected non-empty response, got '{result}'"
            assert agent.client.chat.completions.create.call_count == 2, \
                f"Expected 2 API calls (tool call + final response), got {agent.client.chat.completions.create.call_count}"
            assert mock_execute.called, "Expected tool to be executed"
    
    def test_process_message_with_conversation_history(self, agent):
        """
        Test processing message with conversation history.
        
        Arrange: Agent with conversation history
        Act: Call process_message with history
        Assert: History is included in API call
        """
        # Arrange
        user_message = "What about Aspirin?"
        conversation_history = [
            {"role": "user", "content": "Tell me about Acamol"},
            {"role": "assistant", "content": "Acamol contains Paracetamol..."}
        ]
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = "Aspirin is a medication containing Acetylsalicylic acid."
        mock_message.tool_calls = None
        mock_response.choices = [Mock(message=mock_message)]
        agent.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Act
        result = agent.process_message(user_message, conversation_history)
        
        # Assert
        assert isinstance(result, str), f"Expected string result, got {type(result)}"
        # Verify history was passed to API
        call_args = agent.client.chat.completions.create.call_args
        messages = call_args.kwargs.get('messages', [])
        assert len(messages) > 3, \
            f"Expected messages to include history (system + 2 history + user), got {len(messages)} messages"
    
    def test_process_message_max_iterations_prevention(self, agent):
        """
        Test that process_message prevents infinite loops with max iterations.
        
        Arrange: Agent with mocked responses that always request tools
        Act: Call process_message
        Assert: Stops after max iterations and returns error message
        """
        # Arrange
        user_message = "Test query"
        
        # Mock response that always requests tool (causes loop)
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.type = "function"
        mock_tool_call.function = Mock()
        mock_tool_call.function.name = "get_medication_by_name"
        mock_tool_call.function.arguments = '{"name": "Test"}'
        
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = None
        mock_message.tool_calls = [mock_tool_call]
        mock_response.choices = [Mock(message=mock_message)]
        
        agent.client.chat.completions.create = Mock(return_value=mock_response)
        
        with patch('app.agent.agent.execute_tool') as mock_execute:
            mock_execute.return_value = {"medication_id": "med_001"}
            
            # Act
            result = agent.process_message(user_message)
            
            # Assert
            assert isinstance(result, str), f"Expected string result, got {type(result)}"
            assert "issue" in result.lower() or "apologize" in result.lower() or "try again" in result.lower(), \
                f"Expected error/retry message, got '{result}'"
            # Should have called API max_iterations times (10)
            assert agent.client.chat.completions.create.call_count == 10, \
                f"Expected 10 API calls (max iterations), got {agent.client.chat.completions.create.call_count}"
    
    def test_process_message_openai_api_error(self, agent):
        """
        Test error handling when OpenAI API call fails.
        
        Arrange: Agent with mocked OpenAI that raises exception
        Act: Call process_message
        Assert: Raises exception with appropriate message
        """
        # Arrange
        user_message = "Test query"
        agent.client.chat.completions.create = Mock(side_effect=Exception("API Error"))
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            agent.process_message(user_message)
        
        assert "Failed to process message" in str(exc_info.value) or "API Error" in str(exc_info.value), \
            f"Expected error message about processing failure, got '{str(exc_info.value)}'"


class TestPharmacyAgentStatelessBehavior:
    """Test suite for PharmacyAgent stateless behavior."""
    
    @pytest.fixture
    def agent(self):
        """Fixture providing PharmacyAgent instance with mocked OpenAI client."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = PharmacyAgent()
            agent.client = Mock()
            return agent
    
    def test_agent_is_stateless_no_persistent_state(self, agent):
        """
        Test that agent does not maintain state between process_message calls.
        
        Arrange: Agent instance
        Act: Call process_message multiple times with different queries
        Assert: Each call is independent (no shared state)
        """
        # Arrange
        message1 = "First query"
        message2 = "Second query"
        
        # Mock responses
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_message.tool_calls = None
        mock_response.choices = [Mock(message=mock_message)]
        agent.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Act
        result1 = agent.process_message(message1)
        result2 = agent.process_message(message2)
        
        # Assert
        # Both should work independently
        assert isinstance(result1, str), f"Expected string result, got {type(result1)}"
        assert isinstance(result2, str), f"Expected string result, got {type(result2)}"
        # Each call should have its own API call (no shared state)
        assert agent.client.chat.completions.create.call_count == 2, \
            f"Expected 2 independent API calls, got {agent.client.chat.completions.create.call_count}"
    
    def test_agent_conversation_history_only_within_session(self, agent):
        """
        Test that conversation history is only used within a single session.
        
        Arrange: Agent with conversation history
        Act: Call process_message with history, then without
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
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_message.tool_calls = None
        mock_response.choices = [Mock(message=mock_message)]
        agent.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Act
        result1 = agent.process_message(message_with_history, conversation_history)
        result2 = agent.process_message(message_without_history)
        
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


class TestPharmacyAgentToolCallProcessing:
    """Test suite for PharmacyAgent tool call processing."""
    
    @pytest.fixture
    def agent(self):
        """Fixture providing PharmacyAgent instance with mocked OpenAI client."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            agent = PharmacyAgent()
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
        
        with patch('app.agent.agent.execute_tool') as mock_execute:
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
        
        with patch('app.agent.agent.execute_tool') as mock_execute:
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


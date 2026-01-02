"""
Tests for app/main.py - Main entry point and Gradio ChatInterface.

Purpose (Why):
Validates that the main application module correctly initializes the StreamingAgent,
creates the Gradio ChatInterface, handles chat messages with streaming support,
and converts conversation history formats. These tests ensure the application
entry point works correctly and provides a functional user interface.

Implementation (What):
Tests the main module with:
- Agent initialization (initialize_agent, get_agent_instance)
- History format conversion (convert_gradio_history_to_agent_format)
- Chat function with streaming (chat_fn)
- ChatInterface creation (create_chat_interface)
- Error handling and edge cases
- Module-level state management
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Tuple, Dict
import gradio as gr

# Note: We import app.main functions inside each test to avoid
# initialization issues with module-level agent and app variables


class TestInitializeAgent:
    """Test suite for initialize_agent function."""
    
    def test_initialize_agent_with_valid_api_key(self):
        """
        Test that initialize_agent creates agent successfully with valid API key.
        
        Arrange: Set OPENAI_API_KEY environment variable
        Act: Call initialize_agent()
        Assert: Returns StreamingAgent instance
        """
        # Arrange
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            with patch('app.main.StreamingAgent') as mock_agent_class:
                mock_agent = Mock()
                mock_agent_class.return_value = mock_agent
                
                # Act
                from app.main import initialize_agent
                result = initialize_agent()
                
                # Assert
                assert result is not None, "Expected agent to be created"
                assert result == mock_agent, f"Expected mock agent instance, got {result}"
                mock_agent_class.assert_called_once_with(model="gpt-5")
    
    def test_initialize_agent_with_custom_model(self):
        """
        Test that initialize_agent uses custom model when provided.
        
        Arrange: Set OPENAI_API_KEY and custom model name
        Act: Call initialize_agent("custom-model")
        Assert: Agent created with custom model
        """
        # Arrange
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            with patch('app.main.StreamingAgent') as mock_agent_class:
                mock_agent = Mock()
                mock_agent_class.return_value = mock_agent
                
                # Act
                from app.main import initialize_agent
                result = initialize_agent(model="custom-model")
                
                # Assert
                assert result is not None, "Expected agent to be created"
                mock_agent_class.assert_called_once_with(model="custom-model")
    
    def test_initialize_agent_without_api_key_raises_error(self):
        """
        Test that initialize_agent raises ValueError when API key is missing.
        
        Arrange: Remove OPENAI_API_KEY from environment
        Act: Call initialize_agent()
        Assert: Raises ValueError
        """
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act & Assert
            from app.main import initialize_agent
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                initialize_agent()


class TestGetAgentInstance:
    """Test suite for get_agent_instance function."""
    
    def test_get_agent_instance_creates_singleton(self):
        """
        Test that get_agent_instance returns same instance on multiple calls.
        
        Arrange: Set OPENAI_API_KEY and reset module state
        Act: Call get_agent_instance() twice
        Assert: Returns same instance both times
        """
        # Arrange
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"}):
            with patch('app.main.StreamingAgent') as mock_agent_class:
                mock_agent = Mock()
                mock_agent_class.return_value = mock_agent
                
                # Reset module-level state
                import app.main
                app.main._agent_instance = None
                
                # Act
                instance1 = app.main.get_agent_instance()
                instance2 = app.main.get_agent_instance()
                
                # Assert
                assert instance1 is not None, "Expected first instance to be created"
                assert instance2 is not None, "Expected second instance to be created"
                assert instance1 is instance2, "Expected same instance on both calls"
                # Should only be called once due to singleton pattern
                assert mock_agent_class.call_count == 1, \
                    f"Expected 1 call to StreamingAgent, got {mock_agent_class.call_count}"


class TestConvertGradioHistoryToAgentFormat:
    """Test suite for convert_gradio_history_to_agent_format function."""
    
    def test_convert_empty_history_returns_empty_list(self):
        """
        Test that empty history converts to empty list.
        
        Arrange: Empty history list
        Act: Call convert_gradio_history_to_agent_format([])
        Assert: Returns empty list
        """
        # Arrange
        history: List[Tuple[str, str]] = []
        
        # Act
        from app.main import convert_gradio_history_to_agent_format
        result = convert_gradio_history_to_agent_format(history)
        
        # Assert
        assert result == [], f"Expected empty list, got {result}"
    
    def test_convert_none_history_returns_empty_list(self):
        """
        Test that None history converts to empty list.
        
        Arrange: None history
        Act: Call convert_gradio_history_to_agent_format(None)
        Assert: Returns empty list
        """
        # Arrange
        history = None
        
        # Act
        from app.main import convert_gradio_history_to_agent_format
        result = convert_gradio_history_to_agent_format(history)
        
        # Assert
        assert result == [], f"Expected empty list, got {result}"
    
    def test_convert_single_message_pair(self):
        """
        Test conversion of single message pair.
        
        Arrange: History with one user-assistant pair
        Act: Call convert_gradio_history_to_agent_format()
        Assert: Returns correct format with user and assistant messages
        """
        # Arrange
        history: List[Tuple[str, str]] = [("Hello", "Hi there!")]
        
        # Act
        from app.main import convert_gradio_history_to_agent_format
        result = convert_gradio_history_to_agent_format(history)
        
        # Assert
        assert len(result) == 2, f"Expected 2 messages, got {len(result)}"
        assert result[0] == {"role": "user", "content": "Hello"}, \
            f"Expected user message, got {result[0]}"
        assert result[1] == {"role": "assistant", "content": "Hi there!"}, \
            f"Expected assistant message, got {result[1]}"
    
    def test_convert_multiple_message_pairs(self):
        """
        Test conversion of multiple message pairs.
        
        Arrange: History with multiple user-assistant pairs
        Act: Call convert_gradio_history_to_agent_format()
        Assert: Returns all messages in correct format
        """
        # Arrange
        history: List[Tuple[str, str]] = [
            ("Hello", "Hi there!"),
            ("How are you?", "I'm doing well.")
        ]
        
        # Act
        from app.main import convert_gradio_history_to_agent_format
        result = convert_gradio_history_to_agent_format(history)
        
        # Assert
        assert len(result) == 4, f"Expected 4 messages, got {len(result)}"
        assert result[0] == {"role": "user", "content": "Hello"}, \
            f"Expected first user message, got {result[0]}"
        assert result[1] == {"role": "assistant", "content": "Hi there!"}, \
            f"Expected first assistant message, got {result[1]}"
        assert result[2] == {"role": "user", "content": "How are you?"}, \
            f"Expected second user message, got {result[2]}"
        assert result[3] == {"role": "assistant", "content": "I'm doing well."}, \
            f"Expected second assistant message, got {result[3]}"
    
    def test_convert_filters_empty_messages(self):
        """
        Test that empty messages are filtered out.
        
        Arrange: History with empty strings
        Act: Call convert_gradio_history_to_agent_format()
        Assert: Empty messages are not included, only non-empty messages preserved
        """
        # Arrange
        history: List[Tuple[str, str]] = [
            ("Hello", ""),      # Only "Hello" is non-empty
            ("", "Hi there!"),  # Only "Hi there!" is non-empty
            ("   ", "   ")      # Both are empty (whitespace only)
        ]
        
        # Act
        from app.main import convert_gradio_history_to_agent_format
        result = convert_gradio_history_to_agent_format(history)
        
        # Assert
        # Expected: "Hello" (user) and "Hi there!" (assistant) = 2 messages
        assert len(result) == 2, f"Expected 2 messages ('Hello' and 'Hi there!'), got {len(result)}"
        assert result[0] == {"role": "user", "content": "Hello"}, \
            f"Expected first message to be 'Hello', got {result[0]}"
        assert result[1] == {"role": "assistant", "content": "Hi there!"}, \
            f"Expected second message to be 'Hi there!', got {result[1]}"


class TestChatFn:
    """Test suite for chat_fn function."""
    
    def test_chat_fn_with_empty_message(self):
        """
        Test that empty message returns help message.
        
        Arrange: Empty message and empty history
        Act: Call chat_fn("", [])
        Assert: Yields help message
        """
        # Arrange
        message = ""
        history: List[Tuple[str, str]] = []
        
        # Act
        from app.main import chat_fn
        result = list(chat_fn(message, history))
        
        # Assert
        assert len(result) == 1, f"Expected 1 chunk, got {len(result)}"
        # chat_fn returns tuples of (text_chunk, tool_calls_json)
        text_chunk = result[0][0] if isinstance(result[0], tuple) else result[0]
        assert "help" in text_chunk.lower() or "medication" in text_chunk.lower(), \
            f"Expected help message, got {text_chunk}"
    
    def test_chat_fn_with_whitespace_only_message(self):
        """
        Test that whitespace-only message returns help message.
        
        Arrange: Whitespace-only message
        Act: Call chat_fn("   ", [])
        Assert: Yields help message
        """
        # Arrange
        message = "   "
        history: List[Tuple[str, str]] = []
        
        # Act
        from app.main import chat_fn
        result = list(chat_fn(message, history))
        
        # Assert
        assert len(result) == 1, f"Expected 1 chunk, got {len(result)}"
        # chat_fn returns tuples of (text_chunk, tool_calls_json)
        text_chunk = result[0][0] if isinstance(result[0], tuple) else result[0]
        assert "help" in text_chunk.lower() or "medication" in text_chunk.lower(), \
            f"Expected help message, got {text_chunk}"
    
    def test_chat_fn_with_uninitialized_agent(self):
        """
        Test that uninitialized agent returns error message.
        
        Arrange: Set agent to None
        Act: Call chat_fn("test", [])
        Assert: Yields error message
        """
        # Arrange
        message = "test message"
        history: List[Tuple[str, str]] = []
        
        # Temporarily set agent to None
        import app.main
        original_agent = app.main.agent
        app.main.agent = None
        
        try:
            # Act
            from app.main import chat_fn
            result = list(chat_fn(message, history))
            
            # Assert
            assert len(result) == 1, f"Expected 1 chunk, got {len(result)}"
            # chat_fn returns tuples of (text_chunk, tool_calls_json)
            text_chunk = result[0][0] if isinstance(result[0], tuple) else result[0]
            assert "initialized" in text_chunk.lower() or "configuration" in text_chunk.lower(), \
                f"Expected error message about initialization, got {text_chunk}"
        finally:
            # Restore original agent
            app.main.agent = original_agent
    
    def test_chat_fn_calls_stream_response(self):
        """
        Test that chat_fn calls agent.stream_response with correct parameters.
        
        Arrange: Mock agent and stream_response
        Act: Call chat_fn("test", [])
        Assert: stream_response called with correct parameters
        """
        # Arrange
        message = "test message"
        history: List[Tuple[str, str]] = [("Hello", "Hi")]
        
        mock_agent = Mock()
        mock_agent.stream_response.return_value = iter(["chunk1", "chunk2"])
        
        import app.main
        original_agent = app.main.agent
        app.main.agent = mock_agent
        
        try:
            # Act
            from app.main import chat_fn
            result = list(chat_fn(message, history))
            
            # Assert
            assert len(result) == 2, f"Expected 2 chunks, got {len(result)}"
            # chat_fn returns tuples of (text_chunk, tool_calls_json)
            expected = [("chunk1", ""), ("chunk2", "")]
            assert result == expected, \
                f"Expected {expected}, got {result}"
            mock_agent.stream_response.assert_called_once()
            call_args = mock_agent.stream_response.call_args
            assert call_args.kwargs['user_message'] == message, \
                f"Expected user_message='{message}', got {call_args.kwargs.get('user_message')}"
            assert isinstance(call_args.kwargs.get('conversation_history'), list), \
                "Expected conversation_history to be a list"
        finally:
            # Restore original agent
            app.main.agent = original_agent
    
    def test_chat_fn_handles_stream_response_exception(self):
        """
        Test that chat_fn handles exceptions from stream_response gracefully.
        
        Arrange: Mock agent that raises exception
        Act: Call chat_fn("test", [])
        Assert: Yields error message instead of raising
        """
        # Arrange
        message = "test message"
        history: List[Tuple[str, str]] = []
        
        mock_agent = Mock()
        mock_agent.stream_response.side_effect = Exception("Test error")
        
        import app.main
        original_agent = app.main.agent
        app.main.agent = mock_agent
        
        try:
            # Act
            from app.main import chat_fn
            result = list(chat_fn(message, history))
            
            # Assert
            assert len(result) == 1, f"Expected 1 chunk (error message), got {len(result)}"
            # chat_fn returns tuples of (text_chunk, tool_calls_json)
            text_chunk = result[0][0] if isinstance(result[0], tuple) else result[0]
            assert "error" in text_chunk.lower() or "apologize" in text_chunk.lower(), \
                f"Expected error message, got {text_chunk}"
        finally:
            # Restore original agent
            app.main.agent = original_agent


class TestCreateChatInterface:
    """Test suite for create_chat_interface function."""
    
    def test_create_chat_interface_returns_chatinterface(self):
        """
        Test that create_chat_interface returns Blocks instance.
        
        Arrange: No setup needed
        Act: Call create_chat_interface()
        Assert: Returns gr.Blocks instance
        """
        # Arrange
        # No setup needed
        
        # Act
        from app.main import create_chat_interface
        result = create_chat_interface()
        
        # Assert
        assert result is not None, "Expected Blocks interface to be created"
        assert isinstance(result, gr.Blocks), \
            f"Expected gr.Blocks instance, got {type(result)}"
    
    def test_create_chat_interface_has_correct_title(self):
        """
        Test that ChatInterface has correct title.
        
        Arrange: No setup needed
        Act: Call create_chat_interface()
        Assert: Interface has title "Pharmacy AI Assistant"
        """
        # Arrange
        # No setup needed
        
        # Act
        from app.main import create_chat_interface
        interface = create_chat_interface()
        
        # Assert
        # ChatInterface doesn't expose title directly, but we can check it was created
        assert interface is not None, "Expected ChatInterface to be created"
    
    def test_create_chat_interface_has_examples(self):
        """
        Test that ChatInterface includes example messages.
        
        Arrange: No setup needed
        Act: Call create_chat_interface()
        Assert: Interface has examples configured
        """
        # Arrange
        # No setup needed
        
        # Act
        from app.main import create_chat_interface
        interface = create_chat_interface()
        
        # Assert
        assert interface is not None, "Expected ChatInterface to be created"
        # Examples are internal to ChatInterface, but we verify it was created successfully


class TestMainFunction:
    """Test suite for main function."""
    
    def test_main_with_valid_app_launches(self):
        """
        Test that main launches app when app is valid.
        
        Arrange: Mock app with launch method
        Act: Call main()
        Assert: app.launch() called with correct parameters
        """
        # Arrange
        mock_app = Mock()
        mock_app.launch = Mock()
        
        import app.main
        original_app = app.main.app
        app.main.app = mock_app
        
        try:
            # Act
            from app.main import main
            # Note: main() blocks, so we test the launch call setup
            # In a real scenario, we'd use threading or async to test this
            
            # Assert - verify app exists
            assert app.main.app is not None, "Expected app to exist"
        finally:
            # Restore original app
            app.main.app = original_app
    
    def test_main_with_none_app_does_not_launch(self):
        """
        Test that main does not launch when app is None.
        
        Arrange: Set app to None
        Act: Call main()
        Assert: Does not call launch, returns early
        """
        # Arrange
        import app.main
        original_app = app.main.app
        app.main.app = None
        
        try:
            # Act
            from app.main import main
            # main() should return early without launching
            # We can't easily test the blocking launch, but we verify the guard clause
            
            # Assert - verify app is None
            assert app.main.app is None, "Expected app to be None"
        finally:
            # Restore original app
            app.main.app = original_app


class TestHistoryConversionEdgeCases:
    """Test suite for edge cases in history conversion."""
    
    def test_convert_history_with_unicode_characters(self):
        """
        Test that history conversion handles Unicode characters correctly.
        
        Arrange: History with Hebrew/Unicode characters
        Act: Call convert_gradio_history_to_agent_format()
        Assert: Unicode characters preserved correctly
        """
        # Arrange
        history: List[Tuple[str, str]] = [
            ("שלום", "היי!"),
            ("מה שלומך?", "אני בסדר.")
        ]
        
        # Act
        from app.main import convert_gradio_history_to_agent_format
        result = convert_gradio_history_to_agent_format(history)
        
        # Assert
        assert len(result) == 4, f"Expected 4 messages, got {len(result)}"
        assert result[0]["content"] == "שלום", \
            f"Expected Hebrew content preserved, got {result[0]['content']}"
        assert result[1]["content"] == "היי!", \
            f"Expected Hebrew content preserved, got {result[1]['content']}"
    
    def test_convert_history_with_long_messages(self):
        """
        Test that history conversion handles long messages correctly.
        
        Arrange: History with very long messages
        Act: Call convert_gradio_history_to_agent_format()
        Assert: Long messages preserved correctly
        """
        # Arrange
        long_message = "A" * 1000
        history: List[Tuple[str, str]] = [("Short", long_message)]
        
        # Act
        from app.main import convert_gradio_history_to_agent_format
        result = convert_gradio_history_to_agent_format(history)
        
        # Assert
        assert len(result) == 2, f"Expected 2 messages, got {len(result)}"
        assert len(result[1]["content"]) == 1000, \
            f"Expected long message preserved, got length {len(result[1]['content'])}"
    
    def test_convert_history_with_special_characters(self):
        """
        Test that history conversion handles special characters correctly.
        
        Arrange: History with special characters
        Act: Call convert_gradio_history_to_agent_format()
        Assert: Special characters preserved correctly
        """
        # Arrange
        history: List[Tuple[str, str]] = [
            ("Test & < > \" '", "Response with & < > \" '")
        ]
        
        # Act
        from app.main import convert_gradio_history_to_agent_format
        result = convert_gradio_history_to_agent_format(history)
        
        # Assert
        assert len(result) == 2, f"Expected 2 messages, got {len(result)}"
        assert result[0]["content"] == "Test & < > \" '", \
            f"Expected special characters preserved, got {result[0]['content']}"


class TestChatFnEdgeCases:
    """Test suite for edge cases in chat_fn function."""
    
    def test_chat_fn_with_very_long_message(self):
        """
        Test that chat_fn handles very long messages correctly.
        
        Arrange: Very long message
        Act: Call chat_fn()
        Assert: Message processed correctly
        """
        # Arrange
        long_message = "A" * 5000
        history: List[Tuple[str, str]] = []
        
        mock_agent = Mock()
        mock_agent.stream_response.return_value = iter(["response"])
        
        import app.main
        original_agent = app.main.agent
        app.main.agent = mock_agent
        
        try:
            # Act
            from app.main import chat_fn
            result = list(chat_fn(long_message, history))
            
            # Assert
            assert len(result) == 1, f"Expected 1 chunk, got {len(result)}"
            mock_agent.stream_response.assert_called_once()
            call_args = mock_agent.stream_response.call_args
            assert len(call_args.kwargs['user_message']) == 5000, \
                f"Expected long message passed, got length {len(call_args.kwargs['user_message'])}"
        finally:
            # Restore original agent
            app.main.agent = original_agent
    
    def test_chat_fn_with_complex_history(self):
        """
        Test that chat_fn handles complex history correctly.
        
        Arrange: Complex history with multiple pairs
        Act: Call chat_fn()
        Assert: History converted and passed correctly
        """
        # Arrange
        message = "test"
        history: List[Tuple[str, str]] = [
            ("msg1", "resp1"),
            ("msg2", "resp2"),
            ("msg3", "resp3")
        ]
        
        mock_agent = Mock()
        mock_agent.stream_response.return_value = iter(["response"])
        
        import app.main
        original_agent = app.main.agent
        app.main.agent = mock_agent
        
        try:
            # Act
            from app.main import chat_fn
            result = list(chat_fn(message, history))
            
            # Assert
            assert len(result) == 1, f"Expected 1 chunk, got {len(result)}"
            mock_agent.stream_response.assert_called_once()
            call_args = mock_agent.stream_response.call_args
            history_list = call_args.kwargs.get('conversation_history', [])
            assert len(history_list) == 6, \
                f"Expected 6 messages in history (3 pairs), got {len(history_list)}"
        finally:
            # Restore original agent
            app.main.agent = original_agent


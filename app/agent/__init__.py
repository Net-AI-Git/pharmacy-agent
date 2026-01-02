"""
Agent module for the Pharmacy AI Assistant.

Purpose (Why):
This module provides the core agent class for the pharmacy assistant.
It exports the StreamingAgent class which handles OpenAI API integration,
function calling for pharmacy tools, and real-time text streaming capabilities
for improved user experience. The agent is stateless and supports both Hebrew
and English as required by the project specifications.

Implementation (What):
Exports the StreamingAgent class from streaming.py for use in other parts of
the application (e.g., main.py for the UI). The StreamingAgent provides
real-time streaming responses as required by the project requirements.
"""

from app.agent.streaming import StreamingAgent

__all__ = ["StreamingAgent"]


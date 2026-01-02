"""
Agent module for the Pharmacy AI Assistant.

Purpose (Why):
This module provides the core agent classes for the pharmacy assistant.
It exports the PharmacyAgent and StreamingAgent classes which handle OpenAI API
integration and function calling for pharmacy tools. StreamingAgent provides
real-time text streaming capabilities for improved user experience.

Implementation (What):
Exports the PharmacyAgent class from agent.py and StreamingAgent class from
streaming.py for use in other parts of the application (e.g., main.py for the UI).
"""

from app.agent.agent import PharmacyAgent
from app.agent.streaming import StreamingAgent

__all__ = ["PharmacyAgent", "StreamingAgent"]


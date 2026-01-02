"""
Correlation ID generation for request tracking.

Purpose (Why):
Provides unique correlation IDs for tracking requests and operations across
the system. Correlation IDs enable full traceability of agent actions and tool
calls, allowing complete audit trails and debugging. Each conversation or
request gets a unique identifier that can be used to trace all related
operations, making it possible to reconstruct the full flow of any interaction.

Implementation (What):
Uses UUID4 to generate unique, non-sequential identifiers. UUID4 provides
128-bit identifiers that are globally unique with extremely low collision
probability. The correlation ID is a string representation of the UUID that
can be easily logged, transmitted, and stored. This follows security and
observability best practices for distributed systems and audit logging.
"""

import uuid
import logging

# Configure module-level logger
logger = logging.getLogger(__name__)


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID for request tracking.
    
    Purpose (Why):
    Creates a unique identifier that can be used to trace all operations
    related to a single request or conversation. This enables complete
    audit trails, debugging, and observability. Every agent action and
    tool call within a conversation can be linked using this correlation ID,
    making it possible to reconstruct the full flow of any interaction.
    
    Implementation (What):
    Generates a UUID4 (random UUID) and returns its string representation.
    UUID4 provides 128-bit identifiers that are globally unique with
    extremely low collision probability. The string format is standard
    UUID format: "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx" where x is
    hexadecimal and y is one of 8, 9, a, or b.
    
    Returns:
        String representation of a UUID4, e.g., "550e8400-e29b-41d4-a716-446655440000"
    
    Example:
        >>> corr_id = generate_correlation_id()
        >>> len(corr_id) == 36
        True
        >>> corr_id.count('-') == 4
        True
    """
    correlation_id = str(uuid.uuid4())
    logger.debug(f"Generated correlation ID: {correlation_id}")
    return correlation_id


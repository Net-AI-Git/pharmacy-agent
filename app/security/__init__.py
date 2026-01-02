"""
Security module for pharmacy agent.

Purpose (Why):
This module provides security, governance, and observability features for the
pharmacy assistant agent. It includes rate limiting, auditing, correlation tracking,
and other security mechanisms required for production deployment.

Implementation (What):
Contains security components including:
- RateLimiter: Prevents uncontrolled loops and limits tool usage
- AuditLogger: Comprehensive logging of all operations with full context
- Correlation: Unique ID generation for request tracking and audit trails
"""

from app.security.rate_limiter import RateLimiter
from app.security.audit_logger import AuditLogger
from app.security.correlation import generate_correlation_id

__all__ = [
    "RateLimiter",
    "AuditLogger",
    "generate_correlation_id"
]


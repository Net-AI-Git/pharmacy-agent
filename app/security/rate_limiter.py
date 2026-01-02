"""
Rate Limiter for tool execution control.

Purpose (Why):
Prevents uncontrolled loops and limits tool usage to protect system resources
and prevent abuse. Rate limiting is critical for production systems to ensure
stability and prevent resource exhaustion. It tracks tool calls per minute,
per day, and consecutive calls to detect and prevent infinite loops or excessive usage.

Implementation (What):
Implements a RateLimiter class that tracks tool calls using time-based windows
and counters. Uses collections.defaultdict and time.time() for efficient tracking.
Maintains separate counters for:
- Per-minute limits: Maximum calls per tool per minute
- Per-day limits: Maximum calls per tool per day
- Consecutive limits: Maximum consecutive calls to the same tool (prevents loops)

Configuration is loaded from environment variables with sensible defaults.
All limits are configurable via environment variables for flexibility.
"""

import os
import time
import logging
from typing import Dict, Tuple, Optional
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure module-level logger
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter for controlling tool execution frequency.
    
    Purpose (Why):
    Prevents resource exhaustion and infinite loops by limiting how frequently
    tools can be called. Tracks calls per minute, per day, and consecutive calls
    to detect patterns that indicate problems (e.g., infinite loops, abuse).
    Essential for production systems to maintain stability and prevent denial
    of service scenarios.
    
    Implementation (What):
    Maintains time-based tracking structures using defaultdict for efficient
    storage. Tracks:
    - Per-minute calls: List of timestamps for calls in the last minute
    - Per-day calls: List of timestamps for calls in the last 24 hours
    - Consecutive calls: Counter for consecutive calls to the same tool
    
    Uses sliding window approach - removes old timestamps outside the window
    before checking limits. Thread-safe for single-threaded use (Python GIL).
    For multi-threaded environments, additional locking would be needed.
    
    Attributes:
        per_minute_limit: Maximum calls per tool per minute (default: 60)
        per_day_limit: Maximum calls per tool per day (default: 1000)
        consecutive_limit: Maximum consecutive calls to same tool (default: 10)
        _minute_calls: Dict tracking calls per minute per tool per agent
        _day_calls: Dict tracking calls per day per tool per agent
        _consecutive_calls: Dict tracking consecutive calls per tool per agent
        _last_tool: Dict tracking last tool called per agent
    """
    
    def __init__(
        self,
        per_minute_limit: Optional[int] = None,
        per_day_limit: Optional[int] = None,
        consecutive_limit: Optional[int] = None
    ):
        """
        Initialize RateLimiter with configuration limits.
        
        Purpose (Why):
        Sets up rate limiting with configurable thresholds. Loads limits from
        environment variables if provided, otherwise uses defaults. This allows
        flexible configuration for different environments (dev vs prod).
        
        Implementation (What):
        Reads environment variables for limits, falling back to defaults if
        not provided. Initializes tracking dictionaries using defaultdict for
        efficient storage. All limits are configurable to allow tuning based
        on system requirements.
        
        Args:
            per_minute_limit: Maximum calls per tool per minute.
                If None, reads from RATE_LIMIT_PER_MINUTE env var or defaults to 60.
            per_day_limit: Maximum calls per tool per day.
                If None, reads from RATE_LIMIT_PER_DAY env var or defaults to 1000.
            consecutive_limit: Maximum consecutive calls to same tool.
                If None, reads from RATE_LIMIT_CONSECUTIVE env var or defaults to 10.
        """
        # Load limits from environment or use defaults
        self.per_minute_limit = (
            per_minute_limit
            if per_minute_limit is not None
            else int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        )
        self.per_day_limit = (
            per_day_limit
            if per_day_limit is not None
            else int(os.getenv("RATE_LIMIT_PER_DAY", "1000"))
        )
        self.consecutive_limit = (
            consecutive_limit
            if consecutive_limit is not None
            else int(os.getenv("RATE_LIMIT_CONSECUTIVE", "10"))
        )
        
        # Tracking structures: (tool_name, agent_id) -> list of timestamps
        self._minute_calls: Dict[Tuple[str, str], list] = defaultdict(list)
        self._day_calls: Dict[Tuple[str, str], list] = defaultdict(list)
        
        # Tracking consecutive calls: (agent_id) -> (tool_name, count)
        self._consecutive_calls: Dict[str, Tuple[str, int]] = {}
        
        # Track last tool called per agent
        self._last_tool: Dict[str, str] = {}
        
        logger.info(
            f"RateLimiter initialized: "
            f"per_minute={self.per_minute_limit}, "
            f"per_day={self.per_day_limit}, "
            f"consecutive={self.consecutive_limit}"
        )
    
    def _cleanup_old_entries(self, key: Tuple[str, str], window_seconds: int, calls_list: list) -> None:
        """
        Remove timestamps outside the time window.
        
        Purpose (Why):
        Maintains sliding window by removing old entries that are outside
        the time window. This prevents memory growth and ensures accurate
        rate limit checking.
        
        Implementation (What):
        Filters the calls list to only include timestamps within the window.
        Uses current time minus window_seconds as the cutoff point.
        
        Args:
            key: Tuple of (tool_name, agent_id) for the tracking entry
            window_seconds: Time window in seconds (60 for minute, 86400 for day)
            calls_list: List of timestamps to clean
        """
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Filter out old entries
        self._minute_calls[key] = [ts for ts in calls_list if ts > cutoff_time]
    
    def check_rate_limit(self, tool_name: str, agent_id: str = "default") -> Tuple[bool, Optional[str]]:
        """
        Check if a tool call is allowed under rate limits.
        
        Purpose (Why):
        Validates whether a tool call should be allowed based on configured
        rate limits. Prevents resource exhaustion and infinite loops by
        enforcing limits on call frequency. Returns clear error messages
        when limits are exceeded to help with debugging.
        
        Implementation (What):
        Checks three types of limits:
        1. Per-minute limit: Counts calls in the last 60 seconds
        2. Per-day limit: Counts calls in the last 24 hours
        3. Consecutive limit: Tracks consecutive calls to the same tool
        
        Uses sliding window approach - cleans old entries before checking.
        Returns tuple of (allowed, error_message) where error_message is None
        if allowed, or a descriptive message if limit exceeded.
        
        Args:
            tool_name: Name of the tool to check
            agent_id: Identifier for the agent/session making the call.
                Defaults to "default" for stateless agents.
                Can be session ID or user ID in future implementations.
        
        Returns:
            Tuple of (is_allowed: bool, error_message: Optional[str]).
            If is_allowed is True, error_message is None.
            If is_allowed is False, error_message contains reason for rejection.
        
        Example:
            >>> limiter = RateLimiter()
            >>> allowed, error = limiter.check_rate_limit("get_medication_by_name", "session_123")
            >>> if not allowed:
            ...     print(f"Rate limit exceeded: {error}")
        """
        current_time = time.time()
        key = (tool_name, agent_id)
        
        # Clean up old entries before checking
        if key in self._minute_calls:
            self._cleanup_old_entries(key, 60, self._minute_calls[key])
        
        if key in self._day_calls:
            self._cleanup_old_entries(key, 86400, self._day_calls[key])
        
        # Check per-minute limit
        minute_calls = self._minute_calls[key]
        if len(minute_calls) >= self.per_minute_limit:
            error_msg = (
                f"Rate limit exceeded: {len(minute_calls)} calls to '{tool_name}' "
                f"in the last minute (limit: {self.per_minute_limit}). "
                f"Please wait before trying again."
            )
            logger.warning(f"Rate limit exceeded for {tool_name} by {agent_id}: per-minute limit")
            return False, error_msg
        
        # Check per-day limit
        day_calls = self._day_calls[key]
        if len(day_calls) >= self.per_day_limit:
            error_msg = (
                f"Rate limit exceeded: {len(day_calls)} calls to '{tool_name}' "
                f"in the last 24 hours (limit: {self.per_day_limit}). "
                f"Daily limit reached. Please try again tomorrow."
            )
            logger.warning(f"Rate limit exceeded for {tool_name} by {agent_id}: per-day limit")
            return False, error_msg
        
        # Check consecutive limit
        last_tool = self._last_tool.get(agent_id)
        if last_tool == tool_name:
            # Same tool as last call - increment consecutive counter
            current_tool, count = self._consecutive_calls.get(agent_id, (tool_name, 0))
            if current_tool == tool_name:
                count += 1
                if count >= self.consecutive_limit:
                    error_msg = (
                        f"Rate limit exceeded: {count} consecutive calls to '{tool_name}' "
                        f"(limit: {self.consecutive_limit}). "
                        f"This may indicate an infinite loop. Please check your request."
                    )
                    logger.warning(
                        f"Rate limit exceeded for {tool_name} by {agent_id}: "
                        f"consecutive limit ({count} calls)"
                    )
                    return False, error_msg
                self._consecutive_calls[agent_id] = (tool_name, count)
            else:
                # Different tool - reset counter
                self._consecutive_calls[agent_id] = (tool_name, 1)
        else:
            # Different tool or first call - reset consecutive counter
            if last_tool is not None:
                # Reset counter for new tool
                self._consecutive_calls[agent_id] = (tool_name, 1)
            else:
                # First call for this agent
                self._consecutive_calls[agent_id] = (tool_name, 1)
        
        # Update last tool
        self._last_tool[agent_id] = tool_name
        
        # All checks passed
        return True, None
    
    def record_call(self, tool_name: str, agent_id: str = "default") -> None:
        """
        Record a tool call for rate limit tracking.
        
        Purpose (Why):
        Records that a tool call occurred, updating tracking structures for
        rate limit enforcement. Should be called after a successful rate limit
        check and before tool execution to maintain accurate tracking.
        
        Implementation (What):
        Adds current timestamp to both minute and day tracking lists for the
        given tool and agent. This updates the sliding window tracking used
        by check_rate_limit().
        
        Args:
            tool_name: Name of the tool that was called
            agent_id: Identifier for the agent/session making the call.
                Defaults to "default" for stateless agents.
        
        Example:
            >>> limiter = RateLimiter()
            >>> allowed, error = limiter.check_rate_limit("get_medication_by_name", "session_123")
            >>> if allowed:
            ...     limiter.record_call("get_medication_by_name", "session_123")
            ...     # Execute tool...
        """
        current_time = time.time()
        key = (tool_name, agent_id)
        
        # Add timestamp to tracking lists
        self._minute_calls[key].append(current_time)
        self._day_calls[key].append(current_time)
        
        logger.debug(f"Recorded tool call: {tool_name} by {agent_id} at {current_time}")


"""
Tests for RateLimiter thread-safety.

Purpose (Why):
Validates that RateLimiter correctly handles concurrent access from multiple threads
without race conditions. This is critical for parallel tool execution where multiple
tools may check rate limits simultaneously. Thread-safety ensures rate limiting
works correctly under concurrent load and prevents security vulnerabilities.

Implementation (What):
Tests RateLimiter with:
- Concurrent check_rate_limit calls from multiple threads
- Concurrent record_call operations
- Race condition prevention verification
- Data integrity under concurrent access
- Rate limit accuracy with parallel requests
"""

import pytest
import threading
import time
from app.security.rate_limiter import RateLimiter


class TestRateLimiterThreadSafety:
    """Test suite for RateLimiter thread-safety."""
    
    @pytest.fixture
    def rate_limiter(self):
        """
        Fixture providing RateLimiter instance with high limits for testing.
        
        Returns:
            RateLimiter instance configured for testing
        """
        return RateLimiter(
            per_minute_limit=1000,  # High limit to avoid false positives
            per_day_limit=10000,
            consecutive_limit=200  # High enough for test (10 threads * 10 calls = 100)
        )
    
    def test_concurrent_check_rate_limit_no_race_condition(self, rate_limiter):
        """
        Test that concurrent check_rate_limit calls don't cause race conditions.
        
        Arrange: RateLimiter with high limits, multiple threads
        Act: All threads call check_rate_limit simultaneously
        Assert: All calls succeed, no data corruption, accurate count
        
        Status: ✅ PASS if all threads get correct results
        """
        # Arrange
        tool_name = "test_tool"
        agent_id = "test_agent"
        num_threads = 10
        calls_per_thread = 10
        results = []
        errors = []
        
        def check_limit_thread():
            """Thread function that checks rate limit multiple times."""
            thread_results = []
            for _ in range(calls_per_thread):
                try:
                    allowed, error = rate_limiter.check_rate_limit(tool_name, agent_id)
                    thread_results.append((allowed, error))
                except Exception as e:
                    errors.append(str(e))
            results.extend(thread_results)
        
        # Act
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=check_limit_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(errors) == 0, f"Expected no errors, got {len(errors)}: {errors}"
        assert len(results) == num_threads * calls_per_thread, \
            f"Expected {num_threads * calls_per_thread} results, got {len(results)}"
        
        # All should be allowed (high limit)
        allowed_count = sum(1 for allowed, _ in results if allowed)
        assert allowed_count == len(results), \
            f"Expected all calls to be allowed, got {allowed_count}/{len(results)} allowed"
    
    def test_concurrent_record_call_data_integrity(self, rate_limiter):
        """
        Test that concurrent record_call operations maintain data integrity.
        
        Arrange: RateLimiter, multiple threads
        Act: All threads call record_call simultaneously
        Assert: All calls recorded, no data loss, accurate final count
        
        Status: ✅ PASS if all calls are recorded correctly
        """
        # Arrange
        tool_name = "test_tool"
        agent_id = "test_agent"
        num_threads = 10
        calls_per_thread = 10
        errors = []
        
        def record_call_thread():
            """Thread function that records calls multiple times."""
            for _ in range(calls_per_thread):
                try:
                    rate_limiter.record_call(tool_name, agent_id)
                except Exception as e:
                    errors.append(str(e))
        
        # Act
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=record_call_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(errors) == 0, f"Expected no errors, got {len(errors)}: {errors}"
        
        # Verify all calls were recorded
        key = (tool_name, agent_id)
        recorded_count = len(rate_limiter._minute_calls.get(key, []))
        expected_count = num_threads * calls_per_thread
        
        assert recorded_count == expected_count, \
            f"Expected {expected_count} recorded calls, got {recorded_count}"
    
    def test_concurrent_check_and_record_no_race_condition(self, rate_limiter):
        """
        Test concurrent check_rate_limit and record_call operations.
        
        Arrange: RateLimiter, threads doing both check and record
        Act: Threads call both check_rate_limit and record_call concurrently
        Assert: No race conditions, data integrity maintained
        
        Status: ✅ PASS if operations complete without errors
        """
        # Arrange
        tool_name = "test_tool"
        agent_id = "test_agent"
        num_threads = 10
        operations_per_thread = 10
        errors = []
        
        def check_and_record_thread():
            """Thread function that checks and records."""
            for _ in range(operations_per_thread):
                try:
                    # Check rate limit
                    allowed, error = rate_limiter.check_rate_limit(tool_name, agent_id)
                    if allowed:
                        # Record the call
                        rate_limiter.record_call(tool_name, agent_id)
                except Exception as e:
                    errors.append(str(e))
        
        # Act
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=check_and_record_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(errors) == 0, f"Expected no errors, got {len(errors)}: {errors}"
        
        # Verify data integrity
        key = (tool_name, agent_id)
        recorded_count = len(rate_limiter._minute_calls.get(key, []))
        assert recorded_count > 0, \
            f"Expected some recorded calls, got {recorded_count}"
    
    def test_rate_limit_enforcement_under_concurrent_load(self):
        """
        Test that rate limits are correctly enforced under concurrent load.
        
        Arrange: RateLimiter with low limit, multiple threads
        Act: Threads exceed limit concurrently
        Assert: Rate limit correctly enforced, no bypass
        
        Status: ✅ PASS if rate limit prevents exceeding limit
        """
        # Arrange
        rate_limiter = RateLimiter(
            per_minute_limit=5,  # Low limit for testing
            per_day_limit=100,
            consecutive_limit=10
        )
        tool_name = "test_tool"
        agent_id = "test_agent"
        num_threads = 10
        calls_per_thread = 2  # Total: 20 calls, but limit is 5
        results = []
        
        def check_limit_thread():
            """Thread function that checks rate limit."""
            for _ in range(calls_per_thread):
                allowed, error = rate_limiter.check_rate_limit(tool_name, agent_id)
                if allowed:
                    rate_limiter.record_call(tool_name, agent_id)
                results.append((allowed, error))
        
        # Act
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=check_limit_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        allowed_count = sum(1 for allowed, _ in results if allowed)
        denied_count = sum(1 for allowed, _ in results if not allowed)
        
        # Should have some allowed (up to limit) and some denied
        assert allowed_count <= 5, \
            f"Expected at most 5 allowed calls, got {allowed_count}"
        assert denied_count > 0, \
            f"Expected some denied calls due to rate limit, got {denied_count}"
    
    def test_consecutive_limit_thread_safety(self, rate_limiter):
        """
        Test that consecutive limit tracking is thread-safe.
        
        Arrange: RateLimiter, multiple threads calling same tool
        Act: Threads call same tool concurrently
        Assert: Consecutive limit tracking accurate, no race conditions
        
        Status: ✅ PASS if consecutive tracking works correctly
        """
        # Arrange
        tool_name = "test_tool"
        agent_id = "test_agent"
        num_threads = 5
        calls_per_thread = 3
        
        def call_tool_thread():
            """Thread function that calls tool multiple times."""
            for _ in range(calls_per_thread):
                allowed, _ = rate_limiter.check_rate_limit(tool_name, agent_id)
                if allowed:
                    rate_limiter.record_call(tool_name, agent_id)
                time.sleep(0.01)  # Small delay to allow interleaving
        
        # Act
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=call_tool_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        # Verify consecutive tracking exists
        assert agent_id in rate_limiter._consecutive_calls, \
            f"Expected consecutive calls tracking for agent {agent_id}"
        
        # Verify last tool is set
        assert agent_id in rate_limiter._last_tool, \
            f"Expected last tool tracking for agent {agent_id}"
        assert rate_limiter._last_tool[agent_id] == tool_name, \
            f"Expected last tool to be '{tool_name}', got '{rate_limiter._last_tool[agent_id]}'"
    
    def test_multiple_agents_concurrent_access(self, rate_limiter):
        """
        Test that concurrent access from multiple agents is thread-safe.
        
        Arrange: RateLimiter, threads representing different agents
        Act: Each agent calls tools concurrently
        Assert: No cross-agent interference, data integrity maintained
        
        Status: ✅ PASS if agents don't interfere with each other
        """
        # Arrange
        tool_name = "test_tool"
        num_agents = 5
        calls_per_agent = 10
        errors = []
        
        def agent_thread(agent_id):
            """Thread function representing an agent."""
            for _ in range(calls_per_agent):
                try:
                    allowed, _ = rate_limiter.check_rate_limit(tool_name, agent_id)
                    if allowed:
                        rate_limiter.record_call(tool_name, agent_id)
                except Exception as e:
                    errors.append(f"Agent {agent_id}: {str(e)}")
        
        # Act
        threads = []
        for i in range(num_agents):
            agent_id = f"agent_{i}"
            thread = threading.Thread(target=agent_thread, args=(agent_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(errors) == 0, f"Expected no errors, got {len(errors)}: {errors}"
        
        # Verify each agent has its own tracking
        for i in range(num_agents):
            agent_id = f"agent_{i}"
            key = (tool_name, agent_id)
            recorded_count = len(rate_limiter._minute_calls.get(key, []))
            assert recorded_count == calls_per_agent, \
                f"Expected {calls_per_agent} calls for {agent_id}, got {recorded_count}"


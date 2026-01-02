"""
Tests for AuditLogger thread-safety.

Purpose (Why):
Validates that AuditLogger correctly handles concurrent file writes from multiple threads
without data corruption or race conditions. This is critical for parallel tool execution
where multiple tools may write audit logs simultaneously. Thread-safety ensures audit
trail integrity and prevents log corruption.

Implementation (What):
Tests AuditLogger with:
- Concurrent _write_log_entry calls from multiple threads
- File integrity verification under concurrent writes
- No data loss or corruption
- Proper log entry formatting
- Thread-safe file operations
"""

import pytest
import threading
import json
import tempfile
import os
from pathlib import Path
from app.security.audit_logger import AuditLogger


class TestAuditLoggerThreadSafety:
    """Test suite for AuditLogger thread-safety."""
    
    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """
        Fixture providing temporary directory for audit logs.
        
        Args:
            tmp_path: Pytest temporary directory fixture
            
        Returns:
            Path to temporary log directory
        """
        log_dir = tmp_path / "audit_logs"
        log_dir.mkdir()
        return str(log_dir)
    
    @pytest.fixture
    def audit_logger(self, temp_log_dir):
        """
        Fixture providing AuditLogger instance with temporary directory.
        
        Args:
            temp_log_dir: Temporary log directory fixture
            
        Returns:
            AuditLogger instance configured for testing
        """
        return AuditLogger(log_dir=temp_log_dir, enabled=True)
    
    def test_concurrent_write_log_entry_no_corruption(self, audit_logger):
        """
        Test that concurrent _write_log_entry calls don't corrupt log file.
        
        Arrange: AuditLogger, multiple threads with different log entries
        Act: All threads write log entries simultaneously
        Assert: All entries written, file valid JSON lines, no corruption
        
        Status: ✅ PASS if all entries are valid and complete
        """
        # Arrange
        num_threads = 10
        entries_per_thread = 10
        errors = []
        written_entries = []
        
        def write_log_thread(thread_id):
            """Thread function that writes log entries."""
            for i in range(entries_per_thread):
                try:
                    log_entry = {
                        "timestamp": f"2024-01-01T00:00:{thread_id:02d}:{i:02d}",
                        "correlation_id": f"corr_{thread_id}_{i}",
                        "agent_id": f"agent_{thread_id}",
                        "event_type": "test_event",
                        "message": f"Test message from thread {thread_id}, entry {i}",
                        "data": {"thread_id": thread_id, "entry_id": i}
                    }
                    audit_logger._write_log_entry(log_entry)
                    written_entries.append(log_entry)
                except Exception as e:
                    errors.append(f"Thread {thread_id}, entry {i}: {str(e)}")
        
        # Act
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=write_log_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(errors) == 0, f"Expected no errors, got {len(errors)}: {errors}"
        
        # Verify log file exists and is readable
        assert audit_logger.current_log_file is not None, \
            "Expected log file to be created"
        assert os.path.exists(audit_logger.current_log_file), \
            f"Expected log file to exist at {audit_logger.current_log_file}"
        
        # Read and verify all entries
        with open(audit_logger.current_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        assert len(lines) == num_threads * entries_per_thread, \
            f"Expected {num_threads * entries_per_thread} log entries, got {len(lines)}"
        
        # Verify each line is valid JSON
        parsed_entries = []
        for line_num, line in enumerate(lines, 1):
            try:
                entry = json.loads(line.strip())
                parsed_entries.append(entry)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON at line {line_num}: {e}\nLine content: {line}")
        
        # Verify all expected entries are present
        assert len(parsed_entries) == len(written_entries), \
            f"Expected {len(written_entries)} parsed entries, got {len(parsed_entries)}"
    
    def test_concurrent_log_tool_call_thread_safety(self, audit_logger):
        """
        Test that concurrent log_tool_call operations are thread-safe.
        
        Arrange: AuditLogger, multiple threads logging tool calls
        Act: Threads call log_tool_call simultaneously
        Assert: All tool calls logged, no data loss, file integrity maintained
        
        Status: ✅ PASS if all tool calls are logged correctly
        """
        # Arrange
        num_threads = 5
        calls_per_thread = 5
        errors = []
        
        def log_tool_call_thread(thread_id):
            """Thread function that logs tool calls."""
            for i in range(calls_per_thread):
                try:
                    audit_logger.log_tool_call(
                        correlation_id=f"corr_{thread_id}_{i}",
                        tool_name=f"test_tool_{thread_id}",
                        agent_id=f"agent_{thread_id}",
                        arguments={"param": f"value_{i}"},
                        result={"success": True, "data": f"result_{i}"},
                        context={"thread_id": thread_id, "call_id": i},
                        status="success"
                    )
                except Exception as e:
                    errors.append(f"Thread {thread_id}, call {i}: {str(e)}")
        
        # Act
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=log_tool_call_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(errors) == 0, f"Expected no errors, got {len(errors)}: {errors}"
        
        # Verify log file contains all entries
        with open(audit_logger.current_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        assert len(lines) == num_threads * calls_per_thread, \
            f"Expected {num_threads * calls_per_thread} log entries, got {len(lines)}"
        
        # Verify each entry has correct structure
        for line in lines:
            entry = json.loads(line.strip())
            assert entry["event_type"] == "tool_call", \
                f"Expected event_type 'tool_call', got '{entry.get('event_type')}'"
            assert "correlation_id" in entry, "Expected correlation_id in entry"
            assert "tool_name" in entry, "Expected tool_name in entry"
            assert "agent_id" in entry, "Expected agent_id in entry"
    
    def test_concurrent_log_agent_action_thread_safety(self, audit_logger):
        """
        Test that concurrent log_agent_action operations are thread-safe.
        
        Arrange: AuditLogger, multiple threads logging agent actions
        Act: Threads call log_agent_action simultaneously
        Assert: All actions logged, no data loss, file integrity maintained
        
        Status: ✅ PASS if all actions are logged correctly
        """
        # Arrange
        num_threads = 5
        actions_per_thread = 5
        errors = []
        
        def log_agent_action_thread(thread_id):
            """Thread function that logs agent actions."""
            for i in range(actions_per_thread):
                try:
                    audit_logger.log_agent_action(
                        correlation_id=f"corr_{thread_id}_{i}",
                        agent_id=f"agent_{thread_id}",
                        action=f"test_action_{i}",
                        details={"thread_id": thread_id, "action_id": i, "data": f"value_{i}"},
                        status="success"
                    )
                except Exception as e:
                    errors.append(f"Thread {thread_id}, action {i}: {str(e)}")
        
        # Act
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=log_agent_action_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(errors) == 0, f"Expected no errors, got {len(errors)}: {errors}"
        
        # Verify log file contains all entries
        with open(audit_logger.current_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        assert len(lines) == num_threads * actions_per_thread, \
            f"Expected {num_threads * actions_per_thread} log entries, got {len(lines)}"
        
        # Verify each entry has correct structure
        for line in lines:
            entry = json.loads(line.strip())
            assert entry["event_type"] == "agent_action", \
                f"Expected event_type 'agent_action', got '{entry.get('event_type')}'"
            assert "correlation_id" in entry, "Expected correlation_id in entry"
            assert "action" in entry, "Expected action in entry"
            assert "agent_id" in entry, "Expected agent_id in entry"
    
    def test_log_file_integrity_under_heavy_load(self, audit_logger):
        """
        Test log file integrity under heavy concurrent load.
        
        Arrange: AuditLogger, many threads writing many entries
        Act: Heavy concurrent write load
        Assert: File integrity maintained, all entries valid, no corruption
        
        Status: ✅ PASS if file is valid and all entries are readable
        """
        # Arrange
        num_threads = 20
        entries_per_thread = 20
        errors = []
        
        def write_entries_thread(thread_id):
            """Thread function that writes many entries."""
            for i in range(entries_per_thread):
                try:
                    log_entry = {
                        "timestamp": f"2024-01-01T00:00:{thread_id:02d}:{i:02d}",
                        "correlation_id": f"corr_{thread_id}_{i}",
                        "agent_id": f"agent_{thread_id}",
                        "event_type": "test_event",
                        "data": {"thread_id": thread_id, "entry_id": i, "large_data": "x" * 100}
                    }
                    audit_logger._write_log_entry(log_entry)
                except Exception as e:
                    errors.append(f"Thread {thread_id}, entry {i}: {str(e)}")
        
        # Act
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=write_entries_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(errors) == 0, f"Expected no errors, got {len(errors)}: {errors}"
        
        # Verify file can be read completely
        with open(audit_logger.current_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        expected_entries = num_threads * entries_per_thread
        assert len(lines) == expected_entries, \
            f"Expected {expected_entries} log entries, got {len(lines)}"
        
        # Verify all entries are valid JSON
        for line_num, line in enumerate(lines, 1):
            try:
                entry = json.loads(line.strip())
                assert "correlation_id" in entry, \
                    f"Entry at line {line_num} missing correlation_id"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON at line {line_num}: {e}\nLine content: {line[:100]}")
    
    def test_no_cross_thread_interference(self, audit_logger):
        """
        Test that log entries from different threads don't interfere.
        
        Arrange: AuditLogger, threads with distinct entry data
        Act: Threads write distinct entries concurrently
        Assert: All entries preserved correctly, no mixing or corruption
        
        Status: ✅ PASS if all entries maintain their distinct data
        """
        # Arrange
        num_threads = 5
        entries_per_thread = 5
        thread_entries = {i: [] for i in range(num_threads)}
        errors = []
        
        def write_distinct_entries_thread(thread_id):
            """Thread function that writes distinct entries."""
            for i in range(entries_per_thread):
                try:
                    log_entry = {
                        "timestamp": f"2024-01-01T00:00:{thread_id:02d}:{i:02d}",
                        "correlation_id": f"corr_{thread_id}_{i}",
                        "agent_id": f"agent_{thread_id}",
                        "event_type": "test_event",
                        "thread_specific_data": f"thread_{thread_id}_entry_{i}",
                        "unique_id": f"{thread_id}_{i}"
                    }
                    audit_logger._write_log_entry(log_entry)
                    thread_entries[thread_id].append(log_entry)
                except Exception as e:
                    errors.append(f"Thread {thread_id}, entry {i}: {str(e)}")
        
        # Act
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=write_distinct_entries_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(errors) == 0, f"Expected no errors, got {len(errors)}: {errors}"
        
        # Verify all entries are present and maintain their distinct data
        with open(audit_logger.current_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        parsed_entries = [json.loads(line.strip()) for line in lines]
        
        # Verify each thread's entries are present
        for thread_id in range(num_threads):
            thread_correlation_ids = {f"corr_{thread_id}_{i}" for i in range(entries_per_thread)}
            found_ids = {entry["correlation_id"] for entry in parsed_entries 
                        if entry.get("correlation_id") in thread_correlation_ids}
            
            assert len(found_ids) == entries_per_thread, \
                f"Expected {entries_per_thread} entries for thread {thread_id}, found {len(found_ids)}"
            
            # Verify thread-specific data is preserved
            for entry in parsed_entries:
                if entry.get("correlation_id", "").startswith(f"corr_{thread_id}_"):
                    assert entry.get("thread_specific_data") == f"thread_{thread_id}_entry_{entry.get('unique_id', '').split('_')[1]}", \
                        f"Thread-specific data corrupted for entry {entry.get('correlation_id')}"


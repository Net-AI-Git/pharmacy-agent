"""
Comprehensive audit logging for agent operations and tool calls.

Purpose (Why):
Provides complete audit trail of all agent actions and tool executions for
security, compliance, debugging, and observability. Every operation is logged
with full context, enabling complete traceability and reconstruction of
agent behavior. This is critical for production systems to meet security
governance requirements, debug issues, and maintain compliance with audit
requirements.

Implementation (What):
Implements AuditLogger class that logs all operations to structured JSON
files. Each log entry includes correlation ID, timestamp, agent ID, tool name
(if applicable), arguments, results, context, and status. Logs are written
to files in a dedicated audit log directory, organized by date for easy
retrieval and analysis. Follows security governance best practices for
comprehensive auditing without exposing sensitive data.
"""

import os
import json
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import glob

# Load environment variables
load_dotenv()

# Configure module-level logger
logger = logging.getLogger(__name__)

# Default audit log directory
DEFAULT_AUDIT_LOG_DIR = "logs/audit"


class AuditLogger:
    """
    Comprehensive audit logger for agent operations and tool calls.
    
    Purpose (Why):
    Logs all agent actions and tool executions with complete context for
    security, compliance, debugging, and observability. Provides full audit
    trail that enables complete traceability of agent behavior. Critical
    for production systems to meet security governance requirements and
    maintain compliance with audit standards.
    
    Implementation (What):
    Writes structured JSON logs to files organized by date. Each log entry
    includes correlation ID, timestamp, agent ID, tool name (if applicable),
    arguments, results, context, and status. Logs are written to a dedicated
    audit log directory, with one file per day for easy retrieval. Thread-safe
    for concurrent execution using threading.Lock to protect file write operations
    during parallel tool execution.
    
    Attributes:
        log_dir: Directory path for audit logs
        enabled: Whether audit logging is enabled (from environment or default: True)
        _lock: Threading lock for thread-safe file write operations
    """
    
    def __init__(self, log_dir: Optional[str] = None, enabled: Optional[bool] = None):
        """
        Initialize AuditLogger with configuration.
        
        Purpose (Why):
        Sets up audit logging with configurable log directory and enable/disable
        flag. Allows flexible configuration for different environments (dev vs prod)
        and enables/disables logging based on environment variables.
        
        Implementation (What):
        Reads log directory from environment variable or uses default. Reads
        enabled flag from environment variable or defaults to True. Creates log
        directory if it doesn't exist. Creates a new log file for this run and
        cleans up old files, keeping only the last 5. All configuration is optional
        to allow flexible setup.
        
        Args:
            log_dir: Directory path for audit logs.
                If None, reads from AUDIT_LOG_DIR env var or uses DEFAULT_AUDIT_LOG_DIR.
            enabled: Whether audit logging is enabled.
                If None, reads from AUDIT_LOGGING_ENABLED env var or defaults to True.
        
        Returns:
            None. Initializes the AuditLogger instance with configured settings.
        
        Raises:
            OSError: If log directory cannot be created (permissions, disk space, etc.).
        """
        self.log_dir = log_dir or os.getenv("AUDIT_LOG_DIR", DEFAULT_AUDIT_LOG_DIR)
        self.enabled = (
            enabled
            if enabled is not None
            else os.getenv("AUDIT_LOGGING_ENABLED", "true").lower() == "true"
        )
        
        # Thread lock for thread-safe file write operations
        self._lock = threading.Lock()
        
        # Create log directory if it doesn't exist
        if self.enabled:
            Path(self.log_dir).mkdir(parents=True, exist_ok=True)
            # Create a new log file for this run
            self.current_log_file = self._create_new_log_file()
            # Clean up old files, keeping only the last 5
            self._cleanup_old_logs()
            logger.info(f"AuditLogger initialized with log directory: {self.log_dir}")
            logger.info(f"Current log file: {self.current_log_file}")
        else:
            self.current_log_file = None
            logger.info("AuditLogger initialized but logging is disabled")
    
    def _create_new_log_file(self) -> str:
        """
        Create a new log file with a unique timestamp.
        
        Purpose (Why):
        Creates a new log file for each run, ensuring that each run's logs are
        isolated and don't mix with previous runs. This allows easy identification
        of logs from a specific run.
        
        Implementation (What):
        Creates a file path based on current timestamp in format:
        audit_YYYY-MM-DD_HH-MM-SS.json in the configured log directory.
        The file is not created here, only the path is generated.
        
        Returns:
            str: Full path to the new log file (file is created on first write).
        
        Raises:
            None. This method only generates a path string and does not perform I/O.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(self.log_dir, f"audit_{timestamp}.json")
    
    def _cleanup_old_logs(self, keep_count: int = 5) -> None:
        """
        Clean up old audit log files, keeping only the most recent ones.
        
        Purpose (Why):
        Prevents disk space from filling up with old log files. Maintains a
        rolling window of recent logs for debugging and analysis while removing
        older files automatically.
        
        Implementation (What):
        Finds all audit log files in the log directory, sorts them by modification
        time (newest first), and deletes all but the most recent keep_count files.
        Only processes files matching the audit_*.json pattern.
        
        Args:
            keep_count: Number of recent log files to keep (default: 5).
                Must be a positive integer.
        
        Returns:
            None. Modifies log directory by deleting old files.
        
        Raises:
            None. All exceptions during file operations are caught and logged,
            but do not propagate to prevent cleanup failures from breaking the application.
        """
        try:
            # Find all audit log files
            pattern = os.path.join(self.log_dir, "audit_*.json")
            log_files = glob.glob(pattern)
            
            if len(log_files) <= keep_count:
                return
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
            
            # Delete old files (keep only the most recent keep_count)
            files_to_delete = log_files[keep_count:]
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    logger.debug(f"Deleted old audit log file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete old audit log file {file_path}: {str(e)}")
            
            if files_to_delete:
                logger.info(f"Cleaned up {len(files_to_delete)} old audit log file(s)")
        except Exception as e:
            logger.warning(f"Failed to clean up old audit logs: {str(e)}")
    
    def start_new_run(self) -> None:
        """
        Start a new run by creating a new log file.
        
        Purpose (Why):
        Allows starting a fresh log file for a new run/session. Ensures that
        each run's logs are isolated in their own file, making it easier to
        analyze logs from a specific run without mixing with previous runs.
        
        Implementation (What):
        Creates a new log file with a unique timestamp and cleans up old log
        files, keeping only the 5 most recent ones. This should be called at
        the start of each run to ensure proper log isolation.
        
        Returns:
            None. Updates self.current_log_file with new log file path.
        
        Raises:
            OSError: If log directory cannot be accessed or log file cannot be created.
        """
        if not self.enabled:
            return
        
        # Create a new log file for this run
        self.current_log_file = self._create_new_log_file()
        # Clean up old files, keeping only the last 5
        self._cleanup_old_logs()
        logger.info(f"Started new audit log run: {self.current_log_file}")
    
    def _write_log_entry(self, log_entry: Dict[str, Any]) -> None:
        """
        Write a log entry to the current audit log file.
        
        Purpose (Why):
        Persists audit log entries to disk for long-term storage and analysis.
        Ensures all operations are recorded for compliance and debugging.
        Thread-safe for concurrent execution when multiple tools write audit logs
        simultaneously during parallel tool execution.
        
        Implementation (What):
        Appends log entry to the current run's log file as a JSON line. Uses JSON lines
        format (one JSON object per line) for easy parsing and streaming.
        Creates file if it doesn't exist. All file write operations are protected
        by threading.Lock to ensure thread-safety during parallel tool execution.
        Handles errors gracefully to prevent audit logging failures from breaking
        the application.
        
        Args:
            log_entry: Dictionary containing log entry data. Must be JSON-serializable.
                Expected keys include: timestamp, correlation_id, agent_id, event_type,
                and other event-specific fields.
        
        Returns:
            None. Writes log entry to file or returns silently if logging is disabled.
        
        Raises:
            None. Exceptions during file write are caught and logged, but do not propagate
            to prevent audit logging failures from breaking the application.
        """
        if not self.enabled or not self.current_log_file:
            return
        
        try:
            # Thread-safe file write operation
            with self._lock:
                # Append log entry as JSON line to the current run's file
                with open(self.current_log_file, "a", encoding="utf-8") as f:
                    json.dump(log_entry, f, ensure_ascii=False, default=str)
                    f.write("\n")
            
            logger.debug(f"Audit log entry written: {log_entry.get('correlation_id')}")
        except Exception as e:
            # Don't let audit logging failures break the application
            logger.error(f"Failed to write audit log entry: {str(e)}", exc_info=True)
    
    def log_tool_call(
        self,
        correlation_id: str,
        tool_name: str,
        agent_id: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        status: str = "success"
    ) -> None:
        """
        Log a tool call execution with full context.
        
        Purpose (Why):
        Records complete information about tool executions for audit trail.
        Enables full traceability of tool usage, debugging of tool-related
        issues, and compliance with audit requirements. Every tool call is
        logged with its inputs, outputs, and context.
        
        Implementation (What):
        Creates a structured log entry containing all tool call information:
        correlation ID, timestamp, agent ID, tool name, arguments, result,
        context, and status. Writes the entry to the audit log file. Status
        can be "success" or "error" to indicate execution outcome.
        
        Args:
            correlation_id: Unique identifier for the request/conversation
            tool_name: Name of the tool that was called
            agent_id: Identifier for the agent/session making the call
            arguments: Dictionary of arguments passed to the tool
            result: Dictionary containing the tool execution result
            context: Optional dictionary with additional context information
                (e.g., user message, conversation history, etc.)
            status: Execution status - "success" or "error"
        
        Returns:
            None. Writes log entry to audit log file.
        
        Raises:
            None. Exceptions during logging are caught and logged internally,
            but do not propagate to prevent audit logging failures from breaking
            the application.
        
        Example:
            >>> logger = AuditLogger()
            >>> logger.log_tool_call(
            ...     correlation_id="123",
            ...     tool_name="get_medication_by_name",
            ...     agent_id="session_456",
            ...     arguments={"name": "Acamol"},
            ...     result={"medication_id": "med_001"},
            ...     status="success"
            ... )
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "correlation_id": correlation_id,
            "agent_id": agent_id,
            "event_type": "tool_call",
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "context": context or {},
            "status": status
        }
        
        self._write_log_entry(log_entry)
        logger.debug(
            f"Logged tool call: {tool_name} by {agent_id} "
            f"(correlation_id: {correlation_id}, status: {status})"
        )
    
    def log_agent_action(
        self,
        correlation_id: str,
        agent_id: str,
        action: str,
        details: Dict[str, Any],
        status: str = "success"
    ) -> None:
        """
        Log an agent action with full context.
        
        Purpose (Why):
        Records agent-level actions (not just tool calls) for complete audit
        trail. Enables tracking of agent behavior, decision-making, and
        high-level operations. Useful for understanding agent flow and
        debugging agent-level issues.
        
        Implementation (What):
        Creates a structured log entry containing agent action information:
        correlation ID, timestamp, agent ID, action type, details, and status.
        Writes the entry to the audit log file. Used for logging agent-level
        events like message processing start, response generation, error
        handling, etc.
        
        Args:
            correlation_id: Unique identifier for the request/conversation
            agent_id: Identifier for the agent/session
            action: Type of action being logged (e.g., "message_received",
                "response_generated", "error_handled")
            details: Dictionary containing action-specific details
            status: Action status - "success" or "error"
        
        Returns:
            None. Writes log entry to audit log file.
        
        Raises:
            None. Exceptions during logging are caught and logged internally,
            but do not propagate to prevent audit logging failures from breaking
            the application.
        
        Example:
            >>> logger = AuditLogger()
            >>> logger.log_agent_action(
            ...     correlation_id="123",
            ...     agent_id="session_456",
            ...     action="message_received",
            ...     details={"message": "Tell me about Acamol"},
            ...     status="success"
            ... )
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "correlation_id": correlation_id,
            "agent_id": agent_id,
            "event_type": "agent_action",
            "action": action,
            "details": details,
            "status": status
        }
        
        self._write_log_entry(log_entry)
        logger.debug(
            f"Logged agent action: {action} by {agent_id} "
            f"(correlation_id: {correlation_id}, status: {status})"
        )


# Module-level shared audit logger instance
# This can be imported and used across the application to ensure
# all modules use the same logger instance and log file
_shared_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """
    Get or create the shared audit logger instance.
    
    Purpose (Why):
    Provides a singleton-like access to the audit logger, ensuring all modules
    use the same logger instance and write to the same log file. This is important
    for maintaining consistent logging across the application.
    
    Implementation (What):
    Creates a shared AuditLogger instance on first call and returns the same
    instance on subsequent calls. This ensures all modules share the same logger.
    
    Returns:
        AuditLogger: The shared AuditLogger instance. Creates a new instance
        on first call and returns the same instance on subsequent calls.
    
    Raises:
        OSError: If log directory cannot be created during first initialization.
    """
    global _shared_audit_logger
    if _shared_audit_logger is None:
        _shared_audit_logger = AuditLogger()
    return _shared_audit_logger


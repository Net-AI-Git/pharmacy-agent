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
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

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
    for single-threaded use (Python GIL). For multi-threaded environments,
    additional locking would be needed.
    
    Attributes:
        log_dir: Directory path for audit logs
        enabled: Whether audit logging is enabled (from environment or default: True)
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
        directory if it doesn't exist. All configuration is optional to allow
        flexible setup.
        
        Args:
            log_dir: Directory path for audit logs.
                If None, reads from AUDIT_LOG_DIR env var or uses DEFAULT_AUDIT_LOG_DIR.
            enabled: Whether audit logging is enabled.
                If None, reads from AUDIT_LOGGING_ENABLED env var or defaults to True.
        """
        self.log_dir = log_dir or os.getenv("AUDIT_LOG_DIR", DEFAULT_AUDIT_LOG_DIR)
        self.enabled = (
            enabled
            if enabled is not None
            else os.getenv("AUDIT_LOGGING_ENABLED", "true").lower() == "true"
        )
        
        # Create log directory if it doesn't exist
        if self.enabled:
            Path(self.log_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"AuditLogger initialized with log directory: {self.log_dir}")
        else:
            logger.info("AuditLogger initialized but logging is disabled")
    
    def _get_log_file_path(self) -> str:
        """
        Get the log file path for today's date.
        
        Purpose (Why):
        Organizes logs by date for easy retrieval and analysis. Each day gets
        its own log file, making it simple to find logs for a specific date
        or time period.
        
        Implementation (What):
        Creates a file path based on today's date in format: YYYY-MM-DD.json
        in the configured log directory.
        
        Returns:
            Full path to today's log file
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"audit_{today}.json")
    
    def _write_log_entry(self, log_entry: Dict[str, Any]) -> None:
        """
        Write a log entry to the audit log file.
        
        Purpose (Why):
        Persists audit log entries to disk for long-term storage and analysis.
        Ensures all operations are recorded for compliance and debugging.
        
        Implementation (What):
        Appends log entry to today's log file as a JSON line. Uses JSON lines
        format (one JSON object per line) for easy parsing and streaming.
        Creates file if it doesn't exist. Handles errors gracefully to prevent
        audit logging failures from breaking the application.
        
        Args:
            log_entry: Dictionary containing log entry data
        """
        if not self.enabled:
            return
        
        try:
            log_file_path = self._get_log_file_path()
            
            # Append log entry as JSON line
            with open(log_file_path, "a", encoding="utf-8") as f:
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


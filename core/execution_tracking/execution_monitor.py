"""
Execution Monitor Module

This module provides functionality for monitoring the execution flow of agents and tasks.
It tracks execution progress, performance metrics, and identifies potential issues.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import logging
from datetime import datetime
from threading import Lock
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Enumeration of possible execution statuses"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionRecord:
    """Represents a record of an execution"""
    execution_id: str
    task_id: str
    agent_id: str
    status: ExecutionStatus
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    error_message: Optional[str]
    metadata: Dict[str, Any]


class ExecutionMonitor:
    """
    Monitors the execution flow of agents and tasks.
    
    This class tracks execution progress, performance metrics, and identifies potential issues.
    """
    
    def __init__(self):
        """Initialize the ExecutionMonitor with empty execution records."""
        self._executions: Dict[str, ExecutionRecord] = {}
        self._agent_executions: Dict[str, List[str]] = {}
        self._task_executions: Dict[str, List[str]] = {}
        self._lock = Lock()
    
    def start_execution(self, execution_id: str, task_id: str, agent_id: str, 
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Start tracking an execution.
        
        Args:
            execution_id (str): The unique identifier for the execution
            task_id (str): The ID of the task being executed
            agent_id (str): The ID of the agent executing the task
            metadata (Optional[Dict[str, Any]]): Additional metadata about the execution
            
        Returns:
            bool: True if execution tracking was started successfully, False otherwise
        """
        with self._lock:
            if execution_id in self._executions:
                logger.warning(f"Execution {execution_id} is already being tracked")
                return False
            
            if metadata is None:
                metadata = {}
            
            execution_record = ExecutionRecord(
                execution_id=execution_id,
                task_id=task_id,
                agent_id=agent_id,
                status=ExecutionStatus.RUNNING,
                start_time=datetime.now().timestamp(),
                end_time=None,
                duration=None,
                error_message=None,
                metadata=metadata
            )
            
            self._executions[execution_id] = execution_record
            
            # Update agent executions mapping
            if agent_id not in self._agent_executions:
                self._agent_executions[agent_id] = []
            self._agent_executions[agent_id].append(execution_id)
            
            # Update task executions mapping
            if task_id not in self._task_executions:
                self._task_executions[task_id] = []
            self._task_executions[task_id].append(execution_id)
            
            logger.debug(f"Started tracking execution {execution_id} for task {task_id} on agent {agent_id}")
            return True
    
    def complete_execution(self, execution_id: str, result: Optional[Any] = None) -> bool:
        """
        Mark an execution as completed.
        
        Args:
            execution_id (str): The ID of the execution to complete
            result (Optional[Any]): The result of the execution
            
        Returns:
            bool: True if execution was marked as completed successfully, False otherwise
        """
        with self._lock:
            if execution_id not in self._executions:
                logger.warning(f"Execution {execution_id} not found")
                return False
            
            execution_record = self._executions[execution_id]
            if execution_record.status != ExecutionStatus.RUNNING:
                logger.warning(f"Execution {execution_id} is not running")
                return False
            
            end_time = datetime.now().timestamp()
            execution_record.status = ExecutionStatus.COMPLETED
            execution_record.end_time = end_time
            execution_record.duration = end_time - execution_record.start_time
            if result is not None:
                execution_record.metadata["result"] = result
            
            logger.debug(f"Completed execution {execution_id}")
            return True
    
    def fail_execution(self, execution_id: str, error_message: str) -> bool:
        """
        Mark an execution as failed.
        
        Args:
            execution_id (str): The ID of the execution to mark as failed
            error_message (str): The error message explaining the failure
            
        Returns:
            bool: True if execution was marked as failed successfully, False otherwise
        """
        with self._lock:
            if execution_id not in self._executions:
                logger.warning(f"Execution {execution_id} not found")
                return False
            
            execution_record = self._executions[execution_id]
            if execution_record.status != ExecutionStatus.RUNNING:
                logger.warning(f"Execution {execution_id} is not running")
                return False
            
            end_time = datetime.now().timestamp()
            execution_record.status = ExecutionStatus.FAILED
            execution_record.end_time = end_time
            execution_record.duration = end_time - execution_record.start_time
            execution_record.error_message = error_message
            
            logger.debug(f"Failed execution {execution_id}: {error_message}")
            return True
    
    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel an execution.
        
        Args:
            execution_id (str): The ID of the execution to cancel
            
        Returns:
            bool: True if execution was cancelled successfully, False otherwise
        """
        with self._lock:
            if execution_id not in self._executions:
                logger.warning(f"Execution {execution_id} not found")
                return False
            
            execution_record = self._executions[execution_id]
            if execution_record.status != ExecutionStatus.RUNNING:
                logger.warning(f"Execution {execution_id} is not running")
                return False
            
            end_time = datetime.now().timestamp()
            execution_record.status = ExecutionStatus.CANCELLED
            execution_record.end_time = end_time
            execution_record.duration = end_time - execution_record.start_time
            
            logger.debug(f"Cancelled execution {execution_id}")
            return True
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """
        Get an execution record by its ID.
        
        Args:
            execution_id (str): The ID of the execution to retrieve
            
        Returns:
            ExecutionRecord: The execution record, or None if not found
        """
        return self._executions.get(execution_id)
    
    def get_agent_executions(self, agent_id: str) -> List[ExecutionRecord]:
        """
        Get all executions for a specific agent.
        
        Args:
            agent_id (str): The ID of the agent
            
        Returns:
            List[ExecutionRecord]: A list of execution records for the agent
        """
        execution_ids = self._agent_executions.get(agent_id, [])
        return [self._executions[exec_id] for exec_id in execution_ids if exec_id in self._executions]
    
    def get_task_executions(self, task_id: str) -> List[ExecutionRecord]:
        """
        Get all executions for a specific task.
        
        Args:
            task_id (str): The ID of the task
            
        Returns:
            List[ExecutionRecord]: A list of execution records for the task
        """
        execution_ids = self._task_executions.get(task_id, [])
        return [self._executions[exec_id] for exec_id in execution_ids if exec_id in self._executions]
    
    def get_executions_by_status(self, status: ExecutionStatus) -> List[ExecutionRecord]:
        """
        Get all executions with a specific status.
        
        Args:
            status (ExecutionStatus): The status to filter by
            
        Returns:
            List[ExecutionRecord]: A list of execution records with the specified status
        """
        return [execution for execution in self._executions.values() if execution.status == status]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get statistics about executions.
        
        Returns:
            Dict[str, Any]: Statistics about executions including counts by status
        """
        status_counts = {}
        total_duration = 0.0
        completed_executions = 0
        
        for execution in self._executions.values():
            status = execution.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if execution.duration is not None:
                total_duration += execution.duration
                if execution.status == ExecutionStatus.COMPLETED:
                    completed_executions += 1
        
        avg_duration = total_duration / completed_executions if completed_executions > 0 else 0
        
        return {
            "total_executions": len(self._executions),
            "status_counts": status_counts,
            "average_duration": avg_duration,
            "total_agents": len(self._agent_executions),
            "total_tasks": len(self._task_executions)
        }
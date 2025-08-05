"""
Gap Detector Module

This module provides functionality for detecting gaps in execution flows.
It identifies missing executions, timing inconsistencies, and potential issues.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
from threading import Lock

from core.execution_tracking.execution_monitor import ExecutionMonitor, ExecutionStatus, ExecutionRecord

logger = logging.getLogger(__name__)


class GapDetector:
    """
    Detects gaps in execution flows.
    
    This class identifies missing executions, timing inconsistencies, and potential issues
    in the execution flow of agents and tasks.
    """
    
    def __init__(self, execution_monitor: ExecutionMonitor):
        """
        Initialize the GapDetector.
        
        Args:
            execution_monitor (ExecutionMonitor): The execution monitor to use for gap detection
        """
        self._execution_monitor = execution_monitor
        self._expected_executions: Dict[str, Dict[str, Any]] = {}
        self._gap_threshold_seconds = 300  # 5 minutes
        self._lock = Lock()
    
    def set_gap_threshold(self, seconds: int) -> bool:
        """
        Set the gap threshold for detecting timing inconsistencies.
        
        Args:
            seconds (int): The number of seconds after which a gap is detected
            
        Returns:
            bool: True if threshold was set successfully, False otherwise
        """
        if seconds > 0:
            self._gap_threshold_seconds = seconds
            logger.debug(f"Set gap threshold to {seconds} seconds")
            return True
        return False
    
    def register_expected_execution(self, execution_id: str, expected_time: float, 
                                  task_id: str, agent_id: str) -> bool:
        """
        Register an expected execution.
        
        Args:
            execution_id (str): The expected execution ID
            expected_time (float): The expected time of execution (timestamp)
            task_id (str): The ID of the task to be executed
            agent_id (str): The ID of the agent expected to execute the task
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        with self._lock:
            self._expected_executions[execution_id] = {
                "expected_time": expected_time,
                "task_id": task_id,
                "agent_id": agent_id,
                "registered_at": datetime.now().timestamp()
            }
            logger.debug(f"Registered expected execution {execution_id}")
            return True
    
    def unregister_expected_execution(self, execution_id: str) -> bool:
        """
        Unregister an expected execution.
        
        Args:
            execution_id (str): The execution ID to unregister
            
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        with self._lock:
            if execution_id in self._expected_executions:
                del self._expected_executions[execution_id]
                logger.debug(f"Unregistered expected execution {execution_id}")
                return True
            return False
    
    def detect_gaps(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect gaps in execution flows.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: A dictionary of detected gaps categorized by type
        """
        gaps = {
            "missing_executions": [],
            "timing_gaps": [],
            "failed_executions": [],
            "long_running_executions": []
        }
        
        current_time = datetime.now().timestamp()
        
        # Detect missing executions
        for execution_id, expected in self._expected_executions.items():
            # Check if execution exists
            execution = self._execution_monitor.get_execution(execution_id)
            if not execution:
                # Check if expected time has passed
                if current_time > expected["expected_time"] + self._gap_threshold_seconds:
                    gaps["missing_executions"].append({
                        "execution_id": execution_id,
                        "task_id": expected["task_id"],
                        "agent_id": expected["agent_id"],
                        "expected_time": expected["expected_time"],
                        "delay_seconds": current_time - expected["expected_time"]
                    })
        
        # Detect timing gaps between consecutive executions
        all_executions = list(self._execution_monitor._executions.values())
        all_executions.sort(key=lambda x: x.start_time)
        
        for i in range(1, len(all_executions)):
            prev_execution = all_executions[i-1]
            curr_execution = all_executions[i]
            
            # Check if both executions are completed
            if (prev_execution.status == ExecutionStatus.COMPLETED and 
                curr_execution.status == ExecutionStatus.COMPLETED):
                gap_duration = curr_execution.start_time - prev_execution.end_time
                if gap_duration > self._gap_threshold_seconds:
                    gaps["timing_gaps"].append({
                        "prev_execution_id": prev_execution.execution_id,
                        "curr_execution_id": curr_execution.execution_id,
                        "gap_duration": gap_duration,
                        "prev_end_time": prev_execution.end_time,
                        "curr_start_time": curr_execution.start_time
                    })
        
        # Detect failed executions
        failed_executions = self._execution_monitor.get_executions_by_status(ExecutionStatus.FAILED)
        for execution in failed_executions:
            gaps["failed_executions"].append({
                "execution_id": execution.execution_id,
                "task_id": execution.task_id,
                "agent_id": execution.agent_id,
                "error_message": execution.error_message,
                "start_time": execution.start_time
            })
        
        # Detect long-running executions
        running_executions = self._execution_monitor.get_executions_by_status(ExecutionStatus.RUNNING)
        for execution in running_executions:
            duration = current_time - execution.start_time
            if duration > self._gap_threshold_seconds:
                gaps["long_running_executions"].append({
                    "execution_id": execution.execution_id,
                    "task_id": execution.task_id,
                    "agent_id": execution.agent_id,
                    "duration": duration,
                    "start_time": execution.start_time
                })
        
        return gaps
    
    def get_gap_summary(self) -> Dict[str, int]:
        """
        Get a summary of detected gaps.
        
        Returns:
            Dict[str, int]: A summary of gap counts by type
        """
        gaps = self.detect_gaps()
        return {gap_type: len(gap_list) for gap_type, gap_list in gaps.items()}
    
    def clear_stale_expected_executions(self, stale_threshold_seconds: int = 3600) -> int:
        """
        Clear stale expected executions that have not been fulfilled.
        
        Args:
            stale_threshold_seconds (int): The threshold in seconds for considering an expected execution stale
            
        Returns:
            int: The number of stale executions cleared
        """
        current_time = datetime.now().timestamp()
        stale_count = 0
        
        with self._lock:
            stale_executions = []
            for execution_id, expected in self._expected_executions.items():
                if current_time - expected["registered_at"] > stale_threshold_seconds:
                    stale_executions.append(execution_id)
            
            for execution_id in stale_executions:
                del self._expected_executions[execution_id]
                stale_count += 1
            
            if stale_count > 0:
                logger.debug(f"Cleared {stale_count} stale expected executions")
        
        return stale_count
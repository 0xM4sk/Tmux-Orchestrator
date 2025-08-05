"""
Recovery Manager Module

This module provides functionality for recovering from execution failures and gaps.
It implements recovery strategies and manages the recovery process.
"""

from typing import Dict, List, Any, Optional, Callable
import logging
from datetime import datetime
from threading import Lock
from enum import Enum

from core.execution_tracking.execution_monitor import ExecutionMonitor, ExecutionStatus
from core.execution_tracking.gap_detector import GapDetector

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Enumeration of possible recovery strategies"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    NOTIFY = "notify"


class RecoveryManager:
    """
    Manages recovery from execution failures and gaps.
    
    This class implements recovery strategies and manages the recovery process
    for failed or missing executions.
    """
    
    def __init__(self, execution_monitor: ExecutionMonitor, gap_detector: GapDetector):
        """
        Initialize the RecoveryManager.
        
        Args:
            execution_monitor (ExecutionMonitor): The execution monitor to use
            gap_detector (GapDetector): The gap detector to use
        """
        self._execution_monitor = execution_monitor
        self._gap_detector = gap_detector
        self._recovery_strategies: Dict[str, Callable] = {}
        self._default_strategy = RecoveryStrategy.RETRY
        self._max_retry_attempts = 3
        self._recovery_history: List[Dict[str, Any]] = []
        self._lock = Lock()
        
        # Register default recovery strategies
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register default recovery strategies."""
        self._recovery_strategies[RecoveryStrategy.RETRY.value] = self._retry_strategy
        self._recovery_strategies[RecoveryStrategy.SKIP.value] = self._skip_strategy
        self._recovery_strategies[RecoveryStrategy.NOTIFY.value] = self._notify_strategy
    
    def set_default_strategy(self, strategy: RecoveryStrategy) -> bool:
        """
        Set the default recovery strategy.
        
        Args:
            strategy (RecoveryStrategy): The default strategy to use
            
        Returns:
            bool: True if strategy was set successfully, False otherwise
        """
        self._default_strategy = strategy
        logger.debug(f"Set default recovery strategy to {strategy.value}")
        return True
    
    def set_max_retry_attempts(self, attempts: int) -> bool:
        """
        Set the maximum number of retry attempts.
        
        Args:
            attempts (int): The maximum number of retry attempts
            
        Returns:
            bool: True if attempts were set successfully, False otherwise
        """
        if attempts > 0:
            self._max_retry_attempts = attempts
            logger.debug(f"Set maximum retry attempts to {attempts}")
            return True
        return False
    
    def register_recovery_strategy(self, strategy_name: str, strategy_function: Callable) -> bool:
        """
        Register a custom recovery strategy.
        
        Args:
            strategy_name (str): The name of the strategy
            strategy_function (Callable): The function implementing the strategy
            
        Returns:
            bool: True if strategy was registered successfully, False otherwise
        """
        self._recovery_strategies[strategy_name] = strategy_function
        logger.debug(f"Registered recovery strategy: {strategy_name}")
        return True
    
    def recover_from_gaps(self) -> Dict[str, Any]:
        """
        Recover from detected gaps in execution flows.
        
        Returns:
            Dict[str, Any]: A summary of recovery actions taken
        """
        gaps = self._gap_detector.detect_gaps()
        recovery_summary = {
            "total_gaps": 0,
            "recovered_gaps": 0,
            "failed_recoveries": 0,
            "recovery_actions": []
        }
        
        # Recover from missing executions
        for gap in gaps["missing_executions"]:
            recovery_summary["total_gaps"] += 1
            result = self._recover_missing_execution(gap)
            if result["success"]:
                recovery_summary["recovered_gaps"] += 1
            else:
                recovery_summary["failed_recoveries"] += 1
            recovery_summary["recovery_actions"].append(result)
        
        # Handle failed executions
        for gap in gaps["failed_executions"]:
            recovery_summary["total_gaps"] += 1
            result = self._recover_failed_execution(gap)
            if result["success"]:
                recovery_summary["recovered_gaps"] += 1
            else:
                recovery_summary["failed_recoveries"] += 1
            recovery_summary["recovery_actions"].append(result)
        
        # Handle long-running executions
        for gap in gaps["long_running_executions"]:
            recovery_summary["total_gaps"] += 1
            result = self._recover_long_running_execution(gap)
            if result["success"]:
                recovery_summary["recovered_gaps"] += 1
            else:
                recovery_summary["failed_recoveries"] += 1
            recovery_summary["recovery_actions"].append(result)
        
        return recovery_summary
    
    def _recover_missing_execution(self, gap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recover from a missing execution.
        
        Args:
            gap (Dict[str, Any]): Information about the missing execution
            
        Returns:
            Dict[str, Any]: Information about the recovery attempt
        """
        execution_id = gap["execution_id"]
        task_id = gap["task_id"]
        agent_id = gap["agent_id"]
        
        logger.info(f"Attempting to recover missing execution {execution_id}")
        
        # Try the default recovery strategy
        strategy = self._default_strategy.value
        if strategy in self._recovery_strategies:
            try:
                result = self._recovery_strategies[strategy](execution_id, task_id, agent_id, gap)
                recovery_record = {
                    "timestamp": datetime.now().timestamp(),
                    "gap_type": "missing_execution",
                    "execution_id": execution_id,
                    "strategy": strategy,
                    "success": result.get("success", False),
                    "details": result.get("details", "")
                }
                
                with self._lock:
                    self._recovery_history.append(recovery_record)
                
                return recovery_record
            except Exception as e:
                logger.error(f"Error during recovery of missing execution {execution_id}: {e}")
                return {
                    "timestamp": datetime.now().timestamp(),
                    "gap_type": "missing_execution",
                    "execution_id": execution_id,
                    "strategy": strategy,
                    "success": False,
                    "details": f"Recovery error: {e}"
                }
        
        return {
            "timestamp": datetime.now().timestamp(),
            "gap_type": "missing_execution",
            "execution_id": execution_id,
            "strategy": strategy,
            "success": False,
            "details": "No valid recovery strategy found"
        }
    
    def _recover_failed_execution(self, gap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recover from a failed execution.
        
        Args:
            gap (Dict[str, Any]): Information about the failed execution
            
        Returns:
            Dict[str, Any]: Information about the recovery attempt
        """
        execution_id = gap["execution_id"]
        task_id = gap["task_id"]
        agent_id = gap["agent_id"]
        error_message = gap["error_message"]
        
        logger.info(f"Attempting to recover failed execution {execution_id}")
        
        # Try the default recovery strategy
        strategy = self._default_strategy.value
        if strategy in self._recovery_strategies:
            try:
                result = self._recovery_strategies[strategy](execution_id, task_id, agent_id, gap)
                recovery_record = {
                    "timestamp": datetime.now().timestamp(),
                    "gap_type": "failed_execution",
                    "execution_id": execution_id,
                    "strategy": strategy,
                    "success": result.get("success", False),
                    "details": result.get("details", "")
                }
                
                with self._lock:
                    self._recovery_history.append(recovery_record)
                
                return recovery_record
            except Exception as e:
                logger.error(f"Error during recovery of failed execution {execution_id}: {e}")
                return {
                    "timestamp": datetime.now().timestamp(),
                    "gap_type": "failed_execution",
                    "execution_id": execution_id,
                    "strategy": strategy,
                    "success": False,
                    "details": f"Recovery error: {e}"
                }
        
        return {
            "timestamp": datetime.now().timestamp(),
            "gap_type": "failed_execution",
            "execution_id": execution_id,
            "strategy": strategy,
            "success": False,
            "details": "No valid recovery strategy found"
        }
    
    def _recover_long_running_execution(self, gap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recover from a long-running execution.
        
        Args:
            gap (Dict[str, Any]): Information about the long-running execution
            
        Returns:
            Dict[str, Any]: Information about the recovery attempt
        """
        execution_id = gap["execution_id"]
        task_id = gap["task_id"]
        agent_id = gap["agent_id"]
        
        logger.info(f"Attempting to recover long-running execution {execution_id}")
        
        # For long-running executions, we'll use the notify strategy by default
        strategy = RecoveryStrategy.NOTIFY.value
        if strategy in self._recovery_strategies:
            try:
                result = self._recovery_strategies[strategy](execution_id, task_id, agent_id, gap)
                recovery_record = {
                    "timestamp": datetime.now().timestamp(),
                    "gap_type": "long_running_execution",
                    "execution_id": execution_id,
                    "strategy": strategy,
                    "success": result.get("success", False),
                    "details": result.get("details", "")
                }
                
                with self._lock:
                    self._recovery_history.append(recovery_record)
                
                return recovery_record
            except Exception as e:
                logger.error(f"Error during recovery of long-running execution {execution_id}: {e}")
                return {
                    "timestamp": datetime.now().timestamp(),
                    "gap_type": "long_running_execution",
                    "execution_id": execution_id,
                    "strategy": strategy,
                    "success": False,
                    "details": f"Recovery error: {e}"
                }
        
        return {
            "timestamp": datetime.now().timestamp(),
            "gap_type": "long_running_execution",
            "execution_id": execution_id,
            "strategy": strategy,
            "success": False,
            "details": "No valid recovery strategy found"
        }
    
    def _retry_strategy(self, execution_id: str, task_id: str, agent_id: str, gap_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retry strategy for recovering executions.
        
        Args:
            execution_id (str): The ID of the execution
            task_id (str): The ID of the task
            agent_id (str): The ID of the agent
            gap_info (Dict[str, Any]): Information about the gap
            
        Returns:
            Dict[str, Any]: Information about the strategy execution
        """
        # Check retry attempts
        retry_count = 0
        for record in self._recovery_history:
            if record.get("execution_id") == execution_id and record.get("strategy") == RecoveryStrategy.RETRY.value:
                retry_count += 1
        
        if retry_count >= self._max_retry_attempts:
            return {
                "success": False,
                "details": f"Max retry attempts ({self._max_retry_attempts}) exceeded"
            }
        
        # Simulate retry logic
        # In a real implementation, this would actually retry the execution
        return {
            "success": True,
            "details": f"Retry attempt {retry_count + 1} initiated for execution {execution_id}"
        }
    
    def _skip_strategy(self, execution_id: str, task_id: str, agent_id: str, gap_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Skip strategy for recovering executions.
        
        Args:
            execution_id (str): The ID of the execution
            task_id (str): The ID of the task
            agent_id (str): The ID of the agent
            gap_info (Dict[str, Any]): Information about the gap
            
        Returns:
            Dict[str, Any]: Information about the strategy execution
        """
        # Simulate skip logic
        # In a real implementation, this would mark the execution as skipped
        return {
            "success": True,
            "details": f"Execution {execution_id} marked as skipped"
        }
    
    def _notify_strategy(self, execution_id: str, task_id: str, agent_id: str, gap_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notify strategy for recovering executions.
        
        Args:
            execution_id (str): The ID of the execution
            task_id (str): The ID of the task
            agent_id (str): The ID of the agent
            gap_info (Dict[str, Any]): Information about the gap
            
        Returns:
            Dict[str, Any]: Information about the strategy execution
        """
        # Simulate notification logic
        # In a real implementation, this would send notifications to administrators
        return {
            "success": True,
            "details": f"Notification sent for execution {execution_id}"
        }
    
    def get_recovery_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the recovery history.
        
        Args:
            limit (Optional[int]): The maximum number of records to return
            
        Returns:
            List[Dict[str, Any]]: The recovery history
        """
        with self._lock:
            history = self._recovery_history.copy()
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """
        Get statistics about recovery actions.
        
        Returns:
            Dict[str, Any]: Statistics about recovery actions
        """
        with self._lock:
            total_recoveries = len(self._recovery_history)
            successful_recoveries = len([r for r in self._recovery_history if r.get("success", False)])
            failed_recoveries = total_recoveries - successful_recoveries
            
            strategy_counts = {}
            for record in self._recovery_history:
                strategy = record.get("strategy", "unknown")
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            "total_recoveries": total_recoveries,
            "successful_recoveries": successful_recoveries,
            "failed_recoveries": failed_recoveries,
            "success_rate": successful_recoveries / total_recoveries if total_recoveries > 0 else 0,
            "strategy_counts": strategy_counts
        }
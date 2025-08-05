"""
Alert System Module

This module provides functionality for managing system alerts.
It handles alert generation, notification, and escalation.
"""

from typing import Dict, List, Any, Optional, Callable
import logging
from datetime import datetime
from threading import Lock
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Enumeration of alert severities"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Enumeration of alert statuses"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"


@dataclass
class Alert:
    """Represents a system alert"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    created_at: float
    updated_at: float
    resolved_at: Optional[float]
    metadata: Dict[str, Any]


class AlertSystem:
    """
    Manages system alerts.
    
    This class handles alert generation, notification, and escalation.
    """
    
    def __init__(self):
        """Initialize the AlertSystem with empty alert storage."""
        self._alerts: Dict[str, Alert] = {}
        self._alert_handlers: Dict[AlertSeverity, List[Callable]] = {}
        self._silenced_alerts: Dict[str, float] = {}  # alert_id -> silence_until_timestamp
        self._alert_history: List[Alert] = []
        self._max_history_size = 1000
        self._lock = Lock()
    
    def add_alert_handler(self, severity: AlertSeverity, handler: Callable) -> bool:
        """
        Add an alert handler for a specific severity level.
        
        Args:
            severity (AlertSeverity): The severity level to handle
            handler (Callable): The function to call when an alert of this severity is generated
            
        Returns:
            bool: True if handler was added successfully, False otherwise
        """
        with self._lock:
            if severity not in self._alert_handlers:
                self._alert_handlers[severity] = []
            self._alert_handlers[severity].append(handler)
            logger.debug(f"Added alert handler for severity {severity.value}")
            return True
    
    def remove_alert_handler(self, severity: AlertSeverity, handler: Callable) -> bool:
        """
        Remove an alert handler for a specific severity level.
        
        Args:
            severity (AlertSeverity): The severity level
            handler (Callable): The handler function to remove
            
        Returns:
            bool: True if handler was removed successfully, False otherwise
        """
        with self._lock:
            if severity in self._alert_handlers and handler in self._alert_handlers[severity]:
                self._alert_handlers[severity].remove(handler)
                logger.debug(f"Removed alert handler for severity {severity.value}")
                return True
            return False
    
    def create_alert(self, alert_id: str, title: str, description: str, 
                    severity: AlertSeverity, source: str, 
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new alert.
        
        Args:
            alert_id (str): The unique identifier for the alert
            title (str): The title of the alert
            description (str): The description of the alert
            severity (AlertSeverity): The severity level of the alert
            source (str): The source of the alert
            metadata (Optional[Dict[str, Any]]): Additional metadata about the alert
            
        Returns:
            bool: True if alert was created successfully, False otherwise
        """
        with self._lock:
            # Check if alert is silenced
            current_time = datetime.now().timestamp()
            if alert_id in self._silenced_alerts:
                if current_time < self._silenced_alerts[alert_id]:
                    logger.debug(f"Alert {alert_id} is silenced, not creating")
                    return False
                else:
                    # Silence period has expired
                    del self._silenced_alerts[alert_id]
            
            if metadata is None:
                metadata = {}
            
            alert = Alert(
                alert_id=alert_id,
                title=title,
                description=description,
                severity=severity,
                status=AlertStatus.ACTIVE,
                source=source,
                created_at=current_time,
                updated_at=current_time,
                resolved_at=None,
                metadata=metadata
            )
            
            self._alerts[alert_id] = alert
            
            # Add to history, maintaining max size
            self._alert_history.append(alert)
            if len(self._alert_history) > self._max_history_size:
                self._alert_history.pop(0)
            
            logger.info(f"Created alert {alert_id}: {title} ({severity.value})")
            
            # Trigger handlers for this severity and higher
            self._trigger_alert_handlers(alert)
            
            return True
    
    def _trigger_alert_handlers(self, alert: Alert):
        """
        Trigger alert handlers for an alert.
        
        Args:
            alert (Alert): The alert to trigger handlers for
        """
        # Trigger handlers for the alert's severity and higher severities
        severity_order = [AlertSeverity.INFO, AlertSeverity.WARNING, AlertSeverity.ERROR, AlertSeverity.CRITICAL]
        alert_severity_index = severity_order.index(alert.severity)
        
        for i in range(alert_severity_index, len(severity_order)):
            severity = severity_order[i]
            if severity in self._alert_handlers:
                for handler in self._alert_handlers[severity]:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.error(f"Error in alert handler for severity {severity.value}: {e}")
    
    def acknowledge_alert(self, alert_id: str, user: Optional[str] = None) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id (str): The ID of the alert to acknowledge
            user (Optional[str]): The user acknowledging the alert
            
        Returns:
            bool: True if alert was acknowledged successfully, False otherwise
        """
        with self._lock:
            if alert_id not in self._alerts:
                logger.warning(f"Alert {alert_id} not found")
                return False
            
            alert = self._alerts[alert_id]
            if alert.status == AlertStatus.RESOLVED:
                logger.warning(f"Alert {alert_id} is already resolved")
                return False
            
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.updated_at = datetime.now().timestamp()
            if user:
                alert.metadata["acknowledged_by"] = user
            
            logger.debug(f"Alert {alert_id} acknowledged by {user or 'system'}")
            return True
    
    def resolve_alert(self, alert_id: str, resolution_notes: Optional[str] = None) -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id (str): The ID of the alert to resolve
            resolution_notes (Optional[str]): Notes about the resolution
            
        Returns:
            bool: True if alert was resolved successfully, False otherwise
        """
        with self._lock:
            if alert_id not in self._alerts:
                logger.warning(f"Alert {alert_id} not found")
                return False
            
            alert = self._alerts[alert_id]
            if alert.status == AlertStatus.RESOLVED:
                logger.warning(f"Alert {alert_id} is already resolved")
                return False
            
            alert.status = AlertStatus.RESOLVED
            alert.updated_at = datetime.now().timestamp()
            alert.resolved_at = alert.updated_at
            if resolution_notes:
                alert.metadata["resolution_notes"] = resolution_notes
            
            logger.debug(f"Alert {alert_id} resolved")
            return True
    
    def silence_alert(self, alert_id: str, duration_seconds: int) -> bool:
        """
        Silence an alert for a specified duration.
        
        Args:
            alert_id (str): The ID of the alert to silence
            duration_seconds (int): The duration to silence the alert in seconds
            
        Returns:
            bool: True if alert was silenced successfully, False otherwise
        """
        with self._lock:
            current_time = datetime.now().timestamp()
            silence_until = current_time + duration_seconds
            self._silenced_alerts[alert_id] = silence_until
            
            # If the alert exists, resolve it
            if alert_id in self._alerts:
                self.resolve_alert(alert_id, "Silenced")
            
            logger.debug(f"Alert {alert_id} silenced for {duration_seconds} seconds")
            return True
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """
        Get an alert by its ID.
        
        Args:
            alert_id (str): The ID of the alert to retrieve
            
        Returns:
            Alert: The alert, or None if not found
        """
        return self._alerts.get(alert_id)
    
    def get_active_alerts(self) -> List[Alert]:
        """
        Get all active alerts.
        
        Returns:
            List[Alert]: A list of active alerts
        """
        with self._lock:
            return [alert for alert in self._alerts.values() 
                   if alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """
        Get all alerts with a specific severity.
        
        Args:
            severity (AlertSeverity): The severity level to filter by
            
        Returns:
            List[Alert]: A list of alerts with the specified severity
        """
        with self._lock:
            return [alert for alert in self._alerts.values() if alert.severity == severity]
    
    def get_alerts_by_source(self, source: str) -> List[Alert]:
        """
        Get all alerts from a specific source.
        
        Args:
            source (str): The source to filter by
            
        Returns:
            List[Alert]: A list of alerts from the specified source
        """
        with self._lock:
            return [alert for alert in self._alerts.values() if alert.source == source]
    
    def get_alert_history(self, limit: Optional[int] = None) -> List[Alert]:
        """
        Get the alert history.
        
        Args:
            limit (Optional[int]): The maximum number of alerts to return
            
        Returns:
            List[Alert]: The alert history
        """
        with self._lock:
            history = self._alert_history.copy()
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """
        Get a summary of alerts.
        
        Returns:
            Dict[str, Any]: A summary of alerts
        """
        with self._lock:
            total_alerts = len(self._alerts)
            active_alerts = len(self.get_active_alerts())
            
            severity_counts = {}
            for alert in self._alerts.values():
                severity = alert.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            status_counts = {}
            for alert in self._alerts.values():
                status = alert.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Get the most recent alert timestamp
            latest_alert_timestamp = 0
            for alert in self._alerts.values():
                if alert.created_at > latest_alert_timestamp:
                    latest_alert_timestamp = alert.created_at
            
            return {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "severity_counts": severity_counts,
                "status_counts": status_counts,
                "latest_alert": latest_alert_timestamp,
                "silenced_alerts": len(self._silenced_alerts)
            }
    
    def clear_resolved_alerts(self) -> int:
        """
        Clear resolved alerts from the active alerts storage.
        
        Returns:
            int: The number of alerts cleared
        """
        with self._lock:
            resolved_alerts = [alert_id for alert_id, alert in self._alerts.items() 
                              if alert.status == AlertStatus.RESOLVED]
            for alert_id in resolved_alerts:
                del self._alerts[alert_id]
            
            logger.debug(f"Cleared {len(resolved_alerts)} resolved alerts")
            return len(resolved_alerts)
"""
Dashboard Manager Module

This module provides functionality for managing the system dashboard.
It handles dashboard configuration, layout, and data visualization.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from threading import Lock
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class DashboardSection(Enum):
    """Enumeration of dashboard sections"""
    AGENT_STATUS = "agent_status"
    EXECUTION_METRICS = "execution_metrics"
    COMMUNICATION_FLOW = "communication_flow"
    SYSTEM_HEALTH = "system_health"
    ALERTS = "alerts"


@dataclass
class DashboardConfig:
    """Configuration for a dashboard"""
    dashboard_id: str
    title: str
    sections: List[DashboardSection]
    refresh_interval: int  # seconds
    enabled: bool = True
    layout: Dict[str, Any] = None


class DashboardManager:
    """
    Manages the system dashboard.
    
    This class handles dashboard configuration, layout, and data visualization.
    """
    
    def __init__(self):
        """Initialize the DashboardManager with empty dashboard storage."""
        self._dashboards: Dict[str, DashboardConfig] = {}
        self._active_dashboard: Optional[str] = None
        self._dashboard_data: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def create_dashboard(self, dashboard_id: str, title: str, sections: List[DashboardSection],
                        refresh_interval: int, layout: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new dashboard.
        
        Args:
            dashboard_id (str): The unique identifier for the dashboard
            title (str): The title of the dashboard
            sections (List[DashboardSection]): The sections to include in the dashboard
            refresh_interval (int): The refresh interval in seconds
            layout (Optional[Dict[str, Any]]): The layout configuration
            
        Returns:
            bool: True if dashboard was created successfully, False otherwise
        """
        with self._lock:
            if dashboard_id in self._dashboards:
                logger.warning(f"Dashboard {dashboard_id} already exists")
                return False
            
            if layout is None:
                layout = {}
            
            dashboard_config = DashboardConfig(
                dashboard_id=dashboard_id,
                title=title,
                sections=sections,
                refresh_interval=refresh_interval,
                layout=layout
            )
            
            self._dashboards[dashboard_id] = dashboard_config
            self._dashboard_data[dashboard_id] = {}
            
            logger.debug(f"Created dashboard {dashboard_id}: {title}")
            return True
    
    def update_dashboard(self, dashboard_id: str, title: Optional[str] = None,
                        sections: Optional[List[DashboardSection]] = None,
                        refresh_interval: Optional[int] = None,
                        layout: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing dashboard.
        
        Args:
            dashboard_id (str): The ID of the dashboard to update
            title (Optional[str]): The new title
            sections (Optional[List[DashboardSection]]): The new sections
            refresh_interval (Optional[int]): The new refresh interval
            layout (Optional[Dict[str, Any]]): The new layout configuration
            
        Returns:
            bool: True if dashboard was updated successfully, False otherwise
        """
        with self._lock:
            if dashboard_id not in self._dashboards:
                logger.warning(f"Dashboard {dashboard_id} not found")
                return False
            
            dashboard_config = self._dashboards[dashboard_id]
            
            if title is not None:
                dashboard_config.title = title
            
            if sections is not None:
                dashboard_config.sections = sections
            
            if refresh_interval is not None:
                dashboard_config.refresh_interval = refresh_interval
            
            if layout is not None:
                dashboard_config.layout = layout
            
            logger.debug(f"Updated dashboard {dashboard_id}")
            return True
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """
        Delete a dashboard.
        
        Args:
            dashboard_id (str): The ID of the dashboard to delete
            
        Returns:
            bool: True if dashboard was deleted successfully, False otherwise
        """
        with self._lock:
            if dashboard_id not in self._dashboards:
                logger.warning(f"Dashboard {dashboard_id} not found")
                return False
            
            del self._dashboards[dashboard_id]
            if dashboard_id in self._dashboard_data:
                del self._dashboard_data[dashboard_id]
            
            if self._active_dashboard == dashboard_id:
                self._active_dashboard = None
            
            logger.debug(f"Deleted dashboard {dashboard_id}")
            return True
    
    def set_active_dashboard(self, dashboard_id: str) -> bool:
        """
        Set the active dashboard.
        
        Args:
            dashboard_id (str): The ID of the dashboard to set as active
            
        Returns:
            bool: True if active dashboard was set successfully, False otherwise
        """
        if dashboard_id not in self._dashboards:
            logger.warning(f"Dashboard {dashboard_id} not found")
            return False
        
        self._active_dashboard = dashboard_id
        logger.debug(f"Set active dashboard to {dashboard_id}")
        return True
    
    def get_active_dashboard(self) -> Optional[DashboardConfig]:
        """
        Get the active dashboard configuration.
        
        Returns:
            DashboardConfig: The active dashboard configuration, or None if no active dashboard
        """
        if self._active_dashboard and self._active_dashboard in self._dashboards:
            return self._dashboards[self._active_dashboard]
        return None
    
    def get_dashboard(self, dashboard_id: str) -> Optional[DashboardConfig]:
        """
        Get a dashboard configuration by its ID.
        
        Args:
            dashboard_id (str): The ID of the dashboard to retrieve
            
        Returns:
            DashboardConfig: The dashboard configuration, or None if not found
        """
        return self._dashboards.get(dashboard_id)
    
    def list_dashboards(self) -> List[str]:
        """
        List all dashboard IDs.
        
        Returns:
            List[str]: A list of all dashboard IDs
        """
        return list(self._dashboards.keys())
    
    def update_dashboard_data(self, dashboard_id: str, section: DashboardSection, 
                             data: Dict[str, Any]) -> bool:
        """
        Update data for a specific dashboard section.
        
        Args:
            dashboard_id (str): The ID of the dashboard
            section (DashboardSection): The section to update
            data (Dict[str, Any]): The data to update
            
        Returns:
            bool: True if data was updated successfully, False otherwise
        """
        with self._lock:
            if dashboard_id not in self._dashboards:
                logger.warning(f"Dashboard {dashboard_id} not found")
                return False
            
            if dashboard_id not in self._dashboard_data:
                self._dashboard_data[dashboard_id] = {}
            
            self._dashboard_data[dashboard_id][section.value] = {
                "data": data,
                "timestamp": datetime.now().timestamp()
            }
            
            logger.debug(f"Updated data for dashboard {dashboard_id}, section {section.value}")
            return True
    
    def get_dashboard_data(self, dashboard_id: str, section: Optional[DashboardSection] = None) -> Dict[str, Any]:
        """
        Get data for a dashboard or specific section.
        
        Args:
            dashboard_id (str): The ID of the dashboard
            section (Optional[DashboardSection]): The specific section to retrieve data for
            
        Returns:
            Dict[str, Any]: The dashboard data
        """
        if dashboard_id not in self._dashboard_data:
            return {}
        
        if section:
            return self._dashboard_data[dashboard_id].get(section.value, {})
        
        return self._dashboard_data[dashboard_id]
    
    def get_dashboard_info(self) -> Dict[str, Any]:
        """
        Get information about all dashboards.
        
        Returns:
            Dict[str, Any]: Information about dashboards
        """
        dashboard_info = {}
        for dashboard_id, config in self._dashboards.items():
            dashboard_info[dashboard_id] = {
                "title": config.title,
                "sections": [section.value for section in config.sections],
                "refresh_interval": config.refresh_interval,
                "enabled": config.enabled
            }
        
        return {
            "total_dashboards": len(self._dashboards),
            "active_dashboard": self._active_dashboard,
            "dashboards": dashboard_info
        }
"""
Metrics Collector Module

This module provides functionality for collecting system metrics.
It gathers data from various system components for dashboard visualization.
"""

from typing import Dict, List, Any, Optional, Callable
import logging
from datetime import datetime
from threading import Lock, Timer
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Enumeration of metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Represents a system metric"""
    name: str
    type: MetricType
    value: Any
    labels: Dict[str, str]
    timestamp: float


class MetricsCollector:
    """
    Collects system metrics for dashboard visualization.
    
    This class gathers data from various system components and prepares it
    for dashboard display.
    """
    
    def __init__(self):
        """Initialize the MetricsCollector with empty metric storage."""
        self._metrics: Dict[str, Metric] = {}
        self._metric_sources: Dict[str, Callable] = {}
        self._collectors: List[Callable] = []
        self._collection_interval = 60  # seconds
        self._collection_timer: Optional[Timer] = None
        self._lock = Lock()
        self._is_collecting = False
    
    def set_collection_interval(self, seconds: int) -> bool:
        """
        Set the metric collection interval.
        
        Args:
            seconds (int): The collection interval in seconds
            
        Returns:
            bool: True if interval was set successfully, False otherwise
        """
        if seconds > 0:
            self._collection_interval = seconds
            logger.debug(f"Set collection interval to {seconds} seconds")
            return True
        return False
    
    def add_metric_source(self, name: str, source_function: Callable) -> bool:
        """
        Add a metric source function.
        
        Args:
            name (str): The name of the metric source
            source_function (Callable): The function that provides metrics
            
        Returns:
            bool: True if source was added successfully, False otherwise
        """
        self._metric_sources[name] = source_function
        logger.debug(f"Added metric source: {name}")
        return True
    
    def remove_metric_source(self, name: str) -> bool:
        """
        Remove a metric source function.
        
        Args:
            name (str): The name of the metric source to remove
            
        Returns:
            bool: True if source was removed successfully, False otherwise
        """
        if name in self._metric_sources:
            del self._metric_sources[name]
            logger.debug(f"Removed metric source: {name}")
            return True
        return False
    
    def add_collector(self, collector_function: Callable) -> bool:
        """
        Add a collector function that gathers metrics from multiple sources.
        
        Args:
            collector_function (Callable): The function that collects metrics
            
        Returns:
            bool: True if collector was added successfully, False otherwise
        """
        self._collectors.append(collector_function)
        logger.debug("Added metric collector")
        return True
    
    def remove_collector(self, collector_function: Callable) -> bool:
        """
        Remove a collector function.
        
        Args:
            collector_function (Callable): The collector function to remove
            
        Returns:
            bool: True if collector was removed successfully, False otherwise
        """
        if collector_function in self._collectors:
            self._collectors.remove(collector_function)
            logger.debug("Removed metric collector")
            return True
        return False
    
    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect metrics from all sources.
        
        Returns:
            Dict[str, Any]: The collected metrics
        """
        if self._is_collecting:
            logger.warning("Metrics collection is already in progress")
            return {}
        
        self._is_collecting = True
        collected_metrics = {}
        
        try:
            # Collect from individual sources
            for name, source_function in self._metric_sources.items():
                try:
                    metrics = source_function()
                    if isinstance(metrics, dict):
                        collected_metrics[name] = metrics
                except Exception as e:
                    logger.error(f"Error collecting metrics from source {name}: {e}")
            
            # Collect from collector functions
            for collector_function in self._collectors:
                try:
                    metrics = collector_function()
                    if isinstance(metrics, dict):
                        collected_metrics.update(metrics)
                except Exception as e:
                    logger.error(f"Error in collector function: {e}")
            
            # Update stored metrics
            with self._lock:
                for source_name, metrics in collected_metrics.items():
                    for metric_name, metric_value in metrics.items():
                        full_metric_name = f"{source_name}.{metric_name}"
                        metric = Metric(
                            name=full_metric_name,
                            type=MetricType.GAUGE,  # Default type
                            value=metric_value,
                            labels={"source": source_name},
                            timestamp=datetime.now().timestamp()
                        )
                        self._metrics[full_metric_name] = metric
            
            logger.debug(f"Collected metrics from {len(collected_metrics)} sources")
        finally:
            self._is_collecting = False
        
        return collected_metrics
    
    def start_periodic_collection(self) -> bool:
        """
        Start periodic metric collection.
        
        Returns:
            bool: True if collection was started successfully, False otherwise
        """
        if self._collection_timer and self._collection_timer.is_alive():
            logger.warning("Periodic collection is already running")
            return False
        
        def _collect_and_reschedule():
            self.collect_metrics()
            self._collection_timer = Timer(self._collection_interval, _collect_and_reschedule)
            self._collection_timer.start()
        
        self._collection_timer = Timer(self._collection_interval, _collect_and_reschedule)
        self._collection_timer.start()
        logger.debug("Started periodic metric collection")
        return True
    
    def stop_periodic_collection(self) -> bool:
        """
        Stop periodic metric collection.
        
        Returns:
            bool: True if collection was stopped successfully, False otherwise
        """
        if self._collection_timer:
            self._collection_timer.cancel()
            self._collection_timer = None
            logger.debug("Stopped periodic metric collection")
            return True
        return False
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """
        Get a specific metric by name.
        
        Args:
            name (str): The name of the metric to retrieve
            
        Returns:
            Metric: The metric, or None if not found
        """
        return self._metrics.get(name)
    
    def get_metrics(self, prefix: Optional[str] = None) -> Dict[str, Metric]:
        """
        Get metrics, optionally filtered by prefix.
        
        Args:
            prefix (Optional[str]): The prefix to filter metrics by
            
        Returns:
            Dict[str, Metric]: The metrics
        """
        with self._lock:
            if prefix:
                return {name: metric for name, metric in self._metrics.items() if name.startswith(prefix)}
            return self._metrics.copy()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all metrics.
        
        Returns:
            Dict[str, Any]: A summary of metrics
        """
        with self._lock:
            metric_count = len(self._metrics)
            metric_types = {}
            for metric in self._metrics.values():
                metric_type = metric.type.value
                metric_types[metric_type] = metric_types.get(metric_type, 0) + 1
            
            # Get the most recent timestamp
            latest_timestamp = 0
            for metric in self._metrics.values():
                if metric.timestamp > latest_timestamp:
                    latest_timestamp = metric.timestamp
            
            return {
                "total_metrics": metric_count,
                "metric_types": metric_types,
                "last_updated": latest_timestamp,
                "sources_count": len(self._metric_sources),
                "collectors_count": len(self._collectors)
            }
    
    def clear_metrics(self) -> bool:
        """
        Clear all stored metrics.
        
        Returns:
            bool: True if metrics were cleared successfully
        """
        with self._lock:
            self._metrics.clear()
        logger.debug("Cleared all metrics")
        return True
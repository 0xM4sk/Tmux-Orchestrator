"""
Message Router Module

This module provides functionality for routing messages between agents and services.
It implements message distribution patterns and routing logic.
"""

from typing import Dict, List, Any, Optional, Callable
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class MessageRouter:
    """
    Routes messages between agents and services in the system.
    
    This class implements message distribution patterns and handles routing logic
    for different types of messages.
    """
    
    def __init__(self):
        """Initialize the MessageRouter with empty routing tables."""
        self._routes: Dict[str, List[Callable]] = {}
        self._default_routes: List[Callable] = []
        self._lock = Lock()
    
    def add_route(self, message_type: str, handler: Callable) -> bool:
        """
        Add a route for a specific message type.
        
        Args:
            message_type (str): The type of message to route
            handler (Callable): The function to handle messages of this type
            
        Returns:
            bool: True if route was added successfully, False otherwise
        """
        with self._lock:
            if message_type not in self._routes:
                self._routes[message_type] = []
            self._routes[message_type].append(handler)
            logger.debug(f"Added route for message type: {message_type}")
            return True
    
    def remove_route(self, message_type: str, handler: Callable) -> bool:
        """
        Remove a route for a specific message type.
        
        Args:
            message_type (str): The type of message to remove route for
            handler (Callable): The function to remove from the route
            
        Returns:
            bool: True if route was removed successfully, False otherwise
        """
        with self._lock:
            if message_type in self._routes and handler in self._routes[message_type]:
                self._routes[message_type].remove(handler)
                # Clean up empty route lists
                if not self._routes[message_type]:
                    del self._routes[message_type]
                logger.debug(f"Removed route for message type: {message_type}")
                return True
            return False
    
    def add_default_route(self, handler: Callable) -> bool:
        """
        Add a default route that handles all messages without specific routes.
        
        Args:
            handler (Callable): The function to handle messages
            
        Returns:
            bool: True if route was added successfully, False otherwise
        """
        with self._lock:
            self._default_routes.append(handler)
            logger.debug("Added default route")
            return True
    
    def remove_default_route(self, handler: Callable) -> bool:
        """
        Remove a default route.
        
        Args:
            handler (Callable): The function to remove from default routes
            
        Returns:
            bool: True if route was removed successfully, False otherwise
        """
        with self._lock:
            if handler in self._default_routes:
                self._default_routes.remove(handler)
                logger.debug("Removed default route")
                return True
            return False
    
    def route_message(self, message: Dict[str, Any]) -> List[Any]:
        """
        Route a message to appropriate handlers.
        
        Args:
            message (Dict[str, Any]): The message to route
            
        Returns:
            List[Any]: A list of results from all handlers that processed the message
        """
        results = []
        message_type = message.get("type", "default")
        
        # Handle specific routes
        if message_type in self._routes:
            for handler in self._routes[message_type]:
                try:
                    result = handler(message)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error in handler for message type {message_type}: {e}")
                    results.append({"error": str(e)})
        
        # Handle default routes
        for handler in self._default_routes:
            try:
                result = handler(message)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in default handler: {e}")
                results.append({"error": str(e)})
        
        return results
    
    def get_routing_info(self) -> Dict[str, Any]:
        """
        Get information about current routes.
        
        Returns:
            Dict[str, Any]: Information about registered routes
        """
        route_info = {}
        for msg_type, handlers in self._routes.items():
            route_info[msg_type] = len(handlers)
        
        return {
            "specific_routes": route_info,
            "default_routes": len(self._default_routes)
        }
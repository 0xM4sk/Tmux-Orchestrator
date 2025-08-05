"""
Agent Factory Module

This module provides functionality for creating and configuring agents.
It implements the factory pattern for agent instantiation.
"""

from typing import Dict, Any, Optional, Type
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class Agent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        """
        Initialize an agent.
        
        Args:
            agent_id (str): The unique identifier for the agent
            config (Dict[str, Any]): Configuration parameters for the agent
        """
        self.agent_id = agent_id
        self.config = config
    
    @abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task (Dict[str, Any]): The task to execute
            
        Returns:
            Dict[str, Any]: The result of the task execution
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dict[str, Any]: The current status information
        """
        pass


class BaseAgent(Agent):
    """A basic implementation of an agent."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        """Initialize a base agent."""
        super().__init__(agent_id, config)
        self.status = "initialized"
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task (Dict[str, Any]): The task to execute
            
        Returns:
            Dict[str, Any]: The result of the task execution
        """
        self.status = "executing"
        # Simulate task execution
        result = {"status": "completed", "output": f"Executed task: {task}"}
        self.status = "idle"
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dict[str, Any]: The current status information
        """
        return {"agent_id": self.agent_id, "status": self.status}


class AgentFactory:
    """
    Factory class for creating agents.
    
    This class implements the factory pattern for creating different types of agents
    with specific configurations.
    """
    
    def __init__(self):
        """Initialize the AgentFactory with an empty registry."""
        self._agent_types: Dict[str, Type[Agent]] = {}
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register the default agent types."""
        self.register_agent_type("base", BaseAgent)
    
    def register_agent_type(self, type_name: str, agent_class: Type[Agent]) -> bool:
        """
        Register a new agent type.
        
        Args:
            type_name (str): The name to register the agent type under
            agent_class (Type[Agent]): The agent class to register
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            if not issubclass(agent_class, Agent):
                logger.error(f"Agent class {agent_class} is not a subclass of Agent")
                return False
            
            self._agent_types[type_name] = agent_class
            logger.debug(f"Registered agent type: {type_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent type {type_name}: {e}")
            return False
    
    def create_agent(self, agent_id: str, agent_type: str, config: Optional[Dict[str, Any]] = None) -> Optional[Agent]:
        """
        Create a new agent instance.
        
        Args:
            agent_id (str): The unique identifier for the agent
            agent_type (str): The type of agent to create
            config (Optional[Dict[str, Any]]): Configuration parameters for the agent
            
        Returns:
            Agent: A new agent instance, or None if creation failed
        """
        if config is None:
            config = {}
        
        agent_class = self._agent_types.get(agent_type)
        if not agent_class:
            logger.error(f"Unknown agent type: {agent_type}")
            return None
        
        try:
            agent = agent_class(agent_id, config)
            logger.debug(f"Created agent {agent_id} of type {agent_type}")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent {agent_id} of type {agent_type}: {e}")
            return None
    
    def get_available_agent_types(self) -> list:
        """
        Get a list of available agent types.
        
        Returns:
            list: A list of registered agent type names
        """
        return list(self._agent_types.keys())
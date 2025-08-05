"""
Agent Registry Module

This module provides functionality for registering and managing agents in the system.
It maintains a central registry of all active agents.
"""

from typing import Dict, List, Optional, Any
import logging
from threading import Lock

from core.agent_management.agent_factory import Agent
from core.agent_management.agent_state_manager import AgentStateManager, AgentState

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Registry for managing agents in the system.
    
    This class maintains a central registry of all agents, their states, and provides
    methods for agent lifecycle management.
    """
    
    def __init__(self, state_manager: AgentStateManager):
        """
        Initialize the AgentRegistry.
        
        Args:
            state_manager (AgentStateManager): The state manager to use for agent states
        """
        self._agents: Dict[str, Agent] = {}
        self._state_manager = state_manager
        self._lock = Lock()
    
    def register_agent(self, agent: Agent) -> bool:
        """
        Register an agent in the registry.
        
        Args:
            agent (Agent): The agent to register
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        with self._lock:
            if agent.agent_id in self._agents:
                logger.warning(f"Agent {agent.agent_id} is already registered")
                return False
            
            self._agents[agent.agent_id] = agent
            self._state_manager.set_agent_state(agent.agent_id, AgentState.IDLE)
            logger.debug(f"Registered agent {agent.agent_id}")
            return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_id (str): The ID of the agent to unregister
            
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        with self._lock:
            if agent_id not in self._agents:
                logger.warning(f"Agent {agent_id} is not registered")
                return False
            
            del self._agents[agent_id]
            self._state_manager.remove_agent(agent_id)
            logger.debug(f"Unregistered agent {agent_id}")
            return True
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by its ID.
        
        Args:
            agent_id (str): The ID of the agent to retrieve
            
        Returns:
            Agent: The agent with the specified ID, or None if not found
        """
        return self._agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, Agent]:
        """
        Get all registered agents.
        
        Returns:
            Dict[str, Agent]: A dictionary of all registered agents
        """
        return self._agents.copy()
    
    def get_agents_by_state(self, state: AgentState) -> List[str]:
        """
        Get all agents with a specific state.
        
        Args:
            state (AgentState): The state to filter by
            
        Returns:
            List[str]: A list of agent IDs with the specified state
        """
        agent_states = self._state_manager.get_all_agent_states()
        return [agent_id for agent_id, agent_state in agent_states.items() if agent_state == state]
    
    def update_agent_state(self, agent_id: str, state: AgentState) -> bool:
        """
        Update the state of an agent.
        
        Args:
            agent_id (str): The ID of the agent to update
            state (AgentState): The new state for the agent
            
        Returns:
            bool: True if the state was updated successfully, False otherwise
        """
        if agent_id not in self._agents:
            logger.warning(f"Agent {agent_id} is not registered")
            return False
        
        return self._state_manager.set_agent_state(agent_id, state)
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """
        Get the state of an agent.
        
        Args:
            agent_id (str): The ID of the agent
            
        Returns:
            AgentState: The current state of the agent, or None if not found
        """
        return self._state_manager.get_agent_state(agent_id)
    
    def execute_task_on_agent(self, agent_id: str, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute a task on a specific agent.
        
        Args:
            agent_id (str): The ID of the agent to execute the task on
            task (Dict[str, Any]): The task to execute
            
        Returns:
            Dict[str, Any]: The result of the task execution, or None if failed
        """
        agent = self.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return None
        
        try:
            # Update state to busy
            self._state_manager.set_agent_state(agent_id, AgentState.BUSY)
            result = agent.execute_task(task)
            # Update state back to idle
            self._state_manager.set_agent_state(agent_id, AgentState.IDLE)
            return result
        except Exception as e:
            logger.error(f"Failed to execute task on agent {agent_id}: {e}")
            self._state_manager.set_agent_state(agent_id, AgentState.ERROR)
            return None
    
    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get information about the registry.
        
        Returns:
            Dict[str, Any]: Information about the registry including agent counts by state
        """
        agent_states = self._state_manager.get_all_agent_states()
        state_counts = {}
        for state in AgentState:
            state_counts[state.value] = len([s for s in agent_states.values() if s == state])
        
        return {
            "total_agents": len(self._agents),
            "state_counts": state_counts,
            "registered_agents": list(self._agents.keys())
        }
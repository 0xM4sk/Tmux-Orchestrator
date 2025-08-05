"""
Agent State Manager Module

This module provides functionality for managing the state of agents in the system.
It handles state transitions, persistence, and retrieval of agent states.
"""

from typing import Dict, Any, Optional
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Enumeration of possible agent states"""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    TERMINATED = "terminated"


class AgentStateManager:
    """
    Manages the state of agents in the system.
    
    This class provides methods for setting, getting, and transitioning agent states,
    as well as persisting state information.
    """
    
    def __init__(self):
        """Initialize the AgentStateManager with an empty state dictionary."""
        self._agent_states: Dict[str, AgentState] = {}
        self._agent_metadata: Dict[str, Dict[str, Any]] = {}
    
    def set_agent_state(self, agent_id: str, state: AgentState) -> bool:
        """
        Set the state of an agent.
        
        Args:
            agent_id (str): The unique identifier of the agent
            state (AgentState): The new state for the agent
            
        Returns:
            bool: True if state was set successfully, False otherwise
        """
        try:
            logger.debug(f"Setting agent {agent_id} state to {state.value}")
            self._agent_states[agent_id] = state
            return True
        except Exception as e:
            logger.error(f"Failed to set agent {agent_id} state: {e}")
            return False
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """
        Get the current state of an agent.
        
        Args:
            agent_id (str): The unique identifier of the agent
            
        Returns:
            AgentState: The current state of the agent, or None if not found
        """
        return self._agent_states.get(agent_id)
    
    def transition_agent_state(self, agent_id: str, from_state: AgentState, to_state: AgentState) -> bool:
        """
        Transition an agent from one state to another.
        
        Args:
            agent_id (str): The unique identifier of the agent
            from_state (AgentState): The expected current state
            to_state (AgentState): The target state
            
        Returns:
            bool: True if transition was successful, False otherwise
        """
        current_state = self.get_agent_state(agent_id)
        if current_state != from_state:
            logger.warning(f"Agent {agent_id} is in state {current_state}, expected {from_state}")
            return False
        
        return self.set_agent_state(agent_id, to_state)
    
    def get_all_agent_states(self) -> Dict[str, AgentState]:
        """
        Get the states of all agents.
        
        Returns:
            Dict[str, AgentState]: A dictionary mapping agent IDs to their states
        """
        return self._agent_states.copy()
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from state management.
        
        Args:
            agent_id (str): The unique identifier of the agent
            
        Returns:
            bool: True if agent was removed, False if not found
        """
        if agent_id in self._agent_states:
            del self._agent_states[agent_id]
            if agent_id in self._agent_metadata:
                del self._agent_metadata[agent_id]
            logger.debug(f"Removed agent {agent_id} from state management")
            return True
        return False
    
    def set_agent_metadata(self, agent_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Set metadata for an agent.
        
        Args:
            agent_id (str): The unique identifier of the agent
            metadata (Dict[str, Any]): The metadata to store
            
        Returns:
            bool: True if metadata was set successfully
        """
        try:
            if agent_id not in self._agent_metadata:
                self._agent_metadata[agent_id] = {}
            self._agent_metadata[agent_id].update(metadata)
            return True
        except Exception as e:
            logger.error(f"Failed to set metadata for agent {agent_id}: {e}")
            return False
    
    def get_agent_metadata(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for an agent.
        
        Args:
            agent_id (str): The unique identifier of the agent
            
        Returns:
            Dict[str, Any]: The metadata for the agent, or None if not found
        """
        return self._agent_metadata.get(agent_id)
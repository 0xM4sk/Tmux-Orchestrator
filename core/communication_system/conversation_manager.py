"""
Conversation Manager Module

This module provides functionality for managing conversations between agents.
It tracks conversation context, history, and manages conversation state.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Enumeration of possible conversation states"""
    ACTIVE = "active"
    IDLE = "idle"
    ENDED = "ended"
    ERROR = "error"


@dataclass
class Message:
    """Represents a message in a conversation"""
    message_id: str
    sender: str
    recipient: str
    content: Dict[str, Any]
    timestamp: float
    type: str = "text"


@dataclass
class Conversation:
    """Represents a conversation between agents"""
    conversation_id: str
    participants: List[str]
    messages: List[Message]
    state: ConversationState
    created_at: float
    updated_at: float
    context: Dict[str, Any]


class ConversationManager:
    """
    Manages conversations between agents.
    
    This class tracks conversation context, history, and manages conversation state.
    """
    
    def __init__(self):
        """Initialize the ConversationManager with empty conversation storage."""
        self._conversations: Dict[str, Conversation] = {}
        self._participant_conversations: Dict[str, List[str]] = {}
        self._lock = Lock()
    
    def create_conversation(self, conversation_id: str, participants: List[str], 
                          initial_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new conversation.
        
        Args:
            conversation_id (str): The unique identifier for the conversation
            participants (List[str]): The list of participant IDs
            initial_context (Optional[Dict[str, Any]]): Initial context for the conversation
            
        Returns:
            bool: True if conversation was created successfully, False otherwise
        """
        with self._lock:
            if conversation_id in self._conversations:
                logger.warning(f"Conversation {conversation_id} already exists")
                return False
            
            if not participants or len(participants) < 2:
                logger.error("A conversation must have at least 2 participants")
                return False
            
            if initial_context is None:
                initial_context = {}
            
            conversation = Conversation(
                conversation_id=conversation_id,
                participants=participants,
                messages=[],
                state=ConversationState.ACTIVE,
                created_at=datetime.now().timestamp(),
                updated_at=datetime.now().timestamp(),
                context=initial_context
            )
            
            self._conversations[conversation_id] = conversation
            
            # Update participant conversation mapping
            for participant in participants:
                if participant not in self._participant_conversations:
                    self._participant_conversations[participant] = []
                self._participant_conversations[participant].append(conversation_id)
            
            logger.debug(f"Created conversation {conversation_id} with participants {participants}")
            return True
    
    def end_conversation(self, conversation_id: str) -> bool:
        """
        End a conversation.
        
        Args:
            conversation_id (str): The ID of the conversation to end
            
        Returns:
            bool: True if conversation was ended successfully, False otherwise
        """
        with self._lock:
            if conversation_id not in self._conversations:
                logger.warning(f"Conversation {conversation_id} not found")
                return False
            
            conversation = self._conversations[conversation_id]
            conversation.state = ConversationState.ENDED
            conversation.updated_at = datetime.now().timestamp()
            
            logger.debug(f"Ended conversation {conversation_id}")
            return True
    
    def add_message(self, conversation_id: str, message: Message) -> bool:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id (str): The ID of the conversation
            message (Message): The message to add
            
        Returns:
            bool: True if message was added successfully, False otherwise
        """
        with self._lock:
            if conversation_id not in self._conversations:
                logger.warning(f"Conversation {conversation_id} not found")
                return False
            
            conversation = self._conversations[conversation_id]
            if conversation.state != ConversationState.ACTIVE:
                logger.warning(f"Cannot add message to inactive conversation {conversation_id}")
                return False
            
            # Verify sender is a participant
            if message.sender not in conversation.participants:
                logger.error(f"Sender {message.sender} is not a participant in conversation {conversation_id}")
                return False
            
            conversation.messages.append(message)
            conversation.updated_at = datetime.now().timestamp()
            
            logger.debug(f"Added message {message.message_id} to conversation {conversation_id}")
            return True
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by its ID.
        
        Args:
            conversation_id (str): The ID of the conversation to retrieve
            
        Returns:
            Conversation: The conversation with the specified ID, or None if not found
        """
        return self._conversations.get(conversation_id)
    
    def get_conversation_history(self, conversation_id: str, limit: Optional[int] = None) -> List[Message]:
        """
        Get the message history of a conversation.
        
        Args:
            conversation_id (str): The ID of the conversation
            limit (Optional[int]): The maximum number of messages to return
            
        Returns:
            List[Message]: The list of messages in the conversation
        """
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return []
        
        messages = conversation.messages
        if limit:
            messages = messages[-limit:]
        return messages
    
    def get_participant_conversations(self, participant_id: str) -> List[str]:
        """
        Get all conversation IDs for a participant.
        
        Args:
            participant_id (str): The ID of the participant
            
        Returns:
            List[str]: A list of conversation IDs the participant is in
        """
        return self._participant_conversations.get(participant_id, []).copy()
    
    def update_conversation_context(self, conversation_id: str, context_updates: Dict[str, Any]) -> bool:
        """
        Update the context of a conversation.
        
        Args:
            conversation_id (str): The ID of the conversation
            context_updates (Dict[str, Any]): The context updates to apply
            
        Returns:
            bool: True if context was updated successfully, False otherwise
        """
        with self._lock:
            if conversation_id not in self._conversations:
                logger.warning(f"Conversation {conversation_id} not found")
                return False
            
            conversation = self._conversations[conversation_id]
            conversation.context.update(context_updates)
            conversation.updated_at = datetime.now().timestamp()
            
            logger.debug(f"Updated context for conversation {conversation_id}")
            return True
    
    def get_active_conversations(self) -> List[str]:
        """
        Get all active conversation IDs.
        
        Returns:
            List[str]: A list of active conversation IDs
        """
        active_conversations = []
        for conv_id, conversation in self._conversations.items():
            if conversation.state == ConversationState.ACTIVE:
                active_conversations.append(conv_id)
        return active_conversations
    
    def get_conversation_info(self) -> Dict[str, Any]:
        """
        Get information about all conversations.
        
        Returns:
            Dict[str, Any]: Information about conversations including counts by state
        """
        state_counts = {}
        for conversation in self._conversations.values():
            state = conversation.state.value
            state_counts[state] = state_counts.get(state, 0) + 1
        
        return {
            "total_conversations": len(self._conversations),
            "state_counts": state_counts,
            "active_conversations": self.get_active_conversations()
        }
"""
Protocol Enforcer Module

This module provides functionality for enforcing communication protocols between agents.
It validates message formats and ensures compliance with system protocols.
"""

from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ProtocolViolation(Enum):
    """Enumeration of possible protocol violations"""
    INVALID_FORMAT = "invalid_format"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    INVALID_FIELD_TYPE = "invalid_field_type"
    EXPIRED_MESSAGE = "expired_message"
    UNAUTHORIZED_SENDER = "unauthorized_sender"


class ProtocolEnforcer:
    """
    Enforces communication protocols between agents.
    
    This class validates message formats and ensures compliance with system protocols.
    """
    
    def __init__(self):
        """Initialize the ProtocolEnforcer with default protocol rules."""
        self._required_fields = ["type", "sender", "timestamp", "content"]
        self._message_expiry_seconds = 300  # 5 minutes
        self._authorized_senders = set()  # Empty set means all senders are authorized
        self._type_validators = {}
        self._violation_counts = {}
    
    def add_required_field(self, field: str) -> bool:
        """
        Add a required field for all messages.
        
        Args:
            field (str): The field that must be present in all messages
            
        Returns:
            bool: True if field was added successfully, False otherwise
        """
        if field not in self._required_fields:
            self._required_fields.append(field)
            logger.debug(f"Added required field: {field}")
        return True
    
    def remove_required_field(self, field: str) -> bool:
        """
        Remove a required field.
        
        Args:
            field (str): The field to remove from required fields
            
        Returns:
            bool: True if field was removed successfully, False otherwise
        """
        if field in self._required_fields:
            self._required_fields.remove(field)
            logger.debug(f"Removed required field: {field}")
            return True
        return False
    
    def set_message_expiry(self, seconds: int) -> bool:
        """
        Set the message expiry time.
        
        Args:
            seconds (int): The number of seconds after which messages expire
            
        Returns:
            bool: True if expiry time was set successfully, False otherwise
        """
        if seconds > 0:
            self._message_expiry_seconds = seconds
            logger.debug(f"Set message expiry to {seconds} seconds")
            return True
        return False
    
    def add_authorized_sender(self, sender: str) -> bool:
        """
        Add an authorized sender.
        
        Args:
            sender (str): The sender ID to authorize
            
        Returns:
            bool: True if sender was added successfully, False otherwise
        """
        self._authorized_senders.add(sender)
        logger.debug(f"Added authorized sender: {sender}")
        return True
    
    def remove_authorized_sender(self, sender: str) -> bool:
        """
        Remove an authorized sender.
        
        Args:
            sender (str): The sender ID to remove from authorized senders
            
        Returns:
            bool: True if sender was removed successfully, False otherwise
        """
        if sender in self._authorized_senders:
            self._authorized_senders.remove(sender)
            logger.debug(f"Removed authorized sender: {sender}")
            return True
        return False
    
    def set_type_validator(self, message_type: str, validator: callable) -> bool:
        """
        Set a custom validator for a specific message type.
        
        Args:
            message_type (str): The message type to validate
            validator (callable): The function to validate messages of this type
            
        Returns:
            bool: True if validator was set successfully, False otherwise
        """
        self._type_validators[message_type] = validator
        logger.debug(f"Set validator for message type: {message_type}")
        return True
    
    def validate_message(self, message: Dict[str, Any]) -> tuple[bool, Optional[ProtocolViolation], Optional[str]]:
        """
        Validate a message against protocol rules.
        
        Args:
            message (Dict[str, Any]): The message to validate
            
        Returns:
            tuple[bool, Optional[ProtocolViolation], Optional[str]]: A tuple containing:
                - Whether the message is valid
                - The type of violation if invalid
                - A description of the violation if invalid
        """
        # Check required fields
        for field in self._required_fields:
            if field not in message:
                self._record_violation(ProtocolViolation.MISSING_REQUIRED_FIELD)
                return False, ProtocolViolation.MISSING_REQUIRED_FIELD, f"Missing required field: {field}"
        
        # Check field types
        if not isinstance(message["type"], str):
            self._record_violation(ProtocolViolation.INVALID_FIELD_TYPE)
            return False, ProtocolViolation.INVALID_FIELD_TYPE, "Message type must be a string"
        
        if not isinstance(message["sender"], str):
            self._record_violation(ProtocolViolation.INVALID_FIELD_TYPE)
            return False, ProtocolViolation.INVALID_FIELD_TYPE, "Message sender must be a string"
        
        if not isinstance(message["timestamp"], (int, float)):
            self._record_violation(ProtocolViolation.INVALID_FIELD_TYPE)
            return False, ProtocolViolation.INVALID_FIELD_TYPE, "Message timestamp must be a number"
        
        if not isinstance(message["content"], dict):
            self._record_violation(ProtocolViolation.INVALID_FIELD_TYPE)
            return False, ProtocolViolation.INVALID_FIELD_TYPE, "Message content must be a dictionary"
        
        # Check message expiry
        current_time = datetime.now().timestamp()
        if current_time - message["timestamp"] > self._message_expiry_seconds:
            self._record_violation(ProtocolViolation.EXPIRED_MESSAGE)
            return False, ProtocolViolation.EXPIRED_MESSAGE, "Message has expired"
        
        # Check authorized sender
        if self._authorized_senders and message["sender"] not in self._authorized_senders:
            self._record_violation(ProtocolViolation.UNAUTHORIZED_SENDER)
            return False, ProtocolViolation.UNAUTHORIZED_SENDER, "Unauthorized sender"
        
        # Run type-specific validator if available
        message_type = message["type"]
        if message_type in self._type_validators:
            try:
                is_valid, error = self._type_validators[message_type](message)
                if not is_valid:
                    self._record_violation(ProtocolViolation.INVALID_FORMAT)
                    return False, ProtocolViolation.INVALID_FORMAT, error
            except Exception as e:
                logger.error(f"Error in custom validator for type {message_type}: {e}")
                self._record_violation(ProtocolViolation.INVALID_FORMAT)
                return False, ProtocolViolation.INVALID_FORMAT, f"Validator error: {e}"
        
        # Message is valid
        return True, None, None
    
    def _record_violation(self, violation_type: ProtocolViolation):
        """
        Record a protocol violation.
        
        Args:
            violation_type (ProtocolViolation): The type of violation to record
        """
        if violation_type not in self._violation_counts:
            self._violation_counts[violation_type] = 0
        self._violation_counts[violation_type] += 1
    
    def get_violation_stats(self) -> Dict[str, int]:
        """
        Get statistics about protocol violations.
        
        Returns:
            Dict[str, int]: A dictionary mapping violation types to their counts
        """
        return {violation.value: count for violation, count in self._violation_counts.items()}
    
    def reset_violation_stats(self) -> bool:
        """
        Reset violation statistics.
        
        Returns:
            bool: True if stats were reset successfully
        """
        self._violation_counts.clear()
        return True
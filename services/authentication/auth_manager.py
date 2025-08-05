"""
Authentication Manager Module

This module provides functionality for managing authentication processes.
It handles user authentication, session management, and credential validation.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
from threading import Lock
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import secrets
import jwt

logger = logging.getLogger(__name__)


class AuthStatus(Enum):
    """Enumeration of authentication statuses"""
    AUTHENTICATED = "authenticated"
    UNAUTHENTICATED = "unauthenticated"
    EXPIRED = "expired"
    INVALID = "invalid"


@dataclass
class AuthSession:
    """Represents an authentication session"""
    session_id: str
    user_id: str
    created_at: float
    expires_at: float
    last_accessed: float
    metadata: Dict[str, Any]


class AuthManager:
    """
    Manages authentication processes for the system.
    
    This class handles user authentication, session management, and credential validation.
    """
    
    def __init__(self, secret_key: str, session_timeout: int = 3600):
        """
        Initialize the AuthManager.
        
        Args:
            secret_key (str): The secret key for token generation
            session_timeout (int): The session timeout in seconds (default: 1 hour)
        """
        self._secret_key = secret_key
        self._session_timeout = session_timeout
        self._sessions: Dict[str, AuthSession] = {}
        self._user_credentials: Dict[str, Dict[str, str]] = {}  # user_id -> {password_hash, salt}
        self._lock = Lock()
    
    def register_user(self, user_id: str, password: str) -> bool:
        """
        Register a new user with a password.
        
        Args:
            user_id (str): The unique identifier for the user
            password (str): The user's password
            
        Returns:
            bool: True if user was registered successfully, False otherwise
        """
        with self._lock:
            if user_id in self._user_credentials:
                logger.warning(f"User {user_id} already exists")
                return False
            
            # Generate salt and hash password
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(password, salt)
            
            self._user_credentials[user_id] = {
                "password_hash": password_hash,
                "salt": salt
            }
            
            logger.debug(f"Registered user: {user_id}")
            return True
    
    def authenticate_user(self, user_id: str, password: str) -> tuple[bool, Optional[str]]:
        """
        Authenticate a user with their credentials.
        
        Args:
            user_id (str): The user's identifier
            password (str): The user's password
            
        Returns:
            tuple[bool, Optional[str]]: A tuple containing:
                - Whether authentication was successful
                - The session ID if successful, None otherwise
        """
        with self._lock:
            # Check if user exists
            if user_id not in self._user_credentials:
                logger.warning(f"User {user_id} not found")
                return False, None
            
            # Verify password
            credentials = self._user_credentials[user_id]
            password_hash = self._hash_password(password, credentials["salt"])
            
            if password_hash != credentials["password_hash"]:
                logger.warning(f"Invalid password for user {user_id}")
                return False, None
            
            # Create session
            session_id = self._generate_session_id()
            current_time = datetime.now().timestamp()
            expires_at = current_time + self._session_timeout
            
            session = AuthSession(
                session_id=session_id,
                user_id=user_id,
                created_at=current_time,
                expires_at=expires_at,
                last_accessed=current_time,
                metadata={}
            )
            
            self._sessions[session_id] = session
            
            logger.debug(f"Authenticated user {user_id} with session {session_id}")
            return True, session_id
    
    def _hash_password(self, password: str, salt: str) -> str:
        """
        Hash a password with a salt.
        
        Args:
            password (str): The password to hash
            salt (str): The salt to use
            
        Returns:
            str: The hashed password
        """
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _generate_session_id(self) -> str:
        """
        Generate a unique session ID.
        
        Returns:
            str: A unique session ID
        """
        return secrets.token_urlsafe(32)
    
    def validate_session(self, session_id: str) -> AuthStatus:
        """
        Validate an authentication session.
        
        Args:
            session_id (str): The session ID to validate
            
        Returns:
            AuthStatus: The authentication status
        """
        with self._lock:
            if session_id not in self._sessions:
                return AuthStatus.UNAUTHENTICATED
            
            session = self._sessions[session_id]
            current_time = datetime.now().timestamp()
            
            # Check if session has expired
            if current_time > session.expires_at:
                # Remove expired session
                del self._sessions[session_id]
                return AuthStatus.EXPIRED
            
            # Update last accessed time
            session.last_accessed = current_time
            
            return AuthStatus.AUTHENTICATED
    
    def get_session_user(self, session_id: str) -> Optional[str]:
        """
        Get the user ID associated with a session.
        
        Args:
            session_id (str): The session ID
            
        Returns:
            str: The user ID, or None if session is invalid
        """
        with self._lock:
            if session_id not in self._sessions:
                return None
            
            session = self._sessions[session_id]
            current_time = datetime.now().timestamp()
            
            # Check if session has expired
            if current_time > session.expires_at:
                # Remove expired session
                del self._sessions[session_id]
                return None
            
            return session.user_id
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate an authentication session.
        
        Args:
            session_id (str): The session ID to invalidate
            
        Returns:
            bool: True if session was invalidated successfully, False otherwise
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.debug(f"Invalidated session {session_id}")
                return True
            return False
    
    def refresh_session(self, session_id: str) -> bool:
        """
        Refresh an authentication session.
        
        Args:
            session_id (str): The session ID to refresh
            
        Returns:
            bool: True if session was refreshed successfully, False otherwise
        """
        with self._lock:
            if session_id not in self._sessions:
                return False
            
            session = self._sessions[session_id]
            current_time = datetime.now().timestamp()
            
            # Check if session has expired
            if current_time > session.expires_at:
                # Remove expired session
                del self._sessions[session_id]
                return False
            
            # Extend session expiration
            session.expires_at = current_time + self._session_timeout
            session.last_accessed = current_time
            
            logger.debug(f"Refreshed session {session_id}")
            return True
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            user_id (str): The user's identifier
            old_password (str): The user's current password
            new_password (str): The user's new password
            
        Returns:
            bool: True if password was changed successfully, False otherwise
        """
        with self._lock:
            # Check if user exists
            if user_id not in self._user_credentials:
                logger.warning(f"User {user_id} not found")
                return False
            
            # Verify old password
            credentials = self._user_credentials[user_id]
            old_password_hash = self._hash_password(old_password, credentials["salt"])
            
            if old_password_hash != credentials["password_hash"]:
                logger.warning(f"Invalid old password for user {user_id}")
                return False
            
            # Generate new salt and hash new password
            new_salt = secrets.token_hex(16)
            new_password_hash = self._hash_password(new_password, new_salt)
            
            self._user_credentials[user_id] = {
                "password_hash": new_password_hash,
                "salt": new_salt
            }
            
            # Invalidate all sessions for this user
            sessions_to_remove = [
                session_id for session_id, session in self._sessions.items()
                if session.user_id == user_id
            ]
            for session_id in sessions_to_remove:
                del self._sessions[session_id]
            
            logger.debug(f"Changed password for user {user_id}")
            return True
    
    def get_auth_info(self) -> Dict[str, Any]:
        """
        Get information about the authentication system.
        
        Returns:
            Dict[str, Any]: Information about the authentication system
        """
        with self._lock:
            total_sessions = len(self._sessions)
            active_sessions = 0
            expired_sessions = 0
            
            current_time = datetime.now().timestamp()
            for session in self._sessions.values():
                if current_time <= session.expires_at:
                    active_sessions += 1
                else:
                    expired_sessions += 1
            
            return {
                "total_users": len(self._user_credentials),
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "expired_sessions": expired_sessions,
                "session_timeout": self._session_timeout
            }
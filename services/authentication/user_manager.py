"""
User Manager Module

This module provides functionality for managing user accounts and profiles.
It handles user registration, profile management, and user data storage.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from threading import Lock
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """Enumeration of user roles"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    SERVICE = "service"


class UserStatus(Enum):
    """Enumeration of user statuses"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


@dataclass
class User:
    """Represents a user account"""
    user_id: str
    username: str
    email: str
    role: UserRole
    status: UserStatus
    created_at: float
    updated_at: float
    last_login: Optional[float]
    profile: Dict[str, Any]


class UserManager:
    """
    Manages user accounts and profiles.
    
    This class handles user registration, profile management, and user data storage.
    """
    
    def __init__(self):
        """Initialize the UserManager with empty user storage."""
        self._users: Dict[str, User] = {}
        self._username_index: Dict[str, str] = {}  # username -> user_id
        self._email_index: Dict[str, str] = {}     # email -> user_id
        self._lock = Lock()
    
    def create_user(self, user_id: str, username: str, email: str, 
                   role: UserRole = UserRole.USER, 
                   profile: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new user account.
        
        Args:
            user_id (str): The unique identifier for the user
            username (str): The user's username
            email (str): The user's email address
            role (UserRole): The user's role (default: USER)
            profile (Optional[Dict[str, Any]]): The user's profile data
            
        Returns:
            bool: True if user was created successfully, False otherwise
        """
        with self._lock:
            # Check if user already exists
            if user_id in self._users:
                logger.warning(f"User {user_id} already exists")
                return False
            
            # Check if username is already taken
            if username in self._username_index:
                logger.warning(f"Username {username} is already taken")
                return False
            
            # Check if email is already used
            if email in self._email_index:
                logger.warning(f"Email {email} is already used")
                return False
            
            if profile is None:
                profile = {}
            
            current_time = datetime.now().timestamp()
            
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                role=role,
                status=UserStatus.ACTIVE,
                created_at=current_time,
                updated_at=current_time,
                last_login=None,
                profile=profile
            )
            
            self._users[user_id] = user
            self._username_index[username] = user_id
            self._email_index[email] = user_id
            
            logger.debug(f"Created user {user_id} with username {username}")
            return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            user_id (str): The user's ID
            
        Returns:
            User: The user account, or None if not found
        """
        return self._users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by their username.
        
        Args:
            username (str): The user's username
            
        Returns:
            User: The user account, or None if not found
        """
        user_id = self._username_index.get(username)
        if user_id:
            return self._users.get(user_id)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email.
        
        Args:
            email (str): The user's email
            
        Returns:
            User: The user account, or None if not found
        """
        user_id = self._email_index.get(email)
        if user_id:
            return self._users.get(user_id)
        return None
    
    def update_user_profile(self, user_id: str, profile_updates: Dict[str, Any]) -> bool:
        """
        Update a user's profile.
        
        Args:
            user_id (str): The user's ID
            profile_updates (Dict[str, Any]): The profile updates to apply
            
        Returns:
            bool: True if profile was updated successfully, False otherwise
        """
        with self._lock:
            if user_id not in self._users:
                logger.warning(f"User {user_id} not found")
                return False
            
            user = self._users[user_id]
            user.profile.update(profile_updates)
            user.updated_at = datetime.now().timestamp()
            
            logger.debug(f"Updated profile for user {user_id}")
            return True
    
    def update_user_role(self, user_id: str, role: UserRole) -> bool:
        """
        Update a user's role.
        
        Args:
            user_id (str): The user's ID
            role (UserRole): The new role
            
        Returns:
            bool: True if role was updated successfully, False otherwise
        """
        with self._lock:
            if user_id not in self._users:
                logger.warning(f"User {user_id} not found")
                return False
            
            user = self._users[user_id]
            user.role = role
            user.updated_at = datetime.now().timestamp()
            
            logger.debug(f"Updated role for user {user_id} to {role.value}")
            return True
    
    def update_user_status(self, user_id: str, status: UserStatus) -> bool:
        """
        Update a user's status.
        
        Args:
            user_id (str): The user's ID
            status (UserStatus): The new status
            
        Returns:
            bool: True if status was updated successfully, False otherwise
        """
        with self._lock:
            if user_id not in self._users:
                logger.warning(f"User {user_id} not found")
                return False
            
            user = self._users[user_id]
            user.status = status
            user.updated_at = datetime.now().timestamp()
            
            logger.debug(f"Updated status for user {user_id} to {status.value}")
            return True
    
    def record_user_login(self, user_id: str) -> bool:
        """
        Record a user login.
        
        Args:
            user_id (str): The user's ID
            
        Returns:
            bool: True if login was recorded successfully, False otherwise
        """
        with self._lock:
            if user_id not in self._users:
                logger.warning(f"User {user_id} not found")
                return False
            
            user = self._users[user_id]
            user.last_login = datetime.now().timestamp()
            user.updated_at = user.last_login
            
            logger.debug(f"Recorded login for user {user_id}")
            return True
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user account.
        
        Args:
            user_id (str): The user's ID
            
        Returns:
            bool: True if user was deleted successfully, False otherwise
        """
        with self._lock:
            if user_id not in self._users:
                logger.warning(f"User {user_id} not found")
                return False
            
            user = self._users[user_id]
            username = user.username
            email = user.email
            
            # Update indices
            if username in self._username_index:
                del self._username_index[username]
            if email in self._email_index:
                del self._email_index[email]
            
            # Mark user as deleted instead of removing completely
            user.status = UserStatus.DELETED
            user.updated_at = datetime.now().timestamp()
            
            logger.debug(f"Deleted user {user_id}")
            return True
    
    def list_users(self, status: Optional[UserStatus] = None, role: Optional[UserRole] = None) -> List[User]:
        """
        List users, optionally filtered by status and role.
        
        Args:
            status (Optional[UserStatus]): The status to filter by
            role (Optional[UserRole]): The role to filter by
            
        Returns:
            List[User]: The list of users
        """
        with self._lock:
            users = list(self._users.values())
            
            if status:
                users = [u for u in users if u.status == status]
            
            if role:
                users = [u for u in users if u.role == role]
            
            return users
    
    def search_users(self, query: str) -> List[User]:
        """
        Search users by username or email.
        
        Args:
            query (str): The search query
            
        Returns:
            List[User]: The list of matching users
        """
        with self._lock:
            results = []
            query = query.lower()
            
            for user in self._users.values():
                if (query in user.username.lower() or 
                    query in user.email.lower() or
                    query in user.user_id.lower()):
                    results.append(user)
            
            return results
    
    def get_user_count(self) -> Dict[str, int]:
        """
        Get user counts by status and role.
        
        Returns:
            Dict[str, int]: User counts
        """
        with self._lock:
            status_counts = {}
            role_counts = {}
            
            for user in self._users.values():
                # Count by status
                status = user.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count by role
                role = user.role.value
                role_counts[role] = role_counts.get(role, 0) + 1
            
            return {
                "total_users": len(self._users),
                "status_counts": status_counts,
                "role_counts": role_counts
            }
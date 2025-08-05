"""
Token Manager Module

This module provides functionality for managing authentication tokens.
It handles token generation, validation, and refresh operations.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from threading import Lock
from dataclasses import dataclass, asdict
import jwt
import secrets

logger = logging.getLogger(__name__)


@dataclass
class Token:
    """Represents an authentication token"""
    token_id: str
    user_id: str
    token_type: str
    created_at: float
    expires_at: float
    scopes: list
    metadata: Dict[str, Any]


class TokenManager:
    """
    Manages authentication tokens for the system.
    
    This class handles token generation, validation, and refresh operations.
    """
    
    def __init__(self, secret_key: str, default_token_lifetime: int = 3600):
        """
        Initialize the TokenManager.
        
        Args:
            secret_key (str): The secret key for token signing
            default_token_lifetime (int): The default token lifetime in seconds (default: 1 hour)
        """
        self._secret_key = secret_key
        self._default_token_lifetime = default_token_lifetime
        self._tokens: Dict[str, Token] = {}
        self._user_tokens: Dict[str, list] = {}  # user_id -> list of token_ids
        self._lock = Lock()
    
    def generate_token(self, user_id: str, token_type: str = "access", 
                      lifetime: Optional[int] = None, scopes: Optional[list] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Generate a new authentication token.
        
        Args:
            user_id (str): The user ID to associate with the token
            token_type (str): The type of token (default: "access")
            lifetime (Optional[int]): The token lifetime in seconds (default: default_token_lifetime)
            scopes (Optional[list]): The scopes associated with the token
            metadata (Optional[Dict[str, Any]]): Additional metadata
            
        Returns:
            Optional[str]: The generated token, or None if generation failed
        """
        with self._lock:
            if lifetime is None:
                lifetime = self._default_token_lifetime
            
            if scopes is None:
                scopes = []
            
            if metadata is None:
                metadata = {}
            
            # Generate token ID
            token_id = self._generate_token_id()
            
            # Create timestamps
            current_time = datetime.now().timestamp()
            expires_at = current_time + lifetime
            
            # Create token object
            token_obj = Token(
                token_id=token_id,
                user_id=user_id,
                token_type=token_type,
                created_at=current_time,
                expires_at=expires_at,
                scopes=scopes,
                metadata=metadata
            )
            
            # Store token
            self._tokens[token_id] = token_obj
            
            # Update user tokens index
            if user_id not in self._user_tokens:
                self._user_tokens[user_id] = []
            self._user_tokens[user_id].append(token_id)
            
            # Generate JWT token
            payload = {
                "token_id": token_id,
                "user_id": user_id,
                "token_type": token_type,
                "scopes": scopes,
                "exp": expires_at,
                "iat": current_time
            }
            
            try:
                jwt_token = jwt.encode(payload, self._secret_key, algorithm="HS256")
                logger.debug(f"Generated {token_type} token for user {user_id}")
                return jwt_token
            except Exception as e:
                logger.error(f"Error generating JWT token: {e}")
                # Clean up the stored token object since JWT generation failed
                del self._tokens[token_id]
                self._user_tokens[user_id].remove(token_id)
                if not self._user_tokens[user_id]:
                    del self._user_tokens[user_id]
                return None
    
    def _generate_token_id(self) -> str:
        """
        Generate a unique token ID.
        
        Returns:
            str: A unique token ID
        """
        return secrets.token_urlsafe(32)
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate an authentication token.
        
        Args:
            token (str): The token to validate
            
        Returns:
            Optional[Dict[str, Any]]: The token payload if valid, None otherwise
        """
        try:
            # Decode JWT token
            payload = jwt.decode(token, self._secret_key, algorithms=["HS256"])
            
            token_id = payload.get("token_id")
            user_id = payload.get("user_id")
            exp = payload.get("exp")
            
            # Check if token exists in our storage
            with self._lock:
                if token_id not in self._tokens:
                    logger.warning(f"Token {token_id} not found in storage")
                    return None
                
                token_obj = self._tokens[token_id]
                
                # Check if token is expired
                current_time = datetime.now().timestamp()
                if current_time > token_obj.expires_at:
                    logger.warning(f"Token {token_id} has expired")
                    self._remove_token(token_id, user_id)
                    return None
                
                # Check if user ID matches
                if token_obj.user_id != user_id:
                    logger.warning(f"User ID mismatch for token {token_id}")
                    return None
                
                # Check if expiration in payload matches our storage
                if exp != token_obj.expires_at:
                    logger.warning(f"Expiration mismatch for token {token_id}")
                    return None
            
            logger.debug(f"Validated token {token_id} for user {user_id}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired signature")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token (str): The refresh token
            
        Returns:
            Optional[str]: The new access token, or None if refresh failed
        """
        # Validate refresh token
        payload = self.validate_token(refresh_token)
        if not payload:
            return None
        
        # Check if it's actually a refresh token
        if payload.get("token_type") != "refresh":
            logger.warning("Token is not a refresh token")
            return None
        
        user_id = payload.get("user_id")
        scopes = payload.get("scopes", [])
        
        # Generate new access token
        return self.generate_token(
            user_id=user_id,
            token_type="access",
            scopes=scopes
        )
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke an authentication token.
        
        Args:
            token (str): The token to revoke
            
        Returns:
            bool: True if token was revoked successfully, False otherwise
        """
        try:
            # Decode token to get token_id
            payload = jwt.decode(token, self._secret_key, algorithms=["HS256"])
            token_id = payload.get("token_id")
            user_id = payload.get("user_id")
            
            with self._lock:
                return self._remove_token(token_id, user_id)
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False
    
    def revoke_user_tokens(self, user_id: str) -> int:
        """
        Revoke all tokens for a specific user.
        
        Args:
            user_id (str): The user ID
            
        Returns:
            int: The number of tokens revoked
        """
        with self._lock:
            if user_id not in self._user_tokens:
                return 0
            
            token_ids = self._user_tokens[user_id].copy()
            revoked_count = 0
            
            for token_id in token_ids:
                if self._remove_token(token_id, user_id):
                    revoked_count += 1
            
            return revoked_count
    
    def _remove_token(self, token_id: str, user_id: str) -> bool:
        """
        Remove a token from storage.
        
        Args:
            token_id (str): The token ID
            user_id (str): The user ID
            
        Returns:
            bool: True if token was removed successfully, False otherwise
        """
        if token_id in self._tokens:
            del self._tokens[token_id]
            
            # Update user tokens index
            if user_id in self._user_tokens and token_id in self._user_tokens[user_id]:
                self._user_tokens[user_id].remove(token_id)
                if not self._user_tokens[user_id]:
                    del self._user_tokens[user_id]
            
            logger.debug(f"Removed token {token_id} for user {user_id}")
            return True
        
        return False
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a token.
        
        Args:
            token (str): The token to get information for
            
        Returns:
            Optional[Dict[str, Any]]: Information about the token, or None if invalid
        """
        payload = self.validate_token(token)
        if not payload:
            return None
        
        token_id = payload.get("token_id")
        
        with self._lock:
            if token_id in self._tokens:
                token_obj = self._tokens[token_id]
                return {
                    "token_id": token_obj.token_id,
                    "user_id": token_obj.user_id,
                    "token_type": token_obj.token_type,
                    "created_at": token_obj.created_at,
                    "expires_at": token_obj.expires_at,
                    "scopes": token_obj.scopes,
                    "is_valid": True
                }
        
        return None
    
    def get_user_token_count(self, user_id: str) -> int:
        """
        Get the number of active tokens for a user.
        
        Args:
            user_id (str): The user ID
            
        Returns:
            int: The number of active tokens
        """
        with self._lock:
            if user_id not in self._user_tokens:
                return 0
            
            # Count only non-expired tokens
            current_time = datetime.now().timestamp()
            active_count = 0
            
            for token_id in self._user_tokens[user_id]:
                if token_id in self._tokens:
                    token_obj = self._tokens[token_id]
                    if current_time <= token_obj.expires_at:
                        active_count += 1
            
            return active_count
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens from storage.
        
        Returns:
            int: The number of expired tokens removed
        """
        with self._lock:
            current_time = datetime.now().timestamp()
            expired_tokens = []
            
            # Find expired tokens
            for token_id, token_obj in self._tokens.items():
                if current_time > token_obj.expires_at:
                    expired_tokens.append((token_id, token_obj.user_id))
            
            # Remove expired tokens
            for token_id, user_id in expired_tokens:
                self._remove_token(token_id, user_id)
            
            logger.debug(f"Cleaned up {len(expired_tokens)} expired tokens")
            return len(expired_tokens)
    
    def get_token_stats(self) -> Dict[str, Any]:
        """
        Get statistics about tokens.
        
        Returns:
            Dict[str, Any]: Token statistics
        """
        with self._lock:
            total_tokens = len(self._tokens)
            
            # Count by type
            type_counts = {}
            current_time = datetime.now().timestamp()
            active_tokens = 0
            expired_tokens = 0
            
            for token_obj in self._tokens.values():
                token_type = token_obj.token_type
                type_counts[token_type] = type_counts.get(token_type, 0) + 1
                
                if current_time <= token_obj.expires_at:
                    active_tokens += 1
                else:
                    expired_tokens += 1
            
            # Count users with tokens
            users_with_tokens = len(self._user_tokens)
            
            return {
                "total_tokens": total_tokens,
                "active_tokens": active_tokens,
                "expired_tokens": expired_tokens,
                "type_counts": type_counts,
                "users_with_tokens": users_with_tokens
            }
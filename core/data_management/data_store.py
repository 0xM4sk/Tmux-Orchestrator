"""
Data Store Module

This module provides functionality for storing and retrieving system data.
It handles data persistence, caching, and retrieval operations.
"""

from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
from threading import Lock
from dataclasses import dataclass, asdict
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class DataRecord:
    """Represents a data record in the store"""
    key: str
    data: Any
    created_at: float
    updated_at: float
    expires_at: Optional[float]
    tags: List[str]


class DataStore:
    """
    Manages data storage and retrieval for the system.
    
    This class handles data persistence, caching, and retrieval operations.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the DataStore.
        
        Args:
            storage_path (Optional[str]): The path to the storage file, if using file-based storage
        """
        self._data: Dict[str, DataRecord] = {}
        self._tags_index: Dict[str, List[str]] = {}  # tag -> list of keys
        self._storage_path = storage_path
        self._lock = Lock()
        
        # Load data from storage if path is provided
        if self._storage_path:
            self._load_from_storage()
    
    def _load_from_storage(self) -> bool:
        """
        Load data from persistent storage.
        
        Returns:
            bool: True if data was loaded successfully, False otherwise
        """
        if not self._storage_path or not os.path.exists(self._storage_path):
            return False
        
        try:
            with open(self._storage_path, 'r') as f:
                data = json.load(f)
            
            # Convert loaded data to DataRecord objects
            for key, record_data in data.items():
                record = DataRecord(
                    key=key,
                    data=record_data.get("data"),
                    created_at=record_data.get("created_at", 0),
                    updated_at=record_data.get("updated_at", 0),
                    expires_at=record_data.get("expires_at"),
                    tags=record_data.get("tags", [])
                )
                self._data[key] = record
                
                # Update tags index
                for tag in record.tags:
                    if tag not in self._tags_index:
                        self._tags_index[tag] = []
                    if key not in self._tags_index[tag]:
                        self._tags_index[tag].append(key)
            
            logger.debug(f"Loaded {len(self._data)} records from storage")
            return True
        except Exception as e:
            logger.error(f"Error loading data from storage: {e}")
            return False
    
    def _save_to_storage(self) -> bool:
        """
        Save data to persistent storage.
        
        Returns:
            bool: True if data was saved successfully, False otherwise
        """
        if not self._storage_path:
            return False
        
        try:
            # Convert DataRecord objects to dictionaries for JSON serialization
            data_to_save = {}
            for key, record in self._data.items():
                data_to_save[key] = {
                    "data": record.data,
                    "created_at": record.created_at,
                    "updated_at": record.updated_at,
                    "expires_at": record.expires_at,
                    "tags": record.tags
                }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
            
            with open(self._storage_path, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            
            logger.debug(f"Saved {len(data_to_save)} records to storage")
            return True
        except Exception as e:
            logger.error(f"Error saving data to storage: {e}")
            return False
    
    def store(self, key: str, data: Any, expires_in: Optional[int] = None, 
              tags: Optional[List[str]] = None) -> bool:
        """
        Store data in the data store.
        
        Args:
            key (str): The key to store the data under
            data (Any): The data to store
            expires_in (Optional[int]): The number of seconds until the data expires
            tags (Optional[List[str]]): Tags to associate with the data
            
        Returns:
            bool: True if data was stored successfully, False otherwise
        """
        with self._lock:
            current_time = datetime.now().timestamp()
            expires_at = current_time + expires_in if expires_in else None
            
            if tags is None:
                tags = []
            
            # Remove key from old tags
            if key in self._data:
                old_record = self._data[key]
                for tag in old_record.tags:
                    if tag in self._tags_index and key in self._tags_index[tag]:
                        self._tags_index[tag].remove(key)
            
            # Create new record
            record = DataRecord(
                key=key,
                data=data,
                created_at=current_time if key not in self._data else self._data[key].created_at,
                updated_at=current_time,
                expires_at=expires_at,
                tags=tags
            )
            
            self._data[key] = record
            
            # Update tags index
            for tag in tags:
                if tag not in self._tags_index:
                    self._tags_index[tag] = []
                if key not in self._tags_index[tag]:
                    self._tags_index[tag].append(key)
            
            logger.debug(f"Stored data with key: {key}")
            
            # Save to storage if path is provided
            if self._storage_path:
                self._save_to_storage()
            
            return True
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data from the data store.
        
        Args:
            key (str): The key of the data to retrieve
            
        Returns:
            Any: The retrieved data, or None if not found or expired
        """
        with self._lock:
            if key not in self._data:
                return None
            
            record = self._data[key]
            
            # Check if data has expired
            current_time = datetime.now().timestamp()
            if record.expires_at and current_time > record.expires_at:
                self._delete_record(key, record)
                return None
            
            return record.data
    
    def delete(self, key: str) -> bool:
        """
        Delete data from the data store.
        
        Args:
            key (str): The key of the data to delete
            
        Returns:
            bool: True if data was deleted successfully, False otherwise
        """
        with self._lock:
            if key not in self._data:
                return False
            
            record = self._data[key]
            self._delete_record(key, record)
            
            logger.debug(f"Deleted data with key: {key}")
            
            # Save to storage if path is provided
            if self._storage_path:
                self._save_to_storage()
            
            return True
    
    def _delete_record(self, key: str, record: DataRecord):
        """
        Delete a record and update indices.
        
        Args:
            key (str): The key of the record to delete
            record (DataRecord): The record to delete
        """
        # Remove from tags index
        for tag in record.tags:
            if tag in self._tags_index and key in self._tags_index[tag]:
                self._tags_index[tag].remove(key)
                # Clean up empty tag entries
                if not self._tags_index[tag]:
                    del self._tags_index[tag]
        
        # Remove from data store
        del self._data[key]
    
    def get_keys_by_tag(self, tag: str) -> List[str]:
        """
        Get all keys associated with a specific tag.
        
        Args:
            tag (str): The tag to search for
            
        Returns:
            List[str]: A list of keys associated with the tag
        """
        with self._lock:
            return self._tags_index.get(tag, []).copy()
    
    def get_data_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Get all data associated with a specific tag.
        
        Args:
            tag (str): The tag to search for
            
        Returns:
            Dict[str, Any]: A dictionary of key-value pairs for the tagged data
        """
        with self._lock:
            keys = self._tags_index.get(tag, [])
            result = {}
            for key in keys:
                data = self.retrieve(key)
                if data is not None:
                    result[key] = data
            return result
    
    def update(self, key: str, data: Any) -> bool:
        """
        Update existing data in the data store.
        
        Args:
            key (str): The key of the data to update
            data (Any): The new data
            
        Returns:
            bool: True if data was updated successfully, False otherwise
        """
        with self._lock:
            if key not in self._data:
                return False
            
            record = self._data[key]
            record.data = data
            record.updated_at = datetime.now().timestamp()
            
            logger.debug(f"Updated data with key: {key}")
            
            # Save to storage if path is provided
            if self._storage_path:
                self._save_to_storage()
            
            return True
    
    def exists(self, key: str) -> bool:
        """
        Check if data exists in the data store.
        
        Args:
            key (str): The key to check
            
        Returns:
            bool: True if data exists, False otherwise
        """
        with self._lock:
            if key not in self._data:
                return False
            
            record = self._data[key]
            
            # Check if data has expired
            current_time = datetime.now().timestamp()
            if record.expires_at and current_time > record.expires_at:
                self._delete_record(key, record)
                return False
            
            return True
    
    def list_keys(self) -> List[str]:
        """
        List all keys in the data store.
        
        Returns:
            List[str]: A list of all keys
        """
        with self._lock:
            # Clean up expired records first
            current_time = datetime.now().timestamp()
            expired_keys = []
            for key, record in self._data.items():
                if record.expires_at and current_time > record.expires_at:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._delete_record(key, self._data[key])
            
            return list(self._data.keys())
    
    def clear_expired(self) -> int:
        """
        Clear all expired data from the store.
        
        Returns:
            int: The number of expired records cleared
        """
        with self._lock:
            current_time = datetime.now().timestamp()
            expired_keys = []
            for key, record in self._data.items():
                if record.expires_at and current_time > record.expires_at:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._delete_record(key, self._data[key])
            
            if expired_keys and self._storage_path:
                self._save_to_storage()
            
            logger.debug(f"Cleared {len(expired_keys)} expired records")
            return len(expired_keys)
    
    def get_store_info(self) -> Dict[str, Any]:
        """
        Get information about the data store.
        
        Returns:
            Dict[str, Any]: Information about the data store
        """
        with self._lock:
            total_records = len(self._data)
            tag_count = len(self._tags_index)
            
            # Count records by tag
            records_by_tag = {}
            for tag, keys in self._tags_index.items():
                records_by_tag[tag] = len(keys)
            
            return {
                "total_records": total_records,
                "tag_count": tag_count,
                "records_by_tag": records_by_tag,
                "storage_path": self._storage_path
            }
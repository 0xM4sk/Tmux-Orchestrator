#!/usr/bin/env python3
"""
Qwen 3 Coder API Client for Tmux Orchestrator
Handles communication with local Ollama server running Qwen 3 Coder model
"""

import json
import requests
import time
import asyncio
import aiohttp
from typing import List, Dict, Optional, AsyncGenerator, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Represents a single message in a conversation"""
    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: datetime
    tokens: Optional[int] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Create Message from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

@dataclass
class QwenConfig:
    """Configuration for Qwen API client"""
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:7b"
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'QwenConfig':
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return cls()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return cls()

class QwenAPIError(Exception):
    """Custom exception for Qwen API errors"""
    pass

class QwenClient:
    """
    Client for communicating with Qwen 3 Coder via Ollama API
    Provides both synchronous and asynchronous interfaces
    """
    
    def __init__(self, config: Optional[QwenConfig] = None):
        self.config = config or QwenConfig()
        self.session = requests.Session()
        self.session.timeout = self.config.timeout
        
        # Verify Ollama is running and model is available
        self._verify_connection()
    
    def _verify_connection(self) -> None:
        """Verify Ollama server is running and model is available"""
        try:
            # Check if Ollama is running
            response = self.session.get(f"{self.config.base_url}/api/tags")
            response.raise_for_status()
            
            # Check if our model is available
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            if self.config.model not in model_names:
                logger.warning(f"Model {self.config.model} not found. Available models: {model_names}")
                logger.info(f"To install the model, run: ollama pull {self.config.model}")
            else:
                logger.info(f"Connected to Ollama. Model {self.config.model} is available.")
                
        except requests.exceptions.ConnectionError:
            raise QwenAPIError(
                f"Cannot connect to Ollama server at {self.config.base_url}. "
                "Please ensure Ollama is running."
            )
        except Exception as e:
            logger.error(f"Error verifying connection: {e}")
    
    def _make_request(self, endpoint: str, data: Dict, stream: bool = False) -> Union[Dict, requests.Response]:
        """Make HTTP request with retry logic"""
        url = f"{self.config.base_url}{endpoint}"
        
        for attempt in range(self.config.max_retries):
            try:
                if stream:
                    response = self.session.post(url, json=data, stream=True)
                else:
                    response = self.session.post(url, json=data)
                
                response.raise_for_status()
                
                if stream:
                    return response
                else:
                    return response.json()
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise QwenAPIError(f"Request failed after {self.config.max_retries} attempts: {e}")
                
                logger.warning(f"Request attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
    
    def chat_completion(self, messages: List[Message], stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        """
        Send chat completion request to Qwen
        
        Args:
            messages: List of conversation messages
            stream: Whether to stream the response
            
        Returns:
            Complete response string or async generator for streaming
        """
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        request_data = {
            "model": self.config.model,
            "messages": ollama_messages,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            },
            "stream": stream
        }
        
        if stream:
            return self._stream_response(request_data)
        else:
            response = self._make_request("/api/chat", request_data)
            return response.get("message", {}).get("content", "")
    
    def _stream_response(self, request_data: Dict) -> AsyncGenerator[str, None]:
        """Handle streaming response from Ollama"""
        response = self._make_request("/api/chat", request_data, stream=True)
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    if 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        if content:
                            yield content
                    
                    # Check if this is the final chunk
                    if chunk.get('done', False):
                        break
                        
                except json.JSONDecodeError:
                    continue
    
    def generate_completion(self, prompt: str, stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate completion for a single prompt (non-chat mode)
        
        Args:
            prompt: Input prompt
            stream: Whether to stream the response
            
        Returns:
            Complete response string or async generator for streaming
        """
        request_data = {
            "model": self.config.model,
            "prompt": prompt,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            },
            "stream": stream
        }
        
        if stream:
            return self._stream_generate_response(request_data)
        else:
            response = self._make_request("/api/generate", request_data)
            return response.get("response", "")
    
    def _stream_generate_response(self, request_data: Dict) -> AsyncGenerator[str, None]:
        """Handle streaming response for generate endpoint"""
        response = self._make_request("/api/generate", request_data, stream=True)
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    if 'response' in chunk:
                        content = chunk['response']
                        if content:
                            yield content
                    
                    # Check if this is the final chunk
                    if chunk.get('done', False):
                        break
                        
                except json.JSONDecodeError:
                    continue
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        try:
            response = self.session.get(f"{self.config.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get('models', [])
            return [model['name'] for model in models]
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []
    
    def health_check(self) -> Dict[str, Union[bool, str, List[str]]]:
        """Perform health check on Ollama server and model"""
        health_status = {
            "server_running": False,
            "model_available": False,
            "model_name": self.config.model,
            "available_models": [],
            "error": None
        }
        
        try:
            # Check server
            response = self.session.get(f"{self.config.base_url}/api/tags")
            response.raise_for_status()
            health_status["server_running"] = True
            
            # Check models
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            health_status["available_models"] = model_names
            health_status["model_available"] = self.config.model in model_names
            
        except requests.exceptions.ConnectionError:
            health_status["error"] = f"Cannot connect to Ollama server at {self.config.base_url}"
        except Exception as e:
            health_status["error"] = str(e)
        
        return health_status
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of token count for text
        Uses approximation of ~4 characters per token for English text
        """
        return len(text) // 4
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()

# Async version of the client
class AsyncQwenClient:
    """Async version of QwenClient for concurrent operations"""
    
    def __init__(self, config: Optional[QwenConfig] = None):
        self.config = config or QwenConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def chat_completion(self, messages: List[Message]) -> str:
        """Async chat completion"""
        if not self.session:
            raise QwenAPIError("Client not initialized. Use 'async with AsyncQwenClient()' pattern.")
        
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        request_data = {
            "model": self.config.model,
            "messages": ollama_messages,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        url = f"{self.config.base_url}/api/chat"
        
        async with self.session.post(url, json=request_data) as response:
            response.raise_for_status()
            result = await response.json()
            return result.get("message", {}).get("content", "")

# Utility functions
def create_system_message(content: str) -> Message:
    """Create a system message"""
    return Message(role="system", content=content, timestamp=datetime.now())

def create_user_message(content: str) -> Message:
    """Create a user message"""
    return Message(role="user", content=content, timestamp=datetime.now())

def create_assistant_message(content: str, tokens: Optional[int] = None) -> Message:
    """Create an assistant message"""
    return Message(role="assistant", content=content, timestamp=datetime.now(), tokens=tokens)

# Example usage and testing
if __name__ == "__main__":
    # Test the client
    config = QwenConfig()
    client = QwenClient(config)
    
    # Health check
    health = client.health_check()
    print("Health Check:", json.dumps(health, indent=2))
    
    if health["server_running"] and health["model_available"]:
        # Test chat completion
        messages = [
            create_system_message("You are a helpful AI assistant specialized in software development."),
            create_user_message("Hello! Can you help me with Python programming?")
        ]
        
        try:
            response = client.chat_completion(messages)
            print(f"\nQwen Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
    
    client.close()
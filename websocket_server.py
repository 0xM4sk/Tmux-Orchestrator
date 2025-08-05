#!/usr/bin/env python3
"""
Simple WebSocket Server for Qwen Orchestrator
Enables real-time communication between agents
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Set
import threading
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketServer:
    """Simple WebSocket server for real-time agent communication"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.message_handlers: Dict[str, callable] = {}
        
    async def register_client(self, websocket: websockets.WebSocketServerProtocol, agent_id: str):
        """Register a new client"""
        self.clients[agent_id] = websocket
        logger.info(f"Client {agent_id} connected")
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                "type": "welcome",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Connected to WebSocket server"
            }))
            
            # Listen for messages from this client
            async for message in websocket:
                await self.handle_message(agent_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {agent_id} disconnected")
        finally:
            # Remove client when disconnected
            if agent_id in self.clients:
                del self.clients[agent_id]
                
    async def handle_message(self, agent_id: str, message: str):
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            logger.info(f"Received message from {agent_id}: {message_type}")
            
            # Handle different message types
            if message_type == "agent_message":
                await self.handle_agent_message(agent_id, data)
            elif message_type == "status_update":
                await self.handle_status_update(agent_id, data)
            elif message_type == "execution_log":
                await self.handle_execution_log(agent_id, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from {agent_id}: {message}")
        except Exception as e:
            logger.error(f"Error handling message from {agent_id}: {e}")
            
    async def handle_agent_message(self, agent_id: str, data: Dict):
        """Handle agent message"""
        target_agent = data.get("target_agent")
        content = data.get("content")
        
        if target_agent and target_agent in self.clients:
            # Forward message to target agent
            response = {
                "type": "agent_message",
                "from_agent": agent_id,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            await self.clients[target_agent].send(json.dumps(response))
            logger.info(f"Forwarded message from {agent_id} to {target_agent}")
        else:
            # Send error back to sender
            error_response = {
                "type": "error",
                "message": f"Target agent {target_agent} not found or not connected",
                "timestamp": datetime.now().isoformat()
            }
            await self.clients[agent_id].send(json.dumps(error_response))
            
    async def handle_status_update(self, agent_id: str, data: Dict):
        """Handle status update from agent"""
        status = data.get("status")
        logger.info(f"Status update from {agent_id}: {status}")
        
        # Broadcast status update to all connected clients
        status_update = {
            "type": "status_update",
            "agent_id": agent_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all connected clients
        for client_id, websocket in self.clients.items():
            if client_id != agent_id:  # Don't send back to sender
                try:
                    await websocket.send(json.dumps(status_update))
                except Exception as e:
                    logger.error(f"Error sending status update to {client_id}: {e}")
                    
    async def handle_execution_log(self, agent_id: str, data: Dict):
        """Handle execution log from agent"""
        action = data.get("action")
        status = data.get("status")
        logger.info(f"Execution log from {agent_id}: {action} - {status}")
        
        # Store execution log (in a real implementation, you might want to persist this)
        # For now, we'll just log it
        
    async def send_message_to_agent(self, target_agent: str, message: Dict):
        """Send a message to a specific agent"""
        if target_agent in self.clients:
            try:
                await self.clients[target_agent].send(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to {target_agent}: {e}")
                return False
        else:
            logger.warning(f"Target agent {target_agent} not connected")
            return False
            
    async def broadcast_message(self, message: Dict, exclude_agent: str = None):
        """Broadcast message to all connected agents"""
        for agent_id, websocket in self.clients.items():
            if agent_id != exclude_agent:
                try:
                    await websocket.send(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting message to {agent_id}: {e}")
                    
    async def start_server(self):
        """Start the WebSocket server"""
        async def handler(websocket, path):
            # Expect first message to be registration
            try:
                registration_message = await websocket.recv()
                registration_data = json.loads(registration_message)
                
                if registration_data.get("type") == "register":
                    agent_id = registration_data.get("agent_id")
                    if agent_id:
                        await self.register_client(websocket, agent_id)
                    else:
                        await websocket.close(code=1008, reason="No agent_id provided")
                else:
                    await websocket.close(code=1008, reason="First message must be registration")
                    
            except Exception as e:
                logger.error(f"Error during registration: {e}")
                await websocket.close(code=1011, reason="Registration error")
                
        server = await websockets.serve(handler, self.host, self.port)
        logger.info(f"WebSocket server started on {self.host}:{self.port}")
        return server
        
    def run(self):
        """Run the WebSocket server"""
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            logger.info("WebSocket server stopped")

# Example usage
if __name__ == "__main__":
    server = WebSocketServer()
    server.run()
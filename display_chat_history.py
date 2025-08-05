#!/usr/bin/env python3
"""
Display chat history between agents in a chat room structure
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from agent_state import AgentStateManager
from conversation_manager import ConversationManager
from qwen_client import QwenClient, QwenConfig

# Suppress INFO logs
logging.getLogger().setLevel(logging.WARNING)

def load_conversation_history(agent_id: str, days_back: int = 7) -> List[Dict]:
    """Load conversation history for an agent"""
    try:
        # Initialize components
        config = QwenConfig()
        qwen_client = QwenClient(config)
        state_manager = AgentStateManager()
        conv_manager = ConversationManager(state_manager, qwen_client)
        
        # Get conversation history
        history = conv_manager.get_conversation_history(agent_id, limit=100)  # Last 100 messages
        
        # Convert to dictionary format for easier handling
        messages = []
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if hasattr(msg, 'timestamp') else datetime.now().isoformat(),
                "sender": msg.metadata.get("sender", "unknown") if msg.metadata else "unknown"
            })
        
        qwen_client.close()
        return messages
        
    except Exception as e:
        print(f"Error loading conversation history for {agent_id}: {e}")
        return []

def format_message_for_display(message: Dict) -> str:
    """Format a message for display in chat format"""
    try:
        timestamp = datetime.fromisoformat(message["timestamp"])
        time_str = timestamp.strftime("%H:%M:%S")
        
        role_display = {
            "user": "👤 User",
            "assistant": "🤖 Agent",
            "system": "⚙️ System"
        }
        
        role = role_display.get(message["role"], message["role"])
        sender = message.get("sender", "unknown")
        
        # For agent messages, show the agent ID
        if message["role"] == "assistant":
            display_name = f"🤖 {sender}" if sender != "unknown" else "🤖 Agent"
        elif message["role"] == "user" and sender != "unknown":
            display_name = f"👤 {sender}"
        else:
            display_name = role
        
        # Improve agent naming for better readability
        if sender != "unknown" and sender != "user":
            # Extract agent type and number from agent ID
            if sender.startswith("project_manager_"):
                display_name = f"👑 PM"
            elif sender.startswith("developer_"):
                # Extract developer number if present
                if "_" in sender:
                    parts = sender.split("_")
                    if len(parts) >= 4 and parts[-1].isdigit():
                        display_name = f"👨‍💻 Dev{parts[-1]}"
                    else:
                        display_name = "👨‍💻 Dev"
                else:
                    display_name = "👨‍💻 Dev"
            elif sender.startswith("qa_"):
                display_name = "🕵️ QA"
            elif sender.startswith("orchestrator"):
                display_name = "🧭 Orchestrator"
            else:
                # For other agents, just show a cleaner name
                display_name = f"🤖 {sender.split('_')[0].title()}"
        
        # Special handling for the chat history display to show actual agent identities
        if "developer_project-strangers-calendar-app" in sender:
            # Extract developer number if present
            if "_" in sender and sender.split("_")[-1].isdigit():
                dev_num = sender.split("_")[-1]
                display_name = f"👨‍💻 Dev-{dev_num}"
            else:
                display_name = "👨‍💻 Dev"
        elif "project_manager_project-strangers-calendar-app" in sender:
            display_name = "👑 User (PM)"
        elif sender == "user":
            display_name = "👤 User"
        elif sender == "system":
            display_name = "⚙️ Sys Prompt"
        
        # Format the content, handling multi-line content
        content = message["content"].strip()
        formatted_content = "\n".join([f"    {line}" for line in content.split("\n")])
        
        return f"[{time_str}] {display_name}:\n{formatted_content}"
        
    except Exception as e:
        return f"[Error formatting message: {e}]\n{message}"

def display_agent_chat_history(agent_id: str):
    """Display chat history for a specific agent"""
    print(f"=== Chat History for Agent: {agent_id} ===")
    print()
    
    messages = load_conversation_history(agent_id)
    
    if not messages:
        print("No conversation history found.")
        return
    
    # Sort messages by timestamp
    messages.sort(key=lambda x: x["timestamp"])
    
    # Display messages in chat format
    for message in messages:
        formatted_message = format_message_for_display(message)
        print(formatted_message)
        print()

def display_all_agents_chat_history():
    """Display chat history for all active agents"""
    try:
        # Initialize components
        config = QwenConfig()
        qwen_client = QwenClient(config)
        state_manager = AgentStateManager()
        
        # Get all active agents
        active_agents = state_manager.get_active_agents()
        
        if not active_agents:
            print("No active agents found.")
            return
        
        print("=== Chat History for All Active Agents ===")
        print()
        
        # Display chat history for each agent
        for agent in active_agents:
            print(f"--- {agent.agent_id} ({agent.agent_type.value}) ---")
            messages = load_conversation_history(agent.agent_id, days_back=1)
            
            if not messages:
                print("  No recent conversation history.")
                print()
                continue
            
            # Sort messages by timestamp and show last 10
            messages.sort(key=lambda x: x["timestamp"])
            recent_messages = messages[-10:]  # Last 10 messages
            
            for message in recent_messages:
                formatted_message = format_message_for_display(message)
                # Indent for better readability
                indented_message = "\n".join([f"  {line}" for line in formatted_message.split("\n")])
                print(indented_message)
            print()
        
        qwen_client.close()
        
    except Exception as e:
        print(f"Error displaying all agents chat history: {e}")

def main():
    """Main function to display chat history"""
    import sys
    
    if len(sys.argv) > 1:
        agent_id = sys.argv[1]
        display_agent_chat_history(agent_id)
    else:
        display_all_agents_chat_history()

if __name__ == "__main__":
    main()
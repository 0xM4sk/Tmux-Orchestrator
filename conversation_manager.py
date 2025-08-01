#!/usr/bin/env python3
"""
Conversation Manager for Tmux Orchestrator
Handles conversation persistence, context window optimization, and message routing
Enhanced with agentic execution capabilities
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging
import threading
from collections import deque

from qwen_client import Message, QwenClient, create_system_message, create_user_message, create_assistant_message
from agent_state import AgentState, AgentStateManager, ConversationState
from agentic_capabilities import create_agentic_system_prompt
from execution_processor import ExecutionProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Manages conversation history, context window optimization, and message persistence
    """
    
    def __init__(self, state_manager: AgentStateManager, qwen_client: QwenClient):
        self.state_manager = state_manager
        self.qwen_client = qwen_client
        self.base_dir = state_manager.base_dir
        self.conversations_dir = state_manager.conversations_dir
        
        # In-memory conversation cache for active agents
        self._conversation_cache: Dict[str, deque] = {}
        self._cache_lock = threading.RLock()
        
        # Context window limits (tokens)
        self.max_context_tokens = 28000  # Leave room for response
        self.summary_trigger_tokens = 24000  # When to create summary
        self.keep_recent_messages = 20  # Always keep recent messages
        
        # Agentic execution capabilities
        self.execution_processor = ExecutionProcessor()
    
    def add_message(self, agent_id: str, message: Message) -> bool:
        """Add a message to agent's conversation history"""
        try:
            # Update agent state
            agent = self.state_manager.get_agent(agent_id)
            if not agent:
                logger.error(f"Agent {agent_id} not found")
                return False
            
            # Add to in-memory cache
            with self._cache_lock:
                if agent_id not in self._conversation_cache:
                    self._conversation_cache[agent_id] = deque(maxlen=1000)  # Limit memory usage
                
                self._conversation_cache[agent_id].append(message)
            
            # Update conversation state
            agent.conversation_state.message_count += 1
            if message.tokens:
                agent.conversation_state.total_tokens_used += message.tokens
            
            # Estimate tokens if not provided
            if not message.tokens:
                message.tokens = self.qwen_client.estimate_tokens(message.content)
                agent.conversation_state.total_tokens_used += message.tokens
            
            # Check if summarization is needed
            current_tokens = self._calculate_conversation_tokens(agent_id)
            agent.conversation_state.context_window_usage = current_tokens / self.max_context_tokens
            
            if current_tokens > self.summary_trigger_tokens:
                agent.conversation_state.needs_summarization = True
            
            # Persist to disk
            self._persist_message(agent_id, message)
            
            # Update agent state
            self.state_manager.update_agent(agent)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding message for agent {agent_id}: {e}")
            return False
    
    def get_conversation_history(self, agent_id: str, limit: Optional[int] = None) -> List[Message]:
        """Get conversation history for an agent"""
        try:
            # Check cache first
            with self._cache_lock:
                if agent_id in self._conversation_cache:
                    messages = list(self._conversation_cache[agent_id])
                    if limit:
                        messages = messages[-limit:]
                    return messages
            
            # Load from disk if not in cache
            messages = self._load_conversation_from_disk(agent_id)
            
            # Cache the messages
            with self._cache_lock:
                self._conversation_cache[agent_id] = deque(messages, maxlen=1000)
            
            if limit:
                messages = messages[-limit:]
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation history for agent {agent_id}: {e}")
            return []
    
    def get_optimized_context(self, agent_id: str) -> List[Message]:
        """Get optimized conversation context for API calls"""
        agent = self.state_manager.get_agent(agent_id)
        if not agent:
            return []
        
        messages = self.get_conversation_history(agent_id)
        
        # If we need summarization, create it
        if agent.conversation_state.needs_summarization:
            messages = self._create_summarized_context(agent_id, messages)
            
            # Update agent state
            agent.conversation_state.needs_summarization = False
            agent.conversation_state.last_summary_at = datetime.now()
            self.state_manager.update_agent(agent)
        
        # Ensure we don't exceed context window
        return self._trim_to_context_window(messages)
    
    def send_message_to_agent(self, agent_id: str, content: str, sender: str = "user") -> Optional[str]:
        """Send a message to an agent and get response"""
        try:
            agent = self.state_manager.get_agent(agent_id)
            if not agent:
                logger.error(f"Agent {agent_id} not found")
                return None
            
            # Create user message
            user_message = create_user_message(content)
            self.add_message(agent_id, user_message)
            
            # Get optimized context for API call
            context_messages = self.get_optimized_context(agent_id)
            
            # Ensure system message is first with agentic capabilities
            if not context_messages or context_messages[0].role != "system":
                # Enhance system prompt with agentic capabilities
                enhanced_prompt = create_agentic_system_prompt(agent.role_config.system_prompt)
                system_message = create_system_message(enhanced_prompt)
                context_messages.insert(0, system_message)
            else:
                # Update existing system message with agentic capabilities
                original_prompt = context_messages[0].content
                enhanced_prompt = create_agentic_system_prompt(original_prompt)
                context_messages[0].content = enhanced_prompt
            
            # Get response from Qwen
            start_time = datetime.now()
            response_content = self.qwen_client.chat_completion(context_messages)
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Process response for agentic execution
            execution_result = self.execution_processor.process_response(response_content, agent_id)
            
            # Use the modified response (with execution results)
            final_response = execution_result["modified_response"]
            executed_actions = execution_result["executed_actions"]
            
            # Create assistant message with execution metadata
            response_tokens = self.qwen_client.estimate_tokens(final_response)
            assistant_message = create_assistant_message(
                final_response,
                tokens=response_tokens
            )
            assistant_message.metadata = {
                "response_time": response_time,
                "model": agent.role_config.model,
                "sender": sender,
                "executed_actions": executed_actions,
                "execution_results": execution_result["execution_results"]
            }
            
            # Add response to conversation
            self.add_message(agent_id, assistant_message)
            
            # Log execution activity
            if executed_actions > 0:
                logger.info(f"Agent {agent_id} executed {executed_actions} actions")
            
            # Update performance metrics
            agent.performance_metrics.average_response_time = (
                (agent.performance_metrics.average_response_time * agent.conversation_state.message_count + response_time) /
                (agent.conversation_state.message_count + 1)
            )
            self.state_manager.update_agent(agent)
            
            logger.info(f"Agent {agent_id} responded in {response_time:.2f}s with {executed_actions} actions executed")
            return final_response
            
        except Exception as e:
            logger.error(f"Error sending message to agent {agent_id}: {e}")
            
            # Update error metrics
            agent = self.state_manager.get_agent(agent_id)
            if agent:
                agent.performance_metrics.last_error = str(e)
                agent.performance_metrics.success_rate = max(0, agent.performance_metrics.success_rate - 0.1)
                self.state_manager.update_agent(agent)
            
            return None
    
    def _calculate_conversation_tokens(self, agent_id: str) -> int:
        """Calculate total tokens in conversation"""
        messages = self.get_conversation_history(agent_id)
        total_tokens = 0
        
        for message in messages:
            if message.tokens:
                total_tokens += message.tokens
            else:
                total_tokens += self.qwen_client.estimate_tokens(message.content)
        
        return total_tokens
    
    def _create_summarized_context(self, agent_id: str, messages: List[Message]) -> List[Message]:
        """Create summarized context to fit within token limits"""
        if len(messages) <= self.keep_recent_messages:
            return messages
        
        # Keep system message, recent messages, and create summary of the middle
        system_messages = [msg for msg in messages if msg.role == "system"]
        recent_messages = messages[-self.keep_recent_messages:]
        middle_messages = messages[len(system_messages):-self.keep_recent_messages]
        
        if not middle_messages:
            return system_messages + recent_messages
        
        # Create summary of middle messages
        summary_content = self._create_conversation_summary(agent_id, middle_messages)
        summary_message = create_system_message(f"[CONVERSATION SUMMARY]\n{summary_content}")
        
        return system_messages + [summary_message] + recent_messages
    
    def _create_conversation_summary(self, agent_id: str, messages: List[Message]) -> str:
        """Create a summary of conversation messages"""
        try:
            # Prepare messages for summarization
            conversation_text = ""
            for msg in messages:
                role_prefix = {"user": "Human", "assistant": "Agent", "system": "System"}.get(msg.role, msg.role)
                conversation_text += f"{role_prefix}: {msg.content}\n\n"
            
            # Create summarization prompt
            summary_prompt = f"""Please create a concise summary of this conversation that preserves the key context, decisions made, and current state. Focus on:
1. Main topics discussed
2. Decisions or conclusions reached
3. Current tasks or objectives
4. Important technical details
5. Any blockers or issues mentioned

Conversation to summarize:
{conversation_text}

Summary:"""
            
            # Use a simple completion for summarization
            summary = self.qwen_client.generate_completion(summary_prompt)
            
            # Add metadata
            summary_with_meta = f"""Summary of {len(messages)} messages from {messages[0].timestamp.strftime('%Y-%m-%d %H:%M')} to {messages[-1].timestamp.strftime('%Y-%m-%d %H:%M')}:

{summary}

[End of summary - conversation continues below]"""
            
            return summary_with_meta
            
        except Exception as e:
            logger.error(f"Error creating conversation summary: {e}")
            # Fallback to simple truncation summary
            return f"[Summary of {len(messages)} messages - detailed summary unavailable due to error: {str(e)}]"
    
    def _trim_to_context_window(self, messages: List[Message]) -> List[Message]:
        """Trim messages to fit within context window"""
        total_tokens = 0
        result_messages = []
        
        # Always include system messages
        system_messages = [msg for msg in messages if msg.role == "system"]
        other_messages = [msg for msg in messages if msg.role != "system"]
        
        # Add system messages first
        for msg in system_messages:
            tokens = msg.tokens or self.qwen_client.estimate_tokens(msg.content)
            total_tokens += tokens
            result_messages.append(msg)
        
        # Add other messages from most recent backwards
        for msg in reversed(other_messages):
            tokens = msg.tokens or self.qwen_client.estimate_tokens(msg.content)
            if total_tokens + tokens > self.max_context_tokens:
                break
            total_tokens += tokens
            result_messages.insert(-len(system_messages) if system_messages else 0, msg)
        
        return result_messages
    
    def _persist_message(self, agent_id: str, message: Message):
        """Persist message to disk"""
        try:
            # Create conversation directory if it doesn't exist
            conv_dir = self.conversations_dir / agent_id
            conv_dir.mkdir(exist_ok=True)
            
            # Get today's log file
            today = message.timestamp.strftime('%Y-%m-%d')
            log_file = conv_dir / f"{today}.jsonl"
            
            # Append message to log file
            with open(log_file, 'a') as f:
                json.dump(message.to_dict(), f)
                f.write('\n')
                
        except Exception as e:
            logger.error(f"Error persisting message for agent {agent_id}: {e}")
    
    def _load_conversation_from_disk(self, agent_id: str, days_back: int = 7) -> List[Message]:
        """Load conversation history from disk"""
        messages = []
        conv_dir = self.conversations_dir / agent_id
        
        if not conv_dir.exists():
            return messages
        
        # Load messages from the last N days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        current_date = start_date
        while current_date <= end_date:
            log_file = conv_dir / f"{current_date.strftime('%Y-%m-%d')}.jsonl"
            
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                message_data = json.loads(line.strip())
                                message = Message.from_dict(message_data)
                                messages.append(message)
                except Exception as e:
                    logger.error(f"Error loading messages from {log_file}: {e}")
            
            current_date += timedelta(days=1)
        
        # Sort by timestamp
        messages.sort(key=lambda m: m.timestamp)
        return messages
    
    def get_conversation_summary(self, agent_id: str, days_back: int = 1) -> Dict:
        """Get conversation summary for an agent"""
        messages = self._load_conversation_from_disk(agent_id, days_back)
        
        if not messages:
            return {
                "agent_id": agent_id,
                "period": f"last {days_back} days",
                "message_count": 0,
                "summary": "No conversation history found"
            }
        
        # Calculate statistics
        user_messages = [m for m in messages if m.role == "user"]
        assistant_messages = [m for m in messages if m.role == "assistant"]
        
        total_tokens = sum(m.tokens or 0 for m in messages)
        avg_response_time = 0
        
        if assistant_messages:
            response_times = [
                m.metadata.get("response_time", 0) 
                for m in assistant_messages 
                if m.metadata and "response_time" in m.metadata
            ]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        # Create summary
        summary_text = self._create_conversation_summary(agent_id, messages[-50:])  # Last 50 messages
        
        return {
            "agent_id": agent_id,
            "period": f"last {days_back} days",
            "message_count": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_tokens": total_tokens,
            "average_response_time": avg_response_time,
            "first_message": messages[0].timestamp.isoformat() if messages else None,
            "last_message": messages[-1].timestamp.isoformat() if messages else None,
            "summary": summary_text
        }
    
    def cleanup_old_conversations(self, days_to_keep: int = 30):
        """Clean up old conversation files"""
        cutoff_date = datetime.now().date() - timedelta(days=days_to_keep)
        cleaned_files = 0
        
        for agent_dir in self.conversations_dir.iterdir():
            if agent_dir.is_dir():
                for log_file in agent_dir.glob("*.jsonl"):
                    try:
                        # Parse date from filename
                        date_str = log_file.stem
                        file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        
                        if file_date < cutoff_date:
                            log_file.unlink()
                            cleaned_files += 1
                            
                    except ValueError:
                        # Skip files that don't match date format
                        continue
                    except Exception as e:
                        logger.error(f"Error cleaning up {log_file}: {e}")
        
        logger.info(f"Cleaned up {cleaned_files} old conversation files")
        return cleaned_files

# Example usage and testing
if __name__ == "__main__":
    from qwen_client import QwenClient, QwenConfig
    
    # Test the conversation manager
    config = QwenConfig()
    qwen_client = QwenClient(config)
    state_manager = AgentStateManager()
    conv_manager = ConversationManager(state_manager, qwen_client)
    
    # Create test agent
    from agent_state import AgentType
    agent_id = state_manager.create_agent(AgentType.DEVELOPER, "test-session", 0)
    
    # Test conversation
    response = conv_manager.send_message_to_agent(
        agent_id, 
        "Hello! Can you help me understand how to implement authentication in a web application?"
    )
    
    if response:
        print(f"Agent response: {response[:200]}...")
        
        # Get conversation history
        history = conv_manager.get_conversation_history(agent_id)
        print(f"Conversation has {len(history)} messages")
        
        # Get summary
        summary = conv_manager.get_conversation_summary(agent_id)
        print(f"Summary: {summary}")
    
    qwen_client.close()
#!/usr/bin/env python3
"""
Agent Communication Protocols for Qwen Orchestrator
Handles structured communication between agents with message routing and coordination
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import logging

from qwen_client import QwenClient, create_user_message
from agent_state import AgentStateManager, AgentType, AgentStatus
from conversation_manager import ConversationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of inter-agent messages"""
    STATUS_REQUEST = "status_request"
    STATUS_RESPONSE = "status_response"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETION = "task_completion"
    COORDINATION = "coordination"
    ESCALATION = "escalation"
    BROADCAST = "broadcast"
    DIRECT_MESSAGE = "direct_message"

class Priority(Enum):
    """Message priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class AgentMessage:
    """Structured message between agents"""
    
    def __init__(self, 
                 from_agent: str,
                 to_agent: str,
                 message_type: MessageType,
                 content: str,
                 priority: Priority = Priority.MEDIUM,
                 metadata: Optional[Dict] = None):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.content = content
        self.priority = priority
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.message_id = f"{from_agent}_{to_agent}_{int(time.time())}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "content": self.content,
            "priority": self.priority.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentMessage':
        """Create from dictionary"""
        msg = cls(
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            priority=Priority(data["priority"]),
            metadata=data.get("metadata", {})
        )
        msg.message_id = data["message_id"]
        msg.timestamp = datetime.fromisoformat(data["timestamp"])
        return msg

class CommunicationHub:
    """
    Central hub for agent communication
    Handles message routing, coordination, and protocol enforcement
    """
    
    def __init__(self, state_manager: AgentStateManager, conversation_manager: ConversationManager):
        self.state_manager = state_manager
        self.conversation_manager = conversation_manager
        
        # Message templates for structured communication
        self.message_templates = self._load_message_templates()
    
    def _load_message_templates(self) -> Dict[str, str]:
        """Load message templates for structured communication"""
        return {
            "status_request": "STATUS REQUEST: Please provide: 1) Completed tasks, 2) Current work, 3) Any blockers, 4) ETA for current task",
            
            "task_assignment": """TASK ASSIGNMENT
Task ID: {task_id}
Assigned to: {assignee}
Objective: {objective}
Success Criteria:
{success_criteria}
Priority: {priority}
Deadline: {deadline}
Additional Notes: {notes}""",
            
            "task_completion": """TASK COMPLETION REPORT
Task ID: {task_id}
Status: {status}
Completed: {completion_time}
Summary: {summary}
Deliverables: {deliverables}
Issues Encountered: {issues}
Next Steps: {next_steps}""",
            
            "escalation": """ESCALATION NOTICE
Issue: {issue}
Severity: {severity}
Affected Components: {components}
Attempted Solutions: {attempts}
Requesting: {request}
Urgency: {urgency}""",
            
            "coordination": """COORDINATION MESSAGE
Topic: {topic}
Stakeholders: {stakeholders}
Action Required: {action}
Timeline: {timeline}
Dependencies: {dependencies}"""
        }
    
    def send_message(self, from_agent: str, to_agent: str, message_type: MessageType, 
                    content: str, priority: Priority = Priority.MEDIUM, 
                    metadata: Optional[Dict] = None) -> bool:
        """Send a structured message between agents"""
        try:
            # Validate agents exist
            sender = self.state_manager.get_agent(from_agent)
            recipient = self.state_manager.get_agent(to_agent)
            
            if not sender:
                logger.error(f"Sender agent {from_agent} not found")
                return False
            
            if not recipient:
                logger.error(f"Recipient agent {to_agent} not found")
                return False
            
            # Create structured message
            agent_message = AgentMessage(
                from_agent=from_agent,
                to_agent=to_agent,
                message_type=message_type,
                content=content,
                priority=priority,
                metadata=metadata
            )
            
            # Format message for delivery
            formatted_content = self._format_message_for_delivery(agent_message)
            
            # Send via conversation manager
            response = self.conversation_manager.send_message_to_agent(
                to_agent, formatted_content, sender=from_agent
            )
            
            if response:
                logger.info(f"Message sent from {from_agent} to {to_agent}: {message_type.value}")
                
                # Log the communication
                self._log_communication(agent_message, response)
                
                return True
            else:
                logger.error(f"Failed to deliver message from {from_agent} to {to_agent}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def _format_message_for_delivery(self, message: AgentMessage) -> str:
        """Format message for delivery to recipient agent"""
        priority_emoji = {
            Priority.LOW: "🔵",
            Priority.MEDIUM: "🟡", 
            Priority.HIGH: "🟠",
            Priority.URGENT: "🔴"
        }
        
        type_emoji = {
            MessageType.STATUS_REQUEST: "📊",
            MessageType.TASK_ASSIGNMENT: "📋",
            MessageType.COORDINATION: "🤝",
            MessageType.ESCALATION: "🚨",
            MessageType.BROADCAST: "📢",
            MessageType.DIRECT_MESSAGE: "💬"
        }
        
        formatted = f"""
{priority_emoji.get(message.priority, '⚪')} {type_emoji.get(message.message_type, '📝')} Message from {message.from_agent}

Type: {message.message_type.value.title()}
Priority: {message.priority.value.title()}
Time: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{message.content}
"""
        
        if message.metadata:
            formatted += f"\nMetadata: {json.dumps(message.metadata, indent=2)}"
        
        return formatted.strip()
    
    def _log_communication(self, message: AgentMessage, response: str):
        """Log communication for audit trail"""
        try:
            log_dir = self.state_manager.base_dir / "logs"
            log_file = log_dir / "communication.log"
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "message": message.to_dict(),
                "response_preview": response[:200] + "..." if len(response) > 200 else response
            }
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Error logging communication: {e}")
    
    def request_status(self, from_agent: str, to_agent: str) -> bool:
        """Request status update from an agent"""
        return self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.STATUS_REQUEST,
            content=self.message_templates["status_request"],
            priority=Priority.MEDIUM
        )
    
    def assign_task(self, from_agent: str, to_agent: str, task_details: Dict) -> bool:
        """Assign a task to an agent"""
        content = self.message_templates["task_assignment"].format(
            task_id=task_details.get("task_id", "TASK_" + str(int(time.time()))),
            assignee=to_agent,
            objective=task_details.get("objective", ""),
            success_criteria=task_details.get("success_criteria", ""),
            priority=task_details.get("priority", "medium"),
            deadline=task_details.get("deadline", "TBD"),
            notes=task_details.get("notes", "")
        )
        
        return self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.TASK_ASSIGNMENT,
            content=content,
            priority=Priority.HIGH,
            metadata=task_details
        )
    
    def report_completion(self, from_agent: str, to_agent: str, completion_details: Dict) -> bool:
        """Report task completion"""
        content = self.message_templates["task_completion"].format(
            task_id=completion_details.get("task_id", ""),
            status=completion_details.get("status", "completed"),
            completion_time=completion_details.get("completion_time", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            summary=completion_details.get("summary", ""),
            deliverables=completion_details.get("deliverables", ""),
            issues=completion_details.get("issues", "None"),
            next_steps=completion_details.get("next_steps", "")
        )
        
        return self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.TASK_COMPLETION,
            content=content,
            priority=Priority.MEDIUM,
            metadata=completion_details
        )
    
    def escalate_issue(self, from_agent: str, to_agent: str, issue_details: Dict) -> bool:
        """Escalate an issue to higher authority"""
        content = self.message_templates["escalation"].format(
            issue=issue_details.get("issue", ""),
            severity=issue_details.get("severity", "medium"),
            components=issue_details.get("components", ""),
            attempts=issue_details.get("attempts", ""),
            request=issue_details.get("request", ""),
            urgency=issue_details.get("urgency", "normal")
        )
        
        return self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.ESCALATION,
            content=content,
            priority=Priority.URGENT,
            metadata=issue_details
        )
    
    def coordinate_agents(self, from_agent: str, target_agents: List[str], coordination_details: Dict) -> List[bool]:
        """Send coordination message to multiple agents"""
        content = self.message_templates["coordination"].format(
            topic=coordination_details.get("topic", ""),
            stakeholders=", ".join(target_agents),
            action=coordination_details.get("action", ""),
            timeline=coordination_details.get("timeline", ""),
            dependencies=coordination_details.get("dependencies", "")
        )
        
        results = []
        for target_agent in target_agents:
            result = self.send_message(
                from_agent=from_agent,
                to_agent=target_agent,
                message_type=MessageType.COORDINATION,
                content=content,
                priority=Priority.HIGH,
                metadata=coordination_details
            )
            results.append(result)
        
        return results
    
    def broadcast_message(self, from_agent: str, message: str, agent_types: Optional[List[AgentType]] = None) -> List[bool]:
        """Broadcast message to multiple agents"""
        # Get target agents
        if agent_types:
            target_agents = []
            for agent in self.state_manager.get_active_agents():
                if agent.agent_type in agent_types:
                    target_agents.append(agent.agent_id)
        else:
            target_agents = [agent.agent_id for agent in self.state_manager.get_active_agents()]
        
        # Remove sender from targets
        if from_agent in target_agents:
            target_agents.remove(from_agent)
        
        results = []
        for target_agent in target_agents:
            result = self.send_message(
                from_agent=from_agent,
                to_agent=target_agent,
                message_type=MessageType.BROADCAST,
                content=f"BROADCAST MESSAGE:\n\n{message}",
                priority=Priority.MEDIUM
            )
            results.append(result)
        
        return results
    
    def get_communication_stats(self, days_back: int = 7) -> Dict:
        """Get communication statistics"""
        try:
            log_file = self.state_manager.base_dir / "logs" / "communication.log"
            
            if not log_file.exists():
                return {"error": "No communication log found"}
            
            # Parse log entries
            entries = []
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_entries = [
                entry for entry in entries
                if datetime.fromisoformat(entry["timestamp"]) > cutoff_date
            ]
            
            # Calculate statistics
            total_messages = len(recent_entries)
            by_type = {}
            by_priority = {}
            by_agent = {}
            
            for entry in recent_entries:
                msg = entry["message"]
                
                # Count by type
                msg_type = msg["message_type"]
                by_type[msg_type] = by_type.get(msg_type, 0) + 1
                
                # Count by priority
                priority = msg["priority"]
                by_priority[priority] = by_priority.get(priority, 0) + 1
                
                # Count by agent
                from_agent = msg["from_agent"]
                by_agent[from_agent] = by_agent.get(from_agent, 0) + 1
            
            return {
                "period_days": days_back,
                "total_messages": total_messages,
                "by_type": by_type,
                "by_priority": by_priority,
                "by_agent": by_agent,
                "most_active_agent": max(by_agent.items(), key=lambda x: x[1])[0] if by_agent else None
            }
            
        except Exception as e:
            logger.error(f"Error getting communication stats: {e}")
            return {"error": str(e)}

# Convenience functions for common communication patterns
def create_communication_hub(state_manager: AgentStateManager, conversation_manager: ConversationManager) -> CommunicationHub:
    """Create a communication hub instance"""
    return CommunicationHub(state_manager, conversation_manager)

def send_status_request(hub: CommunicationHub, from_agent: str, to_agent: str) -> bool:
    """Send a status request"""
    return hub.request_status(from_agent, to_agent)

def assign_task_to_agent(hub: CommunicationHub, manager: str, developer: str, task: Dict) -> bool:
    """Assign a task from manager to developer"""
    return hub.assign_task(manager, developer, task)

def escalate_to_orchestrator(hub: CommunicationHub, from_agent: str, issue: Dict) -> bool:
    """Escalate an issue to the orchestrator"""
    return hub.escalate_issue(from_agent, "orchestrator", issue)

# Example usage and testing
if __name__ == "__main__":
    from qwen_client import QwenClient, QwenConfig
    
    # Test communication protocols
    config = QwenConfig()
    qwen_client = QwenClient(config)
    state_manager = AgentStateManager()
    conversation_manager = ConversationManager(state_manager, qwen_client)
    
    # Create communication hub
    hub = CommunicationHub(state_manager, conversation_manager)
    
    # Test message sending (would need actual agents)
    print("Communication Hub initialized successfully")
    print("Available message types:", [t.value for t in MessageType])
    print("Available priorities:", [p.value for p in Priority])
    
    qwen_client.close()
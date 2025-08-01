#!/usr/bin/env python3
"""
Qwen Control - System Management Tool for Tmux Orchestrator
Replaces claude_control.py with Qwen-based agent management
Enhanced with autonomous capabilities
"""

import sys
import argparse
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import os

from qwen_client import QwenClient, QwenConfig
from agent_state import AgentStateManager, AgentType, AgentStatus
from conversation_manager import ConversationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QwenControl:
    """
    System management and control interface for Qwen-based orchestrator
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.qwen_config = QwenConfig.load_from_file(config_path) if config_path else QwenConfig()
        self.qwen_client = QwenClient(self.qwen_config)
        self.state_manager = AgentStateManager()
        self.conversation_manager = ConversationManager(self.state_manager, self.qwen_client)
    
    def status(self, detail_level: str = "summary") -> Dict:
        """Get system status"""
        try:
            # Get all active agents
            active_agents = self.state_manager.get_active_agents()
            
            # Get Ollama health
            health = self.qwen_client.health_check()
            
            # Calculate system metrics
            total_messages = sum(agent.conversation_state.message_count for agent in active_agents)
            total_tokens = sum(agent.conversation_state.total_tokens_used for agent in active_agents)
            avg_response_time = 0
            
            if active_agents:
                response_times = [agent.performance_metrics.average_response_time for agent in active_agents]
                avg_response_time = sum(response_times) / len(response_times)
            
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "system_health": {
                    "ollama_server": health["server_running"],
                    "model_available": health["model_available"],
                    "model_name": health["model_name"],
                    "available_models": health["available_models"],
                    "error": health.get("error")
                },
                "agents": {
                    "total_active": len(active_agents),
                    "by_type": self._count_agents_by_type(active_agents),
                    "by_session": self._count_agents_by_session(active_agents)
                },
                "performance": {
                    "total_messages": total_messages,
                    "total_tokens": total_tokens,
                    "average_response_time": avg_response_time
                }
            }
            
            if detail_level == "detailed":
                status_data["agent_details"] = [
                    self._agent_summary(agent) for agent in active_agents
                ]
                
                # Add tmux session information
                status_data["tmux_sessions"] = self._get_tmux_sessions()
            
            return status_data
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _count_agents_by_type(self, agents: List) -> Dict[str, int]:
        """Count agents by type"""
        counts = {}
        for agent in agents:
            agent_type = agent.agent_type.value
            counts[agent_type] = counts.get(agent_type, 0) + 1
        return counts
    
    def _count_agents_by_session(self, agents: List) -> Dict[str, int]:
        """Count agents by session"""
        counts = {}
        for agent in agents:
            session = agent.session_name
            counts[session] = counts.get(session, 0) + 1
        return counts
    
    def _agent_summary(self, agent) -> Dict:
        """Create summary for an agent"""
        return {
            "agent_id": agent.agent_id,
            "type": agent.agent_type.value,
            "session": f"{agent.session_name}:{agent.window_index}",
            "status": agent.status.value,
            "messages": agent.conversation_state.message_count,
            "tokens": agent.conversation_state.total_tokens_used,
            "last_active": agent.last_active.isoformat(),
            "current_project": agent.current_context.active_project,
            "current_task": agent.current_context.current_task,
            "response_time": agent.performance_metrics.average_response_time,
            "success_rate": agent.performance_metrics.success_rate
        }
    
    def _get_tmux_sessions(self) -> List[Dict]:
        """Get tmux session information"""
        try:
            # Get tmux sessions
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}:#{session_attached}:#{session_windows}"],
                capture_output=True, text=True, check=True
            )
            
            sessions = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(':')
                    if len(parts) >= 3:
                        sessions.append({
                            "name": parts[0],
                            "attached": parts[1] == '1',
                            "windows": int(parts[2])
                        })
            
            return sessions
            
        except subprocess.CalledProcessError:
            return []
        except Exception as e:
            logger.error(f"Error getting tmux sessions: {e}")
            return []
    
    def list_agents(self, session_filter: Optional[str] = None) -> List[Dict]:
        """List all agents with optional session filter"""
        try:
            if session_filter:
                agents = self.state_manager.get_session_agents(session_filter)
            else:
                agents = self.state_manager.get_active_agents()
            
            return [self._agent_summary(agent) for agent in agents]
            
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return []
    
    def agent_info(self, agent_id: str) -> Optional[Dict]:
        """Get detailed information about a specific agent"""
        try:
            agent = self.state_manager.get_agent(agent_id)
            if not agent:
                return None
            
            # Get conversation summary
            conv_summary = self.conversation_manager.get_conversation_summary(agent_id, days_back=1)
            
            return {
                "agent_state": agent.to_dict(),
                "conversation_summary": conv_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting agent info for {agent_id}: {e}")
            return None
    
    def send_message(self, agent_id: str, message: str) -> Optional[str]:
        """Send a message to an agent with autonomous capabilities"""
        try:
            # Enhanced message with file reading capabilities
            enhanced_message = self._enhance_message_with_autonomous_context(message)
            
            response = self.conversation_manager.send_message_to_agent(
                agent_id, enhanced_message, sender="qwen_control"
            )
            return response
            
        except Exception as e:
            logger.error(f"Error sending message to {agent_id}: {e}")
            return None
    
    def _enhance_message_with_autonomous_context(self, message: str) -> str:
        """Enhance message with autonomous capabilities and file context"""
        enhanced_message = message
        working_dir = Path.cwd()
        
        # Auto-read common project files if mentioned
        files_to_read = []
        file_patterns = [
            "project_spec.md", "README.md", "package.json",
            "requirements.txt", "spec.md", "specification.md"
        ]
        
        for pattern in file_patterns:
            if pattern.lower() in message.lower():
                file_path = working_dir / pattern
                if file_path.exists():
                    files_to_read.append(pattern)
        
        # Auto-read project_spec.md if message mentions reading specs
        if any(word in message.lower() for word in ["spec", "specification", "project_spec", "read project"]):
            spec_file = working_dir / "project_spec.md"
            if spec_file.exists() and "project_spec.md" not in files_to_read:
                files_to_read.append("project_spec.md")
        
        # Add file contents to message
        if files_to_read:
            enhanced_message += "\n\n=== AUTONOMOUS FILE CONTEXT ===\n"
            enhanced_message += "I have automatically read the following files for you:\n\n"
            
            for file_name in files_to_read:
                try:
                    file_path = working_dir / file_name
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    enhanced_message += f"--- Contents of {file_name} ---\n{content}\n\n"
                    logger.info(f"Auto-read file {file_name} for autonomous context")
                    
                except Exception as e:
                    enhanced_message += f"--- Error reading {file_name}: {str(e)} ---\n\n"
        
        # Add project structure context if relevant
        if any(word in message.lower() for word in ["project", "structure", "analyze", "understand"]):
            try:
                files = list(working_dir.glob("*"))
                file_list = []
                for f in files[:20]:  # Limit to first 20 items
                    if f.is_file():
                        file_list.append(f"📄 {f.name}")
                    elif f.is_dir() and not f.name.startswith('.'):
                        file_list.append(f"📁 {f.name}/")
                
                enhanced_message += f"\n=== PROJECT STRUCTURE CONTEXT ===\n"
                enhanced_message += f"Working Directory: {working_dir}\n"
                enhanced_message += f"Files and Directories:\n" + "\n".join(file_list) + "\n\n"
                
            except Exception as e:
                logger.error(f"Error getting project structure: {e}")
        
        # Add autonomous behavior instructions
        enhanced_message += """
=== AUTONOMOUS BEHAVIOR INSTRUCTIONS ===
You are operating in autonomous mode with the following capabilities:
- File contents have been automatically provided above when relevant
- You should analyze the provided information and give concrete, actionable responses
- Don't ask users to provide file contents - they have been included automatically
- Break down complex requirements into specific tasks and next steps
- Be proactive and suggest concrete actions based on the information provided
- If you need to create or coordinate with other agents, specify exactly what should be done

Respond with specific, actionable guidance based on the context provided above.
"""
        
        return enhanced_message
    
    def create_agent(self, agent_type: str, session_name: str, window_index: int, 
                    agent_id: Optional[str] = None) -> Optional[str]:
        """Create a new agent"""
        try:
            agent_type_enum = AgentType(agent_type)
            created_id = self.state_manager.create_agent(
                agent_type_enum, session_name, window_index, agent_id
            )
            return created_id
            
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return None
    
    def archive_agent(self, agent_id: str) -> bool:
        """Archive an agent"""
        try:
            return self.state_manager.archive_agent(agent_id)
            
        except Exception as e:
            logger.error(f"Error archiving agent {agent_id}: {e}")
            return False
    
    def cleanup_system(self) -> Dict[str, int]:
        """Perform system cleanup"""
        try:
            # Cleanup inactive agents
            inactive_cleaned = self.state_manager.cleanup_inactive_agents()
            
            # Cleanup old conversations
            old_convs_cleaned = self.conversation_manager.cleanup_old_conversations()
            
            return {
                "inactive_agents_cleaned": inactive_cleaned,
                "old_conversations_cleaned": old_convs_cleaned
            }
            
        except Exception as e:
            logger.error(f"Error during system cleanup: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict:
        """Perform comprehensive health check"""
        try:
            # Check Ollama connection
            ollama_health = self.qwen_client.health_check()
            
            # Check agent states
            active_agents = self.state_manager.get_active_agents()
            error_agents = [a for a in active_agents if a.status == AgentStatus.ERROR]
            
            # Check disk space
            base_dir = self.state_manager.base_dir
            disk_usage = self._get_disk_usage(base_dir)
            
            # Check conversation files
            conv_files = list(self.state_manager.conversations_dir.rglob("*.jsonl"))
            
            health_data = {
                "timestamp": datetime.now().isoformat(),
                "ollama": ollama_health,
                "agents": {
                    "total_active": len(active_agents),
                    "error_count": len(error_agents),
                    "error_agents": [a.agent_id for a in error_agents]
                },
                "storage": {
                    "base_directory": str(base_dir),
                    "disk_usage_mb": disk_usage,
                    "conversation_files": len(conv_files)
                },
                "overall_status": "healthy" if ollama_health["server_running"] and len(error_agents) == 0 else "degraded"
            }
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "overall_status": "error"
            }
    
    def _get_disk_usage(self, path: Path) -> float:
        """Get disk usage for a directory in MB"""
        try:
            total_size = 0
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0
    
    def migrate_from_claude(self, claude_logs_dir: str) -> Dict[str, int]:
        """Migrate conversation logs from Claude system"""
        try:
            # This is a placeholder for migration logic
            # In a real implementation, you would:
            # 1. Parse Claude conversation logs
            # 2. Convert to Qwen format
            # 3. Create agent states
            # 4. Import conversation histories
            
            logger.info(f"Migration from {claude_logs_dir} not yet implemented")
            return {"migrated_agents": 0, "migrated_conversations": 0}
            
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close connections"""
        try:
            self.qwen_client.close()
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

def print_status(status_data: Dict, detail_level: str = "summary"):
    """Print formatted status information"""
    print(f"\n🤖 Qwen Orchestrator Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # System health
    health = status_data.get("system_health", {})
    print(f"\n🏥 System Health:")
    print(f"  Ollama Server: {'✅ Running' if health.get('ollama_server') else '❌ Down'}")
    print(f"  Model Available: {'✅ Yes' if health.get('model_available') else '❌ No'}")
    print(f"  Model: {health.get('model_name', 'Unknown')}")
    
    if health.get("error"):
        print(f"  ⚠️  Error: {health['error']}")
    
    # Agent summary
    agents = status_data.get("agents", {})
    print(f"\n👥 Agents:")
    print(f"  Total Active: {agents.get('total_active', 0)}")
    
    by_type = agents.get("by_type", {})
    for agent_type, count in by_type.items():
        print(f"  {agent_type.title()}: {count}")
    
    # Performance
    perf = status_data.get("performance", {})
    print(f"\n⚡ Performance:")
    print(f"  Total Messages: {perf.get('total_messages', 0):,}")
    print(f"  Total Tokens: {perf.get('total_tokens', 0):,}")
    print(f"  Avg Response Time: {perf.get('average_response_time', 0):.2f}s")
    
    # Detailed information
    if detail_level == "detailed" and "agent_details" in status_data:
        print(f"\n📋 Agent Details:")
        for agent in status_data["agent_details"]:
            print(f"  {agent['agent_id']} ({agent['type']}):")
            print(f"    Session: {agent['session']}")
            print(f"    Status: {agent['status']}")
            print(f"    Messages: {agent['messages']}")
            if agent['current_project']:
                print(f"    Project: {agent['current_project']}")
            if agent['current_task']:
                print(f"    Task: {agent['current_task']}")
    
    print()

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Qwen Control - System Management Tool")
    parser.add_argument("--config", help="Path to Qwen configuration file")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.add_argument("detail", nargs="?", choices=["summary", "detailed"], 
                              default="summary", help="Detail level")
    
    # List agents command
    list_parser = subparsers.add_parser("list", help="List agents")
    list_parser.add_argument("--session", help="Filter by session name")
    
    # Agent info command
    info_parser = subparsers.add_parser("info", help="Show agent information")
    info_parser.add_argument("agent_id", help="Agent ID")
    
    # Send message command
    msg_parser = subparsers.add_parser("message", help="Send message to agent")
    msg_parser.add_argument("agent_id", help="Agent ID")
    msg_parser.add_argument("message", help="Message to send")
    
    # Create agent command
    create_parser = subparsers.add_parser("create", help="Create new agent")
    create_parser.add_argument("type", choices=[t.value for t in AgentType], help="Agent type")
    create_parser.add_argument("session", help="Session name")
    create_parser.add_argument("window", type=int, help="Window index")
    create_parser.add_argument("--id", help="Custom agent ID")
    
    # Archive agent command
    archive_parser = subparsers.add_parser("archive", help="Archive agent")
    archive_parser.add_argument("agent_id", help="Agent ID")
    
    # Cleanup command
    subparsers.add_parser("cleanup", help="Perform system cleanup")
    
    # Health check command
    subparsers.add_parser("health", help="Perform health check")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize control system
    try:
        control = QwenControl(args.config)
        
        if args.command == "status":
            status_data = control.status(args.detail)
            if "error" in status_data:
                print(f"❌ Error: {status_data['error']}")
            else:
                print_status(status_data, args.detail)
        
        elif args.command == "list":
            agents = control.list_agents(args.session)
            if agents:
                print(f"\n📋 Agents{' in ' + args.session if args.session else ''}:")
                for agent in agents:
                    print(f"  {agent['agent_id']} ({agent['type']}) - {agent['session']} - {agent['status']}")
            else:
                print("No agents found")
        
        elif args.command == "info":
            info = control.agent_info(args.agent_id)
            if info:
                print(json.dumps(info, indent=2, default=str))
            else:
                print(f"❌ Agent {args.agent_id} not found")
        
        elif args.command == "message":
            response = control.send_message(args.agent_id, args.message)
            if response:
                print(f"\n🤖 Response from {args.agent_id}:")
                print(response)
            else:
                print(f"❌ Failed to send message to {args.agent_id}")
        
        elif args.command == "create":
            agent_id = control.create_agent(args.type, args.session, args.window, args.id)
            if agent_id:
                print(f"✅ Created agent: {agent_id}")
            else:
                print("❌ Failed to create agent")
        
        elif args.command == "archive":
            if control.archive_agent(args.agent_id):
                print(f"✅ Archived agent: {args.agent_id}")
            else:
                print(f"❌ Failed to archive agent: {args.agent_id}")
        
        elif args.command == "cleanup":
            result = control.cleanup_system()
            if "error" in result:
                print(f"❌ Cleanup error: {result['error']}")
            else:
                print(f"✅ Cleanup complete:")
                print(f"  Inactive agents cleaned: {result['inactive_agents_cleaned']}")
                print(f"  Old conversations cleaned: {result['old_conversations_cleaned']}")
        
        elif args.command == "health":
            health_data = control.health_check()
            print(json.dumps(health_data, indent=2, default=str))
        
        control.close()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
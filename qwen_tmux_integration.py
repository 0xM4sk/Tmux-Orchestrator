#!/usr/bin/env python3
"""
Qwen-Tmux Integration Module
Extends tmux_utils.py with Qwen-specific functionality for agent management
"""

import subprocess
import json
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

from tmux_utils import TmuxOrchestrator
from qwen_client import QwenClient, QwenConfig
from agent_state import AgentStateManager, AgentType, AgentStatus
from conversation_manager import ConversationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QwenTmuxOrchestrator(TmuxOrchestrator):
    """
    Enhanced TmuxOrchestrator with Qwen agent integration
    Provides seamless integration between tmux sessions and Qwen agents
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__()
        
        # Initialize Qwen components
        self.qwen_config = QwenConfig.load_from_file(config_path) if config_path else QwenConfig()
        self.qwen_client = QwenClient(self.qwen_config)
        self.state_manager = AgentStateManager()
        self.conversation_manager = ConversationManager(self.state_manager, self.qwen_client)
        
        logger.info("Initialized Qwen-Tmux Orchestrator")
    
    def create_agent_in_window(self, session_name: str, window_index: int, 
                              agent_type: AgentType, agent_id: Optional[str] = None) -> str:
        """Create a Qwen agent and start it in a tmux window"""
        try:
            # Create agent state
            created_agent_id = self.state_manager.create_agent(
                agent_type, session_name, window_index, agent_id
            )
            
            # Start the agent in the tmux window
            self.start_qwen_agent_in_window(session_name, window_index, created_agent_id)
            
            logger.info(f"Created and started agent {created_agent_id} in {session_name}:{window_index}")
            return created_agent_id
            
        except Exception as e:
            logger.error(f"Error creating agent in window: {e}")
            raise
    
    def start_qwen_agent_in_window(self, session_name: str, window_index: int, agent_id: str):
        """Start a Qwen agent in a specific tmux window"""
        try:
            # Build command to start the agent
            cmd = f"python3 qwen_agent.py {agent_id}"
            
            # Send command to tmux window
            tmux_cmd = ["tmux", "send-keys", "-t", f"{session_name}:{window_index}", cmd, "C-m"]
            subprocess.run(tmux_cmd, check=True)
            
            # Wait a moment for the agent to start
            time.sleep(2)
            
            logger.info(f"Started Qwen agent {agent_id} in {session_name}:{window_index}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error starting agent in tmux window: {e}")
            raise
    
    def send_message_to_agent(self, agent_id: str, message: str) -> Optional[str]:
        """Send a message to a Qwen agent and get response"""
        try:
            response = self.conversation_manager.send_message_to_agent(
                agent_id, message, sender="tmux_orchestrator"
            )
            return response
            
        except Exception as e:
            logger.error(f"Error sending message to agent {agent_id}: {e}")
            return None
    
    def get_agent_status_for_window(self, session_name: str, window_index: int) -> Optional[Dict]:
        """Get agent status for a specific tmux window"""
        try:
            agent = self.state_manager.get_agent_by_session_window(session_name, window_index)
            if not agent:
                return None
            
            return {
                "agent_id": agent.agent_id,
                "type": agent.agent_type.value,
                "status": agent.status.value,
                "messages": agent.conversation_state.message_count,
                "tokens": agent.conversation_state.total_tokens_used,
                "last_active": agent.last_active.isoformat(),
                "current_project": agent.current_context.active_project,
                "current_task": agent.current_context.current_task,
                "response_time": agent.performance_metrics.average_response_time
            }
            
        except Exception as e:
            logger.error(f"Error getting agent status for {session_name}:{window_index}: {e}")
            return None
    
    def create_qwen_monitoring_snapshot(self) -> str:
        """Create enhanced monitoring snapshot with Qwen agent information"""
        try:
            # Get base tmux snapshot
            base_snapshot = super().create_monitoring_snapshot()
            
            # Get agent information
            active_agents = self.state_manager.get_active_agents()
            
            # Enhance snapshot with agent data
            enhanced_snapshot = base_snapshot + "\n"
            enhanced_snapshot += "Qwen Agent Information\n"
            enhanced_snapshot += "=" * 50 + "\n\n"
            
            if not active_agents:
                enhanced_snapshot += "No active Qwen agents found.\n\n"
            else:
                for agent in active_agents:
                    enhanced_snapshot += f"Agent: {agent.agent_id} ({agent.agent_type.value})\n"
                    enhanced_snapshot += f"  Session: {agent.session_name}:{agent.window_index}\n"
                    enhanced_snapshot += f"  Status: {agent.status.value}\n"
                    enhanced_snapshot += f"  Messages: {agent.conversation_state.message_count}\n"
                    enhanced_snapshot += f"  Tokens: {agent.conversation_state.total_tokens_used:,}\n"
                    enhanced_snapshot += f"  Last Active: {agent.last_active.strftime('%H:%M:%S')}\n"
                    
                    if agent.current_context.active_project:
                        enhanced_snapshot += f"  Project: {agent.current_context.active_project}\n"
                    if agent.current_context.current_task:
                        enhanced_snapshot += f"  Task: {agent.current_context.current_task}\n"
                    
                    enhanced_snapshot += "\n"
            
            # Add system health
            health = self.qwen_client.health_check()
            enhanced_snapshot += "System Health\n"
            enhanced_snapshot += "-" * 20 + "\n"
            enhanced_snapshot += f"Ollama Server: {'✅ Running' if health['server_running'] else '❌ Down'}\n"
            enhanced_snapshot += f"Model Available: {'✅ Yes' if health['model_available'] else '❌ No'}\n"
            enhanced_snapshot += f"Model: {health['model_name']}\n"
            
            if health.get("error"):
                enhanced_snapshot += f"Error: {health['error']}\n"
            
            return enhanced_snapshot
            
        except Exception as e:
            logger.error(f"Error creating enhanced monitoring snapshot: {e}")
            return super().create_monitoring_snapshot()  # Fallback to base snapshot
    
    def setup_orchestrator_session(self, session_name: str = "qwen-orchestrator") -> str:
        """Set up a complete orchestrator session with agents"""
        try:
            # Create tmux session
            subprocess.run(["tmux", "new-session", "-d", "-s", session_name], check=True)
            
            # Window 0: Orchestrator
            orchestrator_id = self.create_agent_in_window(
                session_name, 0, AgentType.ORCHESTRATOR, "orchestrator"
            )
            subprocess.run(["tmux", "rename-window", "-t", f"{session_name}:0", "Orchestrator"], check=True)
            
            # Window 1: System Monitor
            subprocess.run(["tmux", "new-window", "-t", session_name, "-n", "Monitor"], check=True)
            subprocess.run([
                "tmux", "send-keys", "-t", f"{session_name}:1", 
                "watch -n 5 'python3 qwen_control.py status detailed'", "C-m"
            ], check=True)
            
            # Window 2: Logs
            subprocess.run(["tmux", "new-window", "-t", session_name, "-n", "Logs"], check=True)
            log_dir = self.state_manager.base_dir / "logs"
            subprocess.run([
                "tmux", "send-keys", "-t", f"{session_name}:2", 
                f"tail -f {log_dir}/system.log", "C-m"
            ], check=True)
            
            logger.info(f"Set up orchestrator session: {session_name}")
            return session_name
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error setting up orchestrator session: {e}")
            raise
    
    def deploy_project_team(self, project_name: str, team_config: Dict) -> Dict[str, str]:
        """Deploy a complete project team in a new tmux session"""
        try:
            session_name = f"project-{project_name.lower().replace(' ', '-')}"
            
            # Create project session
            subprocess.run(["tmux", "new-session", "-d", "-s", session_name], check=True)
            
            deployed_agents = {}
            window_index = 0
            
            # Deploy agents based on team configuration
            for role, count in team_config.items():
                agent_type = AgentType(role)
                
                for i in range(count):
                    agent_id = f"{role}_{session_name}"
                    if count > 1:
                        agent_id += f"_{i+1}"
                    
                    # Create window if not the first one
                    if window_index > 0:
                        subprocess.run([
                            "tmux", "new-window", "-t", session_name, 
                            "-n", f"{role.title()}-{i+1}" if count > 1 else role.title()
                        ], check=True)
                    else:
                        subprocess.run([
                            "tmux", "rename-window", "-t", f"{session_name}:0", 
                            f"{role.title()}-{i+1}" if count > 1 else role.title()
                        ], check=True)
                    
                    # Create and start agent
                    created_id = self.create_agent_in_window(
                        session_name, window_index, agent_type, agent_id
                    )
                    
                    # Set project context
                    agent = self.state_manager.get_agent(created_id)
                    if agent:
                        agent.current_context.active_project = project_name
                        self.state_manager.update_agent(agent)
                    
                    deployed_agents[f"{role}_{i+1}" if count > 1 else role] = created_id
                    window_index += 1
            
            logger.info(f"Deployed project team for {project_name}: {deployed_agents}")
            return deployed_agents
            
        except Exception as e:
            logger.error(f"Error deploying project team: {e}")
            raise
    
    def get_system_overview(self) -> Dict:
        """Get comprehensive system overview"""
        try:
            # Get tmux sessions
            sessions = self.get_tmux_sessions()
            
            # Get agent information
            active_agents = self.state_manager.get_active_agents()
            
            # Get system health
            health = self.qwen_client.health_check()
            
            # Calculate metrics
            total_messages = sum(agent.conversation_state.message_count for agent in active_agents)
            total_tokens = sum(agent.conversation_state.total_tokens_used for agent in active_agents)
            
            # Group agents by project
            projects = {}
            for agent in active_agents:
                project = agent.current_context.active_project or "unassigned"
                if project not in projects:
                    projects[project] = []
                projects[project].append({
                    "agent_id": agent.agent_id,
                    "type": agent.agent_type.value,
                    "status": agent.status.value,
                    "session": f"{agent.session_name}:{agent.window_index}"
                })
            
            return {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "system_health": health,
                "tmux_sessions": [{"name": s.name, "windows": len(s.windows), "attached": s.attached} for s in sessions],
                "agents": {
                    "total_active": len(active_agents),
                    "by_type": self._count_by_type(active_agents),
                    "by_status": self._count_by_status(active_agents)
                },
                "projects": projects,
                "performance": {
                    "total_messages": total_messages,
                    "total_tokens": total_tokens,
                    "average_response_time": sum(a.performance_metrics.average_response_time for a in active_agents) / len(active_agents) if active_agents else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system overview: {e}")
            return {"error": str(e)}
    
    def _count_by_type(self, agents: List) -> Dict[str, int]:
        """Count agents by type"""
        counts = {}
        for agent in agents:
            agent_type = agent.agent_type.value
            counts[agent_type] = counts.get(agent_type, 0) + 1
        return counts
    
    def _count_by_status(self, agents: List) -> Dict[str, int]:
        """Count agents by status"""
        counts = {}
        for agent in agents:
            status = agent.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts
    
    def close(self):
        """Close all connections"""
        try:
            self.qwen_client.close()
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

# Utility functions for easy integration
def create_orchestrator_session(session_name: str = "qwen-orchestrator") -> QwenTmuxOrchestrator:
    """Create and set up a new orchestrator session"""
    orchestrator = QwenTmuxOrchestrator()
    orchestrator.setup_orchestrator_session(session_name)
    return orchestrator

def deploy_simple_project(project_name: str, include_qa: bool = True) -> QwenTmuxOrchestrator:
    """Deploy a simple project with PM, Developer, and optionally QA"""
    orchestrator = QwenTmuxOrchestrator()
    
    team_config = {
        "project_manager": 1,
        "developer": 1
    }
    
    if include_qa:
        team_config["qa"] = 1
    
    orchestrator.deploy_project_team(project_name, team_config)
    return orchestrator

def get_quick_status() -> Dict:
    """Get quick system status"""
    orchestrator = QwenTmuxOrchestrator()
    try:
        return orchestrator.get_system_overview()
    finally:
        orchestrator.close()

# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced orchestrator
    orchestrator = QwenTmuxOrchestrator()
    
    try:
        # Get system overview
        overview = orchestrator.get_system_overview()
        print("System Overview:")
        print(json.dumps(overview, indent=2))
        
        # Create monitoring snapshot
        snapshot = orchestrator.create_qwen_monitoring_snapshot()
        print("\nMonitoring Snapshot:")
        print(snapshot)
        
    finally:
        orchestrator.close()
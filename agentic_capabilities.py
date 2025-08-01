#!/usr/bin/env python3
"""
Agentic Capabilities for Qwen Orchestrator
Adds execution capabilities so agents can actually DO things, not just provide advice
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgenticExecutor:
    """
    Provides execution capabilities for agents to actually perform actions
    """
    
    def __init__(self, working_directory: str = "."):
        self.working_directory = Path(working_directory).resolve()
        self.execution_log = []
        
    def create_file(self, file_path: str, content: str) -> bool:
        """Create a file with given content"""
        try:
            full_path = self.working_directory / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log_action(f"Created file: {file_path}")
            logger.info(f"Created file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating file {file_path}: {e}")
            return False
    
    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a shell command and return results"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_directory,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_result = {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            self._log_action(f"Executed command: {command} (exit code: {result.returncode})")
            logger.info(f"Executed command: {command}")
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            error_result = {
                "command": command,
                "error": "Command timed out",
                "success": False
            }
            self._log_action(f"Command timed out: {command}")
            return error_result
            
        except Exception as e:
            error_result = {
                "command": command,
                "error": str(e),
                "success": False
            }
            logger.error(f"Error executing command {command}: {e}")
            return error_result
    
    def create_directory(self, dir_path: str) -> bool:
        """Create a directory"""
        try:
            full_path = self.working_directory / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            self._log_action(f"Created directory: {dir_path}")
            logger.info(f"Created directory: {dir_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
            return False
    
    def git_commit(self, message: str) -> Dict[str, Any]:
        """Perform git commit with message"""
        try:
            # Add all changes
            add_result = self.execute_command("git add -A")
            if not add_result["success"]:
                return add_result
            
            # Commit changes
            commit_result = self.execute_command(f'git commit -m "{message}"')
            
            self._log_action(f"Git commit: {message}")
            return commit_result
            
        except Exception as e:
            logger.error(f"Error with git commit: {e}")
            return {"error": str(e), "success": False}
    
    def create_agent(self, agent_type: str, session: str, window: int) -> Dict[str, Any]:
        """Create a new agent and launch it in a tmux window"""
        try:
            # First create the agent state
            command = f"python3 qwen_control.py create {agent_type} {session} {window}"
            result = self.execute_command(command)
            
            if not result["success"]:
                return result
            
            # Create new tmux window for the agent
            agent_id = f"{agent_type}_{session}"
            window_name = f"{agent_type.title()}"
            
            # Create new window in the session
            tmux_new_window = f"tmux new-window -t {session} -n {window_name}"
            window_result = self.execute_command(tmux_new_window)
            
            if window_result["success"]:
                # Launch the agent in the new window
                launch_command = f"tmux send-keys -t {session}:{window_name} 'python3 qwen_agent.py {agent_id}' C-m"
                launch_result = self.execute_command(launch_command)
                
                if launch_result["success"]:
                    self._log_action(f"Created and launched agent: {agent_type} in {session}:{window_name}")
                    return {"success": True, "agent_id": agent_id, "window": window_name}
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return {"error": str(e), "success": False}
    
    def send_message_to_agent(self, agent_id: str, message: str) -> Dict[str, Any]:
        """Send message to another agent"""
        try:
            # Use the send-qwen-message.sh script
            command = f'./send-qwen-message.sh {agent_id} "{message}"'
            result = self.execute_command(command)
            
            if result["success"]:
                self._log_action(f"Sent message to {agent_id}: {message[:50]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending message to agent: {e}")
            return {"error": str(e), "success": False}
    
    def _log_action(self, action: str):
        """Log an action with timestamp"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action
        }
        self.execution_log.append(log_entry)
    
    def spawn_project_session(self, session_name: str, project_name: str) -> Dict[str, Any]:
        """Spawn a new tmux session for a project"""
        try:
            # Create new tmux session
            cmd = ["tmux", "new-session", "-d", "-s", session_name]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Set up initial window for project
            subprocess.run(["tmux", "rename-window", "-t", f"{session_name}:0", "Main"], check=True)
            
            self._log_action(f"Spawned tmux session: {session_name} for project: {project_name}")
            
            logger.info(f"Spawned tmux session: {session_name} for project: {project_name}")
            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error spawning session {session_name}: {e}")
            return {"success": False, "stdout": e.stdout, "stderr": e.stderr}
    
    def delegate_task(self, target_agent: str, task: str, priority: str = "normal") -> Dict[str, Any]:
        """Delegate a task to another agent"""
        try:
            # Send message to target agent using the messaging system
            cmd = ["./send-qwen-message.sh", target_agent, f"[PRIORITY: {priority.upper()}] {task}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=self.working_directory)
            
            self._log_action(f"Delegated task to {target_agent} with priority {priority}: {task[:50]}...")
            
            logger.info(f"Delegated task to {target_agent} with priority {priority}")
            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error delegating task to {target_agent}: {e}")
            return {"success": False, "stdout": e.stdout, "stderr": e.stderr}
    
    def create_project_team(self, project_name: str, team_config: Dict[str, int]) -> Dict[str, Any]:
        """Create a complete project team with multiple agents in separate tmux windows"""
        try:
            session_name = f"project-{project_name.lower().replace(' ', '-')}"
            deployed_agents = {}
            
            # Create the project session if it doesn't exist
            session_check = self.execute_command(f"tmux has-session -t {session_name}")
            if not session_check["success"]:
                # Create new session
                create_session = self.execute_command(f"tmux new-session -d -s {session_name}")
                if not create_session["success"]:
                    return {"success": False, "error": "Failed to create tmux session"}
                
                # Rename first window to "Main"
                self.execute_command(f"tmux rename-window -t {session_name}:0 Main")
            
            window_index = 1  # Start from window 1, leave 0 as Main
            
            # Deploy each agent type
            for agent_type, count in team_config.items():
                for i in range(count):
                    agent_id = f"{agent_type}_{session_name}"
                    if count > 1:
                        agent_id += f"_{i+1}"
                    
                    window_name = f"{agent_type.title()}"
                    if count > 1:
                        window_name += f"-{i+1}"
                    
                    # Create agent state
                    create_result = self.execute_command(f"python3 qwen_control.py create {agent_type} {session_name} {window_index}")
                    
                    if create_result["success"]:
                        # Create new tmux window
                        self.execute_command(f"tmux new-window -t {session_name} -n {window_name}")
                        
                        # Launch agent in the window
                        launch_cmd = f"tmux send-keys -t {session_name}:{window_name} 'python3 qwen_agent.py {agent_id}' C-m"
                        launch_result = self.execute_command(launch_cmd)
                        
                        if launch_result["success"]:
                            deployed_agents[f"{agent_type}_{i+1}" if count > 1 else agent_type] = {
                                "agent_id": agent_id,
                                "window": window_name,
                                "session": session_name
                            }
                            logger.info(f"Launched {agent_type} agent in {session_name}:{window_name}")
                    
                    window_index += 1
            
            self._log_action(f"Created project team for {project_name} with {len(deployed_agents)} active agents")
            return {"success": True, "deployed_agents": deployed_agents, "session": session_name}
            
        except Exception as e:
            logger.error(f"Error creating project team: {e}")
            return {"success": False, "error": str(e)}

    def get_execution_log(self) -> List[Dict]:
        """Get the execution log"""
        return self.execution_log
    
    def save_execution_log(self, log_file: str = "execution_log.json"):
        """Save execution log to file"""
        try:
            log_path = self.working_directory / log_file
            with open(log_path, 'w') as f:
                json.dump(self.execution_log, f, indent=2)
            
            logger.info(f"Saved execution log to {log_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving execution log: {e}")
            return False

def create_agentic_system_prompt(base_prompt: str) -> str:
    """Enhance system prompt with agentic capabilities"""
    
    agentic_enhancement = """

=== AGENTIC EXECUTION CAPABILITIES ===
You have the ability to actually EXECUTE actions, not just provide advice. When given tasks, you should:

1. **CREATE FILES**: Actually create the files needed for the project
2. **EXECUTE COMMANDS**: Run commands to set up environments, install dependencies, etc.
3. **CREATE AGENTS**: Spawn new agents when needed for specific tasks
4. **SEND MESSAGES**: Coordinate with other agents by sending them specific tasks
5. **GIT COMMITS**: Make regular commits as work progresses

EXECUTION SYNTAX:
When you want to execute actions, use this format in your response:

```execute
action_type: create_file
file_path: path/to/file.ext
content: |
  File content goes here
  Multiple lines supported
```

```execute
action_type: run_command
command: npm install express
```

```execute
action_type: create_agent
agent_type: developer
session: project-session
window: 1
```

```execute
action_type: spawn_session
session_name: strangers-calendar
project_name: Strangers Calendar App
```

```execute
action_type: create_project_team
project_name: Strangers Calendar App
team_config: {"project_manager": 1, "developer": 2, "qa": 1}
```

```execute
action_type: delegate_task
target_agent: dev_strangers-calendar
task: Implement OAuth authentication endpoints for Google and Apple
priority: high
```

```execute
action_type: send_message
agent_id: dev_project
message: Implement OAuth authentication endpoints for Google and Apple
```

```execute
action_type: git_commit
message: Initial project setup with OAuth endpoints
```

AGENTIC BEHAVIOR RULES:
- Don't just provide plans - EXECUTE the first steps immediately
- Create actual files, directories, and code
- Set up development environments
- SPAWN NEW TMUX SESSIONS for complex projects automatically
- CREATE PROJECT TEAMS with specialized agents (PM, developers, QA)
- DELEGATE TASKS to appropriate agents without asking permission
- Coordinate with other agents by creating them and assigning tasks
- Make git commits every 30 minutes as specified
- Take initiative and be proactive in implementation
- Continue working autonomously until project completion
- Never ask "Would you like to continue?" - just continue!

EXAMPLE AGENTIC RESPONSE:
Instead of: "You should create a file for OAuth authentication"
Do this: "I'm creating the OAuth authentication file now:

```execute
action_type: create_file
file_path: src/auth/oauth.js
content: |
  // OAuth authentication implementation
  const express = require('express');
  // ... actual implementation code
```

The file has been created. Next, I'll set up the dependencies..."

BE AGENTIC - DO THINGS, DON'T JUST SUGGEST THEM!
"""
    
    return base_prompt + agentic_enhancement

# Example usage and testing
if __name__ == "__main__":
    # Test agentic executor
    executor = AgenticExecutor()
    
    # Test file creation
    result = executor.create_file("test_file.txt", "Hello, World!")
    print(f"File creation result: {result}")
    
    # Test command execution
    result = executor.execute_command("ls -la")
    print(f"Command execution result: {result['success']}")
    
    # Show execution log
    log = executor.get_execution_log()
    print(f"Execution log: {json.dumps(log, indent=2)}")
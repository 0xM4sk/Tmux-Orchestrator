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
        """Create a new agent using qwen_control.py"""
        try:
            command = f"python3 qwen_control.py create {agent_type} {session} {window}"
            result = self.execute_command(command)
            
            if result["success"]:
                self._log_action(f"Created agent: {agent_type} in {session}:{window}")
            
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
- Coordinate with other agents by creating them and assigning tasks
- Make git commits every 30 minutes as specified
- Take initiative and be proactive in implementation

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
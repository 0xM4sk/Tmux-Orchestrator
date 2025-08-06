#!/usr/bin/env python3
"""
Execution Processor for Qwen Orchestrator
Processes and executes agentic commands from agent responses
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from agentic_capabilities import AgenticExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutionProcessor:
    """
    Processes agent responses and executes any agentic commands found
    """
    
    def __init__(self, working_directory: str = ".", agent_id: str = None, project_name: str = None):
        self.working_directory = working_directory
        self.agent_id = agent_id
        self.project_name = project_name
        
        # Initialize sandboxed executor
        self.executor = AgenticExecutor(working_directory, agent_id, project_name)
        
        self.execution_pattern = re.compile(
            r'```execute\s*\n(.*?)\n```', 
            re.DOTALL | re.MULTILINE
        )
        
        logger.info(f"Initialized ExecutionProcessor for agent {agent_id} with project {project_name}")
    
    def _discover_agents(self) -> List[Dict[str, Any]]:
        """Discover available agents using qwen_control.py"""
        try:
            import subprocess
            import json
            
            # Run qwen_control.py list command to get available agents
            result = subprocess.run(
                ["python3", "qwen_control.py", "list"],
                capture_output=True,
                text=True,
                cwd=self.executor.working_directory
            )
            
            if result.returncode == 0:
                # Parse the output to extract agent information
                # This is a simplified parser - in a real implementation,
                # we might want to use the JSON output option
                lines = result.stdout.strip().split('\n')
                agents = []
                
                # Look for lines that contain agent information
                for line in lines:
                    if ' - ' in line and '(' in line and ')' in line:
                        # This looks like an agent line
                        # Extract agent ID (first part before space)
                        parts = line.split()
                        if parts:
                            agent_id = parts[0]
                            agents.append({"agent_id": agent_id})
                
                return agents
            else:
                logger.error(f"Error discovering agents: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error discovering agents: {e}")
            return []
    
    def process_response(self, response: str, agent_id: str) -> Dict[str, Any]:
        """
        Process an agent response and execute any agentic commands
        Returns execution results and modified response
        """
        execution_results = []
        modified_response = response
        
        # Find all execution blocks
        matches = self.execution_pattern.findall(response)
        
        for match in matches:
            try:
                # Parse the execution block
                execution_data = self._parse_execution_block(match)
                
                if execution_data:
                    # Execute the action
                    result = self._execute_action(execution_data, agent_id)
                    execution_results.append(result)
                    
                    # Replace the execution block with result summary
                    result_summary = self._create_result_summary(result)
                    modified_response = modified_response.replace(
                        f"```execute\n{match}\n```", 
                        result_summary
                    )
                    
            except Exception as e:
                logger.error(f"Error processing execution block: {e}")
                error_result = {
                    "action_type": "error",
                    "error": str(e),
                    "success": False
                }
                execution_results.append(error_result)
        
        return {
            "modified_response": modified_response,
            "execution_results": execution_results,
            "executed_actions": len(execution_results)
        }
    
    def _parse_execution_block(self, block: str) -> Optional[Dict[str, Any]]:
        """Parse an execution block into structured data"""
        try:
            lines = block.strip().split('\n')
            execution_data = {}
            current_key = None
            current_value = []
            
            for line in lines:
                if ':' in line and not line.startswith(' '):
                    # Save previous key-value pair
                    if current_key:
                        if current_key == 'content' and len(current_value) > 1:
                            # Handle multi-line content
                            execution_data[current_key] = '\n'.join(current_value)
                        else:
                            execution_data[current_key] = current_value[0] if current_value else ""
                    
                    # Start new key-value pair
                    key, value = line.split(':', 1)
                    current_key = key.strip()
                    current_value = [value.strip()] if value.strip() else []
                    
                elif current_key and (line.startswith('  ') or line.startswith('\t') or not line.strip()):
                    # Continuation of current value
                    current_value.append(line.lstrip())
                elif current_key:
                    # Non-indented line, treat as continuation
                    current_value.append(line)
            
            # Save the last key-value pair
            if current_key:
                if current_key == 'content' and len(current_value) > 1:
                    execution_data[current_key] = '\n'.join(current_value)
                else:
                    execution_data[current_key] = current_value[0] if current_value else ""
            
            return execution_data if execution_data else None
            
        except Exception as e:
            logger.error(f"Error parsing execution block: {e}")
            return None
    
    def _execute_action(self, execution_data: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute a specific action based on execution data"""
        action_type = execution_data.get('action_type', '').lower()
        
        try:
            if action_type == 'create_file':
                file_path = execution_data.get('file_path', '')
                content = execution_data.get('content', '')
                project_name = execution_data.get('project_name', '')
                
                # If file_path is empty or equals project_name, it's a directory creation request
                if not file_path or file_path == project_name:
                    success = self.executor.create_project_directory(project_name)
                    return {
                        "action_type": "create_directory",
                        "dir_path": f"projects/{project_name}",
                        "project_name": project_name,
                        "success": success,
                        "agent_id": agent_id
                    }
                else:
                    success = self.executor.create_file(file_path, content, project_name)
                    return {
                        "action_type": "create_file",
                        "file_path": file_path,
                        "project_name": project_name,
                        "success": success,
                        "agent_id": agent_id
                    }
                
            elif action_type == 'run_command':
                command = execution_data.get('command', '')
                result = self.executor.execute_command(command)
                
                return {
                    "action_type": "run_command",
                    "command": command,
                    "success": result["success"],
                    "output": result.get("stdout", ""),
                    "error": result.get("stderr", ""),
                    "agent_id": agent_id
                }
                
            elif action_type == 'create_agent':
                agent_type = execution_data.get('agent_type', '')
                session = execution_data.get('session', '')
                window = int(execution_data.get('window', 0))
                
                result = self.executor.create_agent(agent_type, session, window)
                return {
                    "action_type": "create_agent",
                    "agent_type": agent_type,
                    "session": session,
                    "window": window,
                    "success": result["success"],
                    "output": result.get("stdout", ""),
                    "agent_id": agent_id
                }
                
            elif action_type == 'spawn_session':
                session_name = execution_data.get('session_name', '')
                project_name = execution_data.get('project_name', '')
                
                result = self.executor.spawn_project_session(session_name, project_name)
                return {
                    "action_type": "spawn_session",
                    "session_name": session_name,
                    "project_name": project_name,
                    "success": result["success"],
                    "output": result.get("stdout", ""),
                    "agent_id": agent_id
                }
                
            elif action_type == 'delegate_task':
                target_agent = execution_data.get('target_agent', '')
                task = execution_data.get('task', '')
                priority = execution_data.get('priority', 'normal')
                
                result = self.executor.delegate_task(target_agent, task, priority)
                return {
                    "action_type": "delegate_task",
                    "target_agent": target_agent,
                    "task": task,
                    "priority": priority,
                    "success": result["success"],
                    "agent_id": agent_id
                }
                
            elif action_type == 'create_project_team':
                project_name = execution_data.get('project_name', '')
                team_config_raw = execution_data.get('team_config', '{}')
                
                # Parse team_config if it's a string
                if isinstance(team_config_raw, str):
                    try:
                        import json
                        team_config = json.loads(team_config_raw)
                    except json.JSONDecodeError:
                        # Fallback to default config
                        team_config = {"project_manager": 1, "developer": 1, "qa": 1}
                else:
                    team_config = team_config_raw
                
                result = self.executor.create_project_team(project_name, team_config)
                return {
                    "action_type": "create_project_team",
                    "project_name": project_name,
                    "team_config": team_config,
                    "success": result["success"],
                    "deployed_agents": result.get("deployed_agents", {}),
                    "agent_id": agent_id
                }
                
            elif action_type == 'send_message':
                target_agent = execution_data.get('agent_id', '')
                message = execution_data.get('message', '')
                project_name = execution_data.get('project_name', '')
                
                # Validate target agent
                if not target_agent or target_agent == '[discovered_agent_id]':
                    # Discover available agents
                    available_agents = self._discover_agents()
                    if available_agents:
                        # Suggest the first available agent as an example
                        suggested_agent = available_agents[0]['agent_id']
                        error_msg = f"Invalid agent ID. Available agents: {[a['agent_id'] for a in available_agents]}. Example: {suggested_agent}"
                    else:
                        error_msg = "No agents found. Use 'python3 qwen_control.py list' to see available agents."
                    return {
                        "action_type": "send_message",
                        "error": error_msg,
                        "success": False,
                        "agent_id": agent_id
                    }
                
                result = self.executor.send_message_to_agent(target_agent, message, project_name)
                return {
                    "action_type": "send_message",
                    "target_agent": target_agent,
                    "message": message,
                    "project_name": project_name,
                    "success": result["success"],
                    "agent_id": agent_id
                }
                
            elif action_type == 'git_commit':
                message = execution_data.get('message', '')
                project_name = execution_data.get('project_name', '')
                result = self.executor.git_commit(message, project_name)
                
                return {
                    "action_type": "git_commit",
                    "message": message,
                    "project_name": project_name,
                    "success": result["success"],
                    "output": result.get("stdout", ""),
                    "agent_id": agent_id
                }
                
            elif action_type == 'create_directory':
                dir_path = execution_data.get('dir_path', '')
                success = self.executor.create_directory(dir_path)
                
                return {
                    "action_type": "create_directory",
                    "dir_path": dir_path,
                    "success": success,
                    "agent_id": agent_id
                }
                
            else:
                return {
                    "action_type": "unknown",
                    "error": f"Unknown action type: {action_type}",
                    "success": False,
                    "agent_id": agent_id
                }
                
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
            # Request confirmation for failed execution
            confirmation_id = self.request_execution_confirmation(agent_id, f"execute_{action_type}_failed")
            return {
                "action_type": action_type,
                "error": str(e),
                "success": False,
                "agent_id": agent_id,
                "confirmation_id": confirmation_id
            }

    def _create_result_summary(self, result: Dict[str, Any]) -> str:
        """Create a summary of execution results"""
        action_type = result.get('action_type', 'unknown')
        success = result.get('success', False)
        
        if success:
            if action_type == 'create_file':
                return f"✅ **EXECUTED**: Created file `{result.get('file_path', '')}`"
            elif action_type == 'run_command':
                return f"✅ **EXECUTED**: Ran command `{result.get('command', '')}`"
            elif action_type == 'create_agent':
                return f"✅ **EXECUTED**: Created {result.get('agent_type', '')} agent in {result.get('session', '')}:{result.get('window', '')}"
            elif action_type == 'spawn_session':
                return f"✅ **EXECUTED**: Spawned tmux session `{result.get('session_name', '')}` for project `{result.get('project_name', '')}`"
            elif action_type == 'delegate_task':
                return f"✅ **EXECUTED**: Delegated task to {result.get('target_agent', '')} (priority: {result.get('priority', 'normal')})"
            elif action_type == 'create_project_team':
                agents = result.get('deployed_agents', {})
                return f"✅ **EXECUTED**: Created project team for `{result.get('project_name', '')}` with {len(agents)} agents"
            elif action_type == 'send_message':
                if 'error' in result:
                    return f"❌ **EXECUTION FAILED**: {action_type} - {result['error']}"
                project_info = f" for project `{result.get('project_name', '')}`" if result.get('project_name') else ""
                return f"✅ **EXECUTED**: Sent message to {result.get('target_agent', '')}{project_info}"
            elif action_type == 'git_commit':
                project_info = f" for project `{result.get('project_name', '')}`" if result.get('project_name') else ""
                return f"✅ **EXECUTED**: Git commit{project_info}: {result.get('message', '')}"
            elif action_type == 'create_directory':
                return f"✅ **EXECUTED**: Created directory `{result.get('dir_path', '')}`"
            else:
                return f"✅ **EXECUTED**: {action_type}"
        else:
            error = result.get('error', 'Unknown error')
            return f"❌ **EXECUTION FAILED**: {action_type} - {error}"
    
    def get_execution_log(self) -> List[Dict]:
        """Get the execution log from the executor"""
        return self.executor.get_execution_log()
    
    def get_execution_gaps(self) -> List[Dict]:
        """Get identified execution gaps"""
        return self.executor.get_execution_gaps()
    
    def get_execution_summary(self) -> Dict:
        """Get execution summary with gaps information"""
        return self.executor.get_execution_summary()
    
    def request_execution_confirmation(self, agent_id: str, action: str) -> str:
        """Request confirmation for an execution"""
        return self.executor.request_execution_confirmation(agent_id, action)
    
    def confirm_execution(self, confirmation_id: str, confirmed_by: str = "system") -> bool:
        """Confirm an execution"""
        return self.executor.confirm_execution(confirmation_id, confirmed_by)
    
    def get_pending_confirmations(self, agent_id: str = None) -> List[Dict]:
        """Get pending confirmations"""
        return self.executor.get_pending_confirmations(agent_id)
    
    def save_execution_log(self, log_file: str = "execution_log.json") -> bool:
        """Save execution log to file"""
        return self.executor.save_execution_log(log_file)
    
    def get_error_summary(self) -> Dict:
        """Get error summary from executor"""
        return self.executor.get_error_summary()
    
    def get_errors_by_agent(self, agent_id: str) -> List[Dict]:
        """Get errors for a specific agent"""
        return self.executor.get_errors_by_agent(agent_id)
    
    def get_errors_by_action(self, action: str) -> List[Dict]:
        """Get errors for a specific action"""
        return self.executor.get_errors_by_action(action)

# Example usage and testing
if __name__ == "__main__":
    # Test execution processor
    processor = ExecutionProcessor()
    
    # Test response with execution blocks
    test_response = """
I'll create the OAuth authentication file now:

```execute
action_type: create_file
file_path: src/auth/oauth.js
content: |
  // OAuth authentication implementation
  const express = require('express');
  const passport = require('passport');
  
  module.exports = { setupOAuth };
```

Now I'll install the required dependencies:

```execute
action_type: run_command
command: npm install express passport
```

The setup is complete!
"""
    
    result = processor.process_response(test_response, "test_agent")
    print("Execution Results:")
    print(json.dumps(result, indent=2))
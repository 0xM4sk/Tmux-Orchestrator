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
    
    def __init__(self, working_directory: str = "."):
        self.executor = AgenticExecutor(working_directory)
        self.execution_pattern = re.compile(
            r'```execute\s*\n(.*?)\n```', 
            re.DOTALL | re.MULTILINE
        )
    
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
                
                success = self.executor.create_file(file_path, content)
                return {
                    "action_type": "create_file",
                    "file_path": file_path,
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
                
                result = self.executor.send_message_to_agent(target_agent, message)
                return {
                    "action_type": "send_message",
                    "target_agent": target_agent,
                    "message": message,
                    "success": result["success"],
                    "agent_id": agent_id
                }
                
            elif action_type == 'git_commit':
                message = execution_data.get('message', '')
                result = self.executor.git_commit(message)
                
                return {
                    "action_type": "git_commit",
                    "message": message,
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
            return {
                "action_type": action_type,
                "error": str(e),
                "success": False,
                "agent_id": agent_id
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
                return f"✅ **EXECUTED**: Sent message to {result.get('target_agent', '')}"
            elif action_type == 'git_commit':
                return f"✅ **EXECUTED**: Git commit: {result.get('message', '')}"
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
    
    def save_execution_log(self, log_file: str = "execution_log.json") -> bool:
        """Save execution log to file"""
        return self.executor.save_execution_log(log_file)

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
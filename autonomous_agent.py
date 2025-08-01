#!/usr/bin/env python3
"""
Autonomous Agent Enhancement for Qwen Orchestrator
Adds file reading, command execution, and autonomous decision-making capabilities
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from qwen_client import QwenClient, create_system_message, create_user_message
from agent_state import AgentStateManager, AgentType
from conversation_manager import ConversationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutonomousAgent:
    """
    Enhanced agent with autonomous capabilities:
    - File reading and writing
    - Command execution
    - Project analysis
    - Autonomous decision making
    """
    
    def __init__(self, agent_id: str, working_directory: str = "."):
        self.agent_id = agent_id
        self.working_directory = Path(working_directory).resolve()
        
        # Initialize components
        self.qwen_client = QwenClient()
        self.state_manager = AgentStateManager()
        self.conversation_manager = ConversationManager(self.state_manager, self.qwen_client)
        
        # Get agent state
        self.agent_state = self.state_manager.get_agent(agent_id)
        if not self.agent_state:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Enhanced system prompt with autonomous capabilities
        self.enhanced_system_prompt = self._create_enhanced_system_prompt()
        
        logger.info(f"Initialized autonomous agent {agent_id} in {working_directory}")
    
    def _create_enhanced_system_prompt(self) -> str:
        """Create enhanced system prompt with autonomous capabilities"""
        base_prompt = self.agent_state.role_config.system_prompt
        
        autonomous_capabilities = f"""

AUTONOMOUS CAPABILITIES:
You have the following autonomous capabilities to work independently:

1. FILE OPERATIONS:
   - Read files: When asked to read a file, you can access its contents directly
   - List directory contents: You can see what files are available
   - Analyze project structure: You can understand codebases by examining files

2. PROJECT ANALYSIS:
   - When asked to read project_spec.md or similar files, you should immediately analyze the requirements
   - Break down complex projects into actionable tasks
   - Identify what needs to be built and in what order

3. AUTONOMOUS DECISION MAKING:
   - Don't ask users for information you can discover yourself
   - Read files, analyze code, and make informed decisions
   - Propose concrete next steps based on your analysis

4. WORKING DIRECTORY: {self.working_directory}
   - All file operations are relative to this directory
   - You can access any file in this directory or its subdirectories

AUTONOMOUS BEHAVIOR RULES:
- When asked to read a file, immediately provide its contents and analysis
- When given a project specification, break it down into concrete tasks
- Always propose next steps rather than asking for more information
- Be proactive and take initiative in problem-solving
- Use your file reading capabilities to gather information independently

CURRENT CONTEXT:
- Agent ID: {self.agent_id}
- Agent Type: {self.agent_state.agent_type.value}
- Working Directory: {self.working_directory}
- Current Project: {self.agent_state.current_context.active_project or 'Not set'}
- Current Task: {self.agent_state.current_context.current_task or 'Not set'}
"""
        
        return base_prompt + autonomous_capabilities
    
    def read_file(self, file_path: str) -> str:
        """Read a file and return its contents"""
        try:
            full_path = self.working_directory / file_path
            if not full_path.exists():
                return f"File {file_path} not found in {self.working_directory}"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Read file {file_path} ({len(content)} characters)")
            return content
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return f"Error reading file {file_path}: {str(e)}"
    
    def list_files(self, directory: str = ".") -> List[str]:
        """List files in a directory"""
        try:
            dir_path = self.working_directory / directory
            if not dir_path.exists():
                return [f"Directory {directory} not found"]
            
            files = []
            for item in dir_path.iterdir():
                if item.is_file():
                    files.append(f"📄 {item.name}")
                elif item.is_dir():
                    files.append(f"📁 {item.name}/")
            
            return sorted(files)
            
        except Exception as e:
            logger.error(f"Error listing directory {directory}: {e}")
            return [f"Error listing directory: {str(e)}"]
    
    def execute_command(self, command: str) -> str:
        """Execute a shell command and return output"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=self.working_directory,
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            
            logger.info(f"Executed command: {command}")
            return output
            
        except subprocess.TimeoutExpired:
            return f"Command timed out: {command}"
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return f"Error executing command: {str(e)}"
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze the current project structure"""
        analysis = {
            "working_directory": str(self.working_directory),
            "files": self.list_files(),
            "project_type": "unknown",
            "key_files": [],
            "technologies": []
        }
        
        # Check for common project files
        key_files_to_check = [
            "package.json", "requirements.txt", "Gemfile", "go.mod", 
            "Cargo.toml", "pom.xml", "build.gradle", "project_spec.md",
            "README.md", "docker-compose.yml", "Dockerfile"
        ]
        
        for file_name in key_files_to_check:
            if (self.working_directory / file_name).exists():
                analysis["key_files"].append(file_name)
        
        # Determine project type
        if "package.json" in analysis["key_files"]:
            analysis["project_type"] = "Node.js/JavaScript"
            analysis["technologies"].append("JavaScript/TypeScript")
        elif "requirements.txt" in analysis["key_files"]:
            analysis["project_type"] = "Python"
            analysis["technologies"].append("Python")
        elif "Gemfile" in analysis["key_files"]:
            analysis["project_type"] = "Ruby"
            analysis["technologies"].append("Ruby")
        elif "go.mod" in analysis["key_files"]:
            analysis["project_type"] = "Go"
            analysis["technologies"].append("Go")
        
        return analysis
    
    def process_autonomous_message(self, message: str) -> str:
        """Process a message with autonomous capabilities"""
        try:
            # Check if the message involves file operations
            enhanced_message = self._enhance_message_with_context(message)
            
            # Create enhanced system message
            system_msg = create_system_message(self.enhanced_system_prompt)
            user_msg = create_user_message(enhanced_message)
            
            # Get response from Qwen
            messages = [system_msg, user_msg]
            response = self.qwen_client.chat_completion(messages)
            
            # Add to conversation history
            self.conversation_manager.add_message(self.agent_id, user_msg)
            
            # Create assistant message with response
            from qwen_client import create_assistant_message
            assistant_msg = create_assistant_message(response)
            self.conversation_manager.add_message(self.agent_id, assistant_msg)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing autonomous message: {e}")
            return f"Error processing message: {str(e)}"
    
    def _enhance_message_with_context(self, message: str) -> str:
        """Enhance message with file contents and project context"""
        enhanced_message = message
        
        # Check if message mentions specific files
        files_to_read = []
        
        # Common file patterns to auto-read
        file_patterns = [
            "project_spec.md", "README.md", "package.json", 
            "requirements.txt", "spec.md", "specification.md"
        ]
        
        for pattern in file_patterns:
            if pattern.lower() in message.lower():
                files_to_read.append(pattern)
        
        # Auto-read project_spec.md if it exists and message mentions reading it
        if "project_spec" in message.lower() or "spec" in message.lower():
            if (self.working_directory / "project_spec.md").exists():
                files_to_read.append("project_spec.md")
        
        # Add file contents to message
        if files_to_read:
            enhanced_message += "\n\nAUTOMATIC FILE CONTEXT:\n"
            
            for file_name in files_to_read:
                content = self.read_file(file_name)
                if not content.startswith("File") and not content.startswith("Error"):
                    enhanced_message += f"\n--- Contents of {file_name} ---\n{content}\n"
        
        # Add project structure context
        if "project" in message.lower() or "structure" in message.lower():
            project_analysis = self.analyze_project_structure()
            enhanced_message += f"\n\nPROJECT STRUCTURE CONTEXT:\n{json.dumps(project_analysis, indent=2)}\n"
        
        return enhanced_message
    
    def close(self):
        """Close connections"""
        self.qwen_client.close()

# Enhanced message sending function
def send_autonomous_message(agent_id: str, message: str, working_directory: str = ".") -> str:
    """Send message to autonomous agent with enhanced capabilities"""
    try:
        agent = AutonomousAgent(agent_id, working_directory)
        response = agent.process_autonomous_message(message)
        agent.close()
        return response
        
    except Exception as e:
        logger.error(f"Error in autonomous message sending: {e}")
        return f"Error: {str(e)}"

# Example usage and testing
if __name__ == "__main__":
    # Test autonomous agent
    try:
        # This would need an actual agent to exist
        agent = AutonomousAgent("test_agent", ".")
        
        # Test file reading
        files = agent.list_files()
        print("Files in directory:", files)
        
        # Test project analysis
        analysis = agent.analyze_project_structure()
        print("Project analysis:", json.dumps(analysis, indent=2))
        
        agent.close()
        
    except Exception as e:
        print(f"Test error: {e}")
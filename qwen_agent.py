#!/usr/bin/env python3
"""
Qwen Agent Runtime for Tmux Orchestrator
Replaces Claude CLI sessions with persistent API-based agents
Enhanced with autonomous capabilities
"""

import sys
import os
import argparse
import signal
import time
import threading
from pathlib import Path
from typing import Optional
import logging

from qwen_client import QwenClient, QwenConfig
from agent_state import AgentStateManager, AgentType, AgentStatus
from conversation_manager import ConversationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QwenAgent:
    """
    Main agent runtime that runs in tmux windows
    Provides interactive interface and handles agent lifecycle
    """
    
    def __init__(self, agent_id: str, config_path: Optional[str] = None):
        self.agent_id = agent_id
        self.running = False
        self.shutdown_event = threading.Event()
        
        # Initialize components
        self.qwen_config = QwenConfig.load_from_file(config_path) if config_path else QwenConfig()
        self.qwen_client = QwenClient(self.qwen_config)
        self.state_manager = AgentStateManager()
        self.conversation_manager = ConversationManager(self.state_manager, self.qwen_client)
        
        # Get agent state
        self.agent_state = self.state_manager.get_agent(agent_id)
        if not self.agent_state:
            raise ValueError(f"Agent {agent_id} not found. Create it first with create_agent.py")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        
        logger.info(f"Initialized agent {agent_id} ({self.agent_state.agent_type.value})")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
    
    def _heartbeat_loop(self):
        """Periodic heartbeat to update agent status"""
        while not self.shutdown_event.is_set():
            try:
                # Update last active timestamp
                self.agent_state.status = AgentStatus.ACTIVE
                self.state_manager.update_agent(self.agent_state)
                
                # Sleep for 30 seconds
                if self.shutdown_event.wait(30):
                    break
                    
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                time.sleep(5)
    
    def start(self):
        """Start the agent runtime"""
        self.running = True
        self.heartbeat_thread.start()
        
        # Display startup information
        self._display_startup_info()
        
        # Main interaction loop
        try:
            self._interaction_loop()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.shutdown()
    
    def _display_startup_info(self):
        """Display agent startup information"""
        print(f"\n{'='*60}")
        print(f"🤖 Qwen Agent Runtime - {self.agent_state.agent_type.value.title()}")
        print(f"{'='*60}")
        print(f"Agent ID: {self.agent_id}")
        print(f"Session: {self.agent_state.session_name}")
        print(f"Window: {self.agent_state.window_index}")
        print(f"Model: {self.qwen_config.model}")
        print(f"Status: {self.agent_state.status.value}")
        print(f"Created: {self.agent_state.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Messages: {self.agent_state.conversation_state.message_count}")
        
        if self.agent_state.current_context.active_project:
            print(f"Project: {self.agent_state.current_context.active_project}")
        if self.agent_state.current_context.current_task:
            print(f"Task: {self.agent_state.current_context.current_task}")
        
        print(f"\n📝 Role: {self.agent_state.agent_type.value.title()}")
        print(f"System Prompt Preview: {self.agent_state.role_config.system_prompt[:200]}...")
        
        print(f"\n{'='*60}")
        print("💬 Ready for interaction! Type your messages below.")
        print("Commands: /help, /status, /context, /history, /quit")
        print(f"{'='*60}\n")
    
    def _interaction_loop(self):
        """Main interaction loop"""
        while self.running and not self.shutdown_event.is_set():
            try:
                # Get user input
                user_input = input(f"\n[{self.agent_state.agent_type.value}] > ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue
                
                # Process regular message
                self._process_message(user_input)
                
            except EOFError:
                # Handle EOF (Ctrl+D)
                logger.info("Received EOF, shutting down")
                break
            except Exception as e:
                logger.error(f"Error in interaction loop: {e}")
                print(f"❌ Error: {e}")
    
    def _handle_command(self, command: str):
        """Handle special commands"""
        cmd_parts = command[1:].split()
        cmd = cmd_parts[0].lower() if cmd_parts else ""
        
        if cmd == "help":
            self._show_help()
        elif cmd == "status":
            self._show_status()
        elif cmd == "context":
            self._show_context()
        elif cmd == "history":
            limit = int(cmd_parts[1]) if len(cmd_parts) > 1 and cmd_parts[1].isdigit() else 10
            self._show_history(limit)
        elif cmd == "quit" or cmd == "exit":
            self.shutdown()
        elif cmd == "clear":
            os.system('clear' if os.name == 'posix' else 'cls')
        elif cmd == "project":
            if len(cmd_parts) > 1:
                self._set_project(" ".join(cmd_parts[1:]))
            else:
                print(f"Current project: {self.agent_state.current_context.active_project or 'None'}")
        elif cmd == "task":
            if len(cmd_parts) > 1:
                self._set_task(" ".join(cmd_parts[1:]))
            else:
                print(f"Current task: {self.agent_state.current_context.current_task or 'None'}")
        elif cmd == "auto-manage" or cmd == "automate":
            project_name = " ".join(cmd_parts[1:]) if len(cmd_parts) > 1 else "Strangers Calendar App"
            self._auto_manage_project(project_name)
        else:
            print(f"❌ Unknown command: {command}")
            self._show_help()
    
    def _show_help(self):
        """Show available commands"""
        print("\n📚 Available Commands:")
        print("  /help          - Show this help message")
        print("  /status        - Show agent status and metrics")
        print("  /context       - Show current context and relationships")
        print("  /history [N]   - Show last N messages (default: 10)")
        print("  /project <name> - Set current project")
        print("  /task <desc>   - Set current task")
        print("  /clear         - Clear screen")
        print("  /quit          - Shutdown agent")
        print("  /auto-manage [project_name] - Auto-manage project from specification")
        print()
    
    def _show_status(self):
        """Show agent status"""
        agent = self.state_manager.get_agent(self.agent_id)  # Get fresh state
        if not agent:
            print("❌ Agent state not found")
            return
        
        print(f"\n📊 Agent Status - {agent.agent_id}")
        print(f"{'─'*50}")
        print(f"Status: {agent.status.value}")
        print(f"Type: {agent.agent_type.value}")
        print(f"Session: {agent.session_name}:{agent.window_index}")
        print(f"Created: {agent.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last Active: {agent.last_active.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n💬 Conversation:")
        print(f"Messages: {agent.conversation_state.message_count}")
        print(f"Total Tokens: {agent.conversation_state.total_tokens_used:,}")
        print(f"Context Usage: {agent.conversation_state.context_window_usage:.1%}")
        print(f"Needs Summary: {'Yes' if agent.conversation_state.needs_summarization else 'No'}")
        
        print(f"\n⚡ Performance:")
        print(f"Tasks Completed: {agent.performance_metrics.tasks_completed}")
        print(f"Avg Response Time: {agent.performance_metrics.average_response_time:.2f}s")
        print(f"Success Rate: {agent.performance_metrics.success_rate:.1%}")
        if agent.performance_metrics.last_error:
            print(f"Last Error: {agent.performance_metrics.last_error}")
        
        print()
    
    def _show_context(self):
        """Show current context and relationships"""
        agent = self.agent_state
        
        print(f"\n🎯 Current Context - {agent.agent_id}")
        print(f"{'─'*50}")
        print(f"Project: {agent.current_context.active_project or 'None'}")
        print(f"Task: {agent.current_context.current_task or 'None'}")
        print(f"Priority: {agent.current_context.priority_level}")
        if agent.current_context.deadline:
            print(f"Deadline: {agent.current_context.deadline.strftime('%Y-%m-%d %H:%M')}")
        if agent.current_context.notes:
            print(f"Notes: {agent.current_context.notes}")
        
        print(f"\n👥 Relationships:")
        if agent.relationships.reports_to:
            print(f"Reports to: {agent.relationships.reports_to}")
        if agent.relationships.manages:
            print(f"Manages: {', '.join(agent.relationships.manages)}")
        if agent.relationships.collaborates_with:
            print(f"Collaborates with: {', '.join(agent.relationships.collaborates_with)}")
        
        print()
    
    def _show_history(self, limit: int):
        """Show conversation history"""
        messages = self.conversation_manager.get_conversation_history(self.agent_id, limit)
        
        if not messages:
            print("📝 No conversation history found")
            return
        
        print(f"\n📝 Last {len(messages)} Messages:")
        print(f"{'─'*60}")
        
        for msg in messages[-limit:]:
            timestamp = msg.timestamp.strftime('%H:%M:%S')
            role_icon = {"user": "👤", "assistant": "🤖", "system": "⚙️"}.get(msg.role, "❓")
            
            # Truncate long messages
            content = msg.content
            if len(content) > 200:
                content = content[:197] + "..."
            
            print(f"{timestamp} {role_icon} {msg.role}: {content}")
        
        print()
    
    def _set_project(self, project_name: str):
        """Set current project"""
        self.agent_state.current_context.active_project = project_name
        self.state_manager.update_agent(self.agent_state)
        print(f"✅ Set project to: {project_name}")
    
    def _set_task(self, task_description: str):
        """Set current task"""
        self.agent_state.current_context.current_task = task_description
        self.state_manager.update_agent(self.agent_state)
        print(f"✅ Set task to: {task_description}")
    
    def _process_message(self, message: str):
        """Process a regular message with autonomous capabilities"""
        try:
            print(f"\n🤖 Processing message: '{message[:50]}{'...' if len(message) > 50 else ''}")
            
            # Update agent status
            self.agent_state.status = AgentStatus.BUSY
            self.state_manager.update_agent(self.agent_state)
            
            # Enhance message with autonomous context
            enhanced_message = self._enhance_message_with_autonomous_context(message)
            
            # Send enhanced message and get response
            print("📤 Sending message to Qwen model...")
            response = self.conversation_manager.send_message_to_agent(
                self.agent_id,
                enhanced_message,
                sender="interactive"
            )
            
            if response:
                print(f"\n🤖 {self.agent_state.agent_type.value.title()} Response:")
                print(f"{'─'*60}")
                print(response)
                print(f"{'─'*60}")
                
                # Log what the agent is doing
                self._log_agent_activity(message, response)
            else:
                print("❌ Failed to get response from agent")
            
            # Update agent status back to active
            self.agent_state.status = AgentStatus.ACTIVE
            self.state_manager.update_agent(self.agent_state)
            print(f"✅ Agent status updated to: {self.agent_state.status.value}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            print(f"❌ Error processing message: {e}")
            
            # Update error status
            self.agent_state.status = AgentStatus.ERROR
            self.agent_state.performance_metrics.last_error = str(e)
            self.state_manager.update_agent(self.agent_state)
            print(f"⚠️  Agent status updated to: {self.agent_state.status.value}")
    
    def _log_agent_activity(self, input_message: str, response: str):
        """Log agent activity for monitoring purposes"""
        try:
            # Determine what the agent is doing based on the response
            activity = "Processing request"
            
            if "implement" in response.lower() or "code" in response.lower():
                activity = "Implementing solution"
            elif "test" in response.lower() or "qa" in response.lower():
                activity = "Testing/QA activities"
            elif "plan" in response.lower() or "strategy" in response.lower():
                activity = "Planning/Strategy"
            elif "review" in response.lower() or "analyze" in response.lower():
                activity = "Review/Analysis"
            elif "document" in response.lower() or "spec" in response.lower():
                activity = "Documentation"
            elif "research" in response.lower():
                activity = "Research"
                
            print(f"📋 Agent Activity: {activity}")
            
            # Update agent context if needed
            if self.agent_state.current_context.current_task is None:
                # Try to extract task from response
                if "task" in response.lower():
                    # Simple extraction - in a real implementation, you might want more sophisticated parsing
                    lines = response.split('\n')
                    for line in lines:
                        if "task" in line.lower() and ":" in line:
                            task_desc = line.split(":", 1)[1].strip()
                            self._set_task(task_desc[:100] + "..." if len(task_desc) > 100 else task_desc)
                            break
        except Exception as e:
            logger.error(f"Error logging agent activity: {e}")
    
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
        
        # Auto-read project_spec.md if message mentions building, specs, or project
        if any(word in message.lower() for word in ["spec", "specification", "project_spec", "build", "building", "app", "project"]):
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
        if any(word in message.lower() for word in ["project", "structure", "analyze", "understand", "build", "app"]):
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
- For project coordination, create detailed implementation plans with specific tasks

Respond with specific, actionable guidance based on the context provided above.
"""
        
        return enhanced_message
    
    def _auto_expand_project_spec(self, project_name: str = "Strangers Calendar App") -> list:
        """Automatically expand project specification into task list"""
        try:
            # Read the project specification
            spec_path = Path("project_spec.md")
            if not spec_path.exists():
                logger.warning("Project specification not found")
                return []
            
            with open(spec_path, 'r') as f:
                spec_content = f.read()
            
            # Generate system prompt for task expansion
            task_expansion_prompt = f"""
            You are an AI Project Manager. Your task is to automatically expand the following project specification into a detailed task list.
            
            PROJECT SPECIFICATION:
            {spec_content}
            
            INSTRUCTIONS:
            1. Break down the specification into specific, actionable tasks
            2. Prioritize tasks logically (foundational work first)
            3. Assign tasks to appropriate agent types (developer, qa, project_manager)
            4. Include implementation, testing, and documentation tasks
            5. Consider the constraints and deliverables mentioned
            6. Format each task as: "[AGENT_TYPE] Task description"
            
            Example format:
            [developer] Implement OAuth authentication endpoints for Google and Apple
            [developer] Create database schema for temporary calendars
            [qa] Write tests for OAuth authentication
            [developer] Implement phone number and WhatsApp integration
            [developer] Create UI for availability window input
            [developer] Implement availability intersection algorithm
            [developer] Create automatic expiration and cleanup functionality
            [qa] Write tests for calendar creation and sharing
            [qa] Write tests for availability intersection algorithm
            [developer] Create documentation for API endpoints
            [project_manager] Review and update project status
            
            Provide ONLY the task list, one task per line, in priority order.
            """
            
            # Get tasks from Qwen
            tasks_response = self.qwen_client.chat_completion(
                messages=[{"role": "user", "content": task_expansion_prompt}],
                stream=False
            )
            
            if tasks_response and "choices" in tasks_response:
                tasks_content = tasks_response["choices"][0]["message"]["content"]
                # Parse tasks from response
                tasks = [task.strip() for task in tasks_content.split('\n') if task.strip() and task.startswith('[')]
                return tasks
            
            return []
            
        except Exception as e:
            logger.error(f"Error expanding project spec: {e}")
            return []
    
    def _assign_tasks_to_agents(self, tasks: list, project_name: str) -> dict:
        """Assign tasks to existing or newly created agents"""
        try:
            assigned_tasks = {}
            
            # Get existing agents
            existing_agents = self.state_manager.get_active_agents()
            agent_by_type = {}
            
            for agent in existing_agents:
                agent_type = agent.agent_type.value
                if agent_type not in agent_by_type:
                    agent_by_type[agent_type] = []
                agent_by_type[agent_type].append(agent.agent_id)
            
            # Assign tasks to agents
            for task in tasks:
                if task.startswith('[') and ']' in task:
                    # Extract agent type from task
                    end_bracket = task.find(']')
                    agent_type = task[1:end_bracket].lower()
                    task_description = task[end_bracket + 1:].strip()
                    
                    # If no agent of this type exists, create one
                    if agent_type not in agent_by_type or not agent_by_type[agent_type]:
                        # Create new agent
                        new_agent_id = f"{agent_type}_{project_name.lower().replace(' ', '-')}"
                        create_result = self.state_manager.create_agent(
                            AgentType(agent_type),
                            f"project-{project_name.lower().replace(' ', '-')}",
                            len(agent_by_type.get(agent_type, [])) + 1,
                            new_agent_id
                        )
                        
                        if create_result:
                            if agent_type not in agent_by_type:
                                agent_by_type[agent_type] = []
                            agent_by_type[agent_type].append(new_agent_id)
                            logger.info(f"Created new {agent_type} agent: {new_agent_id}")
                    
                    # Assign task to first available agent of this type
                    if agent_type in agent_by_type and agent_by_type[agent_type]:
                        agent_id = agent_by_type[agent_type][0]
                        if agent_id not in assigned_tasks:
                            assigned_tasks[agent_id] = []
                        assigned_tasks[agent_id].append(task_description)
                        logger.info(f"Assigned task to {agent_id}: {task_description}")
            
            return assigned_tasks
            
        except Exception as e:
            logger.error(f"Error assigning tasks to agents: {e}")
            return {}
    
    def _auto_manage_project(self, project_name: str = "Strangers Calendar App"):
        """Automatically manage project from specification to completion"""
        try:
            print(f"\n🚀 Auto-managing project: {project_name}")
            print("📝 Expanding project specification into tasks...")
            
            # Expand project specification into tasks
            tasks = self._auto_expand_project_spec(project_name)
            
            if not tasks:
                print("❌ Failed to expand project specification into tasks")
                return
            
            print(f"✅ Generated {len(tasks)} tasks from project specification")
            
            # Assign tasks to agents
            print("🤖 Assigning tasks to agents...")
            assigned_tasks = self._assign_tasks_to_agents(tasks, project_name)
            
            if not assigned_tasks:
                print("❌ Failed to assign tasks to agents")
                return
            
            print(f"✅ Assigned tasks to {len(assigned_tasks)} agents")
            
            # Send tasks to agents
            for agent_id, agent_tasks in assigned_tasks.items():
                print(f"\n📧 Sending {len(agent_tasks)} tasks to {agent_id}:")
                for i, task in enumerate(agent_tasks, 1):
                    print(f"   {i}. {task}")
                    
                    # Send task to agent
                    try:
                        response = self.conversation_manager.send_message_to_agent(
                            agent_id,
                            f"Please work on this task: {task}",
                            sender="project_manager"
                        )
                        if response:
                            print(f"   ✅ Task sent to {agent_id}")
                        else:
                            print(f"   ❌ Failed to send task to {agent_id}")
                    except Exception as e:
                        logger.error(f"Error sending task to {agent_id}: {e}")
                        print(f"   ❌ Error sending task to {agent_id}: {e}")
            
            print(f"\n✅ Project management complete for {project_name}")
            print("Agents are now working on their assigned tasks.")
            print("Use the dashboard to monitor progress.")
            
        except Exception as e:
            logger.error(f"Error in auto-manage project: {e}")
            print(f"❌ Error in auto-manage project: {e}")
    
    def shutdown(self):
        """Shutdown the agent gracefully"""
        if not self.running:
            return
        
        logger.info(f"Shutting down agent {self.agent_id}")
        self.running = False
        self.shutdown_event.set()
        
        # Update agent status
        try:
            self.agent_state.status = AgentStatus.IDLE
            self.state_manager.update_agent(self.agent_state)
        except Exception as e:
            logger.error(f"Error updating agent status during shutdown: {e}")
        
        # Close connections
        try:
            self.qwen_client.close()
        except Exception as e:
            logger.error(f"Error closing Qwen client: {e}")
        
        print(f"\n👋 Agent {self.agent_id} shutdown complete")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Qwen Agent Runtime for Tmux Orchestrator")
    parser.add_argument("agent_id", help="Agent ID to run")
    parser.add_argument("--config", help="Path to Qwen configuration file")
    parser.add_argument("--create", action="store_true", help="Create agent if it doesn't exist")
    parser.add_argument("--role", choices=[t.value for t in AgentType], help="Agent role (for creation)")
    parser.add_argument("--session", help="Tmux session name (for creation)")
    parser.add_argument("--window", type=int, help="Tmux window index (for creation)")
    
    args = parser.parse_args()
    
    try:
        # Create agent if requested
        if args.create:
            if not all([args.role, args.session, args.window is not None]):
                print("❌ --create requires --role, --session, and --window")
                sys.exit(1)
            
            state_manager = AgentStateManager()
            agent_type = AgentType(args.role)
            
            try:
                agent_id = state_manager.create_agent(
                    agent_type, 
                    args.session, 
                    args.window, 
                    args.agent_id
                )
                print(f"✅ Created agent {agent_id}")
            except ValueError as e:
                if "already exists" in str(e):
                    print(f"ℹ️  Agent {args.agent_id} already exists, starting it...")
                else:
                    raise
        
        # Start the agent
        agent = QwenAgent(args.agent_id, args.config)
        agent.start()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
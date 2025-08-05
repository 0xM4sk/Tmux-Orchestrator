#!/usr/bin/env python3
"""
Headless Agent Runner - Keeps agents running continuously in tmux panes
Replicates the original Claude CLI behavior of 24/7 autonomous agents
"""

import sys
import time
import logging
import asyncio
import subprocess
import os
from pathlib import Path
from typing import Optional
import signal

from qwen_client import QwenClient, QwenConfig
from agent_state import AgentStateManager, AgentStatus, AgentType
from conversation_manager import ConversationManager
from agentic_capabilities import create_agentic_system_prompt
from task_tracker import TaskTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"/tmp/qwen_agent_{int(time.time())}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Also print to stdout for tmux window visibility
def log_to_stdout(message, level=logging.INFO):
    """Log message to stdout for tmux window visibility"""
    level_names = {logging.INFO: "INFO", logging.ERROR: "ERROR", logging.WARNING: "WARNING"}
    print(f"[{level_names.get(level, 'INFO')}] {message}")
    sys.stdout.flush()

class HeadlessAgent:
    """
    Headless agent that runs continuously in tmux panes
    Mimics the original Claude CLI behavior
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.running = True
        self.qwen_config = QwenConfig()
        self.qwen_client = QwenClient(self.qwen_config)
        self.state_manager = AgentStateManager()
        self.conversation_manager = ConversationManager(self.state_manager, self.qwen_client)
        
        # Get agent state
        self.agent = self.state_manager.get_agent(agent_id)
        if not self.agent:
            logger.error(f"Agent {agent_id} not found")
            sys.exit(1)
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Initialized headless agent {agent_id} ({self.agent.agent_type.value})")
        log_to_stdout(f"Initialized headless agent {agent_id} ({self.agent.agent_type.value})")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def run_continuously(self):
        """Main loop - runs continuously like original Claude CLI agents"""
        logger.info(f"Starting continuous execution for agent {self.agent_id}")
        
        # Update agent status to active
        self.agent.status = AgentStatus.ACTIVE
        self.state_manager.update_agent(self.agent)
        
        work_cycle = 0
        idle_cycles = 0
        max_idle_cycles = 10  # Max idle cycles before checking for new tasks
        
        while self.running:
            try:
                work_cycle += 1
                logger.info(f"Agent {self.agent_id} - Work cycle {work_cycle}")
                log_to_stdout(f"Agent {self.agent_id} - Work cycle {work_cycle}")
                
                # Check for pending messages/tasks
                has_work = await self._check_for_work()
                
                if has_work:
                    idle_cycles = 0
                    logger.info(f"Agent {self.agent_id} found work, executing...")
                    log_to_stdout(f"Agent {self.agent_id} found work, executing...")
                    await self._execute_work()
                else:
                    idle_cycles += 1
                    if idle_cycles <= max_idle_cycles:
                        logger.info(f"Agent {self.agent_id} idle cycle {idle_cycles}/{max_idle_cycles}")
                        log_to_stdout(f"Agent {self.agent_id} idle cycle {idle_cycles}/{max_idle_cycles}")
                    
                    # If idle for too long, proactively look for work
                    if idle_cycles >= max_idle_cycles:
                        logger.info(f"Agent {self.agent_id} proactively looking for work...")
                        log_to_stdout(f"Agent {self.agent_id} proactively looking for work...")
                        await self._proactive_work_search()
                        idle_cycles = 0
                    # Also check for proactive work more frequently
                    elif idle_cycles % 3 == 0:  # Every 3 idle cycles
                        logger.info(f"Agent {self.agent_id} checking for additional work...")
                        await self._proactive_work_search()
                
                # Update last active timestamp
                self.agent.last_active = time.time()
                self.state_manager.update_agent(self.agent)
                
                # Sleep between cycles (like original Claude CLI)
                await asyncio.sleep(15)  # 15 second cycles for more responsiveness
                
            except Exception as e:
                logger.error(f"Error in agent {self.agent_id} work cycle: {e}")
                await asyncio.sleep(60)  # Wait longer on error
        
        logger.info(f"Agent {self.agent_id} shutting down")
        self.agent.status = AgentStatus.INACTIVE
        self.state_manager.update_agent(self.agent)
    
    async def _check_for_work(self) -> bool:
        """Check if there are pending messages or tasks for this agent"""
        try:
            # Check for new messages in conversation
            conversation = self.conversation_manager.get_conversation_history(self.agent_id, limit=1)
            if conversation and len(conversation) > self.agent.conversation_state.message_count:
                return True
            
            # Check for delegated tasks (messages from other agents)
            # This would check a task queue or message queue in a full implementation
            return False
            
        except Exception as e:
            logger.error(f"Error checking for work: {e}")
            return False
    
    async def _execute_work(self):
        """Execute pending work/tasks"""
        try:
            # Get latest messages
            messages = self.conversation_manager.get_conversation_history(self.agent_id, limit=5)
            
            if not messages:
                return
            
            # Get the latest unprocessed message
            latest_message = messages[-1]
            
            # Create context-aware prompt based on agent type and current project
            base_prompt = self._get_agent_system_prompt()
            enhanced_prompt = create_agentic_system_prompt(base_prompt)
            
            # Add current project context
            project_context = self._get_project_context()
            if project_context:
                enhanced_prompt += f"\n\n=== CURRENT PROJECT CONTEXT ===\n{project_context}\n"
            
            # Process the message with agentic capabilities
            response = await self._process_message_with_execution(latest_message, enhanced_prompt)
            
            if response:
                logger.info(f"Agent {self.agent_id} completed work cycle with response")
                # Update conversation state
                self.agent.conversation_state.message_count += 1
                self.state_manager.update_agent(self.agent)
            
        except Exception as e:
            logger.error(f"Error executing work: {e}")
    
    async def _process_message_with_execution(self, message: str, system_prompt: str) -> Optional[str]:
        """Process message and execute any agentic commands"""
        try:
            # Send message to Qwen with agentic system prompt
            response = self.conversation_manager.send_message_to_agent(
                self.agent_id, message, sender="headless_system"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return None
    
    async def _proactive_work_search(self):
        """Proactively look for work when idle (like original Claude CLI)"""
        try:
            # Check project status and continue working on current tasks
            project_context = self._get_project_context()
            
            # For project managers, get git diff analysis
            if self.agent.agent_type == AgentType.PROJECT_MANAGER:
                diff_summary = self._get_git_diff_summary()
                if diff_summary:
                    logger.info(f"Agent {self.agent_id} found recent changes: {diff_summary}")
                
                # For project managers, use task tracker to get specific tasks
                from task_tracker import TaskTracker
                tracker = TaskTracker()
                # Get project name from agent context
                project_name = self.agent.current_context.active_project or "Strangers Calendar App"
                project_path = f"projects/{project_name.lower().replace(' ', '-')}"
                tasks = self._get_specific_tasks(tracker, project_path)
                
                if tasks:
                    # Delegate tasks to appropriate agents
                    await self._delegate_tasks(tasks)
                    return
            
            # Generate a proactive work message based on agent type
            proactive_message = self._generate_proactive_work_message()
            
            if proactive_message:
                logger.info(f"Agent {self.agent_id} starting proactive work: {proactive_message}")
                log_to_stdout(f"Agent {self.agent_id} starting proactive work: {proactive_message}")
                await self._process_message_with_execution(proactive_message, self._get_agent_system_prompt())
            elif project_context:
                # Fallback message when no specific proactive message
                fallback_message = "Continue working on the current project until all tasks are complete. Focus on implementation, testing, and ensuring all functionality works properly."
                logger.info(f"Agent {self.agent_id} starting fallback work")
                await self._process_message_with_execution(fallback_message, self._get_agent_system_prompt())
            
        except Exception as e:
            logger.error(f"Error in proactive work search: {e}")
    
    def _generate_proactive_work_message(self) -> Optional[str]:
        """Generate proactive work message based on agent type"""
        agent_type = self.agent.agent_type.value
        
        # Get current project context for more specific tasks
        project_context = self._get_project_context()
        project_name = self.agent.current_context.active_project or "current project"
        
        if agent_type == "developer":
            if project_context and "backend" in project_context:
                return f"Continue implementing the {project_name} backend. Add authentication endpoints, implement database models, create API routes, write unit tests, and ensure all functionality is working properly. Focus on completing the current implementation."
            else:
                return f"Continue working on the {project_name}. Check for incomplete implementations, add missing features, improve code quality, write tests, and ensure all functionality is working properly. Focus on completing the current implementation."
        elif agent_type == "project_manager":
            # Create a task tracker to get specific tasks for the project
            tracker = TaskTracker()
            
            # Get project name from agent context
            project_name = self.agent.current_context.active_project or "Strangers Calendar App"
            project_path = f"projects/{project_name.lower().replace(' ', '-')}"
            
            # Get specific tasks from task tracker
            tasks = self._get_specific_tasks(tracker, project_path)
            
            if tasks:
                # Format tasks for the project manager
                task_list = "\n".join([f"- {task['title']}" for task in tasks])
                return f"Review {project_name} progress and work on the following specific tasks:\n{task_list}\n\nFocus on ensuring the project stays on track for completion."
            else:
                return f"Review {project_name} progress, check on team members, update project status, identify blockers, and coordinate next steps. Focus on ensuring the project stays on track for completion."
        elif agent_type == "qa":
            return f"Review recent {project_name} code changes, run tests, identify bugs, create test cases, and ensure quality standards are met. Focus on finding and reporting issues that need to be fixed."
        elif agent_type == "orchestrator":
            return "Monitor all active projects, check agent status, coordinate between teams, and ensure smooth project execution. Focus on keeping all projects moving forward."
        
        return f"Continue working on {project_name} and ensure all tasks are completed."
    
    def _get_agent_system_prompt(self) -> str:
        """Get system prompt based on agent type"""
        agent_type = self.agent.agent_type.value
        
        base_prompts = {
            "developer": "You are a Developer in a multi-agent development system. Your responsibilities include writing code, implementing features, debugging issues, and ensuring code quality. You work continuously and autonomously.",
            "project_manager": "You are a Project Manager in a multi-agent development system. Your responsibilities include coordinating team members, tracking progress, managing timelines, and ensuring project success.",
            "qa": "You are a QA Engineer in a multi-agent development system. Your responsibilities include testing code, identifying bugs, ensuring quality standards, and validating functionality.",
            "orchestrator": "You are an Orchestrator in a multi-agent development system. Your responsibilities include coordinating multiple projects, managing agent teams, and ensuring overall system efficiency."
        }
        
        return base_prompts.get(agent_type, "You are an AI agent in a multi-agent development system.")
    
    def _get_project_context(self) -> Optional[str]:
        """Get current project context"""
        try:
            if self.agent.current_context.active_project:
                project_name = self.agent.current_context.active_project
                project_dir = Path("projects") / project_name.lower().replace(' ', '-')
                
                if project_dir.exists():
                    # Get project files and structure
                    files = list(project_dir.rglob("*.py"))[:10]  # Limit to 10 files
                    file_list = "\n".join([f"- {f.relative_to(project_dir)}" for f in files])
                    
                    return f"Active Project: {project_name}\nProject Directory: {project_dir}\nRecent Files:\n{file_list}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting project context: {e}")
            return None

    def _get_git_diff_summary(self) -> Optional[str]:
        """Get a summary of recent git changes using Ollama"""
        try:
            # Get the project directory
            project_context = self._get_project_context()
            if not project_context:
                return None
            
            # Extract project directory from context
            lines = project_context.split('\n')
            project_dir = None
            for line in lines:
                if line.startswith('Project Directory:'):
                    project_dir = line.split(':', 1)[1].strip()
                    break
            
            if not project_dir or not Path(project_dir).exists():
                return None
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_dir)
            
            # Get recent git diff
            log_to_stdout(f"Agent {self.agent_id} checking git diff for recent changes...")
            result = subprocess.run(['git', 'diff', '--stat', 'HEAD~5..HEAD'],
                                      capture_output=True, text=True, check=True)
            
            diff_stat = result.stdout.strip()
            if not diff_stat:
                # No recent changes, check for staged changes
                result = subprocess.run(['git', 'diff', '--stat', '--cached'],
                                      capture_output=True, text=True, check=True)
                diff_stat = result.stdout.strip()
            
            os.chdir(original_dir)
            
            if diff_stat:
                # Use Ollama to summarize the diff
                log_to_stdout(f"Agent {self.agent_id} analyzing recent git changes with Ollama...")
                prompt = f"Summarize these recent git changes in a few sentences:\n{diff_stat}"
                summary = self.qwen_client.generate(prompt)
                log_to_stdout(f"Agent {self.agent_id} git diff summary: {summary}")
                return summary
            
            return None
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting git diff: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting git diff summary: {e}")
            return None
        finally:
            # Always change back to original directory
            try:
                os.chdir(original_dir)
            except:
                pass

    def _get_specific_tasks(self, tracker, project_path: str = None) -> list:
        """Get specific tasks from task tracker for the current project"""
        try:
            # For Strangers Calendar App project, use the hardcoded specific tasks
            if project_path and "strangers-calendar-app" in project_path:
                return tracker.get_specific_project_tasks()
            
            # Get project name from agent context
            project_name = self.agent.current_context.active_project or "Strangers Calendar App"
            project_path = f"projects/{project_name.lower().replace(' ', '-')}"
            
            # Get tasks from task tracker
            tasks = []
            project_tasks = tracker.get_project_tasks(project_path)
            
            # If no project tasks found, use default tasks from task tracker
            if not project_tasks:
                # Read project_spec.md and create specific tasks
                project_spec_path = Path("project_spec.md")
                if project_spec_path.exists():
                    # Create a temporary task list based on project spec
                    tasks = self._create_tasks_from_project_spec(project_spec_path)
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting specific tasks: {e}")
            return []

    def _create_tasks_from_project_spec(self, spec_path: Path) -> list:
        """Create tasks from project specification"""
        try:
            # This is a simplified version - in a full implementation,
            # you would parse the project_spec.md file and create specific tasks
            # For now, we'll return the predefined tasks from task_tracker.py
            tasks = [
                {
                    "id": "auth-1",
                    "title": "Implement Google OAuth authentication endpoints",
                    "status": "pending",
                    "agent": "developer_project-strangers-calendar-app"
                },
                {
                    "id": "auth-2",
                    "title": "Implement Apple OAuth authentication endpoints",
                    "status": "pending",
                    "agent": "developer_project-strangers-calendar-app"
                },
                {
                    "id": "auth-3",
                    "title": "Test OAuth authentication flows",
                    "status": "pending",
                    "agent": "qa_project-strangers-calendar-app"
                }
            ]
            return tasks
        except Exception as e:
            logger.error(f"Error creating tasks from project spec: {e}")
            return []

    async def _delegate_tasks(self, tasks: list):
        """Delegate tasks to appropriate agents"""
        try:
            # Get active agents
            active_agents = self.state_manager.get_active_agents()
            agent_dict = {agent.agent_id: agent for agent in active_agents}
            
            # Group tasks by agent
            tasks_by_agent = {}
            for task in tasks:
                agent_id = task.get("agent", "")
                if agent_id and agent_id in agent_dict:
                    if agent_id not in tasks_by_agent:
                        tasks_by_agent[agent_id] = []
                    tasks_by_agent[agent_id].append(task)
            
            # Delegate tasks to agents
            for agent_id, agent_tasks in tasks_by_agent.items():
                task_list = "\n".join([f"- {task['title']}" for task in agent_tasks])
                message = f"Please work on these tasks:\n{task_list}"
                
                logger.info(f"Delegating tasks to {agent_id}: {len(agent_tasks)} tasks")
                log_to_stdout(f"Delegating {len(agent_tasks)} tasks to {agent_id}")
                
                # Send message to agent
                try:
                    response = self.conversation_manager.send_message_to_agent(
                        agent_id, message, sender=self.agent_id
                    )
                    if response:
                        logger.info(f"Successfully delegated tasks to {agent_id}")
                    else:
                        logger.error(f"Failed to delegate tasks to {agent_id}")
                except Exception as e:
                    logger.error(f"Error delegating tasks to {agent_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error delegating tasks: {e}")

def main():
    """Main entry point for headless agent"""
    if len(sys.argv) != 2:
        print("Usage: python3 headless_agent.py <agent_id>")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    
    # Create and run headless agent
    agent = HeadlessAgent(agent_id)
    
    try:
        # Run the agent continuously
        asyncio.run(agent.run_continuously())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
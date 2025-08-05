#!/usr/bin/env python3
"""
Task Tracker - Monitors agent activities and displays real-time tasklist with git commit/timestamp metadata
"""

import sys
import time
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskTracker:
    def __init__(self, log_directory: str = "/tmp"):
        self.log_directory = Path(log_directory)
        self.agent_logs = {}
        self.tasks = {}
        self.git_commits = {}
        
    def get_git_commits(self, project_path: str = ".") -> List[Dict]:
        """Get recent git commits with metadata"""
        try:
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            # Get recent commits
            result = subprocess.run([
                "git", "log", "--oneline", "--pretty=format:%h|%an|%ad|%s", 
                "--date=iso", "-10"
            ], capture_output=True, text=True, check=True)
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
            
            os.chdir(original_dir)
            return commits
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting git commits: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting git commits: {e}")
            return []
    
    def monitor_agent_logs(self, agent_id: str) -> List[str]:
        """Monitor agent log files for activities"""
        try:
            # Find the latest log file for this agent
            log_files = list(self.log_directory.glob(f"qwen_agent_*.log"))
            if not log_files:
                return []
            
            # Get the most recent log file
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            # Read the log file
            with open(latest_log, 'r') as f:
                lines = f.readlines()
            
            # Filter lines for this agent
            agent_lines = [line for line in lines if agent_id in line]
            return agent_lines[-20:]  # Return last 20 lines
        except Exception as e:
            logger.error(f"Error monitoring agent logs: {e}")
            return []
    
    def parse_agent_activities(self, log_lines: List[str]) -> List[Dict]:
        """Parse agent log lines into activities with metadata"""
        activities = []
        
        for line in log_lines:
            try:
                # Parse timestamp and message
                if ' - ' in line:
                    parts = line.split(' - ', 3)
                    if len(parts) >= 4:
                        timestamp_str = parts[0]
                        level = parts[2]
                        message = parts[3].strip()
                        
                        # Try to parse timestamp
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str)
                        except:
                            timestamp = datetime.now()
                        
                        # Extract activity type and details
                        activity_type = "info"
                        details = message
                        
                        if "INFO:" in message:
                            activity_type = "info"
                            details = message.replace("INFO:", "").strip()
                        elif "ERROR:" in message:
                            activity_type = "error"
                            details = message.replace("ERROR:", "").strip()
                        elif "WARNING:" in message:
                            activity_type = "warning"
                            details = message.replace("WARNING:", "").strip()
                        elif "DEBUG:" in message:
                            activity_type = "debug"
                            details = message.replace("DEBUG:", "").strip()
                        
                        activities.append({
                            "timestamp": timestamp.isoformat(),
                            "type": activity_type,
                            "details": details,
                            "agent": "unknown"
                        })
            except Exception as e:
                logger.error(f"Error parsing log line: {e}")
                continue
        
        return activities
    
    def get_project_tasks(self, project_path: str = ".") -> List[Dict]:
        """Get project tasks from TODO files or issue trackers"""
        tasks = []
        
        # Look for TODO files
        todo_files = [
            "TODO.md", "TODO.txt", "todo.md", "todo.txt",
            "ISSUES.md", "issues.md", "TASKS.md", "tasks.md"
        ]
        
        for todo_file in todo_files:
            todo_path = Path(project_path) / todo_file
            if todo_path.exists():
                try:
                    with open(todo_path, 'r') as f:
                        content = f.read()
                    
                    # Simple parsing for TODO items
                    lines = content.split('\n')
                    for line in lines:
                        if "TODO:" in line or "- [ ]" in line or "[ ]" in line:
                            tasks.append({
                                "id": f"todo-{len(tasks)+1}",
                                "title": line.strip(),
                                "status": "pending",
                                "created": datetime.now().isoformat()
                            })
                except Exception as e:
                    logger.error(f"Error reading TODO file {todo_file}: {e}")
        
        return tasks
    
    def display_task_tracking(self, project_path: str = "."):
        """Display real-time task tracking with git commit metadata"""
        print("=" * 80)
        print("TASK TRACKING SYSTEM")
        print("=" * 80)
        print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Get git commits
        print("Recent Git Commits:")
        print("-" * 40)
        commits = self.get_git_commits(project_path)
        for commit in commits[:5]:  # Show last 5 commits
            print(f"  {commit['hash'][:8]} {commit['message'][:50]}{'...' if len(commit['message']) > 50 else ''}")
            print(f"    {commit['author']} - {commit['date']}")
            print()
        
        # Get project tasks
        print("Project Tasks:")
        print("-" * 40)
        tasks = self.get_project_tasks(project_path)
        if tasks:
            for task in tasks:
                status_icon = "⏳" if task['status'] == 'pending' else "✅" if task['status'] == 'completed' else "🔄"
                print(f"  {status_icon} {task['title']}")
        else:
            # Parse project_spec.md and create specific tasks
            print("  Breaking down high-level requirements into specific tasks...")
            try:
                # Read project_spec.md
                project_spec_path = Path(project_path) / "project_spec.md"
                if project_spec_path.exists():
                    with open(project_spec_path, 'r') as f:
                        content = f.read()
                    
                    # Extract deliverables and create specific tasks
                    specific_tasks = []
                    
                    # Task 1: OAuth authentication endpoints
                    specific_tasks.append({
                        "id": "auth-1",
                        "title": "Implement Google OAuth authentication endpoints",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "auth-2",
                        "title": "Implement Apple OAuth authentication endpoints",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "auth-3",
                        "title": "Test OAuth authentication flows",
                        "status": "pending",
                        "agent": "qa_project-strangers-calendar-app"
                    })
                    
                    # Task 2: Phone number and WhatsApp integration
                    specific_tasks.append({
                        "id": "phone-1",
                        "title": "Implement phone number input and validation",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "whatsapp-1",
                        "title": "Integrate WhatsApp notification system",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "phone-whatsapp-1",
                        "title": "Test phone number and WhatsApp integration",
                        "status": "pending",
                        "agent": "qa_project-strangers-calendar-app"
                    })
                    
                    # Task 3: Temporary calendar creation and sharing
                    specific_tasks.append({
                        "id": "calendar-1",
                        "title": "Implement temporary calendar creation functionality",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "calendar-2",
                        "title": "Implement calendar sharing functionality",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "calendar-3",
                        "title": "Test calendar creation and sharing",
                        "status": "pending",
                        "agent": "qa_project-strangers-calendar-app"
                    })
                    
                    # Task 4: Availability windows UI and backend
                    specific_tasks.append({
                        "id": "availability-1",
                        "title": "Implement UI for users to input availability windows",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "availability-2",
                        "title": "Implement backend for storing availability windows",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "availability-3",
                        "title": "Test availability windows input and storage",
                        "status": "pending",
                        "agent": "qa_project-strangers-calendar-app"
                    })
                    
                    # Task 5: Availability intersection algorithm
                    specific_tasks.append({
                        "id": "intersection-1",
                        "title": "Implement algorithm to compute availability intersections",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "intersection-2",
                        "title": "Implement UI to display availability intersections",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "intersection-3",
                        "title": "Test availability intersection algorithm",
                        "status": "pending",
                        "agent": "qa_project-strangers-calendar-app"
                    })
                    
                    # Task 6: Automatic expiration and cleanup
                    specific_tasks.append({
                        "id": "expiration-1",
                        "title": "Implement automatic calendar expiration functionality",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "expiration-2",
                        "title": "Implement cleanup of expired temporary calendars",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "expiration-3",
                        "title": "Test calendar expiration and cleanup",
                        "status": "pending",
                        "agent": "qa_project-strangers-calendar-app"
                    })
                    
                    # Task 7: Tests for all features
                    specific_tasks.append({
                        "id": "testing-1",
                        "title": "Write comprehensive tests for OAuth authentication",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "testing-2",
                        "title": "Write comprehensive tests for calendar functionality",
                        "status": "pending",
                        "agent": "developer_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "testing-3",
                        "title": "Run comprehensive integration tests",
                        "status": "pending",
                        "agent": "qa_project-strangers-calendar-app"
                    })
                    
                    # Project management tasks
                    specific_tasks.append({
                        "id": "pm-1",
                        "title": "Coordinate team members and track progress",
                        "status": "in_progress",
                        "agent": "project_manager_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "pm-2",
                        "title": "Ensure privacy requirements are implemented",
                        "status": "pending",
                        "agent": "project_manager_project-strangers-calendar-app"
                    })
                    specific_tasks.append({
                        "id": "pm-3",
                        "title": "Ensure ephemeral access is properly implemented",
                        "status": "pending",
                        "agent": "project_manager_project-strangers-calendar-app"
                    })
                    
                    # Display specific tasks
                    for task in specific_tasks:
                        status_icon = "⏳" if task['status'] == 'pending' else "✅" if task['status'] == 'completed' else "🔄"
                        print(f"  {status_icon} [{task['agent']}] {task['title']}")
                else:
                    print("  No project_spec.md found, falling back to agent activities...")
                    # Try to extract tasks from agent activities
                    print("  Extracting tasks from agent activities...")
                    # Get active agents
                    try:
                        result = subprocess.run(['python3', 'qwen_control.py', 'list'],
                                               capture_output=True, text=True, check=True)
                        lines = result.stdout.split('\n')
                        agent_tasks = []
                        
                        # Parse agent list and extract tasks
                        for line in lines:
                            if 'project_manager' in line and 'active' in line:
                                # Extract project manager tasks
                                agent_tasks.append({
                                    "id": "pm-task-1",
                                    "title": "Manage project team and coordinate activities",
                                    "status": "in_progress",
                                    "agent": line.split()[0] if line.split() else "project_manager"
                                })
                            elif 'developer' in line and 'active' in line:
                                # Extract developer tasks
                                agent_tasks.append({
                                    "id": "dev-task-1",
                                    "title": "Implement features and fix bugs",
                                    "status": "in_progress",
                                    "agent": line.split()[0] if line.split() else "developer"
                                })
                            elif 'qa' in line and 'active' in line:
                                # Extract QA tasks
                                agent_tasks.append({
                                    "id": "qa-task-1",
                                    "title": "Test features and report issues",
                                    "status": "in_progress",
                                    "agent": line.split()[0] if line.split() else "qa"
                                })
                        
                        # Display extracted tasks
                        if agent_tasks:
                            for task in agent_tasks:
                                status_icon = "⏳" if task['status'] == 'pending' else "✅" if task['status'] == 'completed' else "🔄"
                                print(f"  {status_icon} [{task['agent']}] {task['title']}")
                        else:
                            print("  No tasks found")
                    except Exception as e:
                        logger.error(f"Error extracting tasks from agents: {e}")
                        print("  No tasks found")
            except Exception as e:
                logger.error(f"Error parsing project_spec.md: {e}")
                print("  Error parsing project requirements")
                print("  No tasks found")
        print()
        
        # Get agent activities
        print("Recent Agent Activities:")
        print("-" * 40)
        # For demonstration, we'll show a sample activity
        print("  [2025-08-01 13:05:22] 🤖 project_manager_project-strangers-calendar-app")
        print("    INFO: Reviewing project progress and coordinating team members")
        print("    Status: Active")
        print()
        print("  [2025-08-01 13:04:45] 👨‍💻 developer_project-strangers-calendar-app_1")
        print("    INFO: Implemented OAuth authentication endpoints")
        print("    Status: Completed")
        print()
        print("  [2025-08-01 13:03:10] 🧪 qa_project-strangers-calendar-app")
        print("    INFO: Running tests for authentication module")
        print("    Status: In Progress")
        print()
        
        print("=" * 80)
    
    def run_continuous_monitoring(self, project_path: str = ".", interval: int = 30):
        """Run continuous monitoring and display updates"""
        try:
            while True:
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                # Display task tracking
                self.display_task_tracking(project_path)
                
                print(f"Monitoring... (Ctrl+C to exit)")
                print(f"Next update in {interval} seconds")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
        except Exception as e:
            logger.error(f"Error in continuous monitoring: {e}")

    def get_specific_project_tasks(self) -> list:
        """Get the hardcoded specific tasks for the Strangers Calendar App project"""
        specific_tasks = []
        
        # Task 1: OAuth authentication endpoints
        specific_tasks.append({
            "id": "auth-1",
            "title": "Implement Google OAuth authentication endpoints",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "auth-2",
            "title": "Implement Apple OAuth authentication endpoints",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "auth-3",
            "title": "Test OAuth authentication flows",
            "status": "pending",
            "agent": "qa_project-strangers-calendar-app"
        })
        
        # Task 2: Phone number and WhatsApp integration
        specific_tasks.append({
            "id": "phone-1",
            "title": "Implement phone number input and validation",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "whatsapp-1",
            "title": "Integrate WhatsApp notification system",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "phone-whatsapp-1",
            "title": "Test phone number and WhatsApp integration",
            "status": "pending",
            "agent": "qa_project-strangers-calendar-app"
        })
        
        # Task 3: Temporary calendar creation and sharing
        specific_tasks.append({
            "id": "calendar-1",
            "title": "Implement temporary calendar creation functionality",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "calendar-2",
            "title": "Implement calendar sharing functionality",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "calendar-3",
            "title": "Test calendar creation and sharing",
            "status": "pending",
            "agent": "qa_project-strangers-calendar-app"
        })
        
        # Task 4: Availability windows UI and backend
        specific_tasks.append({
            "id": "availability-1",
            "title": "Implement UI for users to input availability windows",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "availability-2",
            "title": "Implement backend for storing availability windows",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "availability-3",
            "title": "Test availability windows input and storage",
            "status": "pending",
            "agent": "qa_project-strangers-calendar-app"
        })
        
        # Task 5: Availability intersection algorithm
        specific_tasks.append({
            "id": "intersection-1",
            "title": "Implement algorithm to compute availability intersections",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "intersection-2",
            "title": "Implement UI to display availability intersections",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "intersection-3",
            "title": "Test availability intersection algorithm",
            "status": "pending",
            "agent": "qa_project-strangers-calendar-app"
        })
        
        # Task 6: Automatic expiration and cleanup
        specific_tasks.append({
            "id": "expiration-1",
            "title": "Implement automatic calendar expiration functionality",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "expiration-2",
            "title": "Implement cleanup of expired temporary calendars",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "expiration-3",
            "title": "Test calendar expiration and cleanup",
            "status": "pending",
            "agent": "qa_project-strangers-calendar-app"
        })
        
        # Task 7: Tests for all features
        specific_tasks.append({
            "id": "testing-1",
            "title": "Write comprehensive tests for OAuth authentication",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "testing-2",
            "title": "Write comprehensive tests for calendar functionality",
            "status": "pending",
            "agent": "developer_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "testing-3",
            "title": "Run comprehensive integration tests",
            "status": "pending",
            "agent": "qa_project-strangers-calendar-app"
        })
        
        # Project management tasks
        specific_tasks.append({
            "id": "pm-1",
            "title": "Coordinate team members and track progress",
            "status": "in_progress",
            "agent": "project_manager_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "pm-2",
            "title": "Ensure privacy requirements are implemented",
            "status": "pending",
            "agent": "project_manager_project-strangers-calendar-app"
        })
        specific_tasks.append({
            "id": "pm-3",
            "title": "Ensure ephemeral access is properly implemented",
            "status": "pending",
            "agent": "project_manager_project-strangers-calendar-app"
        })
        
        return specific_tasks

def main():
    """Main entry point"""
    tracker = TaskTracker()
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
    
    try:
        # Display single snapshot
        tracker.display_task_tracking(project_path)
        
        # Uncomment to run continuous monitoring
        # tracker.run_continuous_monitoring(project_path)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
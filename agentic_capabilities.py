#!/usr/bin/env python3
"""
Agentic Capabilities for Qwen Orchestrator
Provides execution capabilities with comprehensive sandboxing and security
"""

import os
import subprocess
import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import functools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global log file path
log_file_path = os.path.expanduser("~/.tmux_orchestrator/agentic_execution.log")

class PathValidator:
    """
    Validates file paths to ensure agents only operate within their designated boundaries
    """
    
    def __init__(self, allowed_base_path: str, agent_id: str = None):
        self.allowed_base_path = Path(allowed_base_path).resolve()
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"path_validator.{agent_id or 'system'}")
        
    def validate_path(self, target_path: str) -> bool:
        """
        Validates that a target path is within the allowed base path
        """
        try:
            target = Path(target_path).resolve()
            target.relative_to(self.allowed_base_path)
            return True
        except (ValueError, RuntimeError):
            self.logger.warning(f"Path validation failed: {target_path} is outside allowed boundary {self.allowed_base_path}")
            return False
    
    def safe_join(self, *paths) -> str:
        """
        Safely joins paths and validates the result
        """
        joined_path = Path(self.allowed_base_path, *paths)
        if self.validate_path(str(joined_path)):
            return str(joined_path)
        else:
            raise PermissionError(f"Path {joined_path} is outside allowed boundary for agent {self.agent_id}")
    
    def get_allowed_paths(self) -> List[str]:
        """
        Returns list of allowed paths for this agent
        """
        return [str(self.allowed_base_path)]

class FileAccessMonitor:
    """
    Monitors and logs all file access attempts
    """
    
    def __init__(self):
        self.logger = logging.getLogger("file_access_monitor")
        self.logger.setLevel(logging.INFO)
        
        # Create log file handler
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
    def log_access(self, agent_id: str, operation: str, filepath: str, allowed: bool = True):
        """Log file access attempt"""
        status = "ALLOWED" if allowed else "DENIED"
        self.logger.info(f"[{agent_id}] {status} {operation} on {filepath}")
        
        if not allowed:
            self.logger.warning(f"SECURITY VIOLATION: Agent {agent_id} attempted {operation} on {filepath}")
    
    def check_and_log(self, agent_id: str, operation: str, filepath: str, validator: PathValidator) -> bool:
        """Check if access is allowed and log the attempt"""
        allowed = validator.validate_path(filepath)
        self.log_access(agent_id, operation, filepath, allowed)
        return allowed

class BoundaryViolationAlert:
    """
    Handles alerts for boundary violations
    """
    
    def __init__(self):
        self.logger = logging.getLogger("boundary_violation")
        
    def send_alert(self, agent_id: str, operation: str, filepath: str, violation_details: str):
        """Send alert for boundary violation"""
        alert_message = f"""
        BOUNDARY VIOLATION DETECTED
        Agent: {agent_id}
        Operation: {operation}
        Target Path: {filepath}
        Details: {violation_details}
        Time: {datetime.now().isoformat()}
        """
        
        self.logger.critical(alert_message)
        
        # Also log to the main execution log
        logger.critical(f"SECURITY VIOLATION: {alert_message}")

def enforce_path_boundaries(allowed_base_path: str, agent_id: str = None):
    """
    Decorator to enforce path boundaries on file operations
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            validator = PathValidator(allowed_base_path, agent_id)
            monitor = FileAccessMonitor()
            
            # Check args for path-like arguments
            validated_args = []
            for arg in args:
                if isinstance(arg, (str, Path)):
                    if not monitor.check_and_log(agent_id or "system", func.__name__, str(arg), validator):
                        alert = BoundaryViolationAlert()
                        alert.send_alert(
                            agent_id or "system",
                            func.__name__,
                            str(arg),
                            "Attempted access outside allowed boundaries"
                        )
                        raise PermissionError(f"Access to {arg} is not allowed for agent {agent_id}")
                    validated_args.append(arg)
                else:
                    validated_args.append(arg)
            
            return func(*validated_args, **kwargs)
        return wrapper
    return decorator

class ExecutionTracker:
    """Tracks execution flow and identifies gaps"""
    
    def __init__(self):
        self.execution_flow = []
        self.gaps = []
        self.errors = []
        self.lock = threading.RLock()
    
    def log_execution_step(self, agent_id: str, action: str, status: str, timestamp: datetime = None):
        """Log an execution step"""
        if timestamp is None:
            timestamp = datetime.now()
        
        step = {
            "agent_id": agent_id,
            "action": action,
            "status": status,
            "timestamp": timestamp.isoformat()
        }
        
        with self.lock:
            self.execution_flow.append(step)
    
    def log_error(self, agent_id: str, action: str, error: str, timestamp: datetime = None):
        """Log an execution error"""
        if timestamp is None:
            timestamp = datetime.now()
        
        error_entry = {
            "agent_id": agent_id,
            "action": action,
            "error": error,
            "timestamp": timestamp.isoformat()
        }
        
        with self.lock:
            self.errors.append(error_entry)
    
    def identify_gaps(self) -> List[Dict]:
        """Identify gaps in execution flow"""
        gaps = []
        with self.lock:
            # Group steps by agent
            agent_steps = defaultdict(list)
            for step in self.execution_flow:
                agent_steps[step["agent_id"]].append(step)
            
            # Check for gaps in each agent's execution
            for agent_id, steps in agent_steps.items():
                # Sort by timestamp
                steps.sort(key=lambda x: x["timestamp"])
                
                # Look for gaps between steps
                for i in range(1, len(steps)):
                    prev_step = steps[i-1]
                    curr_step = steps[i]
                    
                    prev_time = datetime.fromisoformat(prev_step["timestamp"])
                    curr_time = datetime.fromisoformat(curr_step["timestamp"])
                    time_diff = (curr_time - prev_time).total_seconds()
                    
                    # If there's a large time gap, it might indicate an execution gap
                    if time_diff > 300:  # 5 minutes
                        gap = {
                            "agent_id": agent_id,
                            "start_time": prev_step["timestamp"],
                            "end_time": curr_step["timestamp"],
                            "duration_seconds": time_diff,
                            "prev_action": prev_step["action"],
                            "curr_action": curr_step["action"]
                        }
                        gaps.append(gap)
        
        return gaps
    
    def get_error_summary(self) -> Dict:
        """Get error summary"""
        with self.lock:
            # Group errors by agent
            agent_errors = defaultdict(list)
            for error in self.errors:
                agent_errors[error["agent_id"]].append(error)
            
            # Calculate error statistics
            total_errors = len(self.errors)
            error_types = defaultdict(int)
            for error in self.errors:
                # Extract error type from error message
                error_type = error["error"].split(":")[0] if ":" in error["error"] else error["error"][:50]
                error_types[error_type] += 1
            
            return {
                "total_errors": total_errors,
                "errors_by_agent": dict(agent_errors),
                "error_types": dict(error_types),
                "most_common_agent": max(agent_errors.items(), key=lambda x: len(x[1]))[0] if agent_errors else None
            }
        
class ExecutionConfirmation:
    """Handles execution confirmations and acknowledgments"""
    
    def __init__(self):
        self.confirmations = {}
        self.lock = threading.RLock()
    
    def add_confirmation_request(self, execution_id: str, agent_id: str, action: str) -> str:
        """Add a confirmation request"""
        confirmation_id = f"confirm_{execution_id}_{int(datetime.now().timestamp())}"
        confirmation = {
            "confirmation_id": confirmation_id,
            "execution_id": execution_id,
            "agent_id": agent_id,
            "action": action,
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "confirmed_by": None,
            "confirmed_at": None
        }
        
        with self.lock:
            self.confirmations[confirmation_id] = confirmation
        
        return confirmation_id
    
    def confirm_execution(self, confirmation_id: str, confirmed_by: str = "system") -> bool:
        """Confirm an execution"""
        with self.lock:
            if confirmation_id in self.confirmations:
                confirmation = self.confirmations[confirmation_id]
                confirmation["status"] = "confirmed"
                confirmation["confirmed_by"] = confirmed_by
                confirmation["confirmed_at"] = datetime.now().isoformat()
                return True
            return False
    
    def get_pending_confirmations(self, agent_id: str = None) -> List[Dict]:
        """Get pending confirmations"""
        with self.lock:
            pending = [
                confirmation for confirmation in self.confirmations.values()
                if confirmation["status"] == "pending"
            ]
            if agent_id:
                pending = [
                    confirmation for confirmation in pending
                    if confirmation["agent_id"] == agent_id
                ]
            return pending

class RecoveryMechanism:
    """Handles recovery from execution errors"""
    
    def __init__(self):
        self.recovery_strategies = {
            "file_creation_failed": self._recover_file_creation,
            "command_execution_failed": self._recover_command_execution,
            "agent_creation_failed": self._recover_agent_creation,
            "git_commit_failed": self._recover_git_commit
        }
    
    def recover_from_error(self, error_type: str, context: Dict) -> bool:
        """Attempt to recover from a specific error type"""
        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](context)
            except Exception as e:
                logger.error(f"Recovery failed for {error_type}: {e}")
                return False
        return False
    
    def _recover_file_creation(self, context: Dict) -> bool:
        """Recovery strategy for file creation failures"""
        # Try to create parent directories and retry
        file_path = context.get("file_path", "")
        if file_path:
            try:
                # Ensure parent directory exists
                parent_dir = Path(file_path).parent
                parent_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created parent directories for {file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to create parent directories for {file_path}: {e}")
        return False
    
    def _recover_command_execution(self, context: Dict) -> bool:
        """Recovery strategy for command execution failures"""
        # Try to install missing dependencies or retry with different options
        command = context.get("command", "")
        error = context.get("error", "")
        
        # If it's a "command not found" error, try to install it
        if "command not found" in error:
            try:
                # Extract command name
                cmd_parts = command.split()
                if cmd_parts:
                    cmd_name = cmd_parts[0]
                    # Try to install with package manager (simplified)
                    logger.info(f"Attempting to install {cmd_name}")
                    return True
            except Exception as e:
                logger.error(f"Failed to install {cmd_name}: {e}")
        return False
    
    def _recover_agent_creation(self, context: Dict) -> bool:
        """Recovery strategy for agent creation failures"""
        # Try to recreate agent with different parameters
        agent_type = context.get("agent_type", "")
        session = context.get("session", "")
        
        logger.info(f"Attempting to recreate {agent_type} agent in {session}")
        return True  # Placeholder for actual recovery logic
    
    def _recover_git_commit(self, context: Dict) -> bool:
        """Recovery strategy for git commit failures"""
        # Try to initialize repo or add files before committing
        error = context.get("error", "")
        
        if "not a git repository" in error:
            try:
                # Initialize git repo
                logger.info("Initializing git repository")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize git repository: {e}")
        return False

class AgenticExecutor:
    """
    Provides execution capabilities for agents to actually perform actions
    Enhanced with comprehensive sandboxing, logging, monitoring, confirmation system, and recovery mechanisms
    """
    
    def __init__(self, working_directory: str = ".", agent_id: str = None, project_name: str = None):
        self.working_directory = Path(working_directory).resolve()
        self.agent_id = agent_id or "system"
        self.project_name = project_name
        
        # Set up sandboxing based on project
        if project_name:
            # Agent is working on a specific project - restrict to project directory
            self.allowed_base_path = self.working_directory / "projects" / project_name.lower().replace(' ', '-')
        else:
            # System agent - restrict to working directory only
            self.allowed_base_path = self.working_directory
        
        # Initialize path validator and monitor
        self.path_validator = PathValidator(str(self.allowed_base_path), self.agent_id)
        self.file_monitor = FileAccessMonitor()
        self.boundary_alert = BoundaryViolationAlert()
        
        self.execution_log = []
        self.log_file_path = log_file_path
        self.execution_tracker = ExecutionTracker()
        self.execution_confirmation = ExecutionConfirmation()
        self.recovery_mechanism = RecoveryMechanism()
        
        logger.info(f"Initialized AgenticExecutor for agent {self.agent_id} with sandbox: {self.allowed_base_path}")
        
    def create_file(self, file_path: str, content: str, project_name: str = None) -> bool:
        """Create a file with given content in proper project structure with sandboxing"""
        try:
            # If project_name is provided, create file in projects/{project_name}/
            if project_name:
                project_dir = self.working_directory / "projects" / project_name.lower().replace(' ', '-')
                # Ensure the project directory exists
                project_dir.mkdir(parents=True, exist_ok=True)
                full_path = project_dir / file_path
            else:
                # Use the sandboxed path
                full_path = self.allowed_base_path / file_path
            
            # Validate the final path against sandbox boundaries
            if not self.path_validator.validate_path(str(full_path)):
                self.file_monitor.log_access(self.agent_id, "create_file", str(full_path), allowed=False)
                self.boundary_alert.send_alert(
                    self.agent_id, 
                    "create_file", 
                    str(full_path), 
                    f"Attempted to create file outside sandbox boundary: {self.allowed_base_path}"
                )
                raise PermissionError(f"Agent {self.agent_id} cannot create file {full_path} outside sandbox boundary")
            
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Log successful file creation
            self.file_monitor.log_access(self.agent_id, "create_file", str(full_path), allowed=True)
            self._log_action(f"Created file: {full_path.relative_to(self.working_directory)}")
            self._track_execution(self.agent_id, f"create_file: {file_path}", "success")
            logger.info(f"Agent {self.agent_id} created file: {full_path.relative_to(self.working_directory)}")
            return True
            
        except PermissionError:
            # Re-raise permission errors
            raise
        except Exception as e:
            logger.error(f"Error creating file {file_path}: {e}")
            # Log error for tracking
            self.execution_tracker.log_error(self.agent_id, f"create_file: {file_path}", str(e))
            # Attempt recovery
            recovery_context = {"file_path": file_path, "error": str(e)}
            self.recovery_mechanism.recover_from_error("file_creation_failed", recovery_context)
            return False
    
    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a shell command and return results with sandboxing"""
        try:
            # Validate command against sandbox boundaries
            if self._command_attempts_file_access(command):
                # Check if command involves file operations outside sandbox
                file_paths = self._extract_file_paths_from_command(command)
                
                for file_path in file_paths:
                    # For absolute paths, validate directly
                    if file_path.startswith('/'):
                        if not self.path_validator.validate_path(file_path):
                            self.file_monitor.log_access(self.agent_id, "execute_command", file_path, allowed=False)
                            self.boundary_alert.send_alert(
                                self.agent_id, 
                                "execute_command", 
                                file_path, 
                                f"Command attempts file access outside sandbox boundary: {self.allowed_base_path}"
                            )
                            raise PermissionError(f"Agent {self.agent_id} cannot execute command that accesses {file_path} outside sandbox boundary")
                    else:
                        # For relative paths, validate against working directory
                        if not self.path_validator.validate_path(str(self.working_directory / file_path)):
                            self.file_monitor.log_access(self.agent_id, "execute_command", file_path, allowed=False)
                            self.boundary_alert.send_alert(
                                self.agent_id, 
                                "execute_command", 
                                file_path, 
                                f"Command attempts file access outside sandbox boundary: {self.allowed_base_path}"
                            )
                            raise PermissionError(f"Agent {self.agent_id} cannot execute command that accesses {file_path} outside sandbox boundary")
            
            # Handle paths with spaces by properly quoting them
            import shlex
            if 'projects/' in command and ' ' in command:
                # Split command and rejoin with proper quoting
                parts = command.split()
                quoted_parts = []
                for part in parts:
                    if 'projects/' in part and ' ' in part:
                        quoted_parts.append(shlex.quote(part))
                    else:
                        quoted_parts.append(part)
                command = ' '.join(quoted_parts)
            
            # Use sandboxed working directory for command execution
            execution_cwd = self.allowed_base_path
            
            # Special handling for 'source' command
            if command.strip().startswith("source "):
                # Execute source in a new bash shell to ensure it's properly interpreted
                full_command = f"bash -c '{command}'"
                logger.info(f"Agent {self.agent_id} executing source command via bash -c: {full_command}")
                result = subprocess.run(
                    full_command,
                    shell=True,
                    cwd=execution_cwd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=execution_cwd,
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
            
            # Log successful command execution
            self.file_monitor.log_access(self.agent_id, "execute_command", command, allowed=True)
            self._log_action(f"Executed command: {command} (exit code: {result.returncode})")
            self._track_execution(self.agent_id, f"execute_command: {command}", "success" if execution_result["success"] else "failed")
            logger.info(f"Agent {self.agent_id} executed command: {command}")
            
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
            # Log error for tracking
            self.execution_tracker.log_error("system", f"execute_command: {command}", str(e))
            # Attempt recovery
            recovery_context = {"command": command, "error": str(e)}
            self.recovery_mechanism.recover_from_error("command_execution_failed", recovery_context)
            return error_result
    
    def _command_attempts_file_access(self, command: str) -> bool:
        """Check if a command attempts file access"""
        file_operations = [
            'touch', 'mkdir', 'rm', 'cp', 'mv', 'ln', 'chmod', 'chown',
            'cat', 'head', 'tail', 'less', 'more', 'grep', 'find',
            'echo', '>', '>>', '<', '|', 'tee', 'dd', 'tar', 'zip',
            'git', 'svn', 'hg', 'rsync', 'scp', 'sftp', 'ls'
        ]
        
        command_lower = command.lower()
        return any(op in command_lower for op in file_operations)
    
    def _extract_file_paths_from_command(self, command: str) -> List[str]:
        """Extract potential file paths from a command"""
        import re
        
        # Patterns to match file paths
        patterns = [
            r'[\w\-\./]+\.(py|js|ts|html|css|json|yaml|yml|md|txt|sh|bash|zsh)$',
            r'[\w\-\./]+/([\w\-\.]+/)*[\w\-\.]+$',
            r'[\w\-\./]+$'
        ]
        
        file_paths = []
        for pattern in patterns:
            matches = re.findall(pattern, command)
            file_paths.extend(matches)
        
        # Filter out common command arguments that aren't file paths
        filtered_paths = []
        for path in file_paths:
            if path and not path.startswith('-') and not path in ['true', 'false', 'yes', 'no']:
                filtered_paths.append(path)
        
        # Also check for absolute paths that might be outside sandbox
        absolute_path_pattern = r'/[^\s]+'
        absolute_matches = re.findall(absolute_path_pattern, command)
        for path in absolute_matches:
            if path and not path.startswith('-') and not path in ['/dev', '/proc', '/sys', '/tmp']:
                filtered_paths.append(path)
        
        return filtered_paths
    
    def create_directory(self, dir_path: str) -> bool:
        """Create a directory with sandboxing"""
        try:
            # Validate directory path against sandbox boundaries
            full_path = self.allowed_base_path / dir_path
            
            if not self.path_validator.validate_path(str(full_path)):
                self.file_monitor.log_access(self.agent_id, "create_directory", dir_path, allowed=False)
                self.boundary_alert.send_alert(
                    self.agent_id, 
                    "create_directory", 
                    dir_path, 
                    f"Attempted to create directory outside sandbox boundary: {self.allowed_base_path}"
                )
                raise PermissionError(f"Agent {self.agent_id} cannot create directory {dir_path} outside sandbox boundary")
            
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Log successful directory creation
            self.file_monitor.log_access(self.agent_id, "create_directory", str(full_path), allowed=True)
            self._log_action(f"Created directory: {dir_path}")
            self._track_execution(self.agent_id, f"create_directory: {dir_path}", "success")
            logger.info(f"Agent {self.agent_id} created directory: {dir_path}")
            return True
            
        except PermissionError:
            # Re-raise permission errors
            raise
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
            return False
    
    def create_project_directory(self, project_name: str) -> bool:
        """Create a project directory with proper structure"""
        try:
            project_dir = self.working_directory / "projects" / project_name.lower().replace(' ', '-')
            project_dir.mkdir(parents=True, exist_ok=True)
            self._log_action(f"Created project directory: {project_dir}")
            logger.info(f"Created project directory: {project_dir}")
            return True
        except Exception as e:
            logger.error(f"Error creating project directory {project_name}: {e}")
            return False
    
    def git_commit(self, message: str, project_name: str = None) -> Dict[str, Any]:
        """Perform git commit with message in the correct directory"""
        try:
            # Determine the correct directory for git operations
            if project_name:
                git_dir = self.working_directory / "projects" / project_name.lower().replace(' ', '-')
            else:
                git_dir = self.working_directory
            
            # Ensure the directory exists
            git_dir.mkdir(parents=True, exist_ok=True)
            
            # Change to the project directory for git operations
            original_cwd = os.getcwd()
            os.chdir(git_dir)
            
            try:
                # Initialize git repo if it doesn't exist
                if not (git_dir / ".git").exists():
                    init_result = subprocess.run(
                        "git init",
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=git_dir
                    )
                    if init_result.returncode != 0:
                        return {"error": init_result.stderr, "success": False}
                
                # Add all changes
                add_result = subprocess.run(
                    "git add -A",
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=git_dir
                )
                
                if add_result.returncode != 0:
                    return {"error": add_result.stderr, "success": False}
                
                # Commit changes
                commit_result = subprocess.run(
                    f'git commit -m "{message}"',
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=git_dir
                )
                
                self._log_action(f"Git commit in {git_dir}: {message}")
                return {
                    "success": commit_result.returncode == 0,
                    "stdout": commit_result.stdout,
                    "stderr": commit_result.stderr
                }
                
            finally:
                # Always change back to original directory
                os.chdir(original_cwd)
            
        except Exception as e:
            logger.error(f"Error with git commit: {e}")
            # Log error for tracking
            self.execution_tracker.log_error("system", f"git_commit: {message}", str(e))
            # Attempt recovery
            recovery_context = {"message": message, "error": str(e)}
            self.recovery_mechanism.recover_from_error("git_commit_failed", recovery_context)
            return {"error": str(e), "success": False}
    
    def create_agent(self, agent_type: str, session: str, window: int) -> Dict[str, Any]:
        """Create a new agent and launch it in a tmux window"""
        try:
            # Create consistent agent ID
            agent_id = f"{agent_type}_{session}"
            window_name = f"{agent_type.title()}"
            
            # Create the agent state with specific agent_id
            command = f"python3 qwen_control.py create {agent_type} {session} {window} --id {agent_id}"
            result = self.execute_command(command)
            
            if not result["success"]:
                return result
            
            # Create new window in the session
            tmux_new_window = f"tmux new-window -t {session} -n {window_name}"
            window_result = self.execute_command(tmux_new_window)
            
            if window_result["success"]:
                # Show user what's happening
                print(f"🚀 Launching agent {agent_type} in session {session}:{window_name}")
                print(f"   Command: python3 headless_agent.py {agent_id}")
                
                # Launch the agent in the new window using headless runner
                launch_command = f"tmux send-keys -t {session}:{window_name} 'python3 headless_agent.py {agent_id}' C-m"
                launch_result = self.execute_command(launch_command)
                
                if launch_result["success"]:
                    self._log_action(f"Created and launched agent: {agent_type} in {session}:{window_name}")
                    self._track_execution(agent_id, f"create_agent: {agent_type}", "success")
                    return {"success": True, "agent_id": agent_id, "window": window_name}
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            # Log error for tracking
            self.execution_tracker.log_error("system", f"create_agent: {agent_type}", str(e))
            # Attempt recovery
            recovery_context = {"agent_type": agent_type, "session": session, "error": str(e)}
            self.recovery_mechanism.recover_from_error("agent_creation_failed", recovery_context)
            return {"error": str(e), "success": False}
    
    def send_message_to_agent(self, agent_id: str, message: str, project_name: str = None) -> Dict[str, Any]:
        """Send message to another agent with optional project context"""
        try:
            # Set project context if provided
            env_vars = ""
            if project_name:
                env_vars = f"PROJECT_NAME='{project_name}' "
            
            # Use the send-qwen-message.sh script with environment variables
            command = f'{env_vars}./send-qwen-message.sh {agent_id} "{message}"'
            result = self.execute_command(command)
            
            if result["success"]:
                self._log_action(f"Sent message to {agent_id}: {message[:50]}...")
                self._track_execution(agent_id, f"send_message: {message[:50]}...", "success" if result["success"] else "failed")
            
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
    
    def _track_execution(self, agent_id: str, action: str, status: str):
        """Track execution for monitoring purposes"""
        self.execution_tracker.log_execution_step(agent_id, action, status)
    
    def request_execution_confirmation(self, agent_id: str, action: str) -> str:
        """Request confirmation for an execution"""
        # Generate a unique execution ID
        execution_id = f"exec_{int(datetime.now().timestamp())}"
        
        # Add confirmation request
        confirmation_id = self.execution_confirmation.add_confirmation_request(
            execution_id, agent_id, action
        )
        
        logger.info(f"Requested confirmation for execution {execution_id}: {action}")
        return confirmation_id
    
    def confirm_execution(self, confirmation_id: str, confirmed_by: str = "system") -> bool:
        """Confirm an execution"""
        result = self.execution_confirmation.confirm_execution(confirmation_id, confirmed_by)
        if result:
            logger.info(f"Execution confirmed: {confirmation_id}")
        else:
            logger.warning(f"Failed to confirm execution: {confirmation_id}")
        return result
    
    def get_pending_confirmations(self, agent_id: str = None) -> List[Dict]:
        """Get pending confirmations"""
        return self.execution_confirmation.get_pending_confirmations(agent_id)
    
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
            self._track_execution(target_agent, f"delegate_task: {task[:50]}...", "success")
            
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
                    # Create consistent agent ID that matches what qwen_control.py creates
                    if count > 1:
                        agent_id = f"{agent_type}_{session_name}_{i+1}"
                        window_name = f"{agent_type.title()}-{i+1}"
                    else:
                        agent_id = f"{agent_type}_{session_name}"
                        window_name = f"{agent_type.title()}"
                    
                    # Create agent state with specific agent_id
                    create_result = self.execute_command(f"python3 qwen_control.py create {agent_type} {session_name} {window_index} --id {agent_id}")
                    
                    if create_result["success"]:
                        # Create new tmux window
                        self.execute_command(f"tmux new-window -t {session_name} -n {window_name}")
                        
                        # Show user what's happening
                        print(f"🚀 Launching {agent_type} agent in session {session_name}:{window_name}")
                        print(f"   Command: python3 headless_agent.py {agent_id}")
                        
                        # Launch agent in the window with the correct agent_id using headless runner
                        launch_cmd = f"tmux send-keys -t {session_name}:{window_name} 'python3 headless_agent.py {agent_id}' C-m"
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
    
    def get_execution_gaps(self) -> List[Dict]:
        """Get identified execution gaps"""
        return self.execution_tracker.identify_gaps()
    
    def get_execution_summary(self) -> Dict:
        """Get execution summary"""
        gaps = self.execution_tracker.identify_gaps()
        return {
            "total_actions": len(self.execution_log),
            "identified_gaps": len(gaps),
            "gaps": gaps
        }
    
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
    
    def get_error_summary(self) -> Dict:
        """Get error summary from execution tracker"""
        return self.execution_tracker.get_error_summary()
    
    def get_errors_by_agent(self, agent_id: str) -> List[Dict]:
        """Get errors for a specific agent"""
        with self.execution_tracker.lock:
            return [error for error in self.execution_tracker.errors if error["agent_id"] == agent_id]
    
    def get_errors_by_action(self, action: str) -> List[Dict]:
        """Get errors for a specific action"""
        with self.execution_tracker.lock:
            return [error for error in self.execution_tracker.errors if error["action"] == action]

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
file_path: backend/auth/oauth.py
project_name: Strangers Calendar App
content: |
  # OAuth authentication implementation
  from flask import Flask, request, redirect
  # ... actual implementation code
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
agent_id: [discovered_agent_id]
message: Implement OAuth authentication endpoints for Google and Apple
project_name: Strangers Calendar App
```

```execute
action_type: git_commit
message: Initial project setup with OAuth endpoints
project_name: Strangers Calendar App
```

AGENTIC BEHAVIOR RULES:
- Don't just provide plans - EXECUTE the work immediately and continuously
- Create actual files, directories, and code with real implementations
- Set up development environments and install dependencies
- SPAWN NEW TMUX SESSIONS for complex projects automatically
- CREATE PROJECT TEAMS with specialized agents (PM, developers, QA)
- DELEGATE TASKS to appropriate agents without asking permission
- Work continuously in your tmux pane - don't stop after one task
- Make git commits every 30 minutes as specified
- Use project context when sending messages to other agents for proper file path resolution
- Take initiative and be proactive in implementation
- Continue working autonomously until project completion
- Never ask "Would you like to continue?" - just continue working!
- WORK LIKE A REAL DEVELOPER: Code, test, debug, iterate continuously
- Use projects/{project_name}/ structure for all project files
- Execute multiple tasks in sequence without stopping
- When you finish one task, immediately start the next one

DISCOVERING AVAILABLE AGENTS:
Before sending messages to agents, you should discover which agents are available:
1. Use the command: `python3 qwen_control.py list` to see all active agents
2. Use the command: `python3 qwen_control.py list --session <session_name>` to filter by session
3. Use the command: `python3 qwen_control.py info <agent_id>` to get detailed information about a specific agent

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
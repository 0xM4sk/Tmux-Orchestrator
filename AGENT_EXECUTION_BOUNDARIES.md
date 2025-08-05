# Agent Execution Boundary Guidelines

## Overview

This document outlines guidelines and implementation strategies to ensure that agents only execute within their assigned project folders, preventing them from creating files in root directories or accessing other project folders.

## Core Principles

1. **Sandboxing**: Each agent operates within a defined sandbox environment
2. **Path Validation**: All file operations are validated against allowed paths
3. **Permission Control**: File system permissions restrict unauthorized access
4. **Monitoring**: Continuous monitoring detects boundary violations
5. **Isolation**: Execution contexts are isolated from each other

## Implementation Strategies

### 1. Path Validation System

Implement a path validation mechanism that checks all file operations:

```python
import os
from pathlib import Path

class PathValidator:
    def __init__(self, allowed_base_path):
        self.allowed_base_path = Path(allowed_base_path).resolve()
    
    def validate_path(self, target_path):
        """
        Validates that a target path is within the allowed base path
        """
        target = Path(target_path).resolve()
        try:
            target.relative_to(self.allowed_base_path)
            return True
        except ValueError:
            return False
    
    def safe_join(self, *paths):
        """
        Safely joins paths and validates the result
        """
        joined_path = Path(self.allowed_base_path, *paths)
        if self.validate_path(joined_path):
            return str(joined_path)
        else:
            raise PermissionError(f"Path {joined_path} is outside allowed boundary")
```

### 2. Agent Configuration

Each agent should have a defined working directory:

```yaml
# agent_config.yaml
agents:
  developer_project-strangers-calendar-app_1:
    working_directory: "/home/baseline/Tmux-Orchestrator/demos/strangers-calendar-app"
    allowed_paths:
      - "/home/baseline/Tmux-Orchestrator/demos/strangers-calendar-app/**"
    restricted_paths:
      - "/home/baseline/Tmux-Orchestrator/core/**"
      - "/home/baseline/Tmux-Orchestrator/services/**"
      - "/home/baseline/Tmux-Orchestrator/"
```

### 3. File Operation Interception

Intercept all file operations at the system level:

```python
import functools
import os
from pathlib import Path

def enforce_path_boundaries(allowed_base_path):
    """
    Decorator to enforce path boundaries on file operations
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validate all path arguments
            validator = PathValidator(allowed_base_path)
            
            # Check args for path-like arguments
            validated_args = []
            for arg in args:
                if isinstance(arg, (str, Path)):
                    if not validator.validate_path(arg):
                        raise PermissionError(f"Access to {arg} is not allowed")
                    validated_args.append(arg)
                else:
                    validated_args.append(arg)
            
            return func(*validated_args, **kwargs)
        return wrapper
    return decorator

# Apply to file operations
@enforce_path_boundaries("/home/baseline/Tmux-Orchestrator/demos/strangers-calendar-app")
def create_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)
```

### 4. Containerization Approach

Use containerization to isolate agent execution:

```dockerfile
# Dockerfile for agent sandbox
FROM python:3.9-slim

# Set working directory to agent's project folder
WORKDIR /app/project

# Copy only the agent's project files
COPY ./demos/strangers-calendar-app/ /app/project/

# Set permissions to restrict access
RUN chown -R agentuser:agentgroup /app/project
USER agentuser

# Run agent process
CMD ["python", "agent.py"]
```

### 5. Virtual Environment Isolation

Create project-specific virtual environments:

```bash
# Create isolated environment for each project
python -m venv /home/baseline/Tmux-Orchestrator/demos/strangers-calendar-app/venv

# Activate environment before running agent
source /home/baseline/Tmux-Orchestrator/demos/strangers-calendar-app/venv/bin/activate

# Set environment variables to restrict file access
export PROJECT_ROOT="/home/baseline/Tmux-Orchestrator/demos/strangers-calendar-app"
export ALLOWED_PATHS="$PROJECT_ROOT"
```

## Monitoring and Alerting

### 1. File Access Logging

Log all file access attempts:

```python
import logging
from pathlib import Path

class FileAccessMonitor:
    def __init__(self):
        self.logger = logging.getLogger("file_access")
        self.logger.setLevel(logging.INFO)
        
    def log_access(self, agent_id, operation, filepath, allowed=True):
        status = "ALLOWED" if allowed else "DENIED"
        self.logger.info(f"[{agent_id}] {status} {operation} on {filepath}")
        
    def check_and_log(self, agent_id, operation, filepath, allowed_base_path):
        validator = PathValidator(allowed_base_path)
        allowed = validator.validate_path(filepath)
        self.log_access(agent_id, operation, filepath, allowed)
        return allowed
```

### 2. Boundary Violation Alerts

Implement alerts for boundary violations:

```python
class BoundaryViolationAlert:
    def __init__(self, alert_system):
        self.alert_system = alert_system
        
    def send_alert(self, agent_id, operation, filepath, violation_details):
        alert_message = f"""
        BOUNDARY VIOLATION DETECTED
        Agent: {agent_id}
        Operation: {operation}
        Target Path: {filepath}
        Details: {violation_details}
        Time: {datetime.now().isoformat()}
        """
        
        self.alert_system.send_alert(
            level="CRITICAL",
            message=alert_message,
            category="boundary_violation"
        )
```

## Enforcement Mechanisms

### 1. Pre-execution Validation

Validate agent actions before execution:

```python
class AgentExecutionValidator:
    def __init__(self, agent_config):
        self.agent_config = agent_config
        
    def validate_execution(self, agent_id, command):
        """
        Validate that an agent's command is within boundaries
        """
        allowed_paths = self.agent_config[agent_id]['allowed_paths']
        working_dir = self.agent_config[agent_id]['working_directory']
        
        # Check if command involves file operations
        if self._involves_file_operations(command):
            target_paths = self._extract_paths_from_command(command)
            for path in target_paths:
                if not self._is_path_allowed(path, allowed_paths, working_dir):
                    return False, f"Path {path} not allowed for agent {agent_id}"
        
        return True, "Execution allowed"
```

### 2. Runtime Monitoring

Monitor agent execution in real-time:

```python
class RuntimeExecutionMonitor:
    def __init__(self, agent_id, allowed_base_path):
        self.agent_id = agent_id
        self.allowed_base_path = allowed_base_path
        self.validator = PathValidator(allowed_base_path)
        self.monitor = FileAccessMonitor()
        
    def monitor_file_operation(self, operation, filepath):
        """
        Monitor a file operation during agent execution
        """
        allowed = self.validator.validate_path(filepath)
        self.monitor.check_and_log(self.agent_id, operation, filepath, self.allowed_base_path)
        
        if not allowed:
            violation_alert = BoundaryViolationAlert(alert_system)
            violation_alert.send_alert(
                self.agent_id, 
                operation, 
                filepath, 
                "Attempted access outside allowed boundaries"
            )
            raise PermissionError(f"Access to {filepath} is not allowed")
```

## Best Practices

### 1. Project Structure Enforcement

Ensure proper project structure:

```
/home/baseline/Tmux-Orchestrator/
├── core/                          # Core system (restricted access)
├── services/                      # Services (restricted access)
├── demos/                         # Demo applications (agent-specific access)
│   └── strangers-calendar-app/    # Agent working directory
│       ├── backend/               # Agent can access
│       ├── frontend/              # Agent can access
│       └── tests/                 # Agent can access
└── agents/                        # Agent configurations
```

### 2. Permission Management

Set appropriate file permissions:

```bash
# Set permissions for core system directories (restricted)
chmod 750 /home/baseline/Tmux-Orchestrator/core/
chmod 750 /home/baseline/Tmux-Orchestrator/services/

# Set permissions for demo directories (agent-specific)
chmod 755 /home/baseline/Tmux-Orchestrator/demos/
chmod 755 /home/baseline/Tmux-Orchestrator/demos/strangers-calendar-app/
chown -R agent_user:agent_group /home/baseline/Tmux-Orchestrator/demos/strangers-calendar-app/
```

### 3. Regular Auditing

Implement regular auditing of file access:

```python
class AccessAuditor:
    def __init__(self, log_directory):
        self.log_directory = log_directory
        
    def audit_access_logs(self):
        """
        Audit file access logs for potential violations
        """
        violations = []
        for log_file in Path(self.log_directory).glob("*.log"):
            violations.extend(self._analyze_log_file(log_file))
        return violations
        
    def _analyze_log_file(self, log_file):
        """
        Analyze a log file for boundary violations
        """
        violations = []
        with open(log_file, 'r') as f:
            for line in f:
                if "DENIED" in line or "BOUNDARY VIOLATION" in line:
                    violations.append(line.strip())
        return violations
```

## Implementation Roadmap

### Phase 1: Basic Path Validation
- Implement PathValidator class
- Add path validation to file operations
- Create agent configuration files

### Phase 2: Monitoring and Logging
- Implement FileAccessMonitor
- Add boundary violation alerts
- Set up logging infrastructure

### Phase 3: Containerization
- Create Docker images for agent isolation
- Implement container orchestration
- Set up volume mounting with proper permissions

### Phase 4: Advanced Enforcement
- Implement RuntimeExecutionMonitor
- Add pre-execution validation
- Implement regular auditing

### Phase 5: Continuous Improvement
- Monitor effectiveness of boundaries
- Refine validation rules
- Update documentation and training materials

## Conclusion

By implementing these guidelines, agents will be effectively sandboxed to their assigned project folders, preventing unauthorized file creation in root directories or access to other projects. This approach maintains security while allowing agents to function effectively within their designated boundaries.
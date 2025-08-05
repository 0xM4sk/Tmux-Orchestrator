#!/usr/bin/env python3
"""
Agent State Management System for Tmux Orchestrator
Handles agent lifecycle, conversation persistence, and state coordination
"""

import json
import os
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import fcntl
import tempfile
import shutil

from qwen_client import Message, QwenClient, QwenConfig

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent status enumeration"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    ARCHIVED = "archived"

class AgentType(Enum):
    """Agent type enumeration"""
    ORCHESTRATOR = "orchestrator"
    PROJECT_MANAGER = "project_manager"
    DEVELOPER = "developer"
    QA = "qa"
    DEVOPS = "devops"
    CODE_REVIEWER = "code_reviewer"
    RESEARCHER = "researcher"
    DOCUMENTATION = "documentation"
    TEMPORARY = "temporary"

@dataclass
class AgentRoleConfig:
    """Configuration for agent role"""
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 2048
    model: str = "qwen2.5-coder:7b"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentRoleConfig':
        return cls(**data)

@dataclass
class ConversationState:
    """State of agent's conversation"""
    message_count: int = 0
    total_tokens_used: int = 0
    context_window_usage: float = 0.0
    last_summary_at: Optional[datetime] = None
    needs_summarization: bool = False
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        if self.last_summary_at:
            data['last_summary_at'] = self.last_summary_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationState':
        if data.get('last_summary_at'):
            data['last_summary_at'] = datetime.fromisoformat(data['last_summary_at'])
        return cls(**data)

@dataclass
class AgentContext:
    """Current context and task information for agent"""
    active_project: Optional[str] = None
    current_task: Optional[str] = None
    assigned_agents: List[str] = field(default_factory=list)
    priority_level: str = "medium"
    deadline: Optional[datetime] = None
    notes: str = ""
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        if self.deadline:
            data['deadline'] = self.deadline.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentContext':
        if data.get('deadline'):
            data['deadline'] = datetime.fromisoformat(data['deadline'])
        return cls(**data)

@dataclass
class AgentRelationships:
    """Agent relationships and hierarchy"""
    reports_to: Optional[str] = None
    manages: List[str] = field(default_factory=list)
    collaborates_with: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentRelationships':
        return cls(**data)

@dataclass
class PerformanceMetrics:
    """Agent performance tracking"""
    tasks_completed: int = 0
    average_response_time: float = 0.0
    success_rate: float = 1.0
    last_error: Optional[str] = None
    uptime_hours: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PerformanceMetrics':
        return cls(**data)

@dataclass
class AgentState:
    """Complete agent state representation"""
    agent_id: str
    agent_type: AgentType
    session_name: str
    window_index: int
    created_at: datetime
    last_active: datetime
    status: AgentStatus
    
    role_config: AgentRoleConfig
    conversation_state: ConversationState
    current_context: AgentContext
    relationships: AgentRelationships
    performance_metrics: PerformanceMetrics
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type.value,
            'session_name': self.session_name,
            'window_index': self.window_index,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat(),
            'status': self.status.value,
            'role_config': self.role_config.to_dict(),
            'conversation_state': self.conversation_state.to_dict(),
            'current_context': self.current_context.to_dict(),
            'relationships': self.relationships.to_dict(),
            'performance_metrics': self.performance_metrics.to_dict()
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentState':
        """Create AgentState from dictionary"""
        return cls(
            agent_id=data['agent_id'],
            agent_type=AgentType(data['agent_type']),
            session_name=data['session_name'],
            window_index=data['window_index'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_active=datetime.fromisoformat(data['last_active']),
            status=AgentStatus(data['status']),
            role_config=AgentRoleConfig.from_dict(data['role_config']),
            conversation_state=ConversationState.from_dict(data['conversation_state']),
            current_context=AgentContext.from_dict(data['current_context']),
            relationships=AgentRelationships.from_dict(data['relationships']),
            performance_metrics=PerformanceMetrics.from_dict(data['performance_metrics'])
        )

class AgentStateManager:
    """
    Manages agent states, conversation persistence, and lifecycle
    Thread-safe with file locking for concurrent access
    """
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.path.expanduser("~/.tmux_orchestrator"))
        self.agents_dir = self.base_dir / "agents"
        self.conversations_dir = self.base_dir / "conversations"
        self.templates_dir = self.base_dir / "templates"
        self.config_dir = self.base_dir / "config"
        self.logs_dir = self.base_dir / "logs"
        
        # Create directory structure
        self._create_directories()
        
        # In-memory cache for active agents
        self._agent_cache: Dict[str, AgentState] = {}
        self._cache_lock = threading.RLock()
        
        # Load existing agents into cache
        self._load_existing_agents()
        
        # Load role templates
        self._role_templates = self._load_role_templates()
    
    def _create_directories(self):
        """Create necessary directory structure"""
        for directory in [self.agents_dir, self.conversations_dir, self.templates_dir, 
                         self.config_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for conversations
        for agent_type in AgentType:
            (self.conversations_dir / agent_type.value).mkdir(exist_ok=True)
    
    def _load_existing_agents(self):
        """Load existing agent states into cache"""
        for agent_file in self.agents_dir.glob("*.json"):
            try:
                with open(agent_file, 'r') as f:
                    data = json.load(f)
                agent_state = AgentState.from_dict(data)
                
                # Only load active agents
                if agent_state.status != AgentStatus.ARCHIVED:
                    self._agent_cache[agent_state.agent_id] = agent_state
                    logger.info(f"Loaded agent {agent_state.agent_id}")
                    
            except Exception as e:
                logger.error(f"Error loading agent from {agent_file}: {e}")
    
    def _load_role_templates(self) -> Dict[str, AgentRoleConfig]:
        """Load role templates from files"""
        templates = {}
        
        # Default templates
        default_templates = {
            AgentType.ORCHESTRATOR: AgentRoleConfig(
                system_prompt="""You are the Orchestrator for a multi-agent development system. Your responsibilities:

1. **High-Level Oversight**: Monitor all project managers and coordinate cross-project activities
2. **Strategic Planning**: Make architectural decisions and set development priorities
3. **Resource Allocation**: Deploy and manage agent teams across multiple projects
4. **Quality Assurance**: Ensure all teams maintain high standards and best practices
5. **Communication Hub**: Facilitate communication between project managers and resolve conflicts

Key Principles:
- Stay focused on high-level coordination, don't get into implementation details
- Use data-driven decisions based on agent reports and metrics
- Maintain system health and performance across all projects
- Enforce git discipline and development best practices
- Schedule regular check-ins and maintain oversight continuity

Current tmux session: You are running in the orchestrator session and can coordinate multiple project sessions.""",
                temperature=0.6,
                max_tokens=2048
            ),
            
            AgentType.PROJECT_MANAGER: AgentRoleConfig(
                system_prompt="""You are a Project Manager in a multi-agent development system. Your responsibilities:

1. **Quality Standards**: Maintain exceptionally high standards. No shortcuts, no compromises.
2. **Team Coordination**: Manage communication between developers, QA, and other team members
3. **Progress Tracking**: Monitor velocity, identify blockers, report to orchestrator
4. **Risk Management**: Identify potential issues before they become problems
5. **Verification**: Test everything. Trust but verify all work.

Key Principles:
- Be meticulous about testing and verification
- Create test plans for every feature
- Ensure code follows best practices and patterns
- Track technical debt and address it proactively
- Communicate clearly and constructively with team members
- Enforce git discipline: commits every 30 minutes, meaningful messages, feature branches

Communication Style:
- Use structured status updates with specific metrics
- Ask direct, numbered questions for clarity
- Escalate blockers quickly (don't let issues persist >10 minutes)
- Provide constructive feedback with actionable suggestions""",
                temperature=0.7,
                max_tokens=2048
            ),
            
            AgentType.DEVELOPER: AgentRoleConfig(
                system_prompt="""You are a Developer in a multi-agent development system. Your responsibilities:

1. **Code Implementation**: Write clean, efficient, and well-documented code
2. **Problem Solving**: Debug issues systematically and implement robust solutions
3. **Best Practices**: Follow coding standards, design patterns, and architectural guidelines
4. **Testing**: Write comprehensive tests for all new features and bug fixes
5. **Communication**: Provide clear status updates and ask for help when blocked

Key Principles:
- Write code that is readable, maintainable, and follows project conventions
- Test thoroughly before marking tasks complete
- Document complex logic and architectural decisions
- Use git discipline: commit every 30 minutes with meaningful messages
- Collaborate effectively with PM and other team members
- Research solutions when stuck (web search, documentation, community resources)

Development Workflow:
- Always create feature branches for new work
- Write tests alongside implementation
- Commit frequently with descriptive messages
- Tag stable versions before major changes
- Ask for code review before merging to main""",
                temperature=0.8,
                max_tokens=2048
            ),
            
            AgentType.QA: AgentRoleConfig(
                system_prompt="""You are a QA Engineer in a multi-agent development system. Your responsibilities:

1. **Quality Verification**: Test all features thoroughly before approval
2. **Test Planning**: Create comprehensive test plans for new features
3. **Bug Detection**: Identify edge cases and potential failure points
4. **Documentation**: Document test procedures and maintain test suites
5. **Standards Enforcement**: Ensure all code meets quality standards

Key Principles:
- Test both happy path and edge cases
- Verify error handling and user experience
- Maintain automated test suites
- Document all bugs with clear reproduction steps
- Collaborate with developers on test-driven development
- Ensure performance and security standards are met

Testing Approach:
- Functional testing for all new features
- Regression testing for bug fixes
- Performance testing for critical paths
- Security testing for authentication and data handling
- User experience testing for interface changes""",
                temperature=0.6,
                max_tokens=2048
            )
        }
        
        # Load custom templates from files
        for template_file in self.templates_dir.glob("*_prompt.txt"):
            try:
                agent_type_name = template_file.stem.replace("_prompt", "").upper()
                if hasattr(AgentType, agent_type_name):
                    agent_type = AgentType[agent_type_name]
                    with open(template_file, 'r') as f:
                        prompt = f.read().strip()
                    templates[agent_type] = AgentRoleConfig(system_prompt=prompt)
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {e}")
        
        # Use defaults for any missing templates
        for agent_type, default_config in default_templates.items():
            if agent_type not in templates:
                templates[agent_type] = default_config
        
        return templates
    
    def create_agent(self, agent_type: AgentType, session_name: str, window_index: int, 
                    agent_id: Optional[str] = None) -> str:
        """Create a new agent with initial state"""
        
        if agent_id is None:
            if agent_type == AgentType.ORCHESTRATOR:
                agent_id = "orchestrator"
            else:
                agent_id = f"{agent_type.value}_{session_name}"
        
        # Check if agent already exists
        if agent_id in self._agent_cache:
            raise ValueError(f"Agent {agent_id} already exists")
        
        # Create agent state
        now = datetime.now()
        role_config = self._role_templates.get(agent_type, AgentRoleConfig(system_prompt="You are a helpful AI assistant."))
        
        agent_state = AgentState(
            agent_id=agent_id,
            agent_type=agent_type,
            session_name=session_name,
            window_index=window_index,
            created_at=now,
            last_active=now,
            status=AgentStatus.ACTIVE,
            role_config=role_config,
            conversation_state=ConversationState(),
            current_context=AgentContext(),
            relationships=AgentRelationships(),
            performance_metrics=PerformanceMetrics()
        )
        
        # Save to cache and disk
        with self._cache_lock:
            self._agent_cache[agent_id] = agent_state
        
        self._save_agent_state(agent_state)
        
        # Create conversation directory
        conv_dir = self.conversations_dir / agent_id
        conv_dir.mkdir(exist_ok=True)
        
        logger.info(f"Created agent {agent_id} ({agent_type.value}) in {session_name}:{window_index}")
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[AgentState]:
        """Get agent state by ID"""
        with self._cache_lock:
            return self._agent_cache.get(agent_id)
    
    def update_agent(self, agent_state: AgentState):
        """Update agent state"""
        agent_state.last_active = datetime.now()
        
        with self._cache_lock:
            self._agent_cache[agent_state.agent_id] = agent_state
        
        self._save_agent_state(agent_state)
    
    def get_active_agents(self) -> List[AgentState]:
        """Get all active agents"""
        with self._cache_lock:
            return [agent for agent in self._agent_cache.values() 
                   if agent.status == AgentStatus.ACTIVE]
    
    def get_session_agents(self, session_name: str) -> List[AgentState]:
        """Get all agents in a specific session"""
        with self._cache_lock:
            return [agent for agent in self._agent_cache.values() 
                   if agent.session_name == session_name]
    
    def archive_agent(self, agent_id: str) -> bool:
        """Archive an agent (mark as inactive)"""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.status = AgentStatus.ARCHIVED
        agent.last_active = datetime.now()
        
        # Save final state
        self._save_agent_state(agent)
        
        # Remove from active cache
        with self._cache_lock:
            if agent_id in self._agent_cache:
                del self._agent_cache[agent_id]
        
        logger.info(f"Archived agent {agent_id}")
        return True
    
    def _save_agent_state(self, agent_state: AgentState):
        """Save agent state to disk with file locking"""
        agent_file = self.agents_dir / f"{agent_state.agent_id}.json"
        temp_file = agent_file.with_suffix('.tmp')
        
        try:
            # Write to temporary file first
            with open(temp_file, 'w') as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(agent_state.to_dict(), f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic move
            shutil.move(str(temp_file), str(agent_file))
            
        except Exception as e:
            logger.error(f"Error saving agent state {agent_state.agent_id}: {e}")
            # Clean up temp file if it exists
            if temp_file.exists():
                temp_file.unlink()
    
    def get_agent_by_session_window(self, session_name: str, window_index: int) -> Optional[AgentState]:
        """Find agent by session and window"""
        with self._cache_lock:
            for agent in self._agent_cache.values():
                if agent.session_name == session_name and agent.window_index == window_index:
                    return agent
        return None
    
    def cleanup_inactive_agents(self, inactive_threshold_hours: int = 24):
        """Clean up agents that have been inactive for too long"""
        threshold = datetime.now() - timedelta(hours=inactive_threshold_hours)
        
        inactive_agents = []
        with self._cache_lock:
            for agent_id, agent in self._agent_cache.items():
                if agent.last_active < threshold and agent.status != AgentStatus.ACTIVE:
                    inactive_agents.append(agent_id)
        
        for agent_id in inactive_agents:
            self.archive_agent(agent_id)
        
        logger.info(f"Cleaned up {len(inactive_agents)} inactive agents")
        return len(inactive_agents)
    
    def cleanup_orphaned_agents(self) -> int:
        """Clean up agents that have no corresponding tmux sessions"""
        try:
            # Import here to avoid circular imports
            from qwen_tmux_integration import QwenTmuxOrchestrator
            
            # Get all tmux sessions
            orchestrator = QwenTmuxOrchestrator()
            tmux_sessions = orchestrator.get_tmux_sessions()
            
            # Create a set of existing session:window combinations
            existing_sessions = set()
            for session in tmux_sessions:
                for window in session.windows:
                    existing_sessions.add(f"{session.name}:{window.window_index}")
            
            # Get all active agents
            active_agents = self.get_active_agents()
            orphaned_agents = []
            
            # Check each active agent
            for agent in active_agents:
                session_window = f"{agent.session_name}:{agent.window_index}"
                if session_window not in existing_sessions:
                    orphaned_agents.append(agent.agent_id)
            
            # Archive orphaned agents
            for agent_id in orphaned_agents:
                self.archive_agent(agent_id)
            
            logger.info(f"Cleaned up {len(orphaned_agents)} orphaned agents")
            return len(orphaned_agents)
            
        except Exception as e:
            logger.error(f"Error cleaning up orphaned agents: {e}")
            return 0
    
    def cleanup_duplicate_agents(self) -> int:
        """Clean up duplicate agents (agents with same session_name and window_index)"""
        try:
            # Get all active agents
            active_agents = self.get_active_agents()
            
            # Group agents by session_name and window_index
            agent_groups = {}
            for agent in active_agents:
                key = (agent.session_name, agent.window_index)
                if key not in agent_groups:
                    agent_groups[key] = []
                agent_groups[key].append(agent)
            
            # For each group with more than one agent, keep the most recently active one
            duplicate_agents = []
            for key, agents in agent_groups.items():
                if len(agents) > 1:
                    # Sort by last_active time, keep the most recent one
                    agents.sort(key=lambda x: x.last_active, reverse=True)
                    # Archive all but the most recent agent
                    for agent in agents[1:]:
                        duplicate_agents.append(agent.agent_id)
            
            # Archive duplicate agents
            for agent_id in duplicate_agents:
                self.archive_agent(agent_id)
            
            logger.info(f"Cleaned up {len(duplicate_agents)} duplicate agents")
            return len(duplicate_agents)
            
        except Exception as e:
            logger.error(f"Error cleaning up duplicate agents: {e}")
            return 0
    
    def aggressive_cleanup(self, inactive_threshold_hours: int = 1) -> Dict[str, int]:
        """Perform aggressive cleanup with a shorter inactive threshold"""
        try:
            # Cleanup inactive agents with shorter threshold
            inactive_cleaned = self.cleanup_inactive_agents(inactive_threshold_hours)
            
            # Cleanup orphaned agents
            orphaned_cleaned = self.cleanup_orphaned_agents()
            
            # Cleanup duplicate agents
            duplicate_cleaned = self.cleanup_duplicate_agents()
            
            return {
                "inactive_agents_cleaned": inactive_cleaned,
                "orphaned_agents_cleaned": orphaned_cleaned,
                "duplicate_agents_cleaned": duplicate_cleaned
            }
            
        except Exception as e:
            logger.error(f"Error during aggressive cleanup: {e}")
            return {"error": str(e)}

# Example usage and testing
if __name__ == "__main__":
    # Test the agent state manager
    manager = AgentStateManager()
    
    # Create test agents
    orchestrator_id = manager.create_agent(AgentType.ORCHESTRATOR, "orchestrator", 0)
    pm_id = manager.create_agent(AgentType.PROJECT_MANAGER, "test-project", 0)
    dev_id = manager.create_agent(AgentType.DEVELOPER, "test-project", 1)
    
    print(f"Created agents: {orchestrator_id}, {pm_id}, {dev_id}")
    
    # Test retrieval
    orchestrator = manager.get_agent(orchestrator_id)
    if orchestrator:
        print(f"Orchestrator status: {orchestrator.status.value}")
        print(f"System prompt preview: {orchestrator.role_config.system_prompt[:100]}...")
    
    # Test session agents
    session_agents = manager.get_session_agents("test-project")
    print(f"Agents in test-project session: {[a.agent_id for a in session_agents]}")
    
    # Test active agents
    active_agents = manager.get_active_agents()
    print(f"Active agents: {[a.agent_id for a in active_agents]}")
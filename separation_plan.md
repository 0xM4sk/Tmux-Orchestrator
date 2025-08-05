# Plan for Separating Strangers Calendar App Demo from Core Orchestrator

## Current State Analysis

### Core Orchestrator System Structure
The core orchestrator system is well-organized into distinct, loosely-coupled modules:

1. **Agent Management**: Handles agent lifecycle, creation, and registration
   - agent_factory.py
   - agent_registry.py
   - agent_state_manager.py

2. **Communication System**: Manages message routing and conversation handling
   - message_router.py
   - protocol_enforcer.py
   - conversation_manager.py

3. **Execution Tracking**: Monitors agent tasks and handles recovery
   - execution_monitor.py
   - gap_detector.py
   - recovery_manager.py

4. **Dashboard Monitoring**: Provides system metrics and alerting
   - dashboard_manager.py
   - metrics_collector.py
   - alert_system.py

5. **Data Management**: Handles data storage, processing, and validation
   - data_store.py
   - data_processor.py
   - data_validator.py

6. **Services**: Provides authentication and other cross-cutting services
   - authentication/ (auth_manager.py, token_manager.py, user_manager.py)

### Strangers Calendar App Integration Points
The Strangers Calendar App exists as a separate project within the `projects/` directory with multiple variations:
- projects/strangers-calendar-app/
- projects/Strangers Calendar App/
- projects/Strangers_Calendar_App/
- projects/strangers-calendar/

Integration points identified:
1. **Agent Task Management**: 
   - agentic_capabilities.py references the Strangers Calendar App as a project
   - headless_agent.py contains specific logic for the strangers-calendar-app project
   - task_tracker.py has hardcoded task assignments for the Strangers Calendar App

2. **Tmux Session Management**:
   - The system spawns dedicated tmux sessions for the Strangers Calendar App project

3. **Project References**:
   - Multiple files contain specific references to "strangers-calendar-app" in task assignments and agent naming

### Current Integration Issues
1. **Hardcoded Project References**: Several core files contain hardcoded references to the Strangers Calendar App project
2. **Task Assignment Coupling**: The task tracking system has specific logic for the Strangers Calendar App
3. **Directory Structure Mixing**: Multiple variations of the Strangers Calendar App exist in the projects directory
4. **Naming Inconsistency**: Different naming conventions for the same project

## Proposed Directory Structure

To achieve a clean separation between the core orchestrator system and the Strangers Calendar App demo, I propose the following directory structure:

```
/home/baseline/Tmux-Orchestrator/
├── core/                          # Core orchestrator system (unchanged)
│   ├── agent_management/
│   ├── communication_system/
│   ├── dashboard_monitoring/
│   ├── data_management/
│   ├── execution_tracking/
├── services/                      # Core services (unchanged)
│   ├── authentication/
│   ├── notification/
│   └── project_management/
├── demos/                         # NEW: Dedicated directory for all demo applications
│   └── strangers-calendar-app/    # Strangers Calendar App moved here
│       ├── backend/
│       ├── frontend/
│       ├── tests/
│       └── docs/
├── projects/                      # Project templates and examples (cleaned up)
├── docs/                          # Core documentation
├── tests/                         # Core system tests
├── README.md                      # Core system documentation
└── requirements.txt               # Core system requirements
```

### Key Changes in the Proposed Structure
1. **Dedicated Demos Directory**: All demo applications will be moved to a top-level `demos/` directory
2. **Consolidated Strangers Calendar App**: Only one canonical version of the app will be maintained
3. **Clean Projects Directory**: The projects directory will contain only templates and examples, not specific implementations
4. **Clear Separation**: Core system components remain untouched, with demos completely separated

### Benefits of This Structure
1. **Clear Boundaries**: Immediate visual separation between core system and demos
2. **Easier Maintenance**: Demos can be added/removed without affecting core system
3. **Reduced Clutter**: Eliminates multiple versions of the same demo app
4. **Improved Organization**: Logical grouping of similar components
5. **Scalability**: Easy to add new demos without impacting core system

## Detailed Migration Plan

### Phase 1: Preparation and Assessment
1. **Identify Canonical Version**
   - Determine which version of the Strangers Calendar App is the most complete and up-to-date
   - Based on file structure analysis, `projects/strangers-calendar-app/` appears to be the most complete version

2. **Backup Current State**
   - Create a backup of the entire repository before making changes
   - Document the current directory structure for reference

3. **Dependency Analysis**
   - Identify all files that reference the Strangers Calendar App
   - Document current integration points and dependencies

### Phase 2: Directory Restructuring
1. **Create New Demos Directory**
   - Create the `demos/` directory at the root level
   - Set appropriate permissions and ownership

2. **Migrate Strangers Calendar App**
   - Move the canonical version to `demos/strangers-calendar-app/`
   - Remove duplicate versions from the `projects/` directory
   - Update any internal file references within the app

3. **Clean Up Projects Directory**
   - Remove specific implementations from the `projects/` directory
   - Keep only templates and examples

### Phase 3: Codebase Updates
1. **Update Hardcoded References**
   - Modify `agentic_capabilities.py` to use dynamic project references
   - Update `headless_agent.py` to remove hardcoded project logic
   - Refactor `task_tracker.py` to use a more generic task assignment system

2. **Update Configuration Files**
   - Modify any configuration files that reference specific project paths
   - Update documentation to reflect new directory structure

3. **Update Test Files**
   - Modify tests that reference old project paths
   - Ensure all tests pass after migration

### Phase 4: Verification and Testing
1. **Core System Testing**
   - Verify that all core orchestrator functionality remains intact
   - Run integration tests to ensure no regressions

2. **Demo App Testing**
   - Verify that the Strangers Calendar App functions correctly in its new location
   - Test all features and functionality

3. **Agent Task Management Testing**
   - Verify that agents can still work on the Strangers Calendar App project
   - Test task assignment and tracking functionality

### Phase 5: Documentation Updates
1. **Update README Files**
   - Modify main README to document the new directory structure
   - Update any project-specific documentation

2. **Create Migration Guide**
   - Document the migration process for future reference
   - Include instructions for adding new demos

## Recommendations for Maintaining Clear Boundaries

### 1. Interface Design
- Define clear APIs for demo applications to interact with the core system
- Use dependency injection to avoid tight coupling between demos and core components
- Establish contracts that demos must follow to integrate with the orchestrator

### 2. Configuration Management
- Use configuration files to specify demo application paths rather than hardcoded references
- Implement a plugin system that dynamically loads demo applications
- Separate demo-specific configurations from core system configurations

### 3. Task Management
- Refactor the task tracking system to be more generic and data-driven
- Use configuration files or databases to define project tasks rather than hardcoded logic
- Implement a project template system for consistent demo application structure

### 4. Testing Strategy
- Maintain separate test suites for core system and demo applications
- Implement integration tests to verify demo applications work with the core system
- Use mock objects to isolate demo application testing from core system dependencies

### 5. Documentation
- Clearly document the separation between core system and demo applications
- Provide guidelines for adding new demo applications
- Maintain up-to-date architecture diagrams showing the relationship between components

### 6. Version Control
- Consider using git submodules for demo applications to maintain separate version histories
- Use tags or branches to track releases of demo applications independently
- Document the process for updating demo applications without affecting the core system

### 7. Execution Boundary Enforcement
- Implement sandboxing mechanisms to ensure agents only execute within their assigned project folders
- Configure file system permissions to prevent agents from creating files in root or other project directories
- Add validation checks in the agent execution pipeline to verify all file operations are within designated boundaries
- Implement monitoring to detect and alert on any attempts to access files outside assigned project folders
- Use containerization or virtual environments to isolate agent execution contexts

## Implementation Considerations

### 1. Backward Compatibility
- Ensure that existing functionality continues to work during the transition
- Provide migration scripts to update any existing references
- Maintain compatibility with existing configuration files where possible

### 2. Performance Impact
- Minimize any performance impact from the directory restructuring
- Ensure that the dynamic loading of demo applications doesn't significantly slow down the system
- Optimize the task assignment system for better scalability

### 3. Security
- Ensure that demo applications are properly sandboxed from the core system
- Implement proper access controls to prevent demo applications from affecting core functionality
- Review authentication and authorization mechanisms for demo applications

### 4. Monitoring and Logging
- Implement logging to track interactions between demo applications and the core system
- Add monitoring for demo application performance and resource usage
- Ensure error handling is consistent across both core and demo components

## Conclusion

The proposed separation will significantly improve the maintainability and scalability of the Tmux Orchestrator system. By clearly separating the core orchestrator from demo applications, we can:

1. Reduce complexity in the core system
2. Make it easier to add new demo applications
3. Improve the overall organization of the codebase
4. Enable independent development and testing of demo applications
5. Provide a cleaner architecture that's easier for new developers to understand

The migration plan is designed to be executed in phases to minimize disruption to ongoing development while achieving the desired separation.
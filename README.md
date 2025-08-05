# Qwen Orchestrator Framework

A modular, extensible framework for orchestrating AI agents with tmux integration.

## Overview

The Qwen Orchestrator Framework is a comprehensive system for managing and coordinating multiple AI agents in a tmux-based environment. It provides a robust architecture for agent lifecycle management, communication, execution tracking, and monitoring.

## Architecture

The framework is organized into several core modules:

### Core Modules

1. **Agent Management**
   - `agent_state_manager.py`: Manages agent states and lifecycle
   - `agent_factory.py`: Factory pattern implementation for creating agents
   - `agent_registry.py`: Central registry for all active agents

2. **Communication System**
   - `message_router.py`: Routes messages between agents and services
   - `protocol_enforcer.py`: Ensures message format and protocol compliance
   - `conversation_manager.py`: Manages multi-agent conversations

3. **Execution Tracking**
   - `execution_monitor.py`: Monitors agent task execution
   - `gap_detector.py`: Detects execution gaps and inconsistencies
   - `recovery_manager.py`: Manages recovery from execution failures

4. **Dashboard Monitoring**
   - `dashboard_manager.py`: Manages system dashboards and layouts
   - `metrics_collector.py`: Collects system metrics for visualization
   - `alert_system.py`: Handles system alerts and notifications

5. **Data Management**
   - `data_store.py`: Persistent storage for system data
   - `data_processor.py`: Processes and transforms data
   - `data_validator.py`: Validates data integrity and format

### Service Modules

1. **Authentication**
   - `auth_manager.py`: Handles user authentication and session management
   - `token_manager.py`: Manages authentication tokens
   - `user_manager.py`: Manages user accounts and profiles

## Key Features

- **Modular Design**: Clean separation of concerns with well-defined interfaces
- **Agent Orchestration**: Comprehensive agent lifecycle management
- **Communication Framework**: Structured messaging with protocol enforcement
- **Execution Monitoring**: Real-time tracking of agent tasks and performance
- **Dashboard System**: Customizable dashboards for system monitoring
- **Data Management**: Robust data storage, processing, and validation
- **Authentication & Authorization**: Secure user and agent authentication
- **Recovery Mechanisms**: Automated recovery from failures and gaps
- **Extensible Architecture**: Easy to extend with new modules and services

## Repository

This repository is a fork of the original project and contains the refactored implementation of the Qwen Orchestrator Framework.

## Deployment

The framework includes a blue/green deployment script (`blue_green_deploy.sh`) for seamless updates without disrupting running agents.

## Testing

Integration tests are provided in `test_framework_integration.py` to verify that all modules work together properly.

## Requirements

- Python 3.8+
- tmux
- Required Python packages (see `requirements.txt`)

## Usage

1. Ensure all requirements are installed
2. Run the integration tests to verify the framework is working correctly
3. Use the blue/green deployment script for updates
4. Extend with custom modules as needed for specific use cases

## Contributing

This framework is designed to be extended and customized. New modules can be added following the existing patterns and interfaces.

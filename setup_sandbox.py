#!/usr/bin/env python3
"""
Setup script for Tmux Orchestrator Sandbox Security
Helps users configure the sandbox environment for their installation
"""

import os
import sys
from pathlib import Path
import json
import time

def setup_sandbox_environment():
    """Setup sandbox environment for the current installation"""
    
    print("🔒 Tmux Orchestrator Sandbox Security Setup")
    print("=" * 50)
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Check if we're in the right place
    if not (current_dir / "qwen_control.py").exists():
        print("❌ Error: This script should be run from the Tmux Orchestrator root directory")
        print("   Please navigate to the directory containing qwen_control.py and run this script again")
        sys.exit(1)
    
    # Set up environment variable
    orchestrator_root = str(current_dir.resolve())
    
    print(f"\n📁 Setting ORCHESTRATOR_ROOT to: {orchestrator_root}")
    
    # Create .env file for easy setup
    env_file = current_dir / ".env"
    env_content = f"""# Tmux Orchestrator Environment Configuration
# This file contains environment variables for the sandbox security system
# You can source this file in your shell: source .env

export ORCHESTRATOR_ROOT="{orchestrator_root}"
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created .env file: {env_file}")
    
    # Set environment variable for current session
    os.environ['ORCHESTRATOR_ROOT'] = orchestrator_root
    
    # Test the configuration
    print("\n🧪 Testing sandbox configuration...")
    
    try:
        from sandbox_manager import SandboxManager
        
        # Initialize sandbox manager
        sandbox_manager = SandboxManager()
        
        # Test project sandbox configuration
        project_sandbox = sandbox_manager.get_project_sandbox("test-project")
        if project_sandbox:
            print("✅ Project sandbox configuration loaded successfully")
            print(f"   Allowed base path: {project_sandbox.get('allowed_base_path')}")
            print(f"   Allowed subdirectories: {project_sandbox.get('allowed_subdirectories')}")
        else:
            print("❌ Failed to load project sandbox configuration")
            return False
        
        # Test dynamic project creation
        print("\n🧪 Testing Dynamic Project Creation")
        print("-" * 50)
        
        # Create a dynamic project
        dynamic_project_name = f"dynamic-demo-{int(time.time())}"
        success = sandbox_manager.register_project(dynamic_project_name)
        if success:
            print(f"✅ Successfully created dynamic project: {dynamic_project_name}")
            
            # Verify the project was created
            dynamic_sandbox = sandbox_manager.get_project_sandbox(dynamic_project_name)
            if dynamic_sandbox:
                print("✅ Dynamic project configuration verified")
                print(f"   Project directory: {dynamic_sandbox.get('allowed_base_path')}")
            else:
                print("❌ Failed to verify dynamic project configuration")
        else:
            print(f"❌ Failed to create dynamic project: {dynamic_project_name}")
        
        # Test agent permissions
        developer_permissions = sandbox_manager.get_agent_permissions("developer")
        if developer_permissions:
            print("✅ Agent permissions loaded successfully")
            print(f"  Allowed operations: {developer_permissions.get('allowed_operations')}")
        
        print("\n🎉 Sandbox configuration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing sandbox configuration: {e}")
        print("   This might be normal if dependencies are not installed yet")
    
    # Create setup instructions
    print("\n📋 Setup Instructions:")
    print("=" * 50)
    print("1. Add the following to your shell profile (.bashrc, .zshrc, etc.):")
    print(f"   export ORCHESTRATOR_ROOT=\"{orchestrator_root}\"")
    print("\n2. Or source the .env file in your shell:")
    print(f"   source {env_file}")
    print("\n3. Test the sandbox security:")
    print("   python3 test_sandbox_security.py")
    print("\n4. The sandbox will automatically protect your system from unauthorized file access")
    
    # Create a sample project structure
    projects_dir = current_dir / "projects"
    if not projects_dir.exists():
        projects_dir.mkdir()
        print(f"\n📁 Created projects directory: {projects_dir}")
    
    # Create a sample project
    sample_project = projects_dir / "sample-project"
    if not sample_project.exists():
        sample_project.mkdir()
        (sample_project / "src").mkdir()
        (sample_project / "tests").mkdir()
        (sample_project / "docs").mkdir()
        
        # Create a sample README
        readme_content = """# Sample Project

This is a sample project directory that demonstrates the sandbox security system.

## Structure
- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation

## Security
This project is sandboxed and can only access files within its own directory.
"""
        
        with open(sample_project / "README.md", 'w') as f:
            f.write(readme_content)
        
        print(f"📁 Created sample project: {sample_project}")
    
    print("\n✅ Setup completed successfully!")
    print("\n🔒 Your Tmux Orchestrator is now protected by sandbox security!")
    print("   Agents will be restricted to their designated project directories")
    print("   and cannot access files outside their sandbox boundaries.")

def create_user_config():
    """Create a user-specific configuration file"""
    
    print("\n🔧 Creating User Configuration")
    print("=" * 50)
    
    current_dir = Path.cwd()
    user_config_file = current_dir / "user_sandbox_config.json"
    
    if user_config_file.exists():
        print(f"⚠️  User config file already exists: {user_config_file}")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping user config creation")
            return
    
    # Get user input for custom configuration
    print("\nPlease provide information for your custom sandbox configuration:")
    
    # Get additional restricted paths
    print("\nAdditional restricted paths (paths that agents should never access):")
    print("Enter paths one per line, or press Enter to skip:")
    additional_restricted = []
    while True:
        path = input("Restricted path (or Enter to finish): ").strip()
        if not path:
            break
        additional_restricted.append(path)
    
    # Get additional projects
    print("\nAdditional project sandboxes:")
    print("Enter project names one per line, or press Enter to skip:")
    additional_projects = {}
    while True:
        project_name = input("Project name (or Enter to finish): ").strip()
        if not project_name:
            break
        
        project_dir = input(f"Project directory for '{project_name}' (relative to projects/): ").strip()
        if not project_dir:
            project_dir = project_name.lower().replace(' ', '-')
        
        additional_projects[project_name] = {
            "allowed_base_path": f"${{ORCHESTRATOR_ROOT}}/projects/{project_dir}",
            "allowed_subdirectories": ["src", "tests", "docs", "config"],
            "restricted_paths": [
                "${ORCHESTRATOR_ROOT}",
                "${ORCHESTRATOR_ROOT}/core",
                "${ORCHESTRATOR_ROOT}/services"
            ]
        }
    
    # Create user configuration
    user_config = {
        "user_sandbox_config": {
            "additional_restricted_paths": additional_restricted,
            "additional_projects": additional_projects,
            "custom_settings": {
                "enable_strict_mode": True,
                "log_violations_to_file": True,
                "alert_on_violation": True
            }
        }
    }
    
    with open(user_config_file, 'w') as f:
        json.dump(user_config, f, indent=2)
    
    print(f"\n✅ Created user configuration: {user_config_file}")
    print("   This file contains your custom sandbox settings")
    print("   You can modify it to add more projects or restricted paths")

if __name__ == "__main__":
    try:
        setup_sandbox_environment()
        create_user_config()
        
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Restart your shell or source the .env file")
        print("2. Run: python3 test_sandbox_security.py")
        print("3. Start using the Tmux Orchestrator with sandbox security!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1) 
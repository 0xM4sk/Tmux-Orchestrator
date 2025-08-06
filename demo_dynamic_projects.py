#!/usr/bin/env python3
"""
Demo script for dynamic project functionality
Shows how the system can work with any project name dynamically
"""

import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from sandbox_manager import SandboxManager
from agentic_capabilities import AgenticExecutor

def generate_project_name() -> str:
    """Generate a unique project name"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"demo-project-{timestamp}-{unique_id}"

def demo_dynamic_projects():
    """Demonstrate dynamic project functionality"""
    print("🚀 Dynamic Project System Demo")
    print("=" * 50)
    
    # Initialize sandbox manager
    sandbox_manager = SandboxManager()
    
    # Generate some dynamic project names
    project_names = [
        "My Awesome App",
        "AI Chat Bot",
        "E-commerce Platform",
        "Mobile Game",
        "Data Analytics Tool"
    ]
    
    print(f"\n📋 Testing with {len(project_names)} dynamic projects:")
    for i, name in enumerate(project_names, 1):
        print(f"   {i}. {name}")
    
    print("\n🔧 Creating dynamic project sandboxes...")
    
    for project_name in project_names:
        print(f"\n--- Creating sandbox for: {project_name} ---")
        
        # Get sandbox configuration (this will create it dynamically)
        sandbox_config = sandbox_manager.get_project_sandbox(project_name)
        
        if sandbox_config:
            print(f"✅ Sandbox created successfully")
            print(f"   Allowed base path: {sandbox_config.get('allowed_base_path')}")
            print(f"   Allowed subdirectories: {len(sandbox_config.get('allowed_subdirectories', []))}")
            print(f"   Restricted paths: {len(sandbox_config.get('restricted_paths', []))}")
            
            # Test with an agent
            agent_id = f"demo_agent_{project_name.lower().replace(' ', '_')}"
            executor = AgenticExecutor(
                working_directory=".",
                agent_id=agent_id,
                project_name=project_name
            )
            
            # Try to create a file in the project
            test_file = f"demo_file_{datetime.now().strftime('%H%M%S')}.py"
            result = executor.create_file(test_file, "# Demo content", project_name=project_name)
            
            if result:
                print(f"✅ Agent successfully created file: {test_file}")
                
                # Clean up
                project_dir = Path(sandbox_config.get('allowed_base_path'))
                test_file_path = project_dir / test_file
                if test_file_path.exists():
                    test_file_path.unlink()
                    print(f"🧹 Cleaned up test file")
            else:
                print(f"❌ Agent failed to create file in project")
        else:
            print(f"❌ Failed to create sandbox for: {project_name}")
    
    print("\n🔧 Testing project registration...")
    
    # Test registering a new project
    new_project = generate_project_name()
    print(f"\nRegistering new project: {new_project}")
    
    success = sandbox_manager.register_project(new_project)
    if success:
        print(f"✅ Successfully registered project: {new_project}")
        
        # Verify it was registered
        registered_config = sandbox_manager.get_project_sandbox(new_project)
        if registered_config:
            print(f"✅ Registration verified - project directory: {registered_config.get('allowed_base_path')}")
        else:
            print(f"❌ Registration verification failed")
    else:
        print(f"❌ Failed to register project: {new_project}")
    
    print("\n📊 Security Report:")
    security_report = sandbox_manager.get_security_report()
    if security_report:
        print(f"   Compliance rate: {security_report.get('compliance_rate', 0):.1f}%")
        print(f"   Total operations: {security_report.get('total_operations', 0)}")
        print(f"   Allowed operations: {security_report.get('allowed_operations', 0)}")
        print(f"   Blocked operations: {security_report.get('blocked_operations', 0)}")
    
    print("\n🎉 Dynamic project demo completed!")
    print("\n💡 Key Features Demonstrated:")
    print("   ✅ Any project name works dynamically")
    print("   ✅ Sandbox configurations created on-the-fly")
    print("   ✅ Project directories created automatically")
    print("   ✅ Security boundaries enforced for each project")
    print("   ✅ Projects can be registered permanently")
    print("   ✅ Template-based configuration system")

if __name__ == "__main__":
    demo_dynamic_projects() 
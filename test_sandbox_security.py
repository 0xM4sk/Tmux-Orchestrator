#!/usr/bin/env python3
"""
Test script for sandbox security system
Verifies that agents are properly sandboxed and cannot access restricted areas
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import uuid

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from agentic_capabilities import AgenticExecutor
from sandbox_manager import SandboxManager

def generate_dynamic_project_name() -> str:
    """Generate a unique project name for testing"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"dynamic-test-{timestamp}-{unique_id}"

def test_sandbox_security():
    """Test the sandbox security system"""
    print("🔒 Testing Sandbox Security System")
    print("=" * 50)
    
    # Generate dynamic project names for testing
    test_project_1 = generate_dynamic_project_name()
    test_project_2 = generate_dynamic_project_name()
    
    print(f"Using dynamic project names: {test_project_1}, {test_project_2}")
    
    # Initialize sandbox manager
    sandbox_manager = SandboxManager()
    
    try:
        print("\n🧪 Test 1: Agent attempting to create file in root directory (should be blocked)")
        print("-" * 70)
        
        # Create executor for dynamic test project
        executor = AgenticExecutor(
            working_directory=".",
            agent_id="test_agent_1",
            project_name=test_project_1
        )
        
        # Try to create a file in the root directory (should be blocked)
        result = executor.create_file("README.md", "# This should be blocked", project_name=None)
        
        if not result:
            print("✅ SECURITY SUCCESS: Agent was blocked from creating file in root directory")
        else:
            print("❌ SECURITY FAILURE: Agent was able to create file in root directory")
            return False
        
        print("\n🧪 Test 2: Agent attempting to create file in core directory (should be blocked)")
        print("-" * 70)
        
        executor = AgenticExecutor(
            working_directory=".",
            agent_id="test_agent_2",
            project_name=test_project_2
        )
        
        # Try to create a file in the core directory (should be blocked)
        result = executor.create_file("core/test_file.py", "# This should be blocked")
        
        if not result:
            print("✅ SECURITY SUCCESS: Agent was blocked from creating file in core directory")
        else:
            print("❌ SECURITY FAILURE: Agent was able to create file in core directory")
            return False
        
        print("\n🧪 Test 3: Agent creating file in project directory (should succeed)")
        print("-" * 70)
        
        executor = AgenticExecutor(
            working_directory=".",
            agent_id="test_agent_3",
            project_name=test_project_1
        )
        
        # Try to create a file in the project directory (should succeed)
        result = executor.create_file("test_file.py", "# Test content", project_name=test_project_1)
        
        if result:
            print("✅ SECURITY SUCCESS: Agent was able to create file in project directory")
            
            # Clean up test file
            test_file = Path(f"projects/{test_project_1}/test_file.py")
            if test_file.exists():
                test_file.unlink()
        else:
            print("❌ SECURITY FAILURE: Agent was blocked from creating file in project directory")
            return False
        
        print("\n🧪 Test 4: Agent attempting to execute command outside sandbox (should be blocked)")
        print("-" * 70)
        
        executor = AgenticExecutor(
            working_directory=".",
            agent_id="test_agent_4",
            project_name=test_project_2
        )
        
        # Try to execute a command that accesses files outside the sandbox
        result = executor.execute_command("ls /home/baseline/Tmux-Orchestrator/core")
        
        if not result["success"]:
            print("✅ SECURITY SUCCESS: Agent was blocked from executing command outside sandbox")
        else:
            print("❌ SECURITY FAILURE: Agent was able to execute command outside sandbox")
            return False
        
        print("\n🧪 Test 5: Agent executing command within sandbox (should succeed)")
        print("-" * 70)
        
        executor = AgenticExecutor(
            working_directory=".",
            agent_id="test_agent_5",
            project_name=test_project_1
        )
        
        # Try to execute a command within the sandbox
        result = executor.execute_command(f"ls projects/{test_project_1}")
        
        if result["success"]:
            print("✅ SECURITY SUCCESS: Agent was able to execute command within sandbox")
        else:
            print("❌ SECURITY FAILURE: Agent was blocked from executing command within sandbox")
            return False
        
        print("\n🧪 Test 6: Dynamic project sandbox configuration")
        print("-" * 70)
        
        # Test dynamic project sandbox configuration
        project_sandbox = sandbox_manager.get_project_sandbox(test_project_1)
        if project_sandbox:
            print("✅ Project sandbox configuration loaded successfully")
            print(f"   Allowed base path: {project_sandbox.get('allowed_base_path')}")
            print(f"   Allowed subdirectories: {project_sandbox.get('allowed_subdirectories')}")
        else:
            print("❌ Failed to load project sandbox configuration")
            return False
        
        print("\n🧪 Test 7: Sandbox enforcer creation")
        print("-" * 70)
        
        # Test sandbox enforcer creation
        enforcer = sandbox_manager.enforce_sandbox("test_agent", "developer", test_project_1)
        if enforcer:
            print("✅ Sandbox enforcer created successfully")
        else:
            print("❌ Failed to create sandbox enforcer")
            return False
        
        print("\n🧪 Test 8: Security report generation")
        print("-" * 70)
        
        # Test security report
        security_report = sandbox_manager.get_security_report()
        if security_report:
            print("✅ Security report generated successfully")
            print(f"   Compliance rate: {security_report.get('compliance_rate', 0):.1f}%")
            print(f"   Total operations: {security_report.get('total_operations', 0)}")
            print(f"   Allowed operations: {security_report.get('allowed_operations', 0)}")
            print(f"   Blocked operations: {security_report.get('blocked_operations', 0)}")
        else:
            print("❌ Failed to generate security report")
            return False
        
        print("\n🧪 Test 9: Dynamic project registration")
        print("-" * 70)
        
        # Test dynamic project registration
        new_project = generate_dynamic_project_name()
        success = sandbox_manager.register_project(new_project)
        if success:
            print(f"✅ Successfully registered dynamic project: {new_project}")
            
            # Verify the project was registered
            registered_sandbox = sandbox_manager.get_project_sandbox(new_project)
            if registered_sandbox:
                print("✅ Registered project configuration verified")
            else:
                print("❌ Failed to verify registered project configuration")
                return False
        else:
            print(f"❌ Failed to register dynamic project: {new_project}")
            return False
        
        print("\n🎉 ALL TESTS PASSED! Sandbox security system is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_sandbox_security()
    sys.exit(0 if success else 1) 
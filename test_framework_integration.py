#!/usr/bin/env python3
"""
Integration test for the refactored Qwen Orchestrator framework.
This test verifies that all modules work together properly.
"""

import sys
import os
import tempfile
import json
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_agent_management():
    """Test the Agent Management module"""
    print("Testing Agent Management module...")
    
    try:
        from core.agent_management.agent_state_manager import AgentStateManager, AgentState
        from core.agent_management.agent_factory import AgentFactory, BaseAgent
        from core.agent_management.agent_registry import AgentRegistry
        
        # Test AgentStateManager
        state_manager = AgentStateManager()
        assert state_manager.set_agent_state("test_agent_1", AgentState.ACTIVE) == True
        assert state_manager.get_agent_state("test_agent_1") == AgentState.ACTIVE
        assert state_manager.transition_agent_state("test_agent_1", AgentState.ACTIVE, AgentState.IDLE) == True
        assert state_manager.get_agent_state("test_agent_1") == AgentState.IDLE
        
        # Test AgentFactory
        factory = AgentFactory()
        agent = factory.create_agent("test_agent_2", "base", {"test": "config"})
        assert agent is not None
        assert isinstance(agent, BaseAgent)
        
        # Test AgentRegistry
        registry = AgentRegistry(state_manager)
        assert registry.register_agent(agent) == True
        assert registry.get_agent("test_agent_2") is not None
        assert registry.update_agent_state("test_agent_2", AgentState.BUSY) == True
        assert registry.get_agent_state("test_agent_2") == AgentState.BUSY
        
        print("✅ Agent Management module tests passed")
        return True
    except Exception as e:
        print(f"❌ Agent Management module tests failed: {e}")
        return False

def test_communication_system():
    """Test the Communication System module"""
    print("Testing Communication System module...")
    
    try:
        from core.communication_system.message_router import MessageRouter
        from core.communication_system.protocol_enforcer import ProtocolEnforcer, ProtocolViolation
        from core.communication_system.conversation_manager import ConversationManager, Message, ConversationState
        
        # Test MessageRouter
        router = MessageRouter()
        results = []
        def test_handler(message):
            results.append(message)
            return "handled"
        
        assert router.add_route("test_type", test_handler) == True
        router_results = router.route_message({"type": "test_type", "data": "test"})
        assert len(router_results) == 1
        assert router_results[0] == "handled"
        
        # Test ProtocolEnforcer
        enforcer = ProtocolEnforcer()
        valid_message = {
            "type": "test",
            "sender": "test_sender",
            "timestamp": datetime.now().timestamp(),
            "content": {"data": "test"}
        }
        is_valid, violation, description = enforcer.validate_message(valid_message)
        assert is_valid == True
        
        # Test ConversationManager
        conv_manager = ConversationManager()
        participants = ["agent_1", "agent_2"]
        assert conv_manager.create_conversation("test_conv", participants) == True
        conversation = conv_manager.get_conversation("test_conv")
        assert conversation is not None
        assert conversation.state == ConversationState.ACTIVE
        
        print("✅ Communication System module tests passed")
        return True
    except Exception as e:
        print(f"❌ Communication System module tests failed: {e}")
        return False

def test_execution_tracking():
    """Test the Execution Tracking module"""
    print("Testing Execution Tracking module...")
    
    try:
        from core.execution_tracking.execution_monitor import ExecutionMonitor, ExecutionStatus
        from core.execution_tracking.gap_detector import GapDetector
        from core.execution_tracking.recovery_manager import RecoveryManager
        
        # Test ExecutionMonitor
        monitor = ExecutionMonitor()
        assert monitor.start_execution("exec_1", "task_1", "agent_1") == True
        execution = monitor.get_execution("exec_1")
        assert execution is not None
        assert execution.status == ExecutionStatus.RUNNING
        assert monitor.complete_execution("exec_1", "result") == True
        execution = monitor.get_execution("exec_1")
        assert execution.status == ExecutionStatus.COMPLETED
        
        # Test GapDetector
        detector = GapDetector(monitor)
        gaps = detector.detect_gaps()
        assert isinstance(gaps, dict)
        
        # Test RecoveryManager
        recovery = RecoveryManager(monitor, detector)
        recovery_info = recovery.get_recovery_stats()
        assert isinstance(recovery_info, dict)
        
        print("✅ Execution Tracking module tests passed")
        return True
    except Exception as e:
        print(f"❌ Execution Tracking module tests failed: {e}")
        return False

def test_dashboard_monitoring():
    """Test the Dashboard Monitoring module"""
    print("Testing Dashboard Monitoring module...")
    
    try:
        from core.dashboard_monitoring.dashboard_manager import DashboardManager, DashboardSection
        from core.dashboard_monitoring.metrics_collector import MetricsCollector, MetricType
        from core.dashboard_monitoring.alert_system import AlertSystem, AlertSeverity, AlertStatus
        
        # Test DashboardManager
        dashboard_manager = DashboardManager()
        sections = [DashboardSection.AGENT_STATUS, DashboardSection.EXECUTION_METRICS]
        assert dashboard_manager.create_dashboard("test_dashboard", "Test Dashboard", sections, 30) == True
        dashboard = dashboard_manager.get_dashboard("test_dashboard")
        assert dashboard is not None
        assert len(dashboard.sections) == 2
        
        # Test MetricsCollector
        metrics_collector = MetricsCollector()
        def test_source():
            return {"test_metric": 42}
        assert metrics_collector.add_metric_source("test_source", test_source) == True
        metrics = metrics_collector.collect_metrics()
        assert "test_source" in metrics
        
        # Test AlertSystem
        alert_system = AlertSystem()
        assert alert_system.create_alert("test_alert", "Test Alert", "Test description", 
                                       AlertSeverity.WARNING, "test_source") == True
        alert = alert_system.get_alert("test_alert")
        assert alert is not None
        assert alert.severity == AlertSeverity.WARNING
        
        print("✅ Dashboard Monitoring module tests passed")
        return True
    except Exception as e:
        print(f"❌ Dashboard Monitoring module tests failed: {e}")
        return False

def test_data_management():
    """Test the Data Management module"""
    print("Testing Data Management module...")
    
    try:
        from core.data_management.data_store import DataStore
        from core.data_management.data_processor import DataProcessor
        from core.data_management.data_validator import DataValidator, ValidationSeverity
        
        # Test DataStore
        # Use a temporary file for storage
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            storage_path = tmp_file.name
        
        try:
            data_store = DataStore(storage_path)
            assert data_store.store("test_key", {"data": "test_value"}) == True
            retrieved_data = data_store.retrieve("test_key")
            assert retrieved_data is not None
            assert retrieved_data["data"] == "test_value"
        finally:
            # Clean up temporary file
            if os.path.exists(storage_path):
                os.unlink(storage_path)
        
        # Test DataProcessor
        processor = DataProcessor()
        def uppercase_transformer(data):
            if isinstance(data, str):
                return data.upper()
            return data
        assert processor.register_transformer("uppercase", uppercase_transformer) == True
        result = processor.process_data("test", transformers=["uppercase"])
        assert result == "TEST"
        
        # Test DataValidator
        validator = DataValidator()
        results = validator.validate_data("test_data", ["not_empty"])
        assert len(results) > 0
        assert all(isinstance(r.passed, bool) for r in results)
        
        print("✅ Data Management module tests passed")
        return True
    except Exception as e:
        print(f"❌ Data Management module tests failed: {e}")
        return False

def test_authentication_service():
    """Test the Authentication Service module"""
    print("Testing Authentication Service module...")
    
    try:
        from services.authentication.auth_manager import AuthManager, AuthStatus
        from services.authentication.token_manager import TokenManager
        from services.authentication.user_manager import UserManager, UserRole, UserStatus
        
        # Test AuthManager
        auth_manager = AuthManager("test_secret_key")
        # Use the register_user method which handles password hashing internally
        assert auth_manager.register_user("test_user", "test_password") == True
        # Test authentication
        success, session_id = auth_manager.authenticate_user("test_user", "test_password")
        assert success == True
        assert session_id is not None
        # Test session validation
        status = auth_manager.validate_session(session_id)
        assert status == AuthStatus.AUTHENTICATED
        
        # Test TokenManager
        token_manager = TokenManager("test_secret_key")
        token = token_manager.generate_token("test_user", lifetime=3600)
        assert token is not None
        payload = token_manager.validate_token(token)
        assert payload is not None
        assert payload["user_id"] == "test_user"
        
        # Test UserManager
        user_manager = UserManager()
        assert user_manager.create_user("test_user_2", "test_username", "test@example.com") == True
        user = user_manager.get_user("test_user_2")
        assert user is not None
        assert user.username == "test_username"
        
        print("✅ Authentication Service module tests passed")
        return True
    except Exception as e:
        print(f"❌ Authentication Service module tests failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("Running Qwen Orchestrator Framework Integration Tests")
    print("=" * 50)
    
    tests = [
        test_agent_management,
        test_communication_system,
        test_execution_tracking,
        test_dashboard_monitoring,
        test_data_management,
        test_authentication_service
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Integration Tests Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All integration tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
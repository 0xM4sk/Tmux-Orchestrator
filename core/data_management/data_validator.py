"""
Data Validator Module

This module provides functionality for validating data integrity and format.
It handles data validation, schema checking, and quality assurance.
"""

from typing import Dict, List, Any, Optional, Callable, Union
import logging
from datetime import datetime
from threading import Lock
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Enumeration of validation severities"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Represents the result of a validation"""
    validator_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any]
    timestamp: float


@dataclass
class ValidationRule:
    """Represents a validation rule"""
    rule_id: str
    name: str
    description: str
    validator: Callable
    severity: ValidationSeverity
    enabled: bool = True
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().timestamp()


class DataValidator:
    """
    Validates data integrity and format.
    
    This class handles data validation, schema checking, and quality assurance.
    """
    
    def __init__(self):
        """Initialize the DataValidator with empty rule storage."""
        self._rules: Dict[str, ValidationRule] = {}
        self._rule_sets: Dict[str, List[str]] = {}  # rule_set_id -> list of rule_ids
        self._validation_history: List[ValidationResult] = []
        self._max_history_size = 1000
        self._lock = Lock()
        
        # Register default validators
        self._register_default_validators()
    
    def _register_default_validators(self):
        """Register default validation rules."""
        # Not empty validator
        self.register_rule(
            rule_id="not_empty",
            name="Not Empty",
            description="Validates that data is not empty",
            validator=lambda data: data is not None and data != "",
            severity=ValidationSeverity.ERROR
        )
        
        # String length validator
        self.register_rule(
            rule_id="string_length",
            name="String Length",
            description="Validates string length is within bounds",
            validator=lambda data, min_length=0, max_length=None: 
                isinstance(data, str) and 
                len(data) >= min_length and 
                (max_length is None or len(data) <= max_length),
            severity=ValidationSeverity.WARNING
        )
        
        # Numeric range validator
        self.register_rule(
            rule_id="numeric_range",
            name="Numeric Range",
            description="Validates numeric value is within range",
            validator=lambda data, min_value=None, max_value=None: 
                isinstance(data, (int, float)) and 
                (min_value is None or data >= min_value) and 
                (max_value is None or data <= max_value),
            severity=ValidationSeverity.WARNING
        )
        
        # Email format validator
        self.register_rule(
            rule_id="email_format",
            name="Email Format",
            description="Validates email format",
            validator=lambda data: isinstance(data, str) and re.match(r"[^@]+@[^@]+\.[^@]+", data),
            severity=ValidationSeverity.ERROR
        )
    
    def register_rule(self, rule_id: str, name: str, description: str, 
                     validator: Callable, severity: ValidationSeverity, 
                     enabled: bool = True) -> bool:
        """
        Register a validation rule.
        
        Args:
            rule_id (str): The unique identifier for the rule
            name (str): The name of the rule
            description (str): The description of the rule
            validator (Callable): The validation function
            severity (ValidationSeverity): The severity level of validation failures
            enabled (bool): Whether the rule is enabled by default
            
        Returns:
            bool: True if rule was registered successfully, False otherwise
        """
        with self._lock:
            if rule_id in self._rules:
                logger.warning(f"Rule {rule_id} already exists")
                return False
            
            rule = ValidationRule(
                rule_id=rule_id,
                name=name,
                description=description,
                validator=validator,
                severity=severity,
                enabled=enabled
            )
            
            self._rules[rule_id] = rule
            logger.debug(f"Registered validation rule: {rule_id}")
            return True
    
    def unregister_rule(self, rule_id: str) -> bool:
        """
        Unregister a validation rule.
        
        Args:
            rule_id (str): The ID of the rule to unregister
            
        Returns:
            bool: True if rule was unregistered successfully, False otherwise
        """
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                logger.debug(f"Unregistered validation rule: {rule_id}")
                
                # Remove rule from any rule sets
                for rule_set_id, rule_ids in self._rule_sets.items():
                    if rule_id in rule_ids:
                        rule_ids.remove(rule_id)
                
                return True
            return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """
        Enable a validation rule.
        
        Args:
            rule_id (str): The ID of the rule to enable
            
        Returns:
            bool: True if rule was enabled successfully, False otherwise
        """
        with self._lock:
            if rule_id in self._rules:
                self._rules[rule_id].enabled = True
                logger.debug(f"Enabled validation rule: {rule_id}")
                return True
            return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """
        Disable a validation rule.
        
        Args:
            rule_id (str): The ID of the rule to disable
            
        Returns:
            bool: True if rule was disabled successfully, False otherwise
        """
        with self._lock:
            if rule_id in self._rules:
                self._rules[rule_id].enabled = False
                logger.debug(f"Disabled validation rule: {rule_id}")
                return True
            return False
    
    def create_rule_set(self, rule_set_id: str, rule_ids: List[str]) -> bool:
        """
        Create a validation rule set.
        
        Args:
            rule_set_id (str): The unique identifier for the rule set
            rule_ids (List[str]): The IDs of rules to include in the set
            
        Returns:
            bool: True if rule set was created successfully, False otherwise
        """
        with self._lock:
            # Verify all rules exist
            for rule_id in rule_ids:
                if rule_id not in self._rules:
                    logger.error(f"Rule {rule_id} not found")
                    return False
            
            self._rule_sets[rule_set_id] = rule_ids.copy()
            logger.debug(f"Created rule set {rule_set_id} with {len(rule_ids)} rules")
            return True
    
    def delete_rule_set(self, rule_set_id: str) -> bool:
        """
        Delete a validation rule set.
        
        Args:
            rule_set_id (str): The ID of the rule set to delete
            
        Returns:
            bool: True if rule set was deleted successfully, False otherwise
        """
        with self._lock:
            if rule_set_id in self._rule_sets:
                del self._rule_sets[rule_set_id]
                logger.debug(f"Deleted rule set {rule_set_id}")
                return True
            return False
    
    def validate_data(self, data: Any, rule_ids: Optional[List[str]] = None, 
                     rule_set_id: Optional[str] = None, **kwargs) -> List[ValidationResult]:
        """
        Validate data using specified rules or rule set.
        
        Args:
            data (Any): The data to validate
            rule_ids (Optional[List[str]]): Specific rule IDs to apply
            rule_set_id (Optional[str]): The ID of a rule set to apply
            **kwargs: Additional arguments for validators
            
        Returns:
            List[ValidationResult]: The validation results
        """
        # Determine which rules to apply
        rules_to_apply = []
        
        if rule_set_id:
            if rule_set_id in self._rule_sets:
                rule_ids = self._rule_sets[rule_set_id]
            else:
                logger.error(f"Rule set {rule_set_id} not found")
                return []
        
        if rule_ids:
            # Apply specific rules
            for rule_id in rule_ids:
                if rule_id in self._rules:
                    rules_to_apply.append(self._rules[rule_id])
                else:
                    logger.warning(f"Rule {rule_id} not found")
        else:
            # Apply all enabled rules
            with self._lock:
                rules_to_apply = [rule for rule in self._rules.values() if rule.enabled]
        
        # Apply each rule
        results = []
        timestamp = datetime.now().timestamp()
        
        for rule in rules_to_apply:
            if not rule.enabled:
                continue
            
            try:
                # Call validator with data and any additional kwargs
                passed = rule.validator(data, **kwargs)
                
                result = ValidationResult(
                    validator_id=rule.rule_id,
                    passed=passed,
                    severity=rule.severity,
                    message=f"Validation {'passed' if passed else 'failed'}: {rule.name}",
                    details={
                        "rule_name": rule.name,
                        "rule_description": rule.description,
                        "data_type": type(data).__name__,
                        "data_preview": str(data)[:100] if data is not None else "None"
                    },
                    timestamp=timestamp
                )
                
                results.append(result)
                
                # Add to history, maintaining max size
                with self._lock:
                    self._validation_history.append(result)
                    if len(self._validation_history) > self._max_history_size:
                        self._validation_history.pop(0)
                
                if not passed:
                    logger.debug(f"Validation failed for rule {rule.rule_id}: {rule.name}")
            except Exception as e:
                logger.error(f"Error in validator {rule.rule_id}: {e}")
                
                result = ValidationResult(
                    validator_id=rule.rule_id,
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Validator error: {rule.name}",
                    details={
                        "rule_name": rule.name,
                        "error": str(e),
                        "data_type": type(data).__name__
                    },
                    timestamp=timestamp
                )
                
                results.append(result)
                
                # Add to history
                with self._lock:
                    self._validation_history.append(result)
                    if len(self._validation_history) > self._max_history_size:
                        self._validation_history.pop(0)
        
        return results
    
    def get_validation_results(self, severity: Optional[ValidationSeverity] = None, 
                              limit: Optional[int] = None) -> List[ValidationResult]:
        """
        Get validation results, optionally filtered by severity.
        
        Args:
            severity (Optional[ValidationSeverity]): The severity level to filter by
            limit (Optional[int]): The maximum number of results to return
            
        Returns:
            List[ValidationResult]: The validation results
        """
        with self._lock:
            results = self._validation_history.copy()
        
        if severity:
            results = [r for r in results if r.severity == severity]
        
        if limit:
            results = results[-limit:]
        
        return results
    
    def get_rule(self, rule_id: str) -> Optional[ValidationRule]:
        """
        Get a validation rule by its ID.
        
        Args:
            rule_id (str): The ID of the rule to retrieve
            
        Returns:
            ValidationRule: The validation rule, or None if not found
        """
        return self._rules.get(rule_id)
    
    def list_rules(self) -> List[str]:
        """
        List all rule IDs.
        
        Returns:
            List[str]: A list of all rule IDs
        """
        with self._lock:
            return list(self._rules.keys())
    
    def list_rule_sets(self) -> List[str]:
        """
        List all rule set IDs.
        
        Returns:
            List[str]: A list of all rule set IDs
        """
        with self._lock:
            return list(self._rule_sets.keys())
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of validation results.
        
        Returns:
            Dict[str, Any]: A summary of validation results
        """
        with self._lock:
            total_validations = len(self._validation_history)
            
            # Count by severity
            severity_counts = {}
            passed_count = 0
            failed_count = 0
            
            for result in self._validation_history:
                severity = result.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                if result.passed:
                    passed_count += 1
                else:
                    failed_count += 1
            
            # Get the most recent validation timestamp
            latest_validation_timestamp = 0
            if self._validation_history:
                latest_validation_timestamp = max(r.timestamp for r in self._validation_history)
            
            # Count rules and rule sets
            total_rules = len(self._rules)
            enabled_rules = len([r for r in self._rules.values() if r.enabled])
            total_rule_sets = len(self._rule_sets)
            
            return {
                "total_validations": total_validations,
                "passed_validations": passed_count,
                "failed_validations": failed_count,
                "pass_rate": passed_count / total_validations if total_validations > 0 else 0,
                "severity_counts": severity_counts,
                "latest_validation": latest_validation_timestamp,
                "total_rules": total_rules,
                "enabled_rules": enabled_rules,
                "total_rule_sets": total_rule_sets
            }
    
    def clear_validation_history(self) -> bool:
        """
        Clear the validation history.
        
        Returns:
            bool: True if history was cleared successfully
        """
        with self._lock:
            self._validation_history.clear()
        logger.debug("Cleared validation history")
        return True
"""
A simple rules engine implementation for Python.

This module provides a framework for creating and executing business rules organized into policies.
It supports rule chaining, error handling, and policy execution with detailed results.
"""

from dataclasses import dataclass
import inspect
import logging
from string import Template
from typing import Optional, Dict, Any, Type, TypeVar, Callable
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Type variable for request objects

@dataclass(frozen=True)
class RuleResult:
    """
    Represents the result of executing a single rule.

    Attributes:
        rule_id: Unique identifier for the rule
        rule_name: Human-readable name of the rule
        passed: Whether the rule passed or failed
        failure_message: Optional message explaining why the rule failed
        error_message: Optional message containing error details if rule execution failed
    """
    rule_id: str
    rule_name: str
    passed: bool
    failure_message: Optional[str] = None
    error_message: Optional[str] = None

    @staticmethod
    def as_success(rule_id: str, rule_name: str) -> "RuleResult":
        """Create a successful rule result."""
        return RuleResult(rule_id, rule_name, passed=True)

    @staticmethod
    def as_failure(rule_id: str, rule_name: str, failure_message: str) -> "RuleResult":
        """Create a failed rule result with a failure message."""
        return RuleResult(rule_id, rule_name, failure_message=failure_message, passed=False)

    @staticmethod
    def as_error(rule_id: str, rule_name: str, error: str) -> "RuleResult":
        """Create a failed rule result with an error message."""
        return RuleResult(rule_id, rule_name, error_message=error, passed=False)


@dataclass(frozen=True)
class PolicyResult:
    """
    Represents the result of executing a policy containing multiple rules.

    Attributes:
        policy_id: Unique identifier for the policy
        policy_name: Human-readable name of the policy
        rule_results: Dictionary mapping rule IDs to their execution results
        success: Whether all rules in the policy passed
    """
    policy_id: str
    policy_name: str
    rule_results: Dict[str, RuleResult]
    success: bool = False


class Policy:
    """Base class for implementing policy rules.
    
    Policies are collections of rules that can be executed against a request object.
    Subclasses should either implement execute_policy or use the @policy decorator.
    """
    def execute(self, request: T) -> PolicyResult:
        """Execute all rules in this policy against the given request.

        Args:
            request: The object to validate against the policy rules

        Returns:
            PolicyResult containing the results of all rule executions
        """
        return self.execute_policy(request)

    def execute_policy(self, request: T) -> PolicyResult:
        """Template method that should be implemented by subclasses or decorated with @policy.

        Args:
            request: The object to validate against the policy rules

        Returns:
            PolicyResult containing the results of all rule executions

        Raises:
            NotImplementedError: If not implemented by subclass or decorated
        """
        raise NotImplementedError("Subclasses must implement execute_policy or use the @policy decorator.")


def policy(policy_name: str, policy_id: str) -> Callable[[Type[T]], Type[T]]:
    """Class decorator that transforms a class into a Policy implementation.

    This decorator automatically implements the execute_policy method by finding
    all methods decorated with @rule and executing them in order.

    Args:
        policy_name: Human-readable name for the policy
        policy_id: Unique identifier for the policy

    Returns:
        A class decorator that adds policy execution behavior
    """
    def decorator(cls: Type[T]) -> Type[T]:
        cls.policy_name = policy_name
        cls.policy_id = policy_id

        methods_with_decorator = []
        for name, obj in inspect.getmembers(cls, inspect.isfunction):
            if getattr(obj, "is_rule", False):
                methods_with_decorator.append(name)

        def execute(self, request: Any) -> PolicyResult:
            """Execute all rules in the policy against the request.

            Args:
                request: The object to validate against the policy rules

            Returns:
                PolicyResult containing the results of all rule executions
            """
            rule_results = []
            success = False
            if methods_with_decorator:
                for method_name in methods_with_decorator:
                    method = getattr(self, method_name)
                    result = method(request)
                    rule_results.append(result)
                success = all(result.passed for result in rule_results if result is not None)

            return PolicyResult(
                policy_id=policy_id,
                policy_name=policy_name,
                rule_results={result.rule_id: result for result in rule_results},
                success=success
            )

        cls.execute_policy = execute
        return cls

    return decorator


def rule(rule_id: str, rule_name: str, failure_message: Optional[str] = None) -> Callable:
    """Method decorator that marks a method as a rule and handles its execution.

    This decorator wraps a method that returns a boolean into a full rule implementation.
    The wrapped method should return True if the rule passes, False if it fails.

    Args:
        rule_id: Unique identifier for the rule
        rule_name: Human-readable name for the rule
        failure_message: Optional template string for failure messages. Can use {varname}
                        syntax to insert values from the request object

    Returns:
        A decorator that converts a boolean-returning method into a rule
    
    Example:
        @rule("R001", "Check positive balance", "Balance ${balance} must be positive")
        def check_balance(self, request):
            return request.balance > 0
    """
    def rule_decorator(func: Callable[..., bool]) -> Callable[..., RuleResult]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> RuleResult:
            try:
                passed = func(*args, **kwargs)
                if passed:
                    return RuleResult.as_success(wrapper.rule_id, wrapper.rule_name)
                else:
                    message = "Rule failed"
                    if failure_message is not None:
                        context = vars(args[1])  # args[1] is the request object
                        message = Template(failure_message).substitute(context)
                    return RuleResult.as_failure(wrapper.rule_id, wrapper.rule_name, failure_message=message)

            except Exception as ex:
                logger.error("an error occurred in rule %s:%s: %s", wrapper.rule_id, wrapper.rule_name, str(ex))
                return RuleResult.as_error(wrapper.rule_id, wrapper.rule_name, str(ex))

        wrapper.rule_id = rule_id
        wrapper.rule_name = rule_name
        wrapper.is_rule = True
        return wrapper

    return rule_decorator

from dataclasses import dataclass
import inspect
import logging
from string import Template
from typing import Optional, Dict, Any
from functools import wraps

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class RuleResult:
    rule_id: str
    rule_name: str
    passed: bool
    failure_message: Optional[str] = None
    error_message: Optional[str] = None

    @staticmethod
    def as_success(rule_id: str, rule_name: str) -> "RuleResult":
        return RuleResult(rule_id, rule_name, passed=True)

    @staticmethod
    def as_failure(rule_id: str, rule_name: str, failure_message: str) -> "RuleResult":
        return RuleResult(rule_id, rule_name, failure_message=failure_message, passed=False)

    @staticmethod
    def as_error(rule_id: str, rule_name: str, error: str) -> "RuleResult":
        return RuleResult(rule_id, rule_name, error_message=error, passed=False)


@dataclass(frozen=True)
class PolicyResult:
    policy_id: str
    policy_name: str
    rule_results: Dict[str, RuleResult]
    success: bool = False


class Policy:
    def execute(self, request: Any) -> PolicyResult:
        return self.execute_policy(request)

    def execute_policy(self, request: Any) -> PolicyResult:
        raise NotImplementedError("Subclasses must implement execute_policy or use the @policy decorator.")


def policy(policy_name: str, policy_id: str):
    def decorator(cls):
        cls.policy_name = policy_name
        cls.policy_id = policy_id

        methods_with_decorator = []
        for name, obj in inspect.getmembers(cls, inspect.isfunction):
            if getattr(obj, "is_rule", False):
                methods_with_decorator.append(name)

        def execute(self, dto) -> PolicyResult:
            rule_results = []
            success = False
            if methods_with_decorator:
                for method_name in methods_with_decorator:
                    method = getattr(self, method_name)
                    result = method(dto)
                    rule_results.append(result)
                success = all(result.passed for result in rule_results if result is not None)

            return PolicyResult(policy_id=policy_id,
                                policy_name=policy_name,
                                rule_results={result.rule_id: result for result in rule_results},
                                success=success)

        cls.execute_policy = execute

        return cls

    return decorator


def rule(rule_id: str, rule_name: str, failure_message: Optional[str] = None):
    def rule_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                passed = func(*args, **kwargs)
                if passed:
                    return RuleResult.as_success(wrapper.rule_id, wrapper.rule_name)
                else:
                    message = "Rule failed"
                    if failure_message is not None:
                        context = vars(args[1])
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

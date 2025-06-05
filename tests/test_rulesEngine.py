import pytest
from flow.rulesEngine import RuleResult, PolicyResult, rule, policy, Policy


def test_rule_result_as_success():
    result = RuleResult.as_success("rule1")
    assert result.passed is True
    assert result.id == "rule1"
    assert result.failure_message is None
    assert result.error_message is None


def test_rule_result_as_failure():
    failure_message = "This rule failed."
    result = RuleResult.as_failure("rule1", failure_message)
    assert result.passed is False
    assert result.id == "rule1"
    assert result.failure_message == failure_message


def test_rule_result_as_error():
    error_message = "Unexpected error!"
    result = RuleResult.as_error("rule1", error_message)
    assert result.passed is False
    assert result.id == "rule1"
    assert result.error_message == error_message


def test_policy_decorator():
    @policy(policy_id="p1", policy_name="Test Policy")
    class TestPolicy(Policy):
        @rule(rule_id="rule1", rule_name="Test Rule", failure_message="Rule failed")
        def my_rule(self, _):
            return True

    # Ensure the policy and rule decorations work
    policy_instance = TestPolicy()
    result = policy_instance.execute({})
    assert isinstance(result, PolicyResult)
    assert result.success is True
    assert "rule1" in result.rule_results

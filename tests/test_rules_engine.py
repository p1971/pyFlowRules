from flowrules.rules_engine import RuleResult, PolicyResult, rule, policy, Policy


def test_rule_result_as_success():
    result = RuleResult.as_success("R01", "rule1")
    assert result.passed is True
    assert result.rule_id == "R01"
    assert result.rule_name == "rule1"
    assert result.failure_message is None
    assert result.error_message is None


def test_rule_result_as_failure():
    failure_message = "This rule failed."
    result = RuleResult.as_failure("R01", "rule1", failure_message)
    assert result.passed is False
    assert result.rule_id == "R01"
    assert result.rule_name == "rule1"
    assert result.failure_message == failure_message


def test_rule_result_as_error():
    error_message = "Unexpected error!"
    result = RuleResult.as_error("R01", "rule1", error_message)
    assert result.passed is False
    assert result.rule_id == "R01"
    assert result.rule_name == "rule1"
    assert result.error_message == error_message


def test_policy_decorator():
    @policy(policy_id="p1", policy_name="Test Policy")
    class TestPolicy(Policy):
        @rule(rule_id="R01", rule_name="rule1", failure_message="Rule failed")
        def my_rule(self, _):
            return True

    # Ensure the policy and rule decorations work
    policy_instance = TestPolicy()
    result = policy_instance.execute({})
    assert isinstance(result, PolicyResult)
    assert result.success is True
    assert "R01" in result.rule_results


def test_policy_executes_rules_in_declaration_order():
    calls = []

    @policy(policy_id="p1", policy_name="Test Policy")
    class TestPolicy(Policy):
        @rule(rule_id="R01", rule_name="first")
        def z_first_rule(self, _):
            calls.append("first")
            return True

        @rule(rule_id="R02", rule_name="second")
        def a_second_rule(self, _):
            calls.append("second")
            return True

    result = TestPolicy().execute({})

    assert calls == ["first", "second"]
    assert list(result.rule_results) == ["R01", "R02"]
    assert result.success is True


def test_policy_executes_inherited_rules_before_subclass_rules():
    calls = []

    class BasePolicy(Policy):
        @rule(rule_id="R01", rule_name="base")
        def base_rule(self, _):
            calls.append("base")
            return True

    @policy(policy_id="p1", policy_name="Test Policy")
    class TestPolicy(BasePolicy):
        @rule(rule_id="R02", rule_name="subclass")
        def subclass_rule(self, _):
            calls.append("subclass")
            return True

    result = TestPolicy().execute({})

    assert calls == ["base", "subclass"]
    assert list(result.rule_results) == ["R01", "R02"]
    assert result.success is True


def test_rule_failure_message_uses_dict_request_context():
    @policy(policy_id="p1", policy_name="Test Policy")
    class TestPolicy(Policy):
        @rule(
            rule_id="R01",
            rule_name="amount",
            failure_message="Amount ${amount} is too low",
        )
        def amount_is_positive(self, _):
            return False

    result = TestPolicy().execute({"amount": -1})

    rule_result = result.rule_results["R01"]
    assert rule_result.passed is False
    assert rule_result.failure_message == "Amount -1 is too low"
    assert rule_result.error_message is None
    assert result.success is False


def test_rule_failure_message_uses_object_request_context():
    class Request:
        def __init__(self, amount):
            self.amount = amount

    @policy(policy_id="p1", policy_name="Test Policy")
    class TestPolicy(Policy):
        @rule(
            rule_id="R01",
            rule_name="amount",
            failure_message="Amount ${amount} is too low",
        )
        def amount_is_positive(self, _):
            return False

    result = TestPolicy().execute(Request(-1))

    rule_result = result.rule_results["R01"]
    assert rule_result.passed is False
    assert rule_result.failure_message == "Amount -1 is too low"
    assert rule_result.error_message is None


def test_rule_failure_message_leaves_missing_template_values_unchanged():
    @policy(policy_id="p1", policy_name="Test Policy")
    class TestPolicy(Policy):
        @rule(
            rule_id="R01",
            rule_name="amount",
            failure_message="Amount ${amount} is too low",
        )
        def amount_is_positive(self, _):
            return False

    result = TestPolicy().execute({})

    rule_result = result.rule_results["R01"]
    assert rule_result.passed is False
    assert rule_result.failure_message == "Amount ${amount} is too low"
    assert rule_result.error_message is None


def test_rule_exception_returns_error_result():
    @policy(policy_id="p1", policy_name="Test Policy")
    class TestPolicy(Policy):
        @rule(rule_id="R01", rule_name="boom")
        def raises(self, _):
            raise ValueError("boom")

    result = TestPolicy().execute({})

    rule_result = result.rule_results["R01"]
    assert rule_result.passed is False
    assert rule_result.failure_message is None
    assert rule_result.error_message == "boom"
    assert result.success is False

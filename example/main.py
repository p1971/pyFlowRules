from dataclasses import dataclass

from flow.rulesEngine import policy, rule, Policy


@dataclass
class Request:
    id: int
    notional: float
    client: str


@policy(policy_id="P01", policy_name="InitialRequestValidation")
class InitialRequestPolicy(Policy):
    @rule(
        rule_id="R001",
        rule_name="Validate notional",
        failure_message="The notional is too high.")
    def validate_notional(self, r: Request):
        return r.notional < 100000

    @rule(
        rule_id="R0021",
        rule_name="Validate client",
        failure_message="The client is unknown.")
    def validate_client(self, r: Request):
        return r.client in ["client1", "client2"]

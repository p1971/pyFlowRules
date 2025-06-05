from dataclasses import dataclass

from rich.table import Table

from flow.rulesEngine import policy, rule, Policy

from rich.console import Console

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
        rule_id="R002",
        rule_name="Validate client",
        failure_message="The client is unknown.")
    def validate_client(self, r: Request):
        return r.client in ["client1", "client2"]

def main():

    console = Console()

    request = Request(id=1, notional=500000, client="client1")
    policy_instance = InitialRequestPolicy()
    result = policy_instance.execute(request)

    table = Table(show_lines=False, box=None)
    table.add_column()
    table.add_column()
    table.add_column()
    table.add_row(str(result.policy_id), str(result.policy_name), str(result.success))
    console.print(table)

    table = Table()
    table.add_column("Rule Id", justify="right")
    table.add_column("Rule Name", justify="left")
    table.add_column("Passed", justify="center")
    for rule_id, rule_result in result.rule_results.items():
        table.add_row(rule_id, rule_result.rule_name, str(rule_result.passed))
    console.print(table)

if __name__ == "__main__":
    main()

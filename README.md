# py flow rules

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)](#)

A simple rules engine implementation for python.

---

## Features

- Allows the developer to write simple rules policies to aggregate the business logic for an application.

---

## Installation

Clone this repository and install the necessary dependencies.

```bash
git clone https://github.com/p1971/pyFlowRules.git
cd pyFlowRules
python -m venv .venv
source .venv/bin/activate  # On Windows use: .\.venv\Scripts\activate

# For core functionality only (no dependencies required):
pip install -e .

# For development (includes testing tools):
pip install -r requirements-dev.txt

# For running examples:
pip install -r requirements-examples.txt
```

Make sure you have Python 3.10 or above installed.

### Requirements Files

The project uses separate requirements files for different purposes:

- `requirements.txt` - Core dependencies (currently empty as we only use standard library)
- `requirements-dev.txt` - Development dependencies (pytest, coverage, etc.)
- `requirements-examples.txt` - Dependencies for running example code

---

## Usage

Here is an example of how to use the project:

```python
from dataclasses import dataclass

from flow.rulesEngine import policy, rule, Policy

@dataclass
class Request:
    id: int
    notional: float
    client: str
    
@policy(policy_id="P01", policy_name="InitialRequestValidation")
class InitialRequestPolicy(Policy):
    @rule(rule_id="R001", rule_name="Validate notional", failure_message="The notional is too high.")
    def validate_notional(self, r: Request):
        return r.notional < 100000
    
    @rule(rule_id="R002", rule_name="Validate client", failure_message="The client is unknown.")
    def validate_client(self, r: Request):
        return r.client in ["client1", "client2"]
  

policy = InitialRequestPolicy()
result = policy.execute(Request(id=1, notional=90000, client="client1"))
print(result)
```

You can find more examples in the `examples/` directory.
For example
```bash
python -m example.main
```
---

## Running Tests

Unit tests are included for this project. Use `pytest` to run them (recommended):

```bash
pip install pytest  # Install pytest if not already done
pytest
```

---

## Contributing

Contributions are welcome! Please follow these steps to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push your branch (`git push origin feature/your-feature`).
5. Open a pull request.

Make sure your code passes all tests and follows Python best practices.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

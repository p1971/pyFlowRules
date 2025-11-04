"""
A simple rules engine implementation for Python.

This package provides a framework for creating and executing business rules
organized into policies.
"""

from .rules_engine import Policy, rule, policy, RuleResult, PolicyResult
from .__version__ import __version__

__all__ = ['Policy', 'rule', 'policy', 'RuleResult', 'PolicyResult', '__version__']

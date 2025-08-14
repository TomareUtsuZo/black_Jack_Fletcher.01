"""Scenario schema and loading utilities.

This package contains:
- DTO schemas describing scenario files (human-authored YAML/JSON)
- A lightweight loader stub that can parse YAML/JSON later

Scenarios live under `assets/scenarios/` and are meant to be edited without
touching Python. Code here should remain tolerant and well-documented.
"""

from .scenario_schema import ScenarioDTO, ScenarioUnitDTO
from .scenario_loader import ScenarioLoader

__all__ = [
    "ScenarioDTO",
    "ScenarioUnitDTO",
    "ScenarioLoader",
]



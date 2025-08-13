"""Protocol definition for unit modules (minimal shared surface)."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class UnitModule(Protocol):
    """Base protocol that all unit modules must implement."""
    def initialize(self) -> None: ...


"""Scenario loader stub.

Future responsibilities:
- Resolve scenario file paths (env/config + defaults to assets/scenarios/)
- Parse YAML/JSON into ScenarioDTO
- Validate minimal required fields
- Convert DTOs to domain objects (Position, UnitType, NauticalMiles, etc.)

For now, exposes a stub that only reads raw text (no parsing), so build
systems/tests can wire the plumbing without committing to a format.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DEFAULT_SCENARIO_DIR = Path("assets/scenarios")


@dataclass
class ScenarioLoader:
    """Minimal loader to locate and read scenario files.

    This is a placeholder and does not parse or validate content yet.
    """

    base_dir: Path = DEFAULT_SCENARIO_DIR

    def load_raw(self, name: str, ext: Optional[str] = None) -> str:
        """Load a scenario file as raw text.

        Args:
            name: Scenario name without extension (e.g., "test_ships")
            ext: Optional explicit extension ("yaml" or "json"). When omitted,
                 tries .yaml then .json in that order.

        Returns:
            Raw file contents as a string.

        Raises:
            FileNotFoundError: if no matching file is found.
        """
        candidates = []
        if ext:
            candidates.append(self.base_dir / f"{name}.{ext}")
        else:
            candidates.append(self.base_dir / f"{name}.yaml")
            candidates.append(self.base_dir / f"{name}.json")

        for path in candidates:
            if path.exists():
                return path.read_text(encoding="utf-8")

        raise FileNotFoundError(f"Scenario '{name}' not found in {self.base_dir}")



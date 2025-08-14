"""Tests for scenario loader."""

from src.backend.models.game.scenarios import ScenarioLoader


def test_load_raw_test_ships() -> None:
    loader = ScenarioLoader()
    data = loader.load_raw("test_ships")
    assert isinstance(data, str)
    assert "name: test_ships" in data



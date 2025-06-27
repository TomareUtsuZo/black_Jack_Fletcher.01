"""
Tests for bearing calculations and utilities.

These tests verify the Bearing type's functionality including:
- Angle normalization
- Arithmetic operations
- Relative bearing calculations
- Cardinal direction conversions
"""

import math
import pytest
from src.backend.models.common.geometry.bearing import (
    Bearing,
    CardinalDirection,
    NORTH,
    EAST,
    SOUTH,
    WEST,
)

def test_bearing_normalization() -> None:
    """Test bearing normalization."""
    # Basic normalization
    assert Bearing(0).degrees == 0
    assert Bearing(90).degrees == 90
    assert Bearing(180).degrees == 180
    assert Bearing(270).degrees == 270
    assert Bearing(360).degrees == 0

    # Negative angles
    assert Bearing(-90).degrees == 270
    assert Bearing(-180).degrees == 180
    assert Bearing(-270).degrees == 90
    assert Bearing(-360).degrees == 0

    # Angles > 360
    assert Bearing(450).degrees == 90
    assert Bearing(720).degrees == 0
    assert Bearing(810).degrees == 90

def test_bearing_signed_degrees() -> None:
    """Test signed degrees conversion."""
    assert Bearing(0).signed_degrees == 0
    assert Bearing(90).signed_degrees == 90
    assert Bearing(180).signed_degrees == 180
    assert Bearing(270).signed_degrees == -90
    assert Bearing(360).signed_degrees == 0

def test_bearing_radians() -> None:
    """Test radians conversion."""
    assert Bearing(0).radians == 0
    assert Bearing(90).radians == math.pi / 2
    assert Bearing(180).radians == math.pi
    assert Bearing(270).radians == 3 * math.pi / 2
    assert Bearing(360).radians == 0

def test_bearing_arithmetic() -> None:
    """Test bearing arithmetic operations."""
    # Addition
    assert (Bearing(90) + Bearing(90)).degrees == 180
    assert (Bearing(270) + Bearing(180)).degrees == 90
    assert (Bearing(0) + 90).degrees == 90
    
    # Subtraction
    assert (Bearing(180) - Bearing(90)).degrees == 90
    assert (Bearing(0) - Bearing(90)).degrees == 270
    assert (Bearing(90) - 45).degrees == 45

def test_bearing_equality() -> None:
    """Test bearing equality comparisons."""
    # Direct equality
    assert Bearing(90) == Bearing(90)
    assert Bearing(360) == Bearing(0)
    assert Bearing(-90) == Bearing(270)
    
    # Float comparison tolerance
    assert Bearing(90.000001) == Bearing(90)

def test_relative_bearing() -> None:
    """Test relative bearing calculations."""
    # Basic relative bearings
    assert Bearing(90).relative_to(Bearing(0)) == 90  # Target to starboard
    assert Bearing(270).relative_to(Bearing(0)) == -90  # Target to port
    assert Bearing(180).relative_to(Bearing(0)) == 180  # Target behind
    
    # Relative to non-zero reference
    assert Bearing(45).relative_to(Bearing(45)) == 0  # Target ahead
    assert Bearing(315).relative_to(Bearing(45)) == -90  # Target to port
    
    # Crossing the 0/360 boundary
    assert Bearing(350).relative_to(Bearing(10)) == -20
    assert Bearing(10).relative_to(Bearing(350)) == 20

def test_reciprocal_bearing() -> None:
    """Test reciprocal bearing calculations."""
    assert Bearing(0).reciprocal().degrees == 180
    assert Bearing(90).reciprocal().degrees == 270
    assert Bearing(180).reciprocal().degrees == 0
    assert Bearing(270).reciprocal().degrees == 90

def test_cardinal_directions() -> None:
    """Test cardinal direction conversions."""
    # Cardinal points
    assert CardinalDirection.from_bearing(NORTH) == CardinalDirection.N
    assert CardinalDirection.from_bearing(EAST) == CardinalDirection.E
    assert CardinalDirection.from_bearing(SOUTH) == CardinalDirection.S
    assert CardinalDirection.from_bearing(WEST) == CardinalDirection.W
    
    # Intercardinal points
    assert CardinalDirection.from_bearing(Bearing(45)) == CardinalDirection.NE
    assert CardinalDirection.from_bearing(Bearing(135)) == CardinalDirection.SE
    assert CardinalDirection.from_bearing(Bearing(225)) == CardinalDirection.SW
    assert CardinalDirection.from_bearing(Bearing(315)) == CardinalDirection.NW
    
    # Edge cases
    assert CardinalDirection.from_bearing(Bearing(337.5)) == CardinalDirection.N  # Just within North
    assert CardinalDirection.from_bearing(Bearing(22.4)) == CardinalDirection.N   # Just within North

def test_cardinal_to_bearing() -> None:
    """Test converting cardinal directions to bearings."""
    assert CardinalDirection.N.to_bearing().degrees == 0
    assert CardinalDirection.NE.to_bearing().degrees == 45
    assert CardinalDirection.E.to_bearing().degrees == 90
    assert CardinalDirection.SE.to_bearing().degrees == 135
    assert CardinalDirection.S.to_bearing().degrees == 180
    assert CardinalDirection.SW.to_bearing().degrees == 225
    assert CardinalDirection.W.to_bearing().degrees == 270
    assert CardinalDirection.NW.to_bearing().degrees == 315

def test_cardinal_string_representation() -> None:
    """Test string representation of cardinal directions."""
    assert str(CardinalDirection.N) == "N"
    assert str(CardinalDirection.NE) == "NE"
    assert str(CardinalDirection.E) == "E"
    assert str(CardinalDirection.SE) == "SE"
    assert str(CardinalDirection.S) == "S"
    assert str(CardinalDirection.SW) == "SW"
    assert str(CardinalDirection.W) == "W"
    assert str(CardinalDirection.NW) == "NW" 
"""
Tests for the haversine distance calculation functionality.

These tests verify the accuracy of distance and bearing calculations between
geographic positions, with a focus on major international airports with
well-documented coordinates and distances.
"""

import math
import pytest
from typing import NoReturn
from src.backend.models.common.geometry.haversine import (
    calculate_haversine_distance,
    bearing_between
)
from src.backend.models.common.geometry.position import Position
from src.backend.models.common.geometry.nautical_miles import NauticalMiles

# Major international airport coordinates (using game Position)
# Scale factor is 1.0 (1 game unit = 1 degree)
SFO = Position(x=-122.375416, y=37.618806)  # San Francisco International
JFK = Position(x=-73.780968, y=40.641766)   # John F. Kennedy International
LAX = Position(x=-118.408049, y=33.942496)  # Los Angeles International
SEA = Position(x=-122.311777, y=47.449888)  # Seattle-Tacoma International

# Scale factor for converting game coordinates to geographic coordinates
SCALE_FACTOR = 1.0  # 1 game unit = 1 degree

# Common distances in nautical miles
EARTH_CIRCUMFERENCE_NM = NauticalMiles(21600)  # Earth's circumference
HALF_EARTH_CIRCUMFERENCE_NM = NauticalMiles(EARTH_CIRCUMFERENCE_NM.value / 2)

def test_airport_distances() -> None:
    """
    Test distances between major airports.
    
    These distances are verified against current aviation data and
    official airport distance calculations.
    """
    # SFO to JFK (Official distance: 2247 nautical miles)
    distance = calculate_haversine_distance(SFO, JFK, SCALE_FACTOR)
    assert abs(distance.value - NauticalMiles(2247).value) < 1  # Within 1 nautical mile

    # SFO to LAX (Official distance: 293 nautical miles)
    distance = calculate_haversine_distance(SFO, LAX, SCALE_FACTOR)
    assert abs(distance.value - NauticalMiles(293).value) < 1  # Within 1 nautical mile

    # SEA to LAX (Official distance: 829 nautical miles)
    distance = calculate_haversine_distance(SEA, LAX, SCALE_FACTOR)
    assert abs(distance.value - NauticalMiles(829).value) < 5  # Within 5 nautical miles

def test_airport_bearings() -> None:
    """
    Test bearings between major airports.
    
    These bearings are verified against current aviation data.
    """
    # SFO to JFK (Initial bearing: ~70 degrees)
    bearing = bearing_between(SFO, JFK, SCALE_FACTOR)
    assert abs(bearing - 70) < 1  # Within 1 degree

    # SFO to LAX (Initial bearing: ~137.5 degrees)
    bearing = bearing_between(SFO, LAX, SCALE_FACTOR)
    assert abs(bearing - 137.5) < 1  # Within 1 degree

def test_symmetrical_distances() -> None:
    """Test that distances are symmetrical (A to B equals B to A)."""
    dist1 = calculate_haversine_distance(SFO, JFK, SCALE_FACTOR)
    dist2 = calculate_haversine_distance(JFK, SFO, SCALE_FACTOR)
    assert dist1 == dist2

def test_zero_distance() -> None:
    """Test distance calculation between same point."""
    dist = calculate_haversine_distance(SFO, SFO, SCALE_FACTOR)
    assert dist == NauticalMiles(0)

def test_antipodal_points() -> None:
    """Test distance calculation between antipodal points."""
    north_pole = Position(x=0, y=90)
    south_pole = Position(x=0, y=-90)
    dist = calculate_haversine_distance(north_pole, south_pole, SCALE_FACTOR)
    
    # Distance should be half Earth's circumference in nautical miles
    assert abs(dist.value - HALF_EARTH_CIRCUMFERENCE_NM.value) < 10  # Within 10 nautical miles

def test_bearing_edge_cases() -> None:
    """Test bearing calculations for edge cases."""
    # North to South (should be 180 degrees)
    north = Position(x=0, y=10)
    south = Position(x=0, y=0)
    assert bearing_between(north, south, SCALE_FACTOR) == pytest.approx(180, abs=1)
    
    # West to East (should be 90 degrees)
    west = Position(x=0, y=0)
    east = Position(x=10, y=0)
    assert bearing_between(west, east, SCALE_FACTOR) == pytest.approx(90, abs=1)
    
    # East to West (should be 270 degrees)
    assert bearing_between(east, west, SCALE_FACTOR) == pytest.approx(270, abs=1) 
"""
Tests for the Vincenty distance calculation functionality.

These tests verify the accuracy of distance and bearing calculations between
geographic positions, with a focus on major international airports with
well-documented coordinates and distances.
"""

import math
import pytest
from typing import NoReturn
from src.backend.models.common.geometry.vincenty import (
    calculate_haversine_distance,
    calculate_vincenty_distance,
    calculate_vincenty_full,
    bearing_between,
    GeoPosition,
    VincentyResult,
    normalize_radians,
    normalize_degrees,
    degrees_to_radians,
    radians_to_degrees,
    calculate_reduced_latitude,
    METERS_PER_NAUTICAL_MILE
)
from src.backend.models.common.geometry.position import Position
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.common.geometry.bearing import Bearing

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

def test_geo_position_creation() -> None:
    """Test GeoPosition creation and validation."""
    # Valid positions
    pos = GeoPosition(0, 0)
    assert pos.latitude == 0
    assert pos.longitude == 0
    
    pos = GeoPosition(90, 180)
    assert pos.latitude == 90
    assert pos.longitude == 180
    
    pos = GeoPosition(-90, -180)
    assert pos.latitude == -90
    assert pos.longitude == -180
    
    # Invalid positions
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        GeoPosition(91, 0)
    
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        GeoPosition(-91, 0)
        
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        GeoPosition(0, 181)
        
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        GeoPosition(0, -181)

def test_geo_position_conversion() -> None:
    """Test conversion between Position and GeoPosition."""
    # Test with scale factor 1.0
    game_pos = Position(x=10, y=20)
    geo_pos = GeoPosition.from_position(game_pos, 1.0)
    assert geo_pos.longitude == 10
    assert geo_pos.latitude == 20
    
    # Convert back
    converted_pos = geo_pos.to_position(1.0)
    assert converted_pos.x == game_pos.x
    assert converted_pos.y == game_pos.y
    
    # Test with different scale factor
    scale = 2.0
    geo_pos = GeoPosition.from_position(game_pos, scale)
    assert geo_pos.longitude == 5  # 10/2
    assert geo_pos.latitude == 10  # 20/2
    
    # Convert back
    converted_pos = geo_pos.to_position(scale)
    assert converted_pos.x == game_pos.x
    assert converted_pos.y == game_pos.y

def test_angle_conversions() -> None:
    """Test angle conversion functions."""
    # Test degrees to radians
    assert degrees_to_radians(180) == math.pi
    assert degrees_to_radians(90) == math.pi/2
    assert degrees_to_radians(0) == 0
    
    # Test radians to degrees
    assert radians_to_degrees(math.pi) == 180
    assert radians_to_degrees(math.pi/2) == 90
    assert radians_to_degrees(0) == 0

def test_reduced_latitude() -> None:
    """Test reduced latitude calculations."""
    # Test equator (0°)
    result = calculate_reduced_latitude(0)
    assert result.U == 0
    assert result.sin_U == 0
    assert result.cos_U == 1
    
    # Test poles (90°)
    result = calculate_reduced_latitude(math.pi/2)
    assert result.U == pytest.approx(math.pi/2)
    assert result.sin_U == pytest.approx(1)
    assert result.cos_U == pytest.approx(0, abs=1e-6)

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
    assert abs(bearing.degrees - 70) < 1  # Within 1 degree

    # SFO to LAX (Initial bearing: ~137.5 degrees)
    bearing = bearing_between(SFO, LAX, SCALE_FACTOR)
    assert abs(bearing.degrees - 137.5) < 1  # Within 1 degree

def test_symmetrical_distances() -> None:
    """Test that distances are symmetrical (A to B equals B to A)."""
    dist1 = calculate_haversine_distance(SFO, JFK, SCALE_FACTOR)
    dist2 = calculate_haversine_distance(JFK, SFO, SCALE_FACTOR)
    assert dist1.value == pytest.approx(dist2.value)
    
    # Also test with Vincenty
    dist1 = calculate_vincenty_distance(SFO, JFK, SCALE_FACTOR)
    dist2 = calculate_vincenty_distance(JFK, SFO, SCALE_FACTOR)
    assert dist1.value == pytest.approx(dist2.value)

def test_zero_distance() -> None:
    """Test distance calculation between same point."""
    dist = calculate_haversine_distance(SFO, SFO, SCALE_FACTOR)
    assert dist == NauticalMiles(0)
    
    # Also test with Vincenty
    dist = calculate_vincenty_distance(SFO, SFO, SCALE_FACTOR)
    assert dist == NauticalMiles(0)

def test_antipodal_points() -> None:
    """Test distance calculation between antipodal points."""
    north_pole = Position(x=0, y=90)
    south_pole = Position(x=0, y=-90)
    
    # Test both Haversine and Vincenty
    dist_haversine = calculate_haversine_distance(north_pole, south_pole, SCALE_FACTOR)
    dist_vincenty = calculate_vincenty_distance(north_pole, south_pole, SCALE_FACTOR)
    
    # Both should be close to half Earth's circumference
    assert abs(dist_haversine.value - HALF_EARTH_CIRCUMFERENCE_NM.value) < 10
    assert abs(dist_vincenty.value - HALF_EARTH_CIRCUMFERENCE_NM.value) < 10

def test_bearing_edge_cases() -> None:
    """Test bearing calculations for edge cases."""
    # North to South (should be 180 degrees)
    north = Position(x=0, y=10)
    south = Position(x=0, y=0)
    assert bearing_between(north, south, SCALE_FACTOR).degrees == pytest.approx(180, abs=1)
    
    # West to East (should be 90 degrees)
    west = Position(x=0, y=0)
    east = Position(x=10, y=0)
    assert bearing_between(west, east, SCALE_FACTOR).degrees == pytest.approx(90, abs=1)
    
    # East to West (should be 270 degrees)
    assert bearing_between(east, west, SCALE_FACTOR).degrees == pytest.approx(270, abs=1)

def test_equatorial_points() -> None:
    """Test calculations for points on the equator."""
    # Two points on the equator
    point1 = GeoPosition(0, 0)
    point2 = GeoPosition(0, 90)
    
    result = calculate_vincenty_full(point1, point2)
    
    # Should be 1/4 of Earth's circumference
    expected_distance = EARTH_CIRCUMFERENCE_NM.value / 4
    assert abs(result.distance.value - expected_distance) < 10
    
    # Initial bearing should be 90° (due East)
    assert result.initial_bearing.degrees == pytest.approx(90, abs=1)
    
    # Final bearing should also be 90° on equator
    assert result.final_bearing.degrees == pytest.approx(90, abs=1) 
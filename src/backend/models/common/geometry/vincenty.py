"""
Implementation of distance calculations between geographic coordinates.

This module provides functions for calculating accurate distances between points on the Earth's
surface using Vincenty's formulae. Each calculation is broken down into atomic functions
for better testing and debugging capabilities.
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple, NamedTuple

from .nautical_miles import NauticalMiles
from .position import Position
from .bearing import Bearing

# --- Data Types ---
class ReducedLatitude(NamedTuple):
    """Represents a reduced latitude with its sine and cosine components."""
    U: float  # Reduced latitude angle
    sin_U: float  # Sine of reduced latitude
    cos_U: float  # Cosine of reduced latitude

class VincentyResult(NamedTuple):
    """Results from Vincenty's formulae calculations."""
    distance: NauticalMiles  # Distance in nautical miles
    initial_bearing: Bearing  # Initial bearing
    final_bearing: Bearing   # Final bearing

@dataclass(frozen=True)
class GeoPosition:
    """
    Represents an immutable geographic position using latitude and longitude.
    
    Attributes:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
    """
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Validate the latitude and longitude values."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90 degrees, got {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180 degrees, got {self.longitude}")

    def distance_to(self, other: 'GeoPosition') -> NauticalMiles:
        """Calculate the distance to another position using Vincenty's formulae."""
        result = calculate_vincenty_full(self, other)
        return result.distance

    @classmethod
    def from_position(cls, position: Position, scale_factor: float = 1.0) -> 'GeoPosition':
        """Convert a game Position to a GeoPosition using a scale factor."""
        return cls(
            latitude=position.y / scale_factor,
            longitude=position.x / scale_factor
        )

    def to_position(self, scale_factor: float = 1.0) -> Position:
        """Convert to a game Position using a scale factor."""
        return Position(
            x=self.longitude * scale_factor,
            y=self.latitude * scale_factor
        )

# --- Constants ---
WGS84_A = 6378137.0  # semi-major axis in meters
WGS84_B = 6356752.314245  # semi-minor axis in meters
WGS84_F = 1/298.257223563  # flattening
WGS84_E_SQ = WGS84_F * (2 - WGS84_F)  # eccentricity squared
METERS_PER_NAUTICAL_MILE = 1852.0  # Conversion factor from meters to nautical miles

# --- Basic math operations ---
def normalize_radians(angle_rad: float) -> float:
    """Normalize angle to -π to π."""
    while angle_rad > math.pi:
        angle_rad -= 2 * math.pi
    while angle_rad < -math.pi:
        angle_rad += 2 * math.pi
    return angle_rad

def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return math.radians(degrees)

def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return math.degrees(radians)

def normalize_degrees(degrees: float) -> float:
    """Normalize degrees to 0-360 range."""
    return (degrees + 360.0) % 360.0

# --- Coordinate transformations ---
def calculate_reduced_latitude(lat_rad: float) -> ReducedLatitude:
    """Calculate reduced latitude (latitude on auxiliary sphere)."""
    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    
    # U = arctan((1-f) * tan(lat))
    U = math.atan((1 - WGS84_F) * sin_lat / cos_lat)
    sin_U = math.sin(U)
    cos_U = math.cos(U)
    
    return ReducedLatitude(U, sin_U, cos_U)

# --- Vincenty iteration components ---
def calculate_sigma_components(
    reduced_lat1: ReducedLatitude,
    reduced_lat2: ReducedLatitude,
    sin_lambda: float,
    cos_lambda: float
) -> Tuple[float, float, float]:
    """Calculate sigma and its components."""
    # First term: cos(U2) * sin(λ)
    term1 = reduced_lat2.cos_U * sin_lambda
    
    # Second term: cos(U1) * sin(U2) - sin(U1) * cos(U2) * cos(λ)
    term2 = (reduced_lat1.cos_U * reduced_lat2.sin_U - 
             reduced_lat1.sin_U * reduced_lat2.cos_U * cos_lambda)
    
    sin_sigma = math.sqrt(term1 * term1 + term2 * term2)
    cos_sigma = (reduced_lat1.sin_U * reduced_lat2.sin_U + 
                 reduced_lat1.cos_U * reduced_lat2.cos_U * cos_lambda)
    sigma = math.atan2(sin_sigma, cos_sigma)
    
    return sin_sigma, cos_sigma, sigma

def calculate_alpha_components(
    reduced_lat1: ReducedLatitude,
    reduced_lat2: ReducedLatitude,
    sin_lambda: float,
    sin_sigma: float
) -> Tuple[float, float]:
    """Calculate alpha (azimuth) components."""
    sin_alpha = reduced_lat1.cos_U * reduced_lat2.cos_U * sin_lambda / sin_sigma
    cos_sq_alpha = 1 - sin_alpha * sin_alpha
    
    return sin_alpha, cos_sq_alpha

def calculate_cos_2sigma_m(
    cos_sigma: float,
    reduced_lat1: ReducedLatitude,
    reduced_lat2: ReducedLatitude,
    cos_sq_alpha: float
) -> float:
    """Calculate cos(2σₘ)."""
    if cos_sq_alpha == 0:
        return 0  # Equatorial line
    
    cos_2sigma_m = cos_sigma - 2 * reduced_lat1.sin_U * reduced_lat2.sin_U / cos_sq_alpha
    return cos_2sigma_m

def calculate_C_term(cos_sq_alpha: float) -> float:
    """Calculate C term for lambda iteration."""
    C = WGS84_F / 16 * cos_sq_alpha * (4 + WGS84_F * (4 - 3 * cos_sq_alpha))
    return C

def calculate_new_lambda(
    L: float,
    C: float,
    sin_alpha: float,
    sigma: float,
    sin_sigma: float,
    cos_2sigma_m: float,
    cos_sigma: float
) -> float:
    """Calculate new lambda value."""
    lambda_new = L + (1 - C) * WGS84_F * sin_alpha * (
        sigma + C * sin_sigma * (
            cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m * cos_2sigma_m)
        )
    )
    return normalize_radians(lambda_new)

# --- Final distance calculation ---
def calculate_distance_terms(cos_sq_alpha: float) -> Tuple[float, float, float]:
    """Calculate u², A, and B terms for final distance."""
    u_sq = cos_sq_alpha * (WGS84_A ** 2 - WGS84_B ** 2) / WGS84_B ** 2
    
    A = 1 + u_sq / 16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
    
    B = u_sq / 1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
    
    return u_sq, A, B

def calculate_delta_sigma(
    B: float,
    sin_sigma: float,
    cos_2sigma_m: float,
    cos_sigma: float,
    sin_sigma_sq: float
) -> float:
    """Calculate delta sigma correction."""
    delta_sigma = B * sin_sigma * (
        cos_2sigma_m + B / 4 * (
            cos_sigma * (-1 + 2 * cos_2sigma_m * cos_2sigma_m) -
            B / 6 * cos_2sigma_m * (-3 + sin_sigma_sq) * 
            (-3 + 4 * cos_2sigma_m * cos_2sigma_m)
        )
    )
    return delta_sigma

def calculate_final_distance(
    sigma: float,
    delta_sigma: float,
    A: float
) -> NauticalMiles:
    """Calculate final ellipsoidal distance."""
    s = WGS84_B * A * (sigma - delta_sigma)
    return NauticalMiles(s / METERS_PER_NAUTICAL_MILE)

# --- Bearing calculations ---
def calculate_initial_bearing(
    reduced_lat1: ReducedLatitude,
    reduced_lat2: ReducedLatitude,
    sin_lambda: float,
    cos_lambda: float,
    sin_alpha: float
) -> Bearing:
    """Calculate initial bearing."""
    y = sin_lambda * reduced_lat2.cos_U
    x = reduced_lat1.cos_U * reduced_lat2.sin_U - reduced_lat1.sin_U * reduced_lat2.cos_U * cos_lambda
    
    return Bearing(math.degrees(math.atan2(y, x)))

def calculate_final_bearing(
    reduced_lat1: ReducedLatitude,
    sin_sigma: float,
    cos_sigma: float,
    sin_alpha: float
) -> Bearing:
    """Calculate final bearing."""
    cos_alpha = math.sqrt(1 - sin_alpha * sin_alpha)
    y = reduced_lat1.cos_U * sin_alpha
    x = -reduced_lat1.sin_U * cos_sigma + reduced_lat1.cos_U * sin_sigma * cos_alpha
    
    return Bearing(math.degrees(math.atan2(y, x)))

# --- Main calculation function ---
def calculate_vincenty_full(pos1: GeoPosition, pos2: GeoPosition) -> VincentyResult:
    """Calculate distance and bearings between two points using Vincenty's formulae."""
    # Step 1: Convert to radians
    lat1 = math.radians(pos1.latitude)
    lon1 = math.radians(pos1.longitude)
    lat2 = math.radians(pos2.latitude)
    lon2 = math.radians(pos2.longitude)
    
    # Step 2: Calculate reduced latitudes
    reduced_lat1 = calculate_reduced_latitude(lat1)
    reduced_lat2 = calculate_reduced_latitude(lat2)
    
    # Step 3: Initial lambda (longitude difference)
    L = lon2 - lon1
    lambda_old = normalize_radians(L)
    
    # Step 4: Iterate to convergence
    for iteration in range(100):
        # Step 4a: Calculate lambda components
        sin_lambda = math.sin(lambda_old)
        cos_lambda = math.cos(lambda_old)
        
        # Step 4b: Calculate sigma components
        sin_sigma, cos_sigma, sigma = calculate_sigma_components(
            reduced_lat1, reduced_lat2, sin_lambda, cos_lambda
        )
        
        if sin_sigma == 0:
            return VincentyResult(NauticalMiles(0), Bearing(0), Bearing(0))
        
        # Step 4c: Calculate alpha components
        sin_alpha, cos_sq_alpha = calculate_alpha_components(
            reduced_lat1, reduced_lat2, sin_lambda, sin_sigma
        )
        
        # Step 4d: Calculate cos(2σₘ)
        cos_2sigma_m = calculate_cos_2sigma_m(
            cos_sigma, reduced_lat1, reduced_lat2, cos_sq_alpha
        )
        
        # Step 4e: Calculate new lambda
        C = calculate_C_term(cos_sq_alpha)
        lambda_new = calculate_new_lambda(
            L, C, sin_alpha, sigma, sin_sigma,
            cos_2sigma_m, cos_sigma
        )
        
        # Step 4f: Check convergence
        if abs(lambda_new - lambda_old) < 1e-12:
            # Step 5: Calculate final distance
            u_sq, A, B = calculate_distance_terms(cos_sq_alpha)
            delta_sigma = calculate_delta_sigma(
                B, sin_sigma, cos_2sigma_m, cos_sigma,
                sin_sigma * sin_sigma
            )
            distance = calculate_final_distance(sigma, delta_sigma, A)
            
            # Step 6: Calculate bearings using standard great circle formula
            # Account for convergence of meridians by using reduced latitudes
            initial_bearing = calculate_initial_bearing(
                reduced_lat1, reduced_lat2, sin_lambda, cos_lambda, sin_alpha
            )
            
            # Final bearing is initial bearing from point 2 to point 1 + 180°
            final_bearing = calculate_final_bearing(
                reduced_lat1, sin_sigma, cos_sigma, sin_alpha
            )
            
            return VincentyResult(distance, initial_bearing, final_bearing)
        
        lambda_old = lambda_new
    
    raise ValueError("Vincenty formula failed to converge")

def calculate_vincenty_distance(pos1: Position, pos2: Position, scale_factor: float = 1.0) -> NauticalMiles:
    """
    Calculate the distance between two game positions using Vincenty's formulae.
    
    Args:
        pos1: First game position
        pos2: Second game position
        scale_factor: Scale factor to convert game coordinates to geographic coordinates
        
    Returns:
        Distance in nautical miles
    """
    geo_pos1 = GeoPosition.from_position(pos1, scale_factor)
    geo_pos2 = GeoPosition.from_position(pos2, scale_factor)
    result = calculate_vincenty_full(geo_pos1, geo_pos2)
    return result.distance

def calculate_haversine_distance(pos1: Position, pos2: Position, scale_factor: float = 1.0) -> NauticalMiles:
    """
    Alias for Vincenty distance calculation.
    
    Args:
        pos1: First game position
        pos2: Second game position
        scale_factor: Scale factor to convert game coordinates to geographic coordinates
        
    Returns:
        Distance in nautical miles
    """
    return calculate_vincenty_distance(pos1, pos2, scale_factor)

def bearing_between(pos1: Position, pos2: Position, scale_factor: float = 1.0) -> Bearing:
    """
    Calculate the initial bearing from pos1 to pos2 using Vincenty's formulae.
    
    Args:
        pos1: First game position
        pos2: Second game position
        scale_factor: Scale factor to convert game coordinates to geographic coordinates
        
    Returns:
        Initial bearing in degrees
    """
    geo_pos1 = GeoPosition.from_position(pos1, scale_factor)
    geo_pos2 = GeoPosition.from_position(pos2, scale_factor)
    result = calculate_vincenty_full(geo_pos1, geo_pos2)
    return result.initial_bearing 
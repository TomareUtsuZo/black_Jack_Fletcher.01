"""Tests for the NauticalMiles class."""

import pytest
from src.backend.models.common.geometry.nautical_miles import NauticalMiles

@pytest.mark.unit
def test_create_nautical_miles() -> None:
    """Test creating NauticalMiles instances."""
    nm = NauticalMiles(10.0)
    assert nm.value == 10.0
    assert str(nm) == "10.00 NM"
    assert repr(nm) == "NauticalMiles(10.0)"

@pytest.mark.unit
def test_invalid_values() -> None:
    """Test that invalid values raise appropriate errors."""
    with pytest.raises(ValueError):
        NauticalMiles(-1.0)
    
    with pytest.raises(TypeError):
        NauticalMiles("10")  # type: ignore
    
    with pytest.raises(ValueError):
        NauticalMiles.from_meters(-100)
    
    with pytest.raises(ValueError):
        NauticalMiles.from_kilometers(-1)
    
    with pytest.raises(ValueError):
        NauticalMiles.from_statute_miles(-5)

@pytest.mark.unit
def test_conversions() -> None:
    """Test converting between different units."""
    nm = NauticalMiles(1.0)
    
    # Test conversion to meters (1 NM = 1852m exactly)
    assert nm.to_meters() == 1852.0
    
    # Test conversion to kilometers
    assert nm.to_kilometers() == 1.852
    
    # Test conversion to statute miles
    assert pytest.approx(nm.to_statute_miles(), rel=1e-5) == 1.15078

@pytest.mark.unit
def test_from_conversions() -> None:
    """Test creating NauticalMiles from other units."""
    # From meters
    nm = NauticalMiles.from_meters(1852.0)
    assert nm.value == pytest.approx(1.0)
    
    # From kilometers
    nm = NauticalMiles.from_kilometers(1.852)
    assert nm.value == pytest.approx(1.0)
    
    # From statute miles
    nm = NauticalMiles.from_statute_miles(1.15078)
    assert nm.value == pytest.approx(1.0)

@pytest.mark.unit
def test_arithmetic_operations() -> None:
    """Test arithmetic operations with NauticalMiles."""
    nm1 = NauticalMiles(10.0)
    nm2 = NauticalMiles(5.0)
    
    # Addition
    result = nm1 + nm2
    assert isinstance(result, NauticalMiles)
    assert result.value == 15.0
    
    # Subtraction
    result = nm1 - nm2
    assert isinstance(result, NauticalMiles)
    assert result.value == 5.0
    
    # Multiplication by scalar
    result = nm1 * 2
    assert isinstance(result, NauticalMiles)
    assert result.value == 20.0
    
    # Division by scalar
    result = nm1 / 2
    assert isinstance(result, NauticalMiles)
    assert result.value == 5.0
    
    # Test division by zero
    with pytest.raises(ZeroDivisionError):
        nm1 / 0

@pytest.mark.unit
def test_comparisons() -> None:
    """Test comparison operations."""
    nm1 = NauticalMiles(10.0)
    nm2 = NauticalMiles(5.0)
    nm3 = NauticalMiles(10.0)
    
    # Equality
    assert nm1 == nm3
    assert nm1 != nm2
    
    # Less than
    assert nm2 < nm1
    assert not (nm1 < nm2)
    
    # Less than or equal
    assert nm2 <= nm1
    assert nm1 <= nm3
    assert not (nm1 <= nm2)
    
    # Test comparison with non-NauticalMiles
    assert nm1 != "10.0" 
from enum import Enum
from .game_time import GameTime
from datetime import time, timedelta
import astral
from astral.sun import sun
from astral import LocationInfo
from ..geometry.nautical_miles import NauticalMiles


class DayNightState(Enum):
    DAY = 'day'
    NIGHT = 'night'
    DAWN = 'dawn'  # 30 minutes before sunrise
    DUSK = 'dusk'  # 30 minutes after sunset

class DayNightCycle:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self.location = LocationInfo(latitude=latitude, longitude=longitude)
    
    def get_state(self, current_time: GameTime) -> DayNightState:
        s = sun(self.location.observer, date=current_time.to_datetime().date(), tzinfo=current_time.to_datetime().tzinfo)
        sunrise_time = s['sunrise']  # datetime object
        sunset_time = s['sunset']  # datetime object
        current_dt = current_time.to_datetime()
        
        dawn_start = sunrise_time - timedelta(minutes=30)
        dusk_end = sunset_time + timedelta(minutes=30)
        
        if dawn_start <= current_dt < sunrise_time:
            return DayNightState.DAWN
        elif sunrise_time <= current_dt < sunset_time:
            return DayNightState.DAY
        elif sunset_time <= current_dt < dusk_end:
            return DayNightState.DUSK
        else:
            return DayNightState.NIGHT

    def get_moon_phase(self, current_time: GameTime) -> float:
        """
        Get the current moon phase as a float between 0.0 and 1.0.
        
        Args:
            current_time: The current game time.
        
        Returns:
            A float between 0.0 (new moon) and 1.0 (full moon).
        """
        import ephem
        observer = ephem.Observer()
        observer.date = current_time.to_datetime()
        moon = ephem.Moon()
        moon.compute(observer)
        return moon.phase / 100.0  # Normalize ephem phase (0-100%) to 0.0-1.0

    def get_detection_range(self, current_time: GameTime, base_range: NauticalMiles) -> NauticalMiles:
        """
        Calculate visual detection range based on current conditions.
        
        Args:
            current_time: The current game time.
            base_range: Base visual detection range (used for daytime).
            
        Returns:
            NauticalMiles: The detection range based on conditions:
            - Day: base_range
            - Dawn/Dusk: 10nm
            - Night: 1-5nm based on moon phase (1nm new moon, 5nm full moon)
        """
        state = self.get_state(current_time)
        
        if state == DayNightState.NIGHT:
            moon_phase = self.get_moon_phase(current_time)
            # Linear interpolation between 1nm (new moon) and 5nm (full moon)
            night_range = 1.0 + (4.0 * moon_phase)  # moon_phase is 0.0 to 1.0
            return NauticalMiles(night_range)
        elif state in [DayNightState.DAWN, DayNightState.DUSK]:
            return NauticalMiles(10.0)
        else:  # DAY
            return base_range
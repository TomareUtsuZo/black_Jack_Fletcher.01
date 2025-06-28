"""
Tests for the game scheduler module.

These tests verify:
1. Scheduler initialization and configuration
2. Start/stop functionality
3. Tick timing accuracy
4. Error handling
5. Thread management
"""

import pytest
import time
from threading import Event
from typing import List, NoReturn, Any, Callable
from src.backend.models.common.time.game_scheduler import GameScheduler

class TestGameScheduler:
    """Test suite for GameScheduler class."""
    
    def test_scheduler_init_default_values(self) -> None:
        """Test scheduler initialization with default values."""
        scheduler = GameScheduler()
        assert scheduler.tick_interval == 1.0
        assert scheduler.is_running is False
    
    def test_scheduler_init_custom_interval(self) -> None:
        """Test scheduler initialization with custom tick interval."""
        scheduler = GameScheduler(tick_interval=0.5)
        assert scheduler.tick_interval == 0.5
        assert scheduler.is_running is False
    
    def test_start_with_invalid_handler_raises_error(self) -> None:
        """Test that starting with an invalid tick handler raises an error."""
        scheduler = GameScheduler()
        
        # Create a handler with an invalid signature for testing
        # We use Any to tell mypy we know this is wrong
        invalid_handler: Any = lambda x: None
        
        with pytest.raises(TypeError) as exc_info:
            scheduler.start(tick_handler=invalid_handler)
        
        assert "Tick handler must take no arguments" in str(exc_info.value)
    
    def test_double_start_raises_error(self) -> None:
        """Test that starting an already running scheduler raises an error."""
        scheduler = GameScheduler()
        event = Event()
        
        def dummy_handler() -> None:
            event.set()
            
        scheduler.start(tick_handler=dummy_handler)
        try:
            with pytest.raises(RuntimeError, match="Scheduler is already running"):
                scheduler.start(tick_handler=dummy_handler)
        finally:
            scheduler.stop()
    
    def test_tick_timing_accuracy(self) -> None:
        """
        Test that ticks occur at approximately the specified interval.
        
        Note: This test allows for some timing variance due to system scheduling,
        but ensures we're reasonably close to the target interval.
        """
        tick_interval = 0.1  # Use short interval for testing
        allowed_variance = 0.05  # Allow 50ms variance
        tick_count = 0
        last_tick = time.time()
        intervals: List[float] = []
        event = Event()
        
        def tick_handler() -> None:
            nonlocal tick_count, last_tick
            current_time = time.time()
            if tick_count > 0:  # Skip first tick for timing
                intervals.append(current_time - last_tick)
            last_tick = current_time
            tick_count += 1
            if tick_count >= 5:  # Collect 5 intervals
                event.set()
        
        scheduler = GameScheduler(tick_interval=tick_interval)
        scheduler.start(tick_handler=tick_handler)
        
        # Wait for 5 ticks or timeout after 2 seconds
        event.wait(timeout=2.0)
        scheduler.stop()
        
        # Check timing accuracy
        assert len(intervals) >= 3, "Not enough ticks collected"
        for interval in intervals:
            assert abs(interval - tick_interval) < allowed_variance, \
                f"Tick interval {interval} too far from target {tick_interval}"
    
    def test_stop_scheduler(self) -> None:
        """Test that stopping the scheduler properly cleans up resources."""
        scheduler = GameScheduler()
        event = Event()
        
        def dummy_handler() -> None:
            event.set()
            
        # Start the scheduler and verify it's running
        scheduler.start(tick_handler=dummy_handler)
        assert scheduler.is_running is True
        
        # Stop the scheduler and verify cleanup
        scheduler.stop()
        
        # Verify scheduler state and event handling
        assert not event.is_set()  # Event should not be set after stop
        assert scheduler.is_running is False  # Scheduler should be stopped
    
    def test_multiple_stop_calls_safe(self) -> None:
        """Test that multiple stop calls don't raise errors."""
        scheduler = GameScheduler()
        event = Event()
        
        def dummy_handler() -> None:
            event.set()
            
        scheduler.start(tick_handler=dummy_handler)
        scheduler.stop()
        scheduler.stop()  # Should not raise
        assert scheduler.is_running is False
    
    def test_tick_handler_error_handling(self) -> None:
        """Test that errors in tick handler don't crash the scheduler."""
        error_count = 0
        event = Event()
        
        def failing_handler() -> NoReturn:
            nonlocal error_count
            error_count += 1
            if error_count >= 2:
                event.set()
            raise ValueError("Test error")
        
        scheduler = GameScheduler(tick_interval=0.1)
        scheduler.start(tick_handler=failing_handler)
        
        # Wait for at least 2 errors or timeout
        event.wait(timeout=1.0)
        scheduler.stop()
        
        # Scheduler should have continued running despite errors
        assert error_count >= 2, "Handler did not run multiple times"
        assert not scheduler.is_running, "Scheduler did not stop cleanly"
    
    def test_scheduler_as_context_manager(self) -> None:
        """
        Test using scheduler with a context manager pattern.
        
        Note: This test suggests a potential enhancement to make GameScheduler
        a context manager. Consider adding this feature if it proves useful.
        """
        tick_count = 0
        event = Event()
        
        def tick_handler() -> None:
            nonlocal tick_count
            tick_count += 1
            if tick_count >= 3:
                event.set()
        
        scheduler = GameScheduler(tick_interval=0.1)
        scheduler.start(tick_handler=tick_handler)
        
        try:
            event.wait(timeout=1.0)
        finally:
            scheduler.stop()
        
        assert tick_count >= 3, "Not enough ticks occurred"
        assert not scheduler.is_running, "Scheduler did not stop cleanly" 
"""
Tests for the game scheduler module.

These tests verify:
1. Start/stop functionality
2. Error handling
3. Thread management
"""

import pytest
from threading import Event
from typing import Any, NoReturn
from src.backend.models.common.time.game_scheduler import GameScheduler

class TestGameScheduler:
    """Test suite for GameScheduler class."""
    
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
    
    def test_stop_scheduler(self) -> None:
        """Test that stopping the scheduler properly cleans up resources."""
        scheduler = GameScheduler()
        event = Event()
        tick_count = 0
        
        def dummy_handler() -> None:
            nonlocal tick_count
            tick_count += 1
            event.set()
            
        # Start the scheduler and verify it's running
        scheduler.start(tick_handler=dummy_handler)
        assert scheduler.is_running
        
        # Wait for at least one tick
        assert event.wait(timeout=2.0), "Scheduler did not tick within timeout"
        initial_tick_count = tick_count
        
        # Stop the scheduler and verify it stopped
        scheduler.stop()
        assert not scheduler.is_running
        
        # Wait a bit and verify tick count hasn't changed
        Event().wait(0.5)  # type: ignore[unreachable]
        assert tick_count == initial_tick_count, "Tick count changed after stop"
    
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
        
        scheduler = GameScheduler(tick_delay=0.1)
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
        
        scheduler = GameScheduler(tick_delay=0.1)
        scheduler.start(tick_handler=tick_handler)
        
        try:
            event.wait(timeout=1.0)
        finally:
            scheduler.stop()
        
        assert tick_count >= 3, "Not enough ticks occurred"
        assert not scheduler.is_running, "Scheduler did not stop cleanly" 
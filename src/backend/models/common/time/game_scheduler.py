"""
Game scheduler module.

This module provides scheduling functionality for game state updates.
It ensures that game ticks occur at regular intervals.
"""

from typing import Optional, Callable, get_type_hints
from threading import Thread, Event
import time
import inspect
from dataclasses import dataclass, field

@dataclass
class GameScheduler:
    """
    Scheduler for game state updates.
    
    This class is responsible for:
    - Triggering game ticks at regular intervals
    - Managing the scheduler thread
    
    The scheduler runs in a separate thread to avoid blocking the main game loop.
    """
    
    tick_interval: float = field(default=1.0)  # Default 1 second between ticks
    _tick_handler: Optional[Callable[[], None]] = field(default=None, init=False)
    _scheduler_thread: Optional[Thread] = field(default=None, init=False)
    _stop_event: Event = field(default_factory=Event, init=False)
    
    def start(self, tick_handler: Callable[[], None]) -> None:
        """
        Start the scheduler with the given tick handler.
        
        Args:
            tick_handler: Function to call on each tick. Must be a callable
                        taking no arguments and returning None.
                        
        Raises:
            RuntimeError: If scheduler is already running
            TypeError: If tick_handler has invalid signature
        """
        if self._scheduler_thread is not None and self._scheduler_thread.is_alive():
            raise RuntimeError("Scheduler is already running")
            
        # Validate handler signature
        sig = inspect.signature(tick_handler)
        if len(sig.parameters) != 0:
            raise TypeError(
                f"Tick handler must take no arguments. Got: {sig}"
            )
        
        self._tick_handler = tick_handler
        self._stop_event.clear()
        
        self._scheduler_thread = Thread(
            target=self._scheduler_loop,
            name="GameScheduler",
            daemon=True  # Thread will be terminated when main thread exits
        )
        self._scheduler_thread.start()
    
    def stop(self) -> None:
        """Stop the scheduler."""
        if self._scheduler_thread is None:
            return
            
        self._stop_event.set()
        if self._scheduler_thread.is_alive():
            self._scheduler_thread.join()
        self._scheduler_thread = None
        self._tick_handler = None
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop that triggers ticks at regular intervals."""
        if self._tick_handler is None:
            raise RuntimeError("No tick handler set")
            
        last_tick = time.time()
        
        while not self._stop_event.is_set():
            current_time = time.time()
            time_since_last_tick = current_time - last_tick
            
            if time_since_last_tick >= self.tick_interval:
                try:
                    self._tick_handler()
                except Exception as e:
                    # Log the error but don't crash the scheduler
                    print(f"Error in tick handler: {e}")  # TODO: Replace with proper logging
                last_tick = current_time
            
            # Sleep for a short time to avoid busy waiting
            # Use a small sleep interval to maintain timing accuracy
            time.sleep(0.01)  # 10ms sleep
    
    @property
    def is_running(self) -> bool:
        """Check if the scheduler is currently running."""
        return (
            self._scheduler_thread is not None and 
            self._scheduler_thread.is_alive()
        ) 
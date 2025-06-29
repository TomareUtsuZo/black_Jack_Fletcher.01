"""
Game scheduler module.

This module provides scheduling functionality for game state updates.
It runs game ticks in a separate thread.
"""

from typing import Optional, Callable
from threading import Thread, Event
import inspect
from dataclasses import dataclass, field

@dataclass
class GameScheduler:
    """
    Scheduler for game state updates.
    
    This class is responsible for:
    - Running game ticks in a separate thread
    - Managing the scheduler thread
    
    The scheduler runs in a separate thread to avoid blocking the main game loop.
    """
    
    tick_delay: float = field(default=0.01)  # Small delay between ticks to prevent CPU overload
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
        """Main scheduler loop that triggers ticks."""
        if self._tick_handler is None:
            return
            
        while not self._stop_event.is_set():
            try:
                self._tick_handler()
            except Exception:
                pass
            Event().wait(self.tick_delay)
    
    @property
    def is_running(self) -> bool:
        """Check if the scheduler is currently running."""
        return (
            self._scheduler_thread is not None and 
            self._scheduler_thread.is_alive()
        ) 
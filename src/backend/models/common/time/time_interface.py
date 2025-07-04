from abc import ABC, abstractmethod

class TimeInterface(ABC):
    @abstractmethod
    def get_time_state(self):
        '''Abstract method to get the time state. Must be implemented by subclasses.'''
        pass  # No additional logic; just the interface 
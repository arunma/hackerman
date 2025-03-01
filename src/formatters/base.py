from abc import ABC, abstractmethod
from typing import Dict, Any

class Formatter(ABC):
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        """Format the data into a string representation"""
        pass

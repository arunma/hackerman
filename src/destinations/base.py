from abc import ABC, abstractmethod
from typing import Dict, Any

class Destination(ABC):
    @abstractmethod
    def send(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Send content to the destination"""
        pass

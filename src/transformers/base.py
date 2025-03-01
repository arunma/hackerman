from abc import ABC, abstractmethod
from typing import Dict, Any

class Transformer(ABC):
    @abstractmethod
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single piece of data"""
        pass

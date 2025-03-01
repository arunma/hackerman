from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DataSource(ABC):
    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data from the source"""
        pass

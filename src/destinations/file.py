import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from .base import Destination

class FileDestination(Destination):
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def send(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Write content to a file in the output directory"""
        try:
            metadata = metadata or {}
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"digest_{timestamp}.html"
            filepath = self.output_dir / filename
            
            # Write content to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Wrote digest to: {filepath}")
            return True
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            return False

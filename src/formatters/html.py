import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from .base import Formatter

class HTMLFormatter(Formatter):
    def __init__(self, template_path: str = None):
        self.template_path = template_path or "templates/html/digest.html"
        template_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
    def format(self, content: str, metadata: dict) -> str:
        """Format content and metadata into HTML"""
        template = self.env.get_template(self.template_path)
        
        # Add current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # If this is a list of articles, use it directly
        if isinstance(metadata, list):
            articles = metadata
        else:
            # If it's a single article, wrap it in a list
            articles = [metadata]
            
        return template.render(
            articles=articles,
            timestamp=timestamp
        )

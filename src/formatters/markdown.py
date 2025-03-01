from typing import Dict, Any
import os
from jinja2 import Environment, FileSystemLoader
from .base import Formatter

class MarkdownFormatter(Formatter):
    def __init__(self, template_path: str = None):
        template_dir = os.path.dirname(template_path) if template_path else os.path.join(os.getcwd(), 'templates', 'markdown')
        template_file = os.path.basename(template_path) if template_path else 'article.md'
        
        env = Environment(loader=FileSystemLoader(template_dir))
        self.template = env.get_template(template_file)

    def format(self, data: Dict[str, Any]) -> str:
        """Format the data into markdown"""
        return self.template.render(**data)

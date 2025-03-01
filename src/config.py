import os
from typing import Dict, Any, Type
import yaml
from dotenv import load_dotenv

from sources.base import DataSource
from sources.hackernews import HackerNewsSource
from transformers.base import Transformer
from transformers.content_fetcher import ContentFetcher
from transformers.summarizer import ContentSummarizer
from transformers.content_tagger import ContentTagger
from transformers.comment_summarizer import CommentSummarizer
from formatters.base import Formatter
from formatters.markdown import MarkdownFormatter
from formatters.html import HTMLFormatter
from destinations.base import Destination
from destinations.email import EmailDestination
from destinations.telegram import TelegramDestination
from destinations.file import FileDestination

class ConfigurationError(Exception):
    pass

class Config:
    # Registry of available components
    SOURCES = {
        'hackernews': HackerNewsSource
    }
    
    TRANSFORMERS = {
        'content_fetcher': ContentFetcher,
        'summarizer': ContentSummarizer,
        'content_tagger': ContentTagger,
        'comment_summarizer': CommentSummarizer
    }
    
    FORMATTERS = {
        'markdown': MarkdownFormatter,
        'html': HTMLFormatter
    }
    
    DESTINATIONS = {
        'email': EmailDestination,
        'telegram': TelegramDestination,
        'file': FileDestination
    }
    
    @staticmethod
    def load_yaml(path: str) -> Dict[str, Any]:
        """Load and parse YAML configuration file"""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    @classmethod
    def create_component(cls, component_type: Dict[Type, dict], config: Dict[str, Any]) -> Any:
        """Create a component from configuration"""
        if not config or 'type' not in config:
            raise ConfigurationError(f"Invalid component configuration: {config}")
        
        component_class = component_type.get(config['type'])
        if not component_class:
            raise ConfigurationError(f"Unknown component type: {config['type']}")
        
        # Get constructor arguments from config
        kwargs = config.get('args', {})
        
        # Create instance
        try:
            return component_class(**kwargs)
        except Exception as e:
            raise ConfigurationError(f"Error creating {config['type']}: {str(e)}")
    
    @classmethod
    def from_yaml(cls, path: str) -> tuple[DataSource, list[Transformer], Formatter, Destination]:
        """Create pipeline components from YAML configuration"""
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        config = cls.load_yaml(path)
        
        # Create source
        source = cls.create_component(cls.SOURCES, config.get('source'))
        
        # Create transformers
        transformers = []
        for transformer_config in config.get('transformers', []):
            transformer = cls.create_component(cls.TRANSFORMERS, transformer_config)
            transformers.append(transformer)
        
        # Create formatter
        formatter = cls.create_component(cls.FORMATTERS, config.get('formatter'))
        
        # Create destination
        destination = cls.create_component(cls.DESTINATIONS, config.get('destination'))
        
        return source, transformers, formatter, destination

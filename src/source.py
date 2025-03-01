from abc import ABC, abstractmethod
from typing import List, Dict, Any
from hackernews import HackerNews

class DataSource(ABC):
    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data from the source"""
        pass

class HackerNewsSource(DataSource):
    def __init__(self):
        self.hn = HackerNews()

    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch top stories from Hacker News"""
        top_stories = self.hn.top_stories()[:10]  # Limiting to top 10 for demonstration
        stories = []
        
        for story in top_stories:
            if story and hasattr(story, 'url'):
                stories.append({
                    'title': story.title,
                    'url': story.url,
                    'id': story.item_id,
                    'created_at': story.time,
                    'score': story.score,
                    'by': story.by
                })
        
        return stories

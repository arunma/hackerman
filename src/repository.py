from datetime import datetime
from typing import List, Dict
from elasticsearch_dsl import Document, Date, Text, Keyword, Float, Nested

class Article(Document):
    title = Text(fields={'keyword': Keyword()})
    content = Text()
    url = Keyword()
    links = Keyword(multi=True)
    created_at = Date()
    indexed_at = Date()
    summary = Text()
    comment_summaries = Text(multi=True)
    tags = Nested(
        properties={
            'name': Keyword(),
            'score': Float()
        }
    )
    
    class Index:
        name = 'hackerman'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
    
    def save(self, **kwargs):
        if not self.indexed_at:
            self.indexed_at = datetime.now()
        return super().save(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        return cls(
            title=data.get('title'),
            content=data.get('content'),
            url=data.get('url'),
            created_at=data.get('created_at'),
            links=data.get('links', []),
            indexed_at=datetime.now(),
            summary=data.get('summary'),
            comment_summaries=data.get('comment_summaries', []),
            tags=data.get('tags', [])
        )

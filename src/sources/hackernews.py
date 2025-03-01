from typing import List, Dict, Any
import traceback
from datetime import datetime
from hn_sdk.client.v0.client import get_item_by_id, get_top_stories, get_best_stories
from .base import DataSource

class HackerNewsSource(DataSource):
    def __init__(self):
        pass

    def _get_comments(self, story_id: int) -> List[str]:
        """Fetch and extract comments for a story"""
        comments = []
        try:
            story = get_item_by_id(story_id)
            if story and 'kids' in story:
                for kid_id in story['kids'][:10]:  # Limit to top 10 comments
                    try:
                        comment = get_item_by_id(kid_id)
                        if comment and 'text' in comment:
                            comments.append(comment['text'])
                    except Exception as e:
                        print(f"Error fetching comment {kid_id}: {str(e)}")
                        print("Traceback:")
                        traceback.print_exc()
        except Exception as e:
            print(f"Error processing comments for story {story_id}: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
        return comments

    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch top stories from Hacker News"""
        stories = []
        try:
            # Get top story IDs
            top_story_ids = get_best_stories()[:25]
            
            # Fetch each story's details
            for story_id in top_story_ids:
                try:
                    print("Fetching story", story_id)
                    story = get_item_by_id(story_id)
                    if story and story.get('url'):  # Only process stories with URLs
                        # Get comments
                        #comments = self._get_comments(story_id)
                        comments = []
                        
                        # Convert Unix timestamp to datetime
                        created_at = datetime.fromtimestamp(story['time']) if story.get('time') else None
                        
                        stories.append({
                            'title': story.get('title', ''),
                            'url': story['url'],
                            'id': story_id,
                            'created_at': created_at,
                            'score': story.get('score', 0),
                            'by': story.get('by', ''),
                            'comments': comments
                        })
                except Exception as e:
                    print(f"Error processing story {story_id}: {str(e)}")
                    print("Traceback:")
                    traceback.print_exc()
        except Exception as e:
            print(f"Error fetching top stories: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
        
        return stories

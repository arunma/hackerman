from typing import Dict, Any
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage
from .base import Transformer

class ContentTagger(Transformer):
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
        )
        # Load tags from environment
        tags_str = os.getenv('AVAILABLE_TAGS', '')
        self.available_tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        self.score_threshold = float(os.getenv('TAG_SCORE_THRESHOLD', '0.6'))

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tag content with relevant technology categories and importance scores"""
        try:
            if 'content' not in data or not data['content']:
                data['tags'] = []
                return data

            # Combine title and content for better context
            analysis_text = f"Title: {data['title']}\n\nContent: {data['content'][:2000]}"

            messages = [
                HumanMessage(
                    content=f"""Analyze the following text and assign relevant tags from the provided list. 
                    For each assigned tag, provide a relevance score between 0.0 and 1.0, where 1.0 means highly relevant.
                    Only include tags with a score >= {self.score_threshold}. Return the result as a JSON array of objects with 'name' and 'score' fields.
                    
                    Available tags: {', '.join(self.available_tags)}
                    
                    Text to analyze:
                    {analysis_text}
                    
                    Return format example:
                    [
                        {{"name": "tag1", "score": 0.9}},
                        {{"name": "tag2", "score": 0.7}}
                    ]"""
                )
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                # Extract JSON from response
                json_str = response.content.strip()
                if json_str.startswith('```json'):
                    json_str = json_str[7:-3]  # Remove ```json and ``` markers
                tags = json.loads(json_str)
                
                # Validate tags
                validated_tags = []
                for tag in tags:
                    if isinstance(tag, dict) and 'name' in tag and 'score' in tag:
                        if tag['name'] in self.available_tags and self.score_threshold <= float(tag['score']) <= 1.0:
                            validated_tags.append({
                                'name': tag['name'],
                                'score': float(tag['score'])
                            })
                
                data['tags'] = validated_tags
            except json.JSONDecodeError:
                print(f"Error parsing tags JSON for article: {data.get('title', 'Unknown')}")
                data['tags'] = []
            
            return data
        except Exception as e:
            print(f"Error generating tags: {str(e)}")
            data['tags'] = []
            return data

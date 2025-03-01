from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage

class Transformer(ABC):
    @abstractmethod
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single piece of data"""
        pass

class ContentFetcher(Transformer):
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch content from the URL"""
        try:
            response = requests.get(data['url'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate content to avoid token limits
            content = content[:4000]
            
            data['content'] = content
            return data
        except Exception as e:
            data['content'] = f"Error fetching content: {str(e)}"
            return data

class OpenAISummarizer(Transformer):
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
        )

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize content using OpenAI"""
        try:
            if 'content' not in data:
                data['summary'] = "No content available to summarize"
                return data

            messages = [
                HumanMessage(
                    content=f"Please provide a concise summary of the following text in 2-3 sentences:\n\n{data['content']}"
                )
            ]
            
            response = self.llm.invoke(messages)
            data['summary'] = response.content
            return data
        except Exception as e:
            data['summary'] = f"Error generating summary: {str(e)}"
            return data

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
            analysis_text = f"Title: {data['title']}\n\nContent: {data['content'][:2000]}"  # Limit content length

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

class TransformationPipeline:
    def __init__(self, transformers: List[Transformer]):
        self.transformers = transformers

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all transformations in sequence"""
        result = data
        for transformer in self.transformers:
            result = transformer.transform(result)
        return result

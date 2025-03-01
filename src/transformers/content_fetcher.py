from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Transformer

class ContentFetcher(Transformer):
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch content and extract links from the URL"""
        try:
            response = requests.get(data['url'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all links
            links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(data['url'], href)
                    links.append(absolute_url)
            
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
            data['links'] = list(set(links))  # Remove duplicates
            return data
        except Exception as e:
            data['content'] = f"Error fetching content: {str(e)}"
            data['links'] = []
            return data

import os
from typing import Dict, Any
import requests
from .base import Destination

class TelegramDestination(Destination):
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Send content via Telegram"""
        try:
            # For HTML content, use HTML parse mode
            parse_mode = 'HTML' if '<html>' in content else 'Markdown'
            
            # If content is HTML, convert to Telegram-compatible HTML
            if parse_mode == 'HTML':
                # Strip html/head/body tags and keep content
                content = content.split('<body>')[1].split('</body>')[0]
            
            # Telegram has message length limits
            if len(content) > 4096:
                content = content[:4093] + "..."
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    'chat_id': self.chat_id,
                    'text': content,
                    'parse_mode': parse_mode
                }
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending telegram message: {str(e)}")
            return False

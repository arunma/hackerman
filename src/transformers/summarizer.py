from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage
from .base import Transformer

class ContentSummarizer(Transformer):
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

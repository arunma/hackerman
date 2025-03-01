from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage
from .base import Transformer

class CommentSummarizer(Transformer):
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
        )

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize comments from the article"""
        try:
            if not data.get('comments'):
                data['comment_summaries'] = []
                return data

            summaries = []
            for comment in data['comments']:
                if not comment:
                    continue

                messages = [
                    HumanMessage(
                        content=f"Please provide a brief 1-2 sentence summary of this Hacker News comment:\n\n{comment}"
                    )
                ]
                
                response = self.llm.invoke(messages)
                summaries.append(response.content.strip())
            
            data['comment_summaries'] = summaries
            return data
        except Exception as e:
            print(f"Error summarizing comments: {str(e)}")
            data['comment_summaries'] = []
            return data

"""
OpenAI Chat Completions provider for NLP transformations.
"""

import logging
from typing import Tuple, List
import openai
from app.services.nlp_transform.base import BaseNLPProvider
from app.config import config

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseNLPProvider):
    """OpenAI Chat Completions provider."""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=config.openai.api_key)
        self.model = config.openai.model
    
    async def summarize(self, text: str, template: str) -> Tuple[str, List[str]]:
        """
        Generate summary and hashtags using OpenAI Chat Completions.
        
        Args:
            text: Input text to summarize
            template: Prompt template for summarization
            
        Returns:
            Tuple of (summary_text, hashtags_list)
        """
        try:
            # Format the prompt
            prompt = template.format(text=text)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты помощник для создания кратких новостных сводок на русском языке."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Extract hashtags from summary
            hashtags = self._extract_hashtags(summary)
            
            logger.info(f"Generated summary: {summary[:100]}...")
            logger.info(f"Extracted hashtags: {hashtags}")
            
            return summary, hashtags
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from text.
        
        Args:
            text: Text to extract hashtags from
            
        Returns:
            List of hashtags
        """
        hashtags = []
        
        # Simple hashtag extraction - look for words that could be hashtags
        words = text.lower().split()
        
        # Common news-related keywords in Russian and English
        news_keywords = [
            'новости', 'новость', 'события', 'событие', 'происшествие', 'происшествия',
            'политика', 'экономика', 'спорт', 'технологии', 'технология', 'наука',
            'здоровье', 'медицина', 'образование', 'культура', 'искусство',
            'news', 'event', 'events', 'politics', 'economy', 'sport', 'technology',
            'science', 'health', 'medicine', 'education', 'culture', 'art'
        ]
        
        # Extract relevant keywords
        for word in words:
            # Clean word (remove punctuation)
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 3 and clean_word in news_keywords:
                hashtags.append(f"#{clean_word}")
        
        # Add some generic hashtags if none found
        if not hashtags:
            hashtags = ["#новости", "#события"]
        
        # Limit to 5 hashtags
        return hashtags[:5]

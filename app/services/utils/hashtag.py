"""
Hashtag extraction utilities.
"""

import re
from typing import List


def extract_hashtags(text: str) -> List[str]:
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

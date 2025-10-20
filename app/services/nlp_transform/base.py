"""
Base NLP provider interface.
"""

from abc import ABC, abstractmethod
from typing import Tuple, List


class BaseNLPProvider(ABC):
    """Abstract base class for NLP providers."""
    
    @abstractmethod
    async def summarize(self, text: str, template: str) -> Tuple[str, List[str]]:
        """
        Generate summary and hashtags from text.
        
        Args:
            text: Input text to summarize
            template: Prompt template for summarization
            
        Returns:
            Tuple of (summary_text, hashtags_list)
        """
        pass

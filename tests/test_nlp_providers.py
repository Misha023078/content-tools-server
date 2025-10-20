"""
Tests for NLP providers.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.nlp_transform.providers.openai_provider import OpenAIProvider


@pytest.mark.asyncio
async def test_openai_provider_summarize():
    """Test OpenAI provider summarize method."""
    # Mock OpenAI response
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock()]
    mock_response.choices[0].message.content = "Краткая новость о технологиях"
    
    with patch('app.services.nlp_transform.providers.openai_provider.openai.AsyncOpenAI') as mock_openai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        provider = OpenAIProvider()
        summary, hashtags = await provider.summarize(
            "Длинный текст о технологиях и науке",
            "Сожми текст: {text}"
        )
        
        assert summary == "Краткая новость о технологиях"
        assert isinstance(hashtags, list)
        assert all(hashtag.startswith('#') for hashtag in hashtags)


def test_openai_provider_extract_hashtags():
    """Test hashtag extraction from OpenAI provider."""
    provider = OpenAIProvider()
    
    # Test with Russian text
    text = "Новости о технологиях и науке"
    hashtags = provider._extract_hashtags(text)
    
    assert len(hashtags) > 0
    assert all(hashtag.startswith('#') for hashtag in hashtags)
    
    # Test with English text
    text = "Technology news and science updates"
    hashtags = provider._extract_hashtags(text)
    
    assert len(hashtags) > 0
    assert all(hashtag.startswith('#') for hashtag in hashtags)
    
    # Test with empty text
    text = ""
    hashtags = provider._extract_hashtags(text)
    
    # Should return default hashtags
    assert len(hashtags) > 0
    assert "#новости" in hashtags

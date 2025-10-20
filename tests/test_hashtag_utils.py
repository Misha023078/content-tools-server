"""
Tests for hashtag utilities.
"""

import pytest
from app.services.utils.hashtag import extract_hashtags


def test_extract_hashtags_basic():
    """Test basic hashtag extraction."""
    text = "Новости о технологиях и науке"
    hashtags = extract_hashtags(text)
    
    assert len(hashtags) > 0
    assert all(hashtag.startswith('#') for hashtag in hashtags)


def test_extract_hashtags_empty():
    """Test hashtag extraction from empty text."""
    text = ""
    hashtags = extract_hashtags(text)
    
    # Should return default hashtags
    assert len(hashtags) > 0
    assert "#новости" in hashtags


def test_extract_hashtags_english():
    """Test hashtag extraction from English text."""
    text = "Technology news and science updates"
    hashtags = extract_hashtags(text)
    
    assert len(hashtags) > 0
    assert all(hashtag.startswith('#') for hashtag in hashtags)


def test_extract_hashtags_limit():
    """Test hashtag extraction limit."""
    text = "новости технологии наука политика экономика спорт культура искусство"
    hashtags = extract_hashtags(text)
    
    # Should be limited to 5 hashtags
    assert len(hashtags) <= 5

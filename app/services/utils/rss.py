"""
RSS fetching and parsing utilities.
"""

import requests
import feedparser
import hashlib
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from app.config import config

logger = logging.getLogger(__name__)


def fetch_rss_feed(feed_url: str) -> Optional[feedparser.FeedParserDict]:
    """
    Fetch and parse RSS feed from URL.
    
    Args:
        feed_url: URL of the RSS feed
        
    Returns:
        Parsed feed object or None if failed
    """
    try:
        headers = {
            'User-Agent': config.user_agent
        }
        
        response = requests.get(
            feed_url,
            headers=headers,
            timeout=config.fetch_timeout
        )
        response.raise_for_status()
        
        # Parse the feed
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            logger.warning(f"Feed parsing warnings for {feed_url}: {feed.bozo_exception}")
        
        return feed
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch RSS feed {feed_url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing RSS feed {feed_url}: {str(e)}")
        return None


def extract_guid(entry: feedparser.FeedParserDict) -> str:
    """
    Extract or generate GUID for RSS entry.
    
    Priority: entry.id -> entry.link -> (entry.title + entry.published or empty)
    
    Args:
        entry: RSS entry object
        
    Returns:
        GUID string
    """
    # Try entry.id first
    if hasattr(entry, 'id') and entry.id:
        return entry.id
    
    # Try entry.link
    if hasattr(entry, 'link') and entry.link:
        return entry.link
    
    # Generate from title + published
    title = getattr(entry, 'title', '') or ''
    published = getattr(entry, 'published', '') or ''
    
    # Create hash from title + published
    content = f"{title}{published}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def extract_original_text(entry: feedparser.FeedParserDict) -> str:
    """
    Extract original text from RSS entry.
    
    Priority: content[0].value (HTML stripped) -> summary -> title
    
    Args:
        entry: RSS entry object
        
    Returns:
        Extracted text
    """
    # Try content[0].value (HTML stripped)
    if hasattr(entry, 'content') and entry.content:
        try:
            content_html = entry.content[0].value
            soup = BeautifulSoup(content_html, 'html.parser')
            return soup.get_text(strip=True)
        except (IndexError, AttributeError):
            pass
    
    # Try summary
    if hasattr(entry, 'summary') and entry.summary:
        soup = BeautifulSoup(entry.summary, 'html.parser')
        return soup.get_text(strip=True)
    
    # Fallback to title
    if hasattr(entry, 'title') and entry.title:
        return entry.title
    
    return ""


def extract_media_url(entry: feedparser.FeedParserDict) -> Optional[str]:
    """
    Extract media URL from RSS entry content.
    
    Args:
        entry: RSS entry object
        
    Returns:
        Media URL or None
    """
    # Check for media in content
    if hasattr(entry, 'content') and entry.content:
        try:
            content_html = entry.content[0].value
            soup = BeautifulSoup(content_html, 'html.parser')
            
            # Look for images first
            img_tag = soup.find('img')
            if img_tag and img_tag.get('src'):
                return img_tag['src']
            
            # Look for videos
            video_tag = soup.find('video')
            if video_tag and video_tag.get('src'):
                return video_tag['src']
                
        except (IndexError, AttributeError):
            pass
    
    # Check for media in summary
    if hasattr(entry, 'summary') and entry.summary:
        try:
            soup = BeautifulSoup(entry.summary, 'html.parser')
            
            # Look for images
            img_tag = soup.find('img')
            if img_tag and img_tag.get('src'):
                return img_tag['src']
                
        except AttributeError:
            pass
    
    return None


def build_rsshub_url(username: str) -> str:
    """
    Build RSSHub URL for Telegram channel.
    
    Args:
        username: Telegram username (without @)
        
    Returns:
        RSSHub URL
    """
    return f"{config.rsshub_base}/telegram/channel/{username}?showContent"

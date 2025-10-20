"""
RSS ingestion service.
Fetches content from RSS sources and stores new posts.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.models import Source, Post
from app.services.utils.rss import (
    fetch_rss_feed, 
    extract_guid, 
    extract_original_text, 
    extract_media_url,
    build_rsshub_url
)
from app.config import config

logger = logging.getLogger(__name__)


class RSSIngestService:
    """Service for ingesting content from RSS sources."""
    
    def __init__(self):
        self.db = SessionLocal()
    
    async def ingest_all_sources(self) -> Dict[str, Any]:
        """
        Ingest content from all enabled sources.
        
        Returns:
            Dictionary with processing results
        """
        try:
            # Get all enabled sources
            sources = self.db.query(Source).filter(Source.enabled == True).all()
            
            if not sources:
                logger.info("No enabled sources found")
                return {"processed": 0, "new_posts": 0, "errors": 0}
            
            processed = 0
            new_posts = 0
            errors = 0
            
            for source in sources:
                try:
                    result = await self.ingest_source(source)
                    processed += 1
                    new_posts += result.get('new_posts', 0)
                except Exception as e:
                    logger.error(f"Failed to ingest source {source.name}: {str(e)}")
                    errors += 1
            
            logger.info(f"Ingest completed: {processed} sources processed, {new_posts} new posts, {errors} errors")
            return {
                "processed": processed,
                "new_posts": new_posts,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"RSS ingest failed: {str(e)}")
            raise
        finally:
            self.db.close()
    
    async def ingest_source(self, source: Source) -> Dict[str, Any]:
        """
        Ingest content from a single source.
        
        Args:
            source: Source model instance
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Build RSSHub URL
            feed_url = build_rsshub_url(source.username)
            logger.info(f"Fetching feed for source {source.name}: {feed_url}")
            
            # Fetch and parse feed
            feed = fetch_rss_feed(feed_url)
            if not feed or not feed.entries:
                logger.warning(f"No entries found for source {source.name}")
                return {"new_posts": 0}
            
            # Get the top (most recent) entry
            entry = feed.entries[0]
            
            # Extract GUID
            guid = extract_guid(entry)
            logger.info(f"Extracted GUID for source {source.name}: {guid}")
            
            # Check if this is the same as last_guid (no new content)
            if source.last_guid == guid:
                logger.info(f"No new content for source {source.name}")
                return {"new_posts": 0}
            
            # Extract content
            original_text = extract_original_text(entry)
            media_url = extract_media_url(entry)
            
            if not original_text:
                logger.warning(f"No text content found for source {source.name}")
                return {"new_posts": 0}
            
            # Create new post
            post = Post(
                source_id=source.id,
                guid=guid,
                original_text=original_text,
                media_url=media_url,
                status="new"
            )
            
            try:
                self.db.add(post)
                self.db.commit()
                logger.info(f"Created new post for source {source.name}: {guid}")
                return {"new_posts": 1}
                
            except IntegrityError:
                # Post with this GUID already exists for this source
                self.db.rollback()
                logger.info(f"Post already exists for source {source.name}: {guid}")
                return {"new_posts": 0}
                
        except Exception as e:
            logger.error(f"Failed to ingest source {source.name}: {str(e)}")
            self.db.rollback()
            raise

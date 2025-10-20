"""
NLP transformation service.
Processes posts to generate summaries and hashtags.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Post
from app.services.nlp_transform.providers.openai_provider import OpenAIProvider
from app.config import config

logger = logging.getLogger(__name__)


class NLPTransformService:
    """Service for transforming posts with NLP."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.provider = self._get_provider()
    
    def _get_provider(self):
        """Get the configured NLP provider."""
        if config.nlp_provider == "openai":
            return OpenAIProvider()
        else:
            raise ValueError(f"Unsupported NLP provider: {config.nlp_provider}")
    
    async def transform_posts(self) -> Dict[str, Any]:
        """
        Transform all posts with status="new".
        
        Returns:
            Dictionary with processing results
        """
        try:
            # Get all posts with status="new"
            posts = self.db.query(Post).filter(Post.status == "new").all()
            
            if not posts:
                logger.info("No new posts to transform")
                return {"transformed": 0, "errors": 0}
            
            transformed = 0
            errors = 0
            
            for post in posts:
                try:
                    await self.transform_post(post)
                    transformed += 1
                except Exception as e:
                    logger.error(f"Failed to transform post {post.id}: {str(e)}")
                    # Mark post as error
                    post.status = "error"
                    self.db.commit()
                    errors += 1
            
            logger.info(f"Transform completed: {transformed} posts transformed, {errors} errors")
            return {
                "transformed": transformed,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"NLP transform failed: {str(e)}")
            raise
        finally:
            self.db.close()
    
    async def transform_post(self, post: Post):
        """
        Transform a single post.
        
        Args:
            post: Post model instance
        """
        try:
            if not post.original_text:
                logger.warning(f"Post {post.id} has no original text")
                post.status = "error"
                self.db.commit()
                return
            
            # Generate summary and hashtags
            summary, hashtags = await self.provider.summarize(
                post.original_text,
                config.summary_prompt_template
            )
            
            # Update post
            post.summary_text = summary
            post.hashtags = hashtags
            post.status = "ready"
            
            self.db.commit()
            logger.info(f"Transformed post {post.id}: {summary[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to transform post {post.id}: {str(e)}")
            post.status = "error"
            self.db.commit()
            raise

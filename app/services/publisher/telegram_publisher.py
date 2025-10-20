"""
Telegram publisher service.
Publishes posts to Telegram channels.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.db import SessionLocal
from app.models import Post, Source, OurChannel
from app.config import config
import telebot

logger = logging.getLogger(__name__)


class TelegramPublisherService:
    """Service for publishing posts to Telegram channels."""
    
    def __init__(self):
        self.db = SessionLocal()
        if not config.telegram.bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Configure it to enable publishing.")
        self.bot = telebot.TeleBot(config.telegram.bot_token)
    
    async def publish_posts(self) -> Dict[str, Any]:
        """
        Publish all posts with status="ready".
        
        Returns:
            Dictionary with processing results
        """
        try:
            # Get all posts with status="ready" and their related data
            posts = self.db.query(Post).options(
                joinedload(Post.source).joinedload(Source.our_channel)
            ).filter(Post.status == "ready").all()
            
            if not posts:
                logger.info("No ready posts to publish")
                return {"published": 0, "errors": 0}
            
            published = 0
            errors = 0
            
            for post in posts:
                try:
                    success = await self.publish_post(post)
                    if success:
                        published += 1
                    else:
                        errors += 1
                except Exception as e:
                    logger.error(f"Failed to publish post {post.id}: {str(e)}")
                    post.status = "error"
                    self.db.commit()
                    errors += 1
            
            logger.info(f"Publish completed: {published} posts published, {errors} errors")
            return {
                "published": published,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Publish failed: {str(e)}")
            raise
        finally:
            self.db.close()
    
    async def publish_post(self, post: Post) -> bool:
        """
        Publish a single post to Telegram.
        
        Args:
            post: Post model instance
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get target channel
            our_channel = post.source.our_channel
            if not our_channel:
                logger.error(f"No channel found for post {post.id}")
                return False
            
            # Build caption
            caption = self._build_caption(post)
            
            # Determine if we have media
            if post.media_url:
                success = await self._send_media_message(
                    our_channel.tg_chat_id_or_username,
                    post.media_url,
                    caption
                )
            else:
                success = await self._send_text_message(
                    our_channel.tg_chat_id_or_username,
                    caption
                )
            
            if success:
                # Update post status and timestamp
                post.status = "sent"
                post.sent_at = datetime.utcnow()
                
                # Update source.last_guid (critical rule!)
                post.source.last_guid = post.guid
                
                self.db.commit()
                logger.info(f"Successfully published post {post.id} to {our_channel.name}")
                return True
            else:
                logger.error(f"Failed to publish post {post.id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to publish post {post.id}: {str(e)}")
            return False
    
    def _build_caption(self, post: Post) -> str:
        """
        Build caption for Telegram message.
        
        Args:
            post: Post model instance
            
        Returns:
            Caption text
        """
        # Use summary_text if available, otherwise original_text
        main_text = post.summary_text or post.original_text or ""
        
        # Add extra_text if available
        if post.extra_text:
            main_text += f"\n\n{post.extra_text}"
        
        # Add hashtags if available
        if post.hashtags:
            hashtag_text = " ".join(post.hashtags)
            main_text += f"\n\n{hashtag_text}"
        
        return main_text
    
    async def _send_media_message(self, chat_id: str, media_url: str, caption: str) -> bool:
        """
        Send media message to Telegram.
        
        Args:
            chat_id: Telegram chat ID or username
            media_url: URL of media file
            caption: Message caption
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine media type by extension
            media_type = self._get_media_type(media_url)
            
            if media_type == "photo":
                self.bot.send_photo(
                    chat_id=chat_id,
                    photo=media_url,
                    caption=caption,
                    parse_mode=config.telegram_parse_mode,
                    disable_web_page_preview=config.telegram_disable_preview
                )
            elif media_type == "video":
                self.bot.send_video(
                    chat_id=chat_id,
                    video=media_url,
                    caption=caption,
                    parse_mode=config.telegram_parse_mode,
                    disable_web_page_preview=config.telegram_disable_preview
                )
            else:
                # Send as text with link
                message = f"{caption}\n\n{media_url}"
                self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=config.telegram_parse_mode,
                    disable_web_page_preview=config.telegram_disable_preview
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send media message: {str(e)}")
            return False
    
    async def _send_text_message(self, chat_id: str, text: str) -> bool:
        """
        Send text message to Telegram.
        
        Args:
            chat_id: Telegram chat ID or username
            text: Message text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=config.telegram_parse_mode,
                disable_web_page_preview=config.telegram_disable_preview
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send text message: {str(e)}")
            return False
    
    def _get_media_type(self, url: str) -> str:
        """
        Determine media type from URL.
        
        Args:
            url: Media URL
            
        Returns:
            Media type: "photo", "video", or "unknown"
        """
        url_lower = url.lower()
        
        # Image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if any(ext in url_lower for ext in image_extensions):
            return "photo"
        
        # Video extensions
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        if any(ext in url_lower for ext in video_extensions):
            return "video"
        
        return "unknown"

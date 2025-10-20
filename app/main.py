"""
FastAPI application for content-tools-server.
Provides admin API and manual triggers for the content pipeline.
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db import get_db
from app.models import Post, Source, OurChannel
from app.services.rss_ingest import RSSIngestService
from app.services.nlp_transform.service import NLPTransformService
from app.services.publisher.telegram_publisher import TelegramPublisherService
from app.config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.logging.level))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Content Tools Server",
    description="Automated content ingestion, transformation, and publishing system",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"ok": True}


@app.post("/run/ingest")
async def run_ingest():
    """Manually trigger RSS ingestion."""
    try:
        logger.info("Starting manual RSS ingest")
        ingest_service = RSSIngestService()
        result = await ingest_service.ingest_all_sources()
        logger.info(f"RSS ingest completed: {result}")
        return {"status": "success", "message": f"Processed {result.get('processed', 0)} sources"}
    except Exception as e:
        logger.error(f"RSS ingest failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RSS ingest failed: {str(e)}")


@app.post("/run/transform")
async def run_transform():
    """Manually trigger NLP transformation."""
    try:
        logger.info("Starting manual NLP transform")
        transform_service = NLPTransformService()
        result = await transform_service.transform_posts()
        logger.info(f"NLP transform completed: {result}")
        return {"status": "success", "message": f"Transformed {result.get('transformed', 0)} posts"}
    except Exception as e:
        logger.error(f"NLP transform failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"NLP transform failed: {str(e)}")


@app.post("/run/publish")
async def run_publish():
    """Manually trigger publishing."""
    try:
        logger.info("Starting manual publish")
        publisher_service = TelegramPublisherService()
        result = await publisher_service.publish_posts()
        logger.info(f"Publish completed: {result}")
        return {"status": "success", "message": f"Published {result.get('published', 0)} posts"}
    except Exception as e:
        logger.error(f"Publish failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Publish failed: {str(e)}")


@app.get("/posts")
async def get_posts(
    status: Optional[str] = Query(None, description="Filter by status: new, ready, sent, error"),
    limit: int = Query(50, description="Number of posts to return"),
    offset: int = Query(0, description="Number of posts to skip"),
    db: Session = Depends(get_db)
):
    """Get posts with optional filtering and pagination."""
    query = db.query(Post)
    
    if status:
        query = query.filter(Post.status == status)
    
    posts = query.offset(offset).limit(limit).all()
    
    return {
        "posts": [
            {
                "id": str(post.id),
                "source_id": str(post.source_id),
                "guid": post.guid,
                "original_text": post.original_text,
                "summary_text": post.summary_text,
                "media_url": post.media_url,
                "extra_text": post.extra_text,
                "hashtags": post.hashtags,
                "status": post.status,
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "sent_at": post.sent_at.isoformat() if post.sent_at else None
            }
            for post in posts
        ],
        "total": query.count(),
        "limit": limit,
        "offset": offset
    }


@app.get("/sources")
async def get_sources(db: Session = Depends(get_db)):
    """Get all sources."""
    sources = db.query(Source).all()
    
    return {
        "sources": [
            {
                "id": str(source.id),
                "our_channel_id": str(source.our_channel_id),
                "name": source.name,
                "username": source.username,
                "description": source.description,
                "default_image_url": source.default_image_url,
                "source_type": source.source_type,
                "enabled": source.enabled,
                "last_guid": source.last_guid,
                "created_at": source.created_at.isoformat() if source.created_at else None
            }
            for source in sources
        ]
    }


@app.get("/channels")
async def get_channels(db: Session = Depends(get_db)):
    """Get all our channels."""
    channels = db.query(OurChannel).all()
    
    return {
        "channels": [
            {
                "id": str(channel.id),
                "name": channel.name,
                "tg_chat_id_or_username": channel.tg_chat_id_or_username,
                "status": channel.status,
                "created_at": channel.created_at.isoformat() if channel.created_at else None
            }
            for channel in channels
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

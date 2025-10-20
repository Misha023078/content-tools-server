"""
SQLAlchemy models for the content-tools-server application.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db import Base


class OurChannel(Base):
    """Our Telegram channels that will receive content."""
    __tablename__ = "our_channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=uuid.uuid4())
    name = Column(Text, nullable=False)
    tg_chat_id_or_username = Column(Text, nullable=False)  # "@mychannel" or numeric id
    status = Column(Text, default="active")
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow())
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow(), onupdate=datetime.utcnow())
    
    # Relationships
    sources = relationship("Source", back_populates="our_channel")


class Source(Base):
    """RSS sources to fetch content from."""
    __tablename__ = "sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=uuid.uuid4())
    our_channel_id = Column(UUID(as_uuid=True), ForeignKey("our_channels.id"), nullable=False, index=True)
    name = Column(Text, nullable=False)
    username = Column(Text, nullable=False)  # TG username without "@"
    description = Column(Text)
    default_image_url = Column(Text)
    source_type = Column(Text)  # "news" | "commerce"
    enabled = Column(Boolean, default=True)
    last_guid = Column(Text)  # last successfully published guid
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow())
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow(), onupdate=datetime.utcnow())
    
    # Relationships
    our_channel = relationship("OurChannel", back_populates="sources")
    posts = relationship("Post", back_populates="source")


class Post(Base):
    """Posts fetched from RSS sources."""
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=uuid.uuid4())
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False, index=True)
    guid = Column(Text, nullable=False, index=True)  # guid extracted from RSS entry
    original_text = Column(Text)
    summary_text = Column(Text)
    media_url = Column(Text)
    extra_text = Column(Text)
    hashtags = Column(JSONB)  # array of strings
    status = Column(Text, default="new", index=True)  # "new"|"ready"|"sent"|"error"
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow())
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow(), onupdate=datetime.utcnow())
    sent_at = Column(DateTime(timezone=True))
    
    # Relationships
    source = relationship("Source", back_populates="posts")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('source_id', 'guid', name='uq_source_guid'),
    )

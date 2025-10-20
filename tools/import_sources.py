#!/usr/bin/env python3
"""
Excel import CLI tool for sources.
Imports sources from Excel file into the database.
"""

import sys
import os
import pandas as pd
import logging
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.db import SessionLocal
from app.models import OurChannel, Source

logger = logging.getLogger(__name__)


def main():
    """Main function for CLI."""
    if len(sys.argv) != 2:
        print("Usage: python tools/import_sources.py <excel_file>")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    if not os.path.exists(excel_file):
        print(f"Error: File {excel_file} not found")
        sys.exit(1)
    
    try:
        import_sources_from_excel(excel_file)
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def import_sources_from_excel(excel_file: str):
    """
    Import sources from Excel file.
    
    Args:
        excel_file: Path to Excel file
    """
    logger.info(f"Starting import from {excel_file}")
    
    # Read Excel file
    try:
        df = pd.read_excel(excel_file)
        logger.info(f"Loaded {len(df)} rows from Excel file")
    except Exception as e:
        raise Exception(f"Failed to read Excel file: {str(e)}")
    
    # Validate required columns
    required_columns = [
        'our_channel_username',
        'source_name', 
        'source_username',
        'description',
        'default_image_url',
        'source_type',
        'enabled'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise Exception(f"Missing required columns: {missing_columns}")
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        channels_created = 0
        sources_created = 0
        
        for _, row in df.iterrows():
            # Get or create our channel
            our_channel = get_or_create_channel(
                db, 
                row['our_channel_username']
            )
            
            if our_channel.id is None:  # New channel created
                channels_created += 1
            
            # Create source
            source = Source(
                our_channel_id=our_channel.id,
                name=row['source_name'],
                username=row['source_username'].lstrip('@'),  # Remove @ if present
                description=row['description'] if pd.notna(row['description']) else None,
                default_image_url=row['default_image_url'] if pd.notna(row['default_image_url']) else None,
                source_type=row['source_type'] if pd.notna(row['source_type']) else None,
                enabled=bool(row['enabled']) if pd.notna(row['enabled']) else True
            )
            
            db.add(source)
            sources_created += 1
        
        # Commit all changes
        db.commit()
        
        print(f"Import completed successfully:")
        print(f"  - Channels created: {channels_created}")
        print(f"  - Sources created: {sources_created}")
        
        logger.info(f"Import completed: {channels_created} channels, {sources_created} sources")
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Database error: {str(e)}")
    finally:
        db.close()


def get_or_create_channel(db, username: str) -> OurChannel:
    """
    Get existing channel or create new one.
    
    Args:
        db: Database session
        username: Channel username (with or without @)
        
    Returns:
        OurChannel instance
    """
    # Clean username (remove @ if present)
    clean_username = username.lstrip('@')
    
    # Try to find existing channel
    channel = db.query(OurChannel).filter(
        OurChannel.tg_chat_id_or_username == clean_username
    ).first()
    
    if channel:
        return channel
    
    # Create new channel
    channel = OurChannel(
        name=clean_username,
        tg_chat_id_or_username=clean_username,
        status="active"
    )
    
    db.add(channel)
    db.flush()  # Get the ID without committing
    
    return channel


if __name__ == "__main__":
    main()

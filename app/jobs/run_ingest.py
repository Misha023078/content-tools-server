"""
RSS ingest job runner.
"""

import asyncio
import logging
from app.services.rss_ingest import RSSIngestService

logger = logging.getLogger(__name__)


async def main():
    """Run RSS ingest job."""
    try:
        logger.info("Starting RSS ingest job")
        service = RSSIngestService()
        result = await service.ingest_all_sources()
        logger.info(f"RSS ingest job completed: {result}")
        return result
    except Exception as e:
        logger.error(f"RSS ingest job failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

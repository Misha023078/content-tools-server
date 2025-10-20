"""
Publish job runner.
"""

import asyncio
import logging
from app.services.publisher.telegram_publisher import TelegramPublisherService

logger = logging.getLogger(__name__)


async def main():
    """Run publish job."""
    try:
        logger.info("Starting publish job")
        service = TelegramPublisherService()
        result = await service.publish_posts()
        logger.info(f"Publish job completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Publish job failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

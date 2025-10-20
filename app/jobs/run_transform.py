"""
NLP transform job runner.
"""

import asyncio
import logging
from app.services.nlp_transform.service import NLPTransformService

logger = logging.getLogger(__name__)


async def main():
    """Run NLP transform job."""
    try:
        logger.info("Starting NLP transform job")
        service = NLPTransformService()
        result = await service.transform_posts()
        logger.info(f"NLP transform job completed: {result}")
        return result
    except Exception as e:
        logger.error(f"NLP transform job failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

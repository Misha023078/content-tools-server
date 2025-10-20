"""
APScheduler configuration and job management.
"""

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import config

logger = logging.getLogger(__name__)


def run_ingest_job():
    """Run RSS ingest job."""
    try:
        logger.info("Starting scheduled RSS ingest")
        from app.jobs.run_ingest import main
        main()
    except Exception as e:
        logger.error(f"Scheduled RSS ingest failed: {str(e)}")


def run_transform_job():
    """Run NLP transform job."""
    try:
        logger.info("Starting scheduled NLP transform")
        from app.jobs.run_transform import main
        main()
    except Exception as e:
        logger.error(f"Scheduled NLP transform failed: {str(e)}")


def run_publish_job():
    """Run publish job."""
    try:
        logger.info("Starting scheduled publish")
        from app.jobs.run_publish import main
        main()
    except Exception as e:
        logger.error(f"Scheduled publish failed: {str(e)}")


def main():
    """Start the scheduler."""
    logger.info("Starting APScheduler")
    
    scheduler = BlockingScheduler()
    
    # Add cron jobs
    scheduler.add_job(
        run_ingest_job,
        CronTrigger.from_crontab(config.ingest_cron),
        id='rss_ingest',
        name='RSS Ingest Job',
        replace_existing=True
    )
    
    scheduler.add_job(
        run_transform_job,
        CronTrigger.from_crontab(config.transform_cron),
        id='nlp_transform',
        name='NLP Transform Job',
        replace_existing=True
    )
    
    scheduler.add_job(
        run_publish_job,
        CronTrigger.from_crontab(config.publish_cron),
        id='publish',
        name='Publish Job',
        replace_existing=True
    )
    
    logger.info(f"Scheduler configured with jobs:")
    logger.info(f"  - RSS Ingest: {config.ingest_cron}")
    logger.info(f"  - NLP Transform: {config.transform_cron}")
    logger.info(f"  - Publish: {config.publish_cron}")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        scheduler.shutdown()
    except Exception as e:
        logger.error(f"Scheduler failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()

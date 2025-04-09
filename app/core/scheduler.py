import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from app.services.data import DataService
from app.core.db import get_session
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)


async def setup_scheduler(loop: asyncio.AbstractEventLoop):
    """
    Sets up and initializes the background scheduler for periodic tasks.

    This function creates an `AsyncIOScheduler` that runs on the provided event loop and
    schedules the `fetch_and_merge` method of the `DataService` to be executed periodically.
    The job is configured to run at intervals defined by the `FETCH_INTERVAL_SECONDS` setting.

    The function also establishes a database session and initializes the `DataService` with
    the session and settings. If any exceptions are encountered during setup, they are raised
    after attempting to close the session.

    Args:
        loop (asyncio.AbstractEventLoop): The event loop on which the scheduler will run.

    Returns:
        AsyncIOScheduler: The initialized scheduler with the added job.

    Raises:
        Exception: If an error occurs during the setup or job scheduling process.
    """
    settings = get_settings()
    scheduler = AsyncIOScheduler(event_loop=loop)
    session_gen = get_session()
    session = await anext(session_gen)

    logger.info("🗓️ Setting up scheduler...")

    try:
        data_service = DataService(session=session, settting=settings)
        interval = settings.FETCH_INTERVAL_SECONDS

        scheduler.add_job(
            data_service.fetch_and_merge,
            "interval",
            seconds=interval,
            max_instances=1,
            next_run_time=datetime.now(),
        )

        logger.info(f"✅ Scheduled 'fetch_and_merge' to run every {interval} seconds.")
    except Exception as e:
        logger.exception("❌ Failed to set up scheduler.")
        raise e
    finally:
        await session_gen.aclose()
        logger.info("🔒 Scheduler DB session closed.")

    return scheduler

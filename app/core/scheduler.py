import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from app.services.data import DataService
from app.core.db import get_session
from app.core.config import get_settings


# async def setup_scheduler(loop: asyncio.AbstractEventLoop):
#     settings = get_settings()
#     scheduler = AsyncIOScheduler(event_loop=loop)
#     session_gen = get_session()
#     session = await anext(session_gen)

#     try:
#         data_service = DataService(session=session, settting=settings)

#         scheduler.add_job(
#             data_service.fetch_and_merge,
#             "interval",
#             seconds=get_settings().FETCH_INTERVAL_SECONDS,
#             max_instances=1,
#             next_run_time=datetime.now(),
#         )
#     except Exception as e:
#         raise e
#     finally:
#         await session_gen.aclose()

#     return scheduler


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

    try:
        data_service = DataService(session=session, settting=settings)

        scheduler.add_job(
            data_service.fetch_and_merge,
            "interval",
            seconds=get_settings().FETCH_INTERVAL_SECONDS,
            max_instances=1,
            next_run_time=datetime.now(),
        )
    except Exception as e:
        raise e
    finally:
        await session_gen.aclose()

    return scheduler

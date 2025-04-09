import json
import asyncio
import logging
import httpx
from fastapi import Depends
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from app.core.config import get_settings
from app.core.db import get_session
from app.models.models import Storage
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings

logger = logging.getLogger(__name__)


class DataService:
    """
    Service for managing data fetching, saving, and merging operations.

    This service is responsible for fetching data from external sources (e.g., API),
    saving it to the database, loading data from the database, and merging different
    datasets to produce a new one.

    Attributes:
        settings (Settings): The application settings containing configurations like retry limits.
        session (AsyncSession): The SQLAlchemy session for interacting with the database.
    """

    def __init__(self, session: AsyncSession, settting: Settings):
        self.settings = settting
        self.session = session
        logger.info("DataService initialized.")

    async def save_data(self, key: str, value: dict):
        """
        Saves the provided data as JSON in the database under the given key.

        Args:
            key (str): The key under which the data will be saved.
            value (dict): The data to be saved.

        Raises:
             SQLAlchemyError: If an error occurs during the database operation.
             Exception: For any unexpected errors during the saving process.
        """
        logger.info(f"Saving data under key: {key}")
        try:
            json_value = json.dumps(value)
            await self.session.merge(Storage(key=key, value=json_value))
            await self.session.commit()
            logger.info(f"✅ Data saved successfully under key: {key}")
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.exception(f"❌ SQLAlchemyError while saving data with key: {key}")
            raise e
        except Exception as e:
            await self.session.rollback()
            logger.exception(f"❌ Unexpected error while saving data with key: {key}")
            raise e

    async def load_data(self, key: str) -> Optional[dict]:
        """
        Loads data from the database using the provided key.

        Args:
            key (str): The key to identify the data to be loaded.

        Returns:
            Optional[dict]: The data loaded from the database or None if not found.

        Raises:
            SQLAlchemyError: If an error occurs during the database operation.
            Exception: For any unexpected errors during the loading process.
        """
        logger.info(f"Loading data for key: {key}")
        try:
            result = await self.session.execute(
                select(Storage).where(Storage.key == key)
            )
            row = result.scalar_one_or_none()
            if row:
                logger.info(f"✅ Data loaded successfully for key: {key}")
                return json.loads(row.value)
            else:
                logger.warning(f"⚠️ No data found for key: {key}")
                return None
        except SQLAlchemyError as e:
            logger.exception(f"❌ SQLAlchemyError while loading data with key: {key}")
            raise e
        except Exception as e:
            logger.exception(f"❌ Unexpected error while loading data with key: {key}")
            raise e

    async def fetch_data_b(self):
        """
        Fetches data from an external source (DATA B) with retry logic.

        Tries to fetch data from the API for a maximum number of retries. If the maximum
        retries are reached, the function returns cached data from the database.

        Returns:
            dict: The fetched or cached data.

        Raises:
            Exception: If an error occurs during the fetching or retrying process.
        """
        logger.info("📡 Fetching DATA B from external source...")
        attempt = 0
        while attempt < self.settings.MAX_RETRIES:
            try:
                async with httpx.AsyncClient() as client:
                    res = await client.get(get_settings().DATA_B_URL)
                    res.raise_for_status()
                    data = res.json()
                    await self.save_data("data_b", data)
                    logger.info("✅ Successfully fetched and saved DATA B.")
                    return data
            except Exception as e:
                attempt += 1
                logger.warning(f"⚠️ Attempt {attempt} to fetch DATA B failed: {e}")

                if attempt >= self.settings.MAX_RETRIES:
                    logger.error("❌ Max retries reached. Using cached DATA B instead.")
                    return await self.load_data("data_b")

                logger.info(f"🔁 Retrying in {self.settings.RETRY_DELAY} seconds...")
                await asyncio.sleep(self.settings.RETRY_DELAY)

    async def merge_data(self):
        """
        Merges data A and data B and saves the result as data C.

        Retrieves both data A and data B from the database, merges them into one
        dataset, and saves the result as data C.

        Raises:
            Exception: If an error occurs during the merging process.
        """
        logger.info("🔀 Merging DATA A and DATA B into DATA C...")
        data_a = await self.load_data("data_a")
        data_b = await self.load_data("data_b")
        if data_a and data_b:
            merged = {**data_a, **data_b}
            await self.save_data("data_c", merged)
            logger.info("✅ Successfully merged and saved DATA C.")
        else:
            logger.warning("⚠️ Could not merge. One or both datasets are missing.")

    async def fetch_and_merge(self):
        logger.info("📦 Running fetch and merge operation...")
        await self.fetch_data_b()
        await self.merge_data()
        logger.info("✅ Fetch and merge operation completed.")


def get_data_service(session: AsyncSession = Depends(get_session)) -> DataService:
    """
    Dependency injection function to provide an instance of the DataService.

    This function initializes the `DataService` with a database session and application
    settings, which are fetched using the `get_settings` method.

    Args:
        session (AsyncSession, optional): The database session for the service. Defaults to `get_session`.

    Returns:
        DataService: The initialized `DataService` instance.
    """
    settings = get_settings()
    return DataService(session=session, settting=settings)

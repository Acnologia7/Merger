import httpx
import asyncio
import json
from fastapi import Depends
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import get_settings, Settings
from app.core.db import get_session
from app.models.models import Storage


# class DataService:

#     def __init__(self, session: AsyncSession, settting: Settings):
#         self.settings = settting
#         self.session = session

#     async def save_data(self, key: str, value: dict):
#         try:
#             json_value = json.dumps(value)
#             await self.session.merge(Storage(key=key, value=json_value))
#             await self.session.commit()
#         except SQLAlchemyError as e:
#             await self.session.rollback()
#             print(f"SQLAlchemyError occurred: {e}")
#             raise e
#         except Exception as e:
#             await self.session.rollback()
#             print(f"Unexpected error occurred: {e}")
#             raise e

#     async def load_data(self, key: str) -> Optional[dict]:
#         try:
#             result = await self.session.execute(
#                 select(Storage).where(Storage.key == key)
#             )
#             row = result.scalar_one_or_none()
#             return json.loads(row.value) if row else None
#         except SQLAlchemyError as e:
#             print(f"SQLAlchemyError occurred: {e}")
#             raise e
#         except Exception as e:
#             print(f"Unexpected error occurred: {e}")
#             raise e

#     async def fetch_data_b(self):
#         print("Fetching data B...")
#         attempt = 0
#         while attempt < self.settings.MAX_RETRIES:
#             try:
#                 async with httpx.AsyncClient() as client:
#                     res = await client.get(get_settings().DATA_B_URL)
#                     res.raise_for_status()
#                     data = res.json()
#                     await self.save_data("data_b", data)
#                     return data
#             except Exception as e:
#                 attempt += 1
#                 print(f"Attempt {attempt} failed to fetch DATA B: {e}")

#                 if attempt >= self.settings.MAX_RETRIES:
#                     print("Max retries reached. Returning cached data.")
#                     return await self.load_data("data_b")

#                 print(f"Retrying in {self.settings.RETRY_DELAY} seconds...")
#                 await asyncio.sleep(self.settings.RETRY_DELAY)

#     async def merge_data(self):
#         data_a = await self.load_data("data_a")
#         data_b = await self.load_data("data_b")
#         if data_a and data_b:
#             merged = {**data_a, **data_b}
#             await self.save_data("data_c", merged)

#     async def fetch_and_merge(self):
#         await self.fetch_data_b()
#         await self.merge_data()


# def get_data_service(session: AsyncSession = Depends(get_session)) -> DataService:
#     settings = get_settings()
#     return DataService(session=session, settting=settings)


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
        """
        Initializes the DataService instance with a database session and settings.

        Args:
            session (AsyncSession): The database session to interact with the database.
            settting (Settings): Application settings containing various configuration values.
        """
        self.settings = settting
        self.session = session

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
        try:
            json_value = json.dumps(value)
            await self.session.merge(Storage(key=key, value=json_value))
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            print(f"SQLAlchemyError occurred: {e}")
            raise e
        except Exception as e:
            await self.session.rollback()
            print(f"Unexpected error occurred: {e}")
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
        try:
            result = await self.session.execute(
                select(Storage).where(Storage.key == key)
            )
            row = result.scalar_one_or_none()
            return json.loads(row.value) if row else None
        except SQLAlchemyError as e:
            print(f"SQLAlchemyError occurred: {e}")
            raise e
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
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
        print("Fetching data B...")
        attempt = 0
        while attempt < self.settings.MAX_RETRIES:
            try:
                async with httpx.AsyncClient() as client:
                    res = await client.get(get_settings().DATA_B_URL)
                    res.raise_for_status()
                    data = res.json()
                    await self.save_data("data_b", data)
                    return data
            except Exception as e:
                attempt += 1
                print(f"Attempt {attempt} failed to fetch DATA B: {e}")

                if attempt >= self.settings.MAX_RETRIES:
                    print("Max retries reached. Returning cached data.")
                    return await self.load_data("data_b")

                print(f"Retrying in {self.settings.RETRY_DELAY} seconds...")
                await asyncio.sleep(self.settings.RETRY_DELAY)

    async def merge_data(self):
        """
        Merges data A and data B and saves the result as data C.

        Retrieves both data A and data B from the database, merges them into one
        dataset, and saves the result as data C.

        Raises:
            Exception: If an error occurs during the merging process.
        """
        data_a = await self.load_data("data_a")
        data_b = await self.load_data("data_b")
        if data_a and data_b:
            merged = {**data_a, **data_b}
            await self.save_data("data_c", merged)

    async def fetch_and_merge(self):
        """
        Fetches data B and merges it with data A to create data C.

        This method combines the `fetch_data_b` and `merge_data` methods. It first fetches
        data B (with retries) and then merges it with data A to produce data C.

        Raises:
            Exception: If an error occurs during the fetching or merging process.
        """
        await self.fetch_data_b()
        await self.merge_data()


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

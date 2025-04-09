from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError
from app.core.db import init_db
from app.core.exception_handlers import generic_exception_handler, sql_exception_handler
from app.routers.routes import router
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔧 Initializing DB at app startup...")
    await init_db()
    logger.info("✅ DB initialized successfully.")
    yield
    logger.info("🧹 App shutdown cleanup complete.")


app = FastAPI(title="Menu Merger API", version="1.0", lifespan=lifespan)
app.include_router(router)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(SQLAlchemyError, sql_exception_handler)

logger.info("🚀 FastAPI application created and routes registered.")

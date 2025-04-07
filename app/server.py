from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError
from app.core.db import init_db
from app.core.exception_handlers import generic_exception_handler, sql_exception_handler
from app.routers.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Menu Merger API", version="1.0", lifespan=lifespan)
app.include_router(router)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(SQLAlchemyError, sql_exception_handler)

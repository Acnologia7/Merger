from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Generic exception handler for unexpected errors.

    Catches all exceptions and returns a generic 500 server error response
    with a user-friendly message.

    Args:
        request (Request): The incoming HTTP request.
        exc (Exception): The exception that was raised during the request handling.

    Returns:
        JSONResponse: A JSON response with a 500 status code and a generic error message.
    """
    logger.exception(f"❌ Unhandled exception at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Unexpected server error, please contact support."},
    )


async def sql_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Exception handler for SQLAlchemy-related errors.

    Catches SQLAlchemy errors and returns a 500 server error response with a
    generic message, indicating a server-side issue.

    Args:
        request (Request): The incoming HTTP request.
        exc (SQLAlchemyError): The SQLAlchemy error that occurred during the database operation.

    Returns:
        JSONResponse: A JSON response with a 500 status code and a generic error message.
    """
    logger.exception(f"💥 SQLAlchemy error at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Unexpected server error, please contact support."},
    )

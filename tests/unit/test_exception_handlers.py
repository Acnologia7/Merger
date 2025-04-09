import pytest
import json
from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.core.exception_handlers import generic_exception_handler, sql_exception_handler


class MockRequest:
    def __init__(self, url_path="/test"):
        self.url = type("URL", (), {"path": url_path})


@pytest.mark.asyncio
async def test_generic_exception_handler():
    request = MockRequest("/test-generic")
    exception = Exception("Test generic exception")

    response: JSONResponse = await generic_exception_handler(request, exception)

    assert response.status_code == 500
    body = json.loads(response.body.decode())
    assert body == {"message": "Unexpected server error, please contact support."}


@pytest.mark.asyncio
async def test_sql_exception_handler():
    request = MockRequest("/test-sql")
    exception = SQLAlchemyError("Test SQL error")

    response: JSONResponse = await sql_exception_handler(request, exception)

    assert response.status_code == 500
    body = json.loads(response.body.decode())
    assert body == {"message": "Unexpected server error, please contact support."}

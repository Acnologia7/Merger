import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.data import DataService
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings
from app.models.models import Storage


@pytest.fixture
def settings():
    return Settings(
        MAX_RETRIES=3, RETRY_DELAY=2, DATA_B_URL="https://example.com/data-b"
    )


@pytest.fixture
def mock_session():
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.merge = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_save_data_success(mock_session, settings):
    service = DataService(session=mock_session, settting=settings)
    await service.save_data("key", {"foo": "bar"})
    mock_session.merge.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_save_data_sqlalchemy_error(mock_session, settings):
    mock_session.merge.side_effect = Exception("DB Error")
    service = DataService(session=mock_session, settting=settings)

    with pytest.raises(Exception):
        await service.save_data("key", {"foo": "bar"})
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_load_data_found(mock_session, settings):
    storage = Storage(key="key", value='{"foo": "bar"}')
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = storage
    mock_session.execute.return_value = mock_result

    service = DataService(session=mock_session, settting=settings)
    data = await service.load_data("key")
    assert data == {"foo": "bar"}


@pytest.mark.asyncio
async def test_load_data_not_found(mock_session, settings):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    service = DataService(session=mock_session, settting=settings)
    data = await service.load_data("missing_key")
    assert data is None


@pytest.mark.asyncio
async def test_fetch_data_b_success(mock_session, settings):
    service = DataService(session=mock_session, settting=settings)
    response_data = {"fetched": True}

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value=response_data),
            raise_for_status=MagicMock(),
        )
        data = await service.fetch_data_b()
        assert data == response_data


@pytest.mark.asyncio
async def test_fetch_data_b_retries_and_fallback(mock_session, settings):
    service = DataService(session=mock_session, settting=settings)

    with patch("httpx.AsyncClient.get", side_effect=Exception("fail")):
        with patch.object(
            service, "load_data", return_value={"cached": True}
        ) as mock_load:
            data = await service.fetch_data_b()
            assert data == {"cached": True}
            assert mock_load.called


@pytest.mark.asyncio
async def test_merge_data_success(mock_session, settings):
    service = DataService(session=mock_session, settting=settings)

    with patch.object(service, "load_data", side_effect=[{"a": 1}, {"b": 2}]):
        with patch.object(service, "save_data", new_callable=AsyncMock) as mock_save:
            await service.merge_data()
            mock_save.assert_called_once_with("data_c", {"a": 1, "b": 2})


@pytest.mark.asyncio
async def test_merge_data_missing(mock_session, settings):
    service = DataService(session=mock_session, settting=settings)

    with patch.object(service, "load_data", side_effect=[None, {"b": 2}]):
        with patch.object(service, "save_data", new_callable=AsyncMock) as mock_save:
            await service.merge_data()
            mock_save.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_and_merge(mock_session, settings):
    service = DataService(session=mock_session, settting=settings)

    with patch.object(
        service, "fetch_data_b", new_callable=AsyncMock
    ) as mock_fetch, patch.object(
        service, "merge_data", new_callable=AsyncMock
    ) as mock_merge:
        await service.fetch_and_merge()
        mock_fetch.assert_called_once()
        mock_merge.assert_called_once()

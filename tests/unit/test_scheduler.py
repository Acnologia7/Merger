import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.scheduler import setup_scheduler


@pytest.mark.asyncio
async def test_setup_scheduler():
    loop = asyncio.get_event_loop()

    mock_session = AsyncMock()
    mock_session_gen = AsyncMock()
    mock_session_gen.__anext__.return_value = mock_session
    mock_session_gen.aclose = AsyncMock()

    mock_settings = MagicMock()
    mock_settings.FETCH_INTERVAL_SECONDS = 60

    with patch("app.core.scheduler.get_settings", return_value=mock_settings), patch(
        "app.core.scheduler.get_session", return_value=mock_session_gen
    ), patch("app.core.scheduler.DataService") as MockDataService, patch(
        "app.core.scheduler.AsyncIOScheduler"
    ) as MockScheduler:

        mock_data_service = AsyncMock()
        MockDataService.return_value = mock_data_service

        mock_scheduler = MagicMock()
        MockScheduler.return_value = mock_scheduler

        result = await setup_scheduler(loop)

        mock_scheduler.add_job.assert_called_once_with(
            mock_data_service.fetch_and_merge,
            "interval",
            seconds=mock_settings.FETCH_INTERVAL_SECONDS,
            max_instances=1,
            next_run_time=pytest.approx(
                result.add_job.call_args[1]["next_run_time"], abs=2
            ),
        )
        mock_session_gen.aclose.assert_awaited_once()
        assert result == mock_scheduler

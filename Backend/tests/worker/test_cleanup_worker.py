from unittest.mock import MagicMock
from app.worker.cleanup_worker import run_cleanup_cycle


def test_run_cleanup_cycle_calls_service():
    """Verify that run_cleanup_cycle passes the correct retention hours to JobService."""
    mock_db = MagicMock()
    with patch_job_service() as mock_service:
        mock_service.return_value.delete_old_jobs.return_value = 5
        deleted = run_cleanup_cycle(mock_db, older_than_hours=24)

        assert deleted == 5
        mock_service.return_value.delete_old_jobs.assert_called_once_with(hours=24)


def patch_job_service():
    from unittest.mock import patch
    return patch("app.worker.cleanup_worker.JobService")

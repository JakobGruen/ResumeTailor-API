import pytest
import json
from resumetailor.core.session import session_manager
from resumetailor.models import JobProfile, Resume, OutputResume, CoverLetter
from resumetailor.core.constants import BASE_DATA_DIR
from pathlib import Path
import shutil


@pytest.fixture
def test_data_with_job_dir():
    """Fixture providing path to test data with job directory."""
    return BASE_DATA_DIR / "test_with_job"


@pytest.fixture
def test_data_without_job_dir():
    """Fixture providing path to test data without job directory."""
    return BASE_DATA_DIR / "test_without_job"


@pytest.fixture
def test_data_dir():
    """Fixture providing path to main data directory."""
    return BASE_DATA_DIR


@pytest.fixture
def mock_data_dir():
    data_dir = BASE_DATA_DIR / "test_output"
    return data_dir


@pytest.fixture
def mock_client(monkeypatch, mock_data_dir):
    from fastapi.testclient import TestClient
    from resumetailor.main import app

    client = TestClient(app)
    return client


@pytest.fixture
def cleanup_data_dir(mock_session_id):
    yield
    # After test cleanup
    from resumetailor.core.constants import BASE_DATA_DIR

    test_output_dir = BASE_DATA_DIR / mock_session_id
    shutil.rmtree(test_output_dir, ignore_errors=True)


@pytest.fixture
def mock_session_id(mock_client):
    payload = {
        "application_type": "job_application",
        "steps": ["job_profile", "resume", "cover_letter"],
    }
    response = mock_client.post("/application/initialize", json=payload)
    assert response.status_code == 200
    assert "session_id" in response.json()
    return response.json()["session_id"]


@pytest.fixture
def preload_session_data(mock_data_dir, mock_session_id, test_data_with_job_dir):
    """
    Preload test objects into the session_manager for use in tests.
    """

    # Load and set job_description
    with open(test_data_with_job_dir / "job_description.txt") as f:
        session_manager.update_session_data(mock_session_id, job_description=f.read())
    # Load and set job_profile
    with open(test_data_with_job_dir / "job_profile.json") as f:
        session_manager.update_session_data(
            mock_session_id, job_profile=JobProfile(**json.load(f))
        )
    # Load and set refined_resume (use resume.json from test_with_job)
    with open(test_data_with_job_dir / "resume.json") as f:
        session_manager.update_session_data(
            mock_session_id, refined_resume=OutputResume(**json.load(f))
        )
    # Load and set cover_letter
    with open(test_data_with_job_dir / "cover_letter.json") as f:
        session_manager.update_session_data(
            mock_session_id, cover_letter=CoverLetter(**json.load(f))
        )
    # Set data_dir
    session_manager.update_session_data(mock_session_id, data_dir=mock_data_dir)
    yield mock_session_id


@pytest.fixture
def preload_session_data_without_job(
    mock_data_dir, mock_session_id, test_data_without_job_dir
):
    """
    Preload test objects into the session_manager for tests without job data.
    """

    # Load and set refined_resume (use resume.json from test_without_job)
    with open(test_data_without_job_dir / "resume.json") as f:
        session_manager.update_session_data(
            mock_session_id, refined_resume=OutputResume(**json.load(f))
        )
    # Set data_dir
    session_manager.update_session_data(mock_session_id, data_dir=mock_data_dir)
    yield mock_session_id

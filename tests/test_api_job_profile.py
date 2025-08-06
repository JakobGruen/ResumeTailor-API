from pathlib import Path
import json
import pytest

from resumetailor.models import JobProfile


@pytest.fixture
def job_description_text(test_data_with_job_dir):
    with open(test_data_with_job_dir / "job_description.txt") as f:
        return f.read()


@pytest.fixture
def job_description(test_data_with_job_dir):
    with open(test_data_with_job_dir / "job_description.txt") as f:
        return f.read()


@pytest.mark.api
@pytest.mark.job_profile
class TestJobProfileAPI:
    def test_generate_job_profile(self, mock_client, mock_session_id, job_description):
        payload = {"session_id": mock_session_id, "job_description": job_description}
        response = mock_client.post("/job-profile/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        job_profile = JobProfile(**data)
        assert job_profile.position is not None

    def test_edit_job_profile(self, mock_client, mock_session_id, job_description):
        self.test_generate_job_profile(mock_client, mock_session_id, job_description)
        payload = {
            "session_id": mock_session_id,
            "user_edited_profile": None,
            "suggestion": "Add more leadership experience.",
        }
        response = mock_client.post("/job-profile/edit", json=payload)
        assert response.status_code == 200
        data = response.json()
        job_profile = JobProfile(**data)
        assert job_profile.position is not None

    def test_complete_job_profile_save(
        self, mock_client, mock_session_id, job_description
    ):
        self.test_generate_job_profile(mock_client, mock_session_id, job_description)
        payload = {
            "session_id": mock_session_id,
            "user_edited_profile": None,
            "decision": "save",
        }
        response = mock_client.post("/job-profile/complete", json=payload)
        print(response.json())
        assert response.status_code == 200
        assert response.json()["message"].startswith("Job profile saved")

    def test_complete_job_profile_discard(
        self, mock_client, mock_session_id, job_description
    ):
        self.test_generate_job_profile(mock_client, mock_session_id, job_description)
        payload = {
            "session_id": mock_session_id,
            "user_edited_profile": None,
            "decision": "discard",
        }
        response = mock_client.post("/job-profile/complete", json=payload)
        assert response.status_code == 200
        assert response.json()["message"].startswith("Job profile discarded")

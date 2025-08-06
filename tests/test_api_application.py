from pathlib import Path
import json
import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
@pytest.mark.session
class TestSessionAPI:
    def test_initialize_job_application(self, mock_client):
        payload = {
            "application_type": "job_application",
            "steps": ["job_profile", "resume", "cover_letter"],
        }
        response = mock_client.post("/application/initialize", json=payload)
        print(response.json())
        assert response.status_code == 200
        assert "session_id" in response.json()

    def test_initialize_general_resume(self, mock_client):
        payload = {"application_type": "general_resume", "steps": ["resume"]}
        response = mock_client.post("/application/initialize", json=payload)
        print(response.json())
        assert response.status_code == 200
        assert "session_id" in response.json()

    def test_initialize_job_application_invalid_type(self, mock_client):
        payload = {"application_type": "invalid_type", "steps": ["job_profile"]}
        response = mock_client.post("/application/initialize", json=payload)
        assert response.status_code == 422  # unprocessable entry

    def test_initialize_job_application_invalid_step(self, mock_client):
        payload = {
            "application_type": "job_application",
            "steps": ["job_profile", "foo"],
        }
        response = mock_client.post("/application/initialize", json=payload)
        assert response.status_code == 422  # unprocessable entry

    @pytest.mark.resumegen
    def test_complete_application_save(
        self, mock_client, mock_session_id, preload_session_data, cleanup_data_dir
    ):
        payload = {"session_id": mock_session_id, "action": "save"}
        response = mock_client.post(f"/application/complete", json=payload)
        assert response.status_code == 200
        assert response.json()["detail"].startswith("Application rendered and saved")
        data_dir = response.json()["data_dir"]
        assert isinstance(data_dir, str)
        # TODO: test output dir (and cleanup )
        assert Path(data_dir).exists()
        assert (Path(data_dir) / "resume.html").exists()
        assert (Path(data_dir) / "resume.pdf").exists()
        assert (Path(data_dir) / "cover_letter.html").exists()
        assert (Path(data_dir) / "cover_letter.pdf").exists()

    def test_complete_application_discard(
        self, mock_client, mock_session_id, cleanup_data_dir
    ):
        payload = {"session_id": mock_session_id, "action": "discard"}
        response = mock_client.post(f"/application/complete", json=payload)
        assert response.status_code == 200
        assert response.json()["detail"].startswith("Session discarded")

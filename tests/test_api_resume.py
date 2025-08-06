import pytest
from pathlib import Path
import json
from rich import print

from resumetailor.models import Resume
from resumetailor.models.resume import WorkPosition


@pytest.mark.api
@pytest.mark.resume
class TestResumeAPI:
    def test_generate_resume_with_job(
        self, mock_client, mock_session_id, preload_session_data
    ):
        payload = {
            "session_id": mock_session_id,
        }
        response = mock_client.post("/resume/generate", json=payload)
        assert response.status_code == 200
        resume = Resume(**response.json())

    def test_generate_resume_without_job(
        self, mock_client, mock_session_id, preload_session_data
    ):
        payload = {
            "session_id": mock_session_id,
            "job_titles": "Backend Developer, API Engineer",
            "focus_aspects": "REST APIs, Cloud Deployment",
        }
        response = mock_client.post("/resume/generate", json=payload)
        assert response.status_code == 200
        resume = Resume(**response.json())

    def test_edit_resume(self, mock_client, mock_session_id, preload_session_data):
        # First, generate a resume
        self.test_generate_resume_without_job(
            mock_client, mock_session_id, preload_session_data
        )
        # Then, edit a section
        payload = {
            "session_id": mock_session_id,
            "section_key": "work_experience",
            "editing_suggestions": "Add more leadership experience.",
            "user_edited_section": None,
        }
        response = mock_client.post("/resume/edit-section", json=payload)
        assert response.status_code == 200
        for position in response.json():
            WorkPosition(**position)

    def test_complete_resume_save(
        self, mock_client, mock_session_id, preload_session_data
    ):
        self.test_generate_resume_without_job(
            mock_client, mock_session_id, preload_session_data
        )

        payload = {
            "session_id": mock_session_id,
            "user_edited_resume": None,
            "decision": "save",
        }
        response = mock_client.post("/resume/complete", json=payload)
        assert response.status_code == 200
        assert response.json()["message"].startswith("Resume saved")

    def test_complete_resume_discard(
        self, mock_client, mock_session_id, preload_session_data
    ):

        self.test_generate_resume_without_job(
            mock_client, mock_session_id, preload_session_data
        )
        payload = {
            "session_id": mock_session_id,
            "user_edited_resume": None,
            "decision": "discard",
        }
        response = mock_client.post("/resume/complete", json=payload)
        assert response.status_code == 200
        assert response.json()["message"].startswith("Resume discarded")

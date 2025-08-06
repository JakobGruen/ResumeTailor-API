import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from resumetailor.main import app

client = TestClient(app)


@pytest.mark.api
@pytest.mark.data
class TestDataAPI:
    def test_get_full_resume(self):
        response = client.get("/data/full_resume.json")
        assert response.status_code == 200
        assert "personal_information" in response.json() or response.json() != {}

    def test_get_history(self):
        response = client.get("/data/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_job_description_txt(self):
        # Use a known ID from your data/applications directory
        response = client.get("/data/test_with_job/job_description.txt")
        assert response.status_code in (200, 404)

    def test_get_job_profile_json(self):
        # Use a known ID from your data/applications directory
        response = client.get("/data/test_with_job/job_profile.json")
        assert response.status_code in (200, 404)

    def test_get_resume_html(self):
        # Use a known ID from your data/applications directory
        response = client.get("/data/test_with_job/resume.html")
        assert response.status_code in (200, 404)

    def test_get_cover_letter_html(self):
        response = client.get("/data/test_with_job/cover_letter.html")
        assert response.status_code in (200, 404)

    def test_download_resume_pdf(self):
        response = client.get("/data/test_with_job/resume.pdf")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            assert response.headers["content-type"] == "application/pdf"

    def test_download_cover_letter_pdf(self):
        response = client.get("/data/test_with_job/cover_letter.pdf")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            assert response.headers["content-type"] == "application/pdf"

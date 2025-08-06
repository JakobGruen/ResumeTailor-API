import pytest

from resumetailor.models import CoverLetter


@pytest.mark.api
@pytest.mark.cover_letter
class TestCoverLetterAPI:
    def test_generate_cover_letter(self, mock_client, mock_session_id):
        payload = {
            "session_id": mock_session_id,
        }
        response = mock_client.post("/cover-letter/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        CoverLetter(**data)

    def test_edit_cover_letter(self, mock_client, mock_session_id):
        # First, generate a cover letter
        self.test_generate_cover_letter(mock_client, mock_session_id)
        payload = {
            "session_id": mock_session_id,
            "user_edited_cover_letter": None,
            "editing_suggestions": "Highlight teamwork skills.",
        }
        response = mock_client.post("/cover-letter/edit", json=payload)
        assert response.status_code == 200
        data = response.json()
        CoverLetter(**data)

    def test_complete_cover_letter_save(self, mock_client, mock_session_id):
        self.test_generate_cover_letter(mock_client, mock_session_id)
        payload = {
            "session_id": mock_session_id,
            "user_edited_cover_letter": None,
            "decision": "save",
        }
        response = mock_client.post("/cover-letter/complete", json=payload)
        assert response.status_code == 200
        assert response.json()["message"].startswith("Cover letter saved")

    def test_complete_cover_letter_discard(self, mock_client, mock_session_id):
        self.test_generate_cover_letter(mock_client, mock_session_id)
        payload = {
            "session_id": mock_session_id,
            "user_edited_cover_letter": None,
            "decision": "discard",
        }
        response = mock_client.post("/cover-letter/complete", json=payload)
        assert response.status_code == 200
        assert response.json()["message"].startswith("Cover letter discarded")

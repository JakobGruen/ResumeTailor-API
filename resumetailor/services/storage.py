from pathlib import Path
import json
from datetime import datetime

from resumetailor.models import JobProfile, Resume, CoverLetter, PersonalInfo
from resumetailor.core.session import session_manager, Info
from resumetailor.core.constants import BASE_DATA_DIR


def load_anon_info() -> PersonalInfo:
    """
    Load anonymous personal information from a JSON file.
    """
    with open(BASE_DATA_DIR / "anonymous_info.json", "r") as f:
        anon_info = PersonalInfo(**json.load(f))
    return anon_info


def load_private_info() -> PersonalInfo:
    """
    Load private personal information from a JSON file.
    """
    with open(BASE_DATA_DIR / "private_info.json", "r") as f:
        private_info = PersonalInfo(**json.load(f))
    return private_info


def save_private_info(info: PersonalInfo):
    """
    Save private personal information to a JSON file.
    """
    with open(BASE_DATA_DIR / "private_info.json", "w") as f:
        json.dump(info.model_dump(), f, indent=2)


def create_data_dir(session_id: str) -> Path:
    """
    Create a data directory for the session if it does not exist.
    """
    data_dir = (BASE_DATA_DIR / session_id).resolve()
    data_dir.mkdir(parents=True)
    session_manager.update_session_data(session_id=session_id, data_dir=data_dir)
    save_info(session_id)


def save_info(session_id: str):
    """
    Save basic information to the data directory.
    """
    data_dir = session_manager.get_session_data(session_id, "data_dir")
    info: Info = session_manager.get_session_data(session_id, "info")
    info.created_at = datetime.now().date().isoformat()
    session_manager.update_session_data(session_id=session_id, info=info)
    with open(data_dir / "info.json", "w") as f:
        json.dump(info.model_dump(), f, indent=2)


def save_job_profile(session_id: str):
    """
    Save job description and job profile to the data directory for a session.
    """
    data_dir = session_manager.get_session_data(session_id, "data_dir")
    job_description = session_manager.get_session_data(session_id, "job_description")
    with open(data_dir / "job_description.txt", "w") as f:
        f.write(job_description)
    job_profile = session_manager.get_session_data(session_id, "job_profile")
    with open(data_dir / "job_profile.json", "w") as f:
        json.dump(job_profile.model_dump(), f, indent=2)


def load_job_profile(session_id: str) -> JobProfile:
    """
    Load a job profile from the data directory for a session.
    """
    job_profile_path = (
        session_manager.get_session_data(session_id, "data_dir") / "job_profile.json"
    )
    if not job_profile_path.exists():
        raise FileNotFoundError(
            f"Job profile data not found for session_id: {session_id}"
        )
    with open(job_profile_path, "r") as f:
        job_profile = json.load(f)
    return job_profile


def load_full_resume() -> Resume:
    """
    Load the full resume from the data directory.
    """
    resume_path = BASE_DATA_DIR / "full_resume.json"
    if not resume_path.exists():
        raise FileNotFoundError("Full resume data not found.")
    with open(resume_path, "r") as f:
        resume_data = json.load(f)
    resume = Resume(**resume_data)
    save_private_info(resume.personal_information)
    resume.personal_information = load_anon_info()
    return resume


def save_refined_resume(session_id: str):
    """
    Save the refined resume to the data directory for a session.
    """
    data_dir = session_manager.get_session_data(session_id, "data_dir")
    refined_resume = session_manager.get_session_data(session_id, "refined_resume")
    with open(data_dir / "resume.json", "w") as f:
        json.dump(refined_resume.model_dump(), f, indent=2)


def load_refined_resume(session_id: str) -> Resume:
    """
    Load the refined resume from the data directory for a session.
    """
    refined_resume_path = (
        session_manager.get_session_data(session_id, "data_dir") / "resume.json"
    )
    if not refined_resume_path.exists():
        raise FileNotFoundError(
            f"Refined resume data not found for session_id: {session_id}"
        )
    with open(refined_resume_path, "r") as f:
        refined_resume = json.load(f)
    return Resume(**refined_resume)


def save_cover_letter(session_id: str):
    """
    Save the cover letter to the data directory for a session.
    """
    data_dir = session_manager.get_session_data(session_id, "data_dir")
    cover_letter = session_manager.get_session_data(session_id, "cover_letter")
    with open(data_dir / "cover_letter.json", "w") as f:
        json.dump(cover_letter.model_dump(), f, indent=2)


def load_cover_letter(session_id: str) -> CoverLetter:
    """
    Load the cover letter from the data directory for a session.
    """
    cover_letter_path = (
        session_manager.get_session_data(session_id, "data_dir") / "cover_letter.json"
    )
    if not cover_letter_path.exists():
        raise FileNotFoundError(
            f"Cover letter data not found for session_id: {session_id}"
        )
    with open(cover_letter_path, "r") as f:
        cover_letter = json.load(f)
    return CoverLetter(**cover_letter)


def save_html(session_id: str, html_content: str, filename: str) -> Path:
    """
    Save HTML content to a file in the session's data directory.
    """
    data_dir = session_manager.get_session_data(session_id, "data_dir")
    html_path = data_dir / filename
    with open(html_path, "w") as f:
        f.write(html_content)
    return html_path

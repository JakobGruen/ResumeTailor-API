from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Literal
from pathlib import Path
import requests
import base64
import os

from resumetailor.core.session import session_manager
from resumetailor.services.storage import (
    create_data_dir,
    save_job_profile,
    save_refined_resume,
    save_cover_letter,
    load_private_info,
)
from resumetailor.models import OutputResume

# Configuration for ResumeGen microservice
RESUMEGEN_API_URL = os.getenv("RESUMEGEN_API_URL", "http://localhost:8000")


def call_resumegen_api(endpoint: str, data: dict) -> dict:
    """
    Call the ResumeGen microservice API.

    Args:
        endpoint: API endpoint (e.g., 'generate-resume', 'generate-cover-letter')
        data: Request payload

    Returns:
        API response containing html_content and pdf_content
    """
    try:
        response = requests.post(
            f"{RESUMEGEN_API_URL}/{endpoint}",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate document via ResumeGen API: {str(e)}",
        )


def save_generated_content(
    session_id: str, content: dict, file_prefix: str
) -> tuple[Path, Path]:
    """
    Save HTML and PDF content from ResumeGen API response.

    Args:
        session_id: Session identifier
        content: API response containing html_content and pdf_content
        file_prefix: Prefix for output files (e.g., 'resume', 'cover_letter')

    Returns:
        Tuple of (html_path, pdf_path)
    """
    data_dir = session_manager.get_session_data(session_id, "data_dir")
    data_path = Path(data_dir)

    # Save HTML content
    html_path = data_path / f"{file_prefix}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content["html_content"])

    # Save PDF content
    pdf_path = data_path / f"{file_prefix}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(base64.b64decode(content["pdf_content"]))

    return html_path, pdf_path


router = APIRouter()


class ApplicationRequest(BaseModel):
    application_type: Literal["job_application", "general_resume"]
    steps: list[Literal["job_profile", "resume", "cover_letter"]]


@router.post("/application/initialize")
def initialize_job_application(req: ApplicationRequest):
    """
    Initialize a job application session.
    This endpoint creates a new session for the job application process.
    """
    session_id = session_manager.create_session(req.application_type, req.steps)
    return {"session_id": session_id}


class CompleteApplicationRequest(BaseModel):
    session_id: str
    action: Literal["save", "discard"]


@router.post("/application/complete")
def complete_application(req: CompleteApplicationRequest):
    """
    Complete or discard the job application session.
    If action is "save", render and save resume and cover letter using ResumeGen microservice.
    If action is "discard", delete the session and its data.
    """
    if req.action == "discard":
        session_manager.delete_session(req.session_id)
        return {"detail": "Session discarded."}

    # Load session data
    job_profile = session_manager.get_session_data(req.session_id, "job_profile")

    def get_resume(session_id: str) -> OutputResume:
        return session_manager.get_session_data(req.session_id, "refined_resume")

    resume = get_resume(req.session_id)

    cover_letter = session_manager.get_session_data(req.session_id, "cover_letter")

    # Fill private data before processing
    private_info = load_private_info()
    resume.personal_information = private_info
    session_manager.update_session_data(req.session_id, refined_resume=resume)

    # Save JSON data
    create_data_dir(req.session_id)
    if job_profile is not None:
        save_job_profile(req.session_id)
    save_refined_resume(req.session_id)

    try:
        # Generate Resume using ResumeGen microservice
        resume_dict = resume.model_dump()
        resume_dict.pop("personal_information")
        resume_data = {
            "personal_info": private_info.model_dump(),
            "resume_data": resume_dict,
        }

        resume_content = call_resumegen_api("generate-resume", resume_data)
        resume_html_path, resume_pdf_path = save_generated_content(
            req.session_id, resume_content, "resume"
        )

        # Generate Cover Letter using ResumeGen microservice (if exists)
        if cover_letter is not None:
            cover_letter.personal_information = private_info
            save_cover_letter(req.session_id)

            cover_letter_data = {
                "personal_info": cover_letter.personal_information.model_dump(),
                "cover_letter_data": cover_letter.model_dump(),
            }

            cover_letter_content = call_resumegen_api(
                "generate-cover-letter", cover_letter_data
            )
            cover_letter_html_path, cover_letter_pdf_path = save_generated_content(
                req.session_id, cover_letter_content, "cover_letter"
            )

        return {
            "detail": "Application rendered and saved as HTML and PDF using ResumeGen microservice.",
            "data_dir": session_manager.get_session_data(req.session_id, "data_dir"),
        }

    except Exception as e:
        # Clean up session on error
        session_manager.delete_session(req.session_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate application documents: {str(e)}",
        )

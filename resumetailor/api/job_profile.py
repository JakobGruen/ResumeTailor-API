from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from resumetailor.llm import extractor
from resumetailor.models import JobProfile
from resumetailor.core.session import session_manager

router = APIRouter()


class GenerateJobProfileRequest(BaseModel):
    session_id: str
    job_description: str


@router.post("/job-profile/generate", response_model=JobProfile)
def generate_job_profile(req: GenerateJobProfileRequest):
    if req.session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    extracted_profile = extractor.extract(
        job_description=req.job_description, thread_id=req.session_id
    )
    session_manager.update_session_data(
        session_id=req.session_id,
        job_description=req.job_description,
        job_profile=extracted_profile,
    )
    return extracted_profile


class EditJobProfileRequest(BaseModel):
    session_id: str
    user_edited_profile: JobProfile | None = None
    suggestion: str


@router.post("/job-profile/edit", response_model=JobProfile)
def edit_job_profile(req: EditJobProfileRequest):
    if req.session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    ai_edited_profile = extractor.edit(
        thread_id=req.session_id,
        editing_suggestions=req.suggestion,
        edited_job_profile=req.user_edited_profile,
    )
    return ai_edited_profile


class CompleteJobProfileRequest(BaseModel):
    session_id: str
    user_edited_profile: JobProfile | None = None
    decision: Literal["save", "discard"]


@router.post("/job-profile/complete")
def complete_job_profile(req: CompleteJobProfileRequest):
    if req.session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    final_job_profile = extractor.complete(
        thread_id=req.session_id,
        edited_job_profile=req.user_edited_profile,
    )
    if req.decision == "discard":
        session_manager.update_session_data(
            session_id=req.session_id, job_description=None, job_profile=None
        )
        return {"message": "Job profile discarded."}
    elif req.decision == "save":
        session_manager.update_session_data(
            session_id=req.session_id,
            job_profile=final_job_profile,
        )
        return {"message": "Job profile saved."}
    else:
        raise HTTPException(
            status_code=400, detail="Invalid decision. Must be 'save' or 'discard'."
        )

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Literal
from copy import deepcopy as dcp
from rich import print

from resumetailor.llm import resume_writer
from resumetailor.models import Resume, SectionType
from resumetailor.core.session import session_manager, Info
from resumetailor.services.storage import (
    load_full_resume,
    load_private_info,
    load_anon_info,
)


router = APIRouter()


class GenerateResumeRequest(BaseModel):
    session_id: str
    job_titles: str | None = None
    focus_aspects: str | None = None


@router.post("/resume/generate", response_model=Resume)
def generate_resume(req: GenerateResumeRequest):
    if req.session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    full_resume = load_full_resume()
    info = session_manager.get_session_data(req.session_id, "info")
    if info.application_type == "general_resume":
        info.job_titles = req.job_titles
        info.focus_aspects = req.focus_aspects
        job_profile = None
    elif info.application_type == "job_application":
        job_profile = session_manager.get_session_data(req.session_id, "job_profile")
        info.company = job_profile.company
        info.position = job_profile.position
    session_manager.update_session_data(session_id=req.session_id, info=info)
    refined_resume = resume_writer.generate(
        thread_id=req.session_id,
        resume=full_resume,
        job_profile=job_profile,
        job_titles=req.job_titles,
        focus_aspects=req.focus_aspects,
    )
    refined_resume.personal_information = load_private_info()
    return refined_resume


class EditSectionRequest(BaseModel):
    session_id: str
    section_key: str
    editing_suggestions: str
    user_edited_section: SectionType | None


@router.post("/resume/edit-section", response_model=SectionType)
def edit_section(req: EditSectionRequest):
    if req.session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    edited_section = resume_writer.edit_section(
        thread_id=req.session_id,
        section_key=req.section_key,
        editing_suggestions=req.editing_suggestions,
        user_edited_section=req.user_edited_section,
    )
    return edited_section


class CompleteResumeRequest(BaseModel):
    session_id: str
    user_edited_resume: Resume | None = None
    decision: Literal["save", "discard"]


@router.post("/resume/complete")
def complete_resume(req: CompleteResumeRequest):
    if req.session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    if req.user_edited_resume is not None:
        req.user_edited_resume.personal_information = load_anon_info()
    final_resume = resume_writer.complete(
        thread_id=req.session_id, user_edited_resume=req.user_edited_resume
    )
    if req.decision == "discard":
        session_manager.update_session_data(
            session_id=req.session_id, refined_resume=None
        )
        return {"message": "Resume discarded."}
    elif req.decision == "save":
        session_manager.update_session_data(
            session_id=req.session_id,
            refined_resume=final_resume,
        )
        return {"message": "Resume saved."}
    else:
        raise HTTPException(
            status_code=400, detail="Invalid decision. Must be 'save' or 'discard'."
        )

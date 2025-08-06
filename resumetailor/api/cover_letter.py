from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Literal
from copy import deepcopy as dcp

from resumetailor.llm import cover_letter_writer
from resumetailor.models import Resume, CoverLetter
from resumetailor.core.session import session_manager
from resumetailor.services.storage import load_private_info, load_anon_info

router = APIRouter()


class GenerateCoverLetterRequest(BaseModel):
    session_id: str


@router.post("/cover-letter/generate", response_model=CoverLetter)
def generate_cover_letter(req: GenerateCoverLetterRequest):
    if req.session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    job_description = session_manager.get_session_data(
        req.session_id, "job_description"
    )
    job_profile = session_manager.get_session_data(req.session_id, "job_profile")
    refined_resume = session_manager.get_session_data(req.session_id, "refined_resume")
    cover_letter = cover_letter_writer.generate(
        thread_id=req.session_id,
        job_profile=job_profile,
        candidate_resume=refined_resume,
        job_description=job_description,
    )
    cover_letter.personal_information = load_private_info()
    return cover_letter


class EditCoverLetterRequest(BaseModel):
    session_id: str
    editing_suggestions: str
    user_edited_cover_letter: CoverLetter | None


@router.post("/cover-letter/edit", response_model=CoverLetter)
def edit_section(req: EditCoverLetterRequest):
    if req.session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    if req.user_edited_cover_letter is not None:
        req.user_edited_cover_letter.personal_information = load_anon_info()
    edited_cover_letter = cover_letter_writer.edit(
        thread_id=req.session_id,
        editing_suggestions=req.editing_suggestions,
        user_edited_cover_letter=req.user_edited_cover_letter,
    )
    edited_cover_letter.personal_information = load_private_info()
    return edited_cover_letter


class CompleteCoverLetterRequest(BaseModel):
    session_id: str
    user_edited_cover_letter: CoverLetter | None
    decision: Literal["save", "discard"]


@router.post("/cover-letter/complete")
def complete_cover_letter(req: CompleteCoverLetterRequest):
    if req.session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    if req.user_edited_cover_letter is not None:
        req.user_edited_cover_letter.personal_information = load_anon_info()
    final_cover_letter = cover_letter_writer.complete(
        thread_id=req.session_id, user_edited_cover_letter=req.user_edited_cover_letter
    )
    if req.decision == "discard":
        session_manager.update_session_data(
            session_id=req.session_id, cover_letter=None
        )
        return {"message": "Cover letter discarded."}
    elif req.decision == "save":
        final_cover_letter.personal_information = load_private_info()
        session_manager.update_session_data(
            session_id=req.session_id,
            cover_letter=final_cover_letter,
        )
        return {"message": "Cover letter saved."}
    else:
        raise HTTPException(
            status_code=400, detail="Invalid decision. Must be 'save' or 'discard'."
        )

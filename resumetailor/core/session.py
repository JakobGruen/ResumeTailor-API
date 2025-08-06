from rich import print
import uuid
from pydantic import BaseModel, Field
from typing import Any, Literal, List
from pathlib import Path

from resumetailor.models import JobProfile, OutputResume, CoverLetter
from resumetailor.core.constants import BASE_DATA_DIR


class Info(BaseModel):
    application_type: Literal["job_application", "general_resume"]
    steps: list[Literal["job_profile", "resume", "cover_letter"]]
    created_at: str | None = Field(None)
    company: str | None = Field(None)  # for job_application
    position: str | None = Field(None)  # for job_application
    job_titles: str | None = Field(None)  # for general_resume
    focus_aspects: str | None = Field(None)  # for general_resume


class Session(BaseModel):
    session_id: str
    info: Info
    data_dir: Path | None = Field(None)
    job_description: str | None = Field(None)
    job_profile: JobProfile | None = Field(None)
    refined_resume: OutputResume | None = Field(None)
    cover_letter: CoverLetter | None = Field(None)


class SessionManager:
    sessions = {}

    def create_session(
        self,
        application_type: Literal["job_application", "general_resume"],
        steps: list[Literal["job_profile", "resume", "cover_letter"]],
    ) -> str:
        session_id = str(uuid.uuid4())
        info = Info(application_type=application_type, steps=steps)
        self.sessions[session_id] = Session(
            session_id=session_id,
            info=info,
        )
        return session_id

    def get_session(self, session_id: str) -> Session:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        return session

    def get_session_data(self, session_id: str, key: str):
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        try:
            data = getattr(session, key)
        except:
            raise ValueError(f"Data '{key}' not found or empty in session")
        return data

    def update_session_data(self, session_id: str, **kwargs):
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        for key, value in kwargs.items():
            try:
                setattr(session, key, value)
            except Exception as e:
                print(f"Failed to update '{key}' in session data: {e}")
        self.sessions[session_id] = session

    def delete_session(self, session_id: str):
        del self.sessions[session_id]


session_manager = SessionManager()

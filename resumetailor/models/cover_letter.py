from pydantic import BaseModel, Field
from typing import List, Annotated

from resumetailor.models.personal_info import PersonalInfo


class CoverLetter(BaseModel):
    personal_information: PersonalInfo = Field(
        ..., description="Personal information of the candidate."
    )
    company: str = Field(
        ...,
        description="The name of the company to which the letter is addressed.",
    )
    position: str = Field(
        ..., description="The position for which the candidate is applying."
    )
    addressee: str | None = Field(
        None,
        description="The name of the person to whom the letter is addressed. (optional, defaults to `Hiring Team`)",
    )
    opening_paragraph: str = Field(
        ...,
        description="The opening paragraph introducing the candidate and stating the position applied for.",
    )
    body_paragraphs: list[str] = Field(
        ...,
        description="A list of body paragraphs, each highlighting relevant qualifications, experiences, and alignment with the job requirements.",
    )
    closing_paragraph: str = Field(
        ..., description="The closing paragraph expressing enthusiasm and gratitude."
    )

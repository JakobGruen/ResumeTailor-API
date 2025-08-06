from pydantic import BaseModel, Field
from typing import List, Annotated

from resumetailor.models.personal_info import PersonalInfo


class CoverLetter(BaseModel):
    personal_information: PersonalInfo | None = Field(
        None, description="Personal information of the candidate."
    )
    company: str | None = Field(
        None,
        description="The name of the company to which the letter is addressed.",
    )
    position: str | None = Field(
        None, description="The position for which the candidate is applying."
    )
    opening_paragraph: Annotated[
        str,
        Field(
            description="The opening paragraph introducing the candidate and stating the position applied for."
        ),
    ]
    body_paragraphs: Annotated[
        List[str],
        Field(
            description="A list of body paragraphs, each highlighting relevant qualifications, experiences, and alignment with the job requirements."
        ),
    ]
    closing_paragraph: Annotated[
        str,
        Field(description="The closing paragraph expressing enthusiasm and gratitude."),
    ]

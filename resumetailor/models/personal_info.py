from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    """
    Personal information of the candidate.
    """

    name: str | None = Field(None, description="First name of the candidate.")
    surname: str | None = Field(None, description="Surname of the candidate.")
    date_of_birth: str | None = Field(
        None, description="Date of birth of the candidate in DD/MM/YYYY format."
    )
    address: str | None = Field(None, description="Street Address of the candidate.")
    city: str | None = Field(None, description="City of residence of the candidate.")
    country: str | None = Field(
        None, description="Country of residence of the candidate."
    )
    zip_code: str | None = Field(
        None, description="Zip code of the candidate's address."
    )
    email: str | None = Field(None, description="email address of the candidate.")
    phone: str | None = Field(
        None, description="Phone number of the candidate (with prefix)."
    )
    linkedin: str | None = Field(
        None, description="LinkedIn profile URL of the candidate."
    )
    github: str | None = Field(None, description="GitHub profile URL of the candidate.")

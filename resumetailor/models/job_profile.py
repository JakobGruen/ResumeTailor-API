from pydantic import BaseModel, Field

class JobProfile(BaseModel):
    """Information about a job offer."""
    company: str | None = Field(None, description="The company offering the the position.")
    position: str | None = Field(None, description="The position being offered.")
    job_type: str | None = Field(None, description="The type of job (e.g., full-time, part-time, contract).")
    responsibilities: list[str] | None = Field(None, description="A list of responsibilities that the job entails.")
    technical_skills: list[str] | None = Field(None, description="A list of all technical skills required or appreciated for the job (e.g. machine learning, web development, ...).")
    required_technologies: list[str] | None = Field(None, description="A list of technologies the applicant needs to be able to handle (e.g. 'Python', 'Gitlab', ...).")
    soft_skills: list[str] | None = Field(None, description="A list of soft skills required for the job (e.g. 'communication with stakeholders', 'teamwork', 'independent research').")
    languages: list[str] | None = Field(None, description="A list of languages required for the job (e.g. 'English C1', 'Conversational German').")
    additional_requirements: list[str] | None = Field(None, description="Any additional requirements or preferences for the job that do not fit into the other categories.")
    educational_qualifications: list[str] | None = Field(None, description="A list of educational qualifications or certifications required for the job (e.g. 'Masters in Computerscience or related', ).")
    certifications: list[str] | None = Field(None, description="A list of certifications required for the job (e.g. 'AWS Certified Solutions Architect', 'Google Cloud Professional Data Engineer').")
    professional_experience: str | None = Field(None, description="A description of the professional experience required for the job.")
    role_evolution: str | None = Field(None, description="Information about the potential evolution of the role.")
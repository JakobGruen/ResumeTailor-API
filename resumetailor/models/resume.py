from pydantic import BaseModel, Field
from typing import List, Union
from resumetailor.models.personal_info import PersonalInfo

# Education


class EduCourse(BaseModel):
    """
    Information about a course in an educational institution.
    """

    name: str = Field(..., description="Name of the course.")
    description: str | None = Field(
        None, description="Brief description of the course content."
    )
    grade: str | None = Field(None, description="Grade received in the course.")
    acquired_skills: str | list[str] | None = Field(
        None, description="Sentence or list of skills acquired in the course."
    )


class EduProject(BaseModel):
    """
    Information about a project in an educational institution.
    """

    name: str = Field(..., description="Name of the project.")
    description: str | None = Field(
        None, description="Brief description of the project."
    )
    grade: str | None = Field(None, description="Grade or evaluation of the project.")
    acquired_skills: str | list[str] | None = Field(
        None, description="Sentence or list of skills acquired in the course."
    )


class EduGradingSystem(BaseModel):
    """
    Information about a grading system used by an educational institution.
    """

    country: str = Field(..., description="Country where the grading system is used.")
    high: str = Field(..., description="High end of the grading scale.")
    low: str = Field(..., description="Low end of the grading scale.")
    passing_grade: str = Field(..., description="Passing grade in the system.")


class Degree(BaseModel):
    """
    Information about a degree obtained from an educational institution.
    """

    degree: str = Field(..., description="Degree obtained (e.g., BSc, MSc).")
    institution: str = Field(
        ..., description="Institution where the degree was obtained."
    )
    field_of_study: str = Field(
        ..., description="Field of study (e.g., Computer Science)."
    )
    final_evaluation_grade: str | None = Field(
        None, description="Final evaluation or grade."
    )
    honors: str | None = Field(None, description="Honors received, if any.")
    start_year: str | None = Field(
        None, description="Start year of the degree program."
    )
    year_of_completion: str | None = Field(
        None, description="Year of completion of the degree."
    )
    grading_system: EduGradingSystem | None = Field(
        None, description="Grading system used during this degree."
    )
    courses: list[EduCourse] | None = Field(
        None, description="List of courses attended."
    )
    projects: list[EduProject] | None = Field(
        None, description="List of projects (e.g. lab work, internship, thesis)."
    )
    keywords: list[str] | None = Field(
        None, description="List of keywords about the degree."
    )


class WorkPosition(BaseModel):
    """
    Information about a work position in a resume.
    """

    job_title: str = Field(..., description="Job title or position held.")
    company: str | None = Field(
        None, description="Company where the position was held."
    )
    employment_type: str | None = Field(
        None, description="Type of employment (e.g., full-time, contract)."
    )
    employment_period: str | None = Field(
        None, description="Period of employment (e.g., 2020-2022)."
    )
    location: str | None = Field(None, description="Location of the job.")
    industry: str | None = Field(None, description="Industry sector of the company.")
    responsibilities: str | list[str] | None = Field(
        None, description="Description or list of responsibilities."
    )
    acquired_skills: str | list[str] | None = Field(
        None,
        description="Description of list of technical skills or technologies used in this position.",
    )
    achievements: str | list[str] | None = Field(
        None,
        description="Description or list of notable recognitions or quantifiable outcomes achieved in this position.",
    )
    keywords: list[str] | None = Field(
        None, description="List of keywords about this position."
    )


class Project(BaseModel):
    """
    Information about a side project in a resume.
    """

    name: str = Field(..., description="Project name.")
    link: str | None = Field(None, description="Link to the project.")
    platform: str | None = Field(
        None,
        description="Platform where the project is hosted (e.g., GitHub, personal website).",
    )
    description: str | list[str] | None = Field(
        None, description="Description of the projects goal and content."
    )
    acquired_skills: str | list[str] | None = Field(
        None,
        description="Description or list of technical skills or technologies used in this project.",
    )
    achievements: str | list[str] | None = Field(
        None,
        description="Description or list of notable recognitions or quantifiable outcomes achieved by the project.",
    )
    keywords: list[str] | None = Field(
        None, description="List of keywords about this project."
    )


class Achievement(BaseModel):
    """
    Achievement by the candidate.
    """

    title: str = Field(..., description="Title of the achievement.")
    description: str | list[str] | None = Field(
        None, description="Brief description of the achievement."
    )
    relevance: str | list[str] | None = Field(
        None, description="Relevance to professional or academic growth."
    )


class Certification(BaseModel):
    """
    Industrial Certification acquired by the candidate.
    """

    name: str = Field(..., description="Name of the certification.")
    issuing_organization: str = Field(
        ..., description="Organization issuing the certification."
    )
    link: str | None = Field(None, description="Link to verify the certification.")
    description: str | list[str] | None = Field(
        None,
        description="Sentence or bullet point list describing of the certification.",
    )
    acquired_skills: str | list[str] | None = Field(
        None,
        description="Description or list of skills or knowledge acquired through the certification.",
    )
    keywords: list[str] | None = Field(
        None, description="List of keywords about this certification."
    )


class Publication(BaseModel):
    """
    A Publication authored by the candidate.
    """

    title: str = Field(..., description="Title of the publication.")
    authors: str = Field(..., description="Authors of the publication.")
    publisher: str | None = Field(
        None, description="Publisher/Journal of the publication."
    )
    publication_date: str | None = Field(None, description="Publication date.")
    link: str | None = Field(None, description="Link to the publication.")
    description: str | list[str] | None = Field(
        None,
        description="Brief description or bullet point list of the content of the publication.",
    )
    acquired_skills: str | list[str] | None = Field(
        None,
        description="Description or list of technical skills or technologies used in this publication.",
    )
    keywords: list[str] | None = Field(
        None, description="List of keywords about this publication."
    )


# Additional Skills


class Skill(BaseModel):
    name: str = Field(..., description="Additional skill, tool, or technology.")
    proficiency: str | None = Field(None, description="Proficiency level if available.")


class SkillCategory(BaseModel):
    category: str = Field(
        ...,
        description="Type of skill (e.g., Technical Skills, Soft Skills, Languages, Interests).",
    )
    specific_skills: list[Skill] | None = Field(
        ..., description="list of skills, tools, or technologies."
    )


SectionType = List[
    Union[
        Degree,
        WorkPosition,
        Project,
        Achievement,
        Certification,
        SkillCategory,
        Publication,
    ]
]


class Resume(BaseModel):
    """
    The entire resume of one candidate.
    """

    personal_information: PersonalInfo | None = Field(
        None,
        description="Personal information of the candidate, such as name, contact details, and LinkedIn profile.",
    )
    education: list[Degree] | None = Field(
        None, description="The education details of the candidate."
    )
    work_experience: list[WorkPosition] | None = Field(
        None, description="The work experience details of the candidate."
    )
    projects: list[Project] | None = Field(
        None, description="The projects details of the candidate."
    )
    achievements: list[Achievement] | None = Field(
        None, description="The achievements details of the candidate."
    )
    certifications: list[Certification] | None = Field(
        None, description="The certifications details of the candidate."
    )
    additional_skills: list[SkillCategory] | None = Field(
        None, description="The additional skills details of the candidate."
    )
    publications: list[Publication] | None = Field(
        None, description="The publications details of the candidate."
    )

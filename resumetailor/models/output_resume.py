# resumetailor/models/output_resume.py
from pydantic import BaseModel, Field
from typing import List, Union
from resumetailor.models.personal_info import PersonalInfo


# Education


class EduCourseProject(BaseModel):
    """
    Information about a course or a project in an educational institution.
    """

    name: str = Field(..., description="Name of the course or project.")
    grade: str | float | None = Field(
        None, description="Grade received in the course or project (optional)."
    )


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
    final_evaluation_grade: str | float | None = Field(
        None, description="Final evaluation or grade (otional)."
    )
    honors: str | None = Field(None, description="Honors received, if any.")
    start_year: str | None = Field(
        None, description="Start year of the degree program."
    )
    year_of_completion: str | None = Field(
        None, description="Year of completion of the degree (otional)."
    )
    courses: list[EduCourseProject] | None = Field(
        None, description="List of courses attended."
    )
    projects: list[EduCourseProject] | None = Field(
        None, description="List of projects (e.g. lab work, internship, thesis)."
    )


# Work Experience


class WorkPosition(BaseModel):
    """
    Information about a work position in a resume.
    """

    job_title: str = Field(..., description="Job title or position held.")
    company: str = Field(..., description="Company where the position was held.")
    employment_type: str | None = Field(
        None,
        description="Type of employment (e.g., full-time, contract, internship). (optional)",
    )
    employment_period: str = Field(
        ...,
        description="Period of employment (e.g., `2020-2022` or `Aug 2020 - Dec 2020`).",
    )
    location: str | None = Field(None, description="Location of the job. (optional)")
    responsibilities: str | None = Field(
        None, description="Description or list of responsibilities. (optional)"
    )
    acquired_skills: str | None = Field(
        None,
        description="Description of technical skills or technologies used in this position. (optional)",
    )
    achievements: str | None = Field(
        None,
        description="Description of notable recognitions or quantifiable outcomes achieved in this position. (optional)",
    )


# Projects


class Project(BaseModel):
    """
    Information about a side project in a resume.
    """

    name: str = Field(..., description="Project name.")
    link: str | None = Field(None, description="Link to the project. (optional)")
    platform: str | None = Field(
        None,
        description="Platform where the project is hosted (e.g., GitHub, personal website). (optional)",
    )
    description: str | None = Field(
        None,
        description="Description of the project and its goal in one impactful sentence. (optional)",
    )
    acquired_skills: str | None = Field(
        None,
        description="Description of technical skills or technologies used in this project, in one meaningful sentence. (optional)",
    )
    achievements: str | None = Field(
        None,
        description="Single sentence describing notable recognitions or quantifiable outcomes achieved in this project. (optional)",
    )


# Achievememts


class Achievement(BaseModel):
    """
    Achievement by the candidate.
    """

    title: str = Field(..., description="Title/Name of the achievement.")
    description: str = Field(
        ..., description="Impactful description of the achievement in one sentence."
    )
    relevance: str | None = Field(
        None, description="Relevance to professional or academic growth."
    )


# Certifications


class Certification(BaseModel):
    """
    Industrial Certification acquired by the candidate.
    """

    name: str = Field(..., description="Name of the certification.")
    issuing_organization: str = Field(
        ..., description="Organization issuing the certification."
    )
    link: str | None = Field(
        None, description="Link to verify the certification. (optional)"
    )
    description: str | None = Field(
        None,
        description="Impactful sentence describing of the certification. (optional)",
    )
    acquired_skills: str | None = Field(
        None,
        description="Description of skills or knowledge acquired through the certification in a single sentence. (optional)",
    )


# Publications


class Publication(BaseModel):
    """
    A Publication authored by the candidate.
    """

    title: str = Field(..., description="Title of the publication.")
    authors: str = Field(..., description="Authors of the publication.")
    publisher: str | None = Field(
        None, description="Publisher/Journal of the publication."
    )
    publication_year: str = Field(None, description="Publication year in YYYY format.")
    link: str | None = Field(None, description="Link to the publication.")
    description: str | None = Field(
        None,
        description="Brief meaningful description of the content of the publication in a single sentence. (optional)",
    )
    acquired_skills: str | None = Field(
        None,
        description="Single sentence describing technical skills or technologies used in this publication. (optional)",
    )


# Additional Skills


class Skill(BaseModel):
    name: str = Field(..., description="Additional skill, tool, or technology.")
    proficiency: str | None = Field(None, description="Proficiency level. (optional)")


class SkillCategory(BaseModel):
    category: str = Field(
        ...,
        description="Type of skill (e.g., Technical Skills, Soft Skills, Languages, Interests).",
    )
    specific_skills: list[Skill] = Field(
        ..., description="list of skills, tools, or technologies."
    )


class OutputResume(BaseModel):
    """
    The entire resume of one candidate.
    """

    personal_information: PersonalInfo = Field(
        description="Personal information of the candidate, such as name, contact details, and LinkedIn profile.",
    )
    professional_summary: str | list[str] | None = Field(
        None,
        description="A brief summary of the candidate's professional background and career goals.",
    )
    education: list[Degree] = Field(
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

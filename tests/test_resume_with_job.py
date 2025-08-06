# tests/test_job_profile.py
import pytest
from langsmith import testing
import json

from resumetailor.llm import resume_writer
from resumetailor.models import Resume, JobProfile
from tests.utils import score_content

from resumetailor.services.utils import str_to_model, model_to_str

system_message = """
You are an expert reviewer specializing in evaluating AI-refined resumes. Your task is to critically assess the quality of a resume that has been refined by an LLM to better fit a specific job profile. Your review must be thorough, objective, and cover multiple aspects, including but not limited to: job fit, factual faithfulness to the original resume, and the likelihood of the candidate being selected. Pay special attention to any hallucinations or unsupported claims in the refined resume, as accuracy and truthful representation of the candidate are paramount.
"""

prompt = """
**Job Profile (JSON):**
```json
{job_profile}
```

**Full Resume (JSON):**
```json
{full_resume}
```

Please review the following refined resume in the context of the original full resume and the provided job profile. All data is provided in JSON format. Address each of the following aspects in detail:

- Job Fit: How well does the refined resume align with the requirements and expectations of the job profile? Are relevant skills, experiences, and achievements highlighted appropriately?
- Faithfulness: Are all points, claims, and experiences in the refined resume directly supported by information from the original full resume? Identify any hallucinations, exaggerations, or unsupported additions.
- Candidate Representation: Does the refined resume accurately and authentically represent the candidate? Are there any distortions or omissions that misrepresent the candidate's background?
- Likelihood of Success: Based on the refined resume and the job profile, how likely is the candidate to be shortlisted or selected for the position?
- Clarity and Presentation: Is the refined resume well-structured, clear, and professional? Are there any issues with formatting, language, or tone?
- Additional Observations: Note any other strengths, weaknesses, or areas for improvement.

**Refined Resume (JSON):**
```json
{refined_resume}
```

Provide a comprehensive, structured review with specific examples and actionable feedback for each aspect. Assign a score (1-100) to each aspect and conclude the review with a final score (1-100).
"""


@pytest.fixture
def loaded_job_profile(test_data_with_job_dir):
    with open(test_data_with_job_dir / "job_profile.json", "r") as f:
        job_profile_dict = json.load(f)
    return JobProfile(**job_profile_dict)


@pytest.fixture
def loaded_resume(test_data_dir):
    with open(test_data_dir / "full_resume.json", "r") as f:
        resume_dict = json.load(f)
    return Resume(**resume_dict)


@pytest.mark.langsmith
@pytest.mark.resume
def test_resume_with_job(loaded_resume, loaded_job_profile):
    refined_resume = resume_writer.generate(
        thread_id="test",
        resume=loaded_resume,
        job_profile=model_to_str(loaded_job_profile, "json"),
    )
    assert isinstance(
        refined_resume, Resume
    ), "Refined resume is not an instance of the Resume schema"
    score_result = score_content(
        system_message=system_message,
        prompt=prompt,
        job_profile=model_to_str(loaded_job_profile, "json"),
        full_resume=model_to_str(loaded_resume, "json"),
        refined_resume=model_to_str(refined_resume, "json"),
    )
    assert score_result.score > 50

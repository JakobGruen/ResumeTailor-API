# tests/test_job_profile.py
import pytest
from langsmith import testing
import json

from resumetailor.llm import resume_writer
from resumetailor.models import Resume, JobProfile
from tests.utils import score_content

from resumetailor.services.utils import str_to_model, model_to_str

system_message = """
You are an expert reviewer specializing in evaluating AI-refined resumes. Your task is to critically assess the quality of a resume that has been refined by an LLM to be more presentable and impactful, without reference to a specific job profile. In this evaluation, you are also provided with a list of target job titles and specific focus aspects that the refined resume should emphasize. Your review must be thorough, objective, and cover multiple aspects, including but not limited to: overall quality, factual faithfulness to the original resume, and the likelihood of the candidate being attractive to potential employers for the given job titles and focus aspects. Pay special attention to any hallucinations or unsupported claims in the refined resume, as accuracy and truthful representation of the candidate are paramount. Consider how well the refined resume addresses the provided job titles and focus aspects.
"""

prompt = """
**Full Resume (JSON):**
```json
{full_resume}
```

**Job Titles:**
```
{job_titles}
```

**Focus Aspects:**
```
{focus_aspects}
```

Please review the following refined resume in the context of the original full resume, the provided job titles, and the focus aspects. All data is provided in JSON format. Address each of the following aspects in detail:

- Overall Quality: How well does the refined resume present the candidate? Are relevant skills, experiences, and achievements highlighted appropriately for a general audience of employers, especially in relation to the provided job titles and focus aspects?
- Faithfulness: Are all points, claims, and experiences in the refined resume directly supported by information from the original full resume? Identify any hallucinations, exaggerations, or unsupported additions.
- Candidate Representation: Does the refined resume accurately and authentically represent the candidate? Are there any distortions or omissions that misrepresent the candidate's background?
- Attractiveness to Employers: Based on the refined resume, job titles, and focus aspects, how likely is the candidate to attract interest from potential employers in relevant fields?
- Clarity and Presentation: Is the refined resume well-structured, clear, and professional? Are there any issues with formatting, language, or tone?
- Additional Observations: Note any other strengths, weaknesses, or areas for improvement.

**Refined Resume (JSON):**
```json
{refined_resume}
```

Provide a comprehensive, structured review with specific examples and actionable feedback for each aspect. Assign a score (1-100) to each aspect and conclude the review with a final score (1-100).
"""

job_titles = "AI Engineer, Data Scientist, Machine Learning Engineer"
focus_aspects = (
    "independent research, problem-solving skills, interdisciplinary communication"
)


@pytest.fixture
def loaded_resume(test_data_dir):
    with open(test_data_dir / "full_resume.json", "r") as f:
        resume_dict = json.load(f)
    return Resume(**resume_dict)


@pytest.mark.langsmith
@pytest.mark.resume
def test_resume_without_job(loaded_resume):
    refined_resume = resume_writer.generate(
        thread_id="test",
        resume=loaded_resume,
        job_titles=job_titles,
        focus_aspects=focus_aspects,
    )
    assert isinstance(
        refined_resume, Resume
    ), "Refined resume is not an instance of the Resume schema"
    score_result = score_content(
        system_message=system_message,
        prompt=prompt,
        full_resume=model_to_str(loaded_resume, "json"),
        refined_resume=model_to_str(refined_resume, "json"),
        job_titles=job_titles,
        focus_aspects=focus_aspects,
    )
    assert score_result.score > 50

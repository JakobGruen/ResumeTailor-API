# tests/test_job_profile.py
import pytest
from langsmith import testing
from rich import print

from resumetailor.llm import extractor
from resumetailor.models import JobProfile
from resumetailor.services.utils import str_to_model, model_to_str

from tests.utils import score_content


@pytest.fixture
def loaded_job_description(test_data_with_job_dir):
    with open(test_data_with_job_dir / "job_description.txt", "r") as f:
        job_description = f.read()
    return job_description


system_message = """
You are an expert reviewer specializing in evaluating AI-extracted job profiles. Your task is to critically assess the quality of a job profile that has been extracted by an LLM from a job description. Your review must be thorough, objective, and cover multiple aspects, including but not limited to: relevance, completeness, and faithfulness to the original job description. Pay special attention to any hallucinations or unsupported claims in the extracted job profile, as accuracy and truthful representation of the job requirements are paramount.
"""

prompt = """
**Job Description (text):**
```
{job_description}
```

Please review the following extracted job profile in the context of the original job description. Address each of the following aspects in detail:

- Relevance: How well does the extracted job profile capture the key requirements, responsibilities, and qualifications from the job description?
- Completeness: Are all important aspects of the job description represented in the extracted job profile? Are any critical elements missing?
- Faithfulness: Are all points in the extracted job profile directly supported by information from the job description? Identify any hallucinations, exaggerations, or unsupported additions.
- Clarity and Structure: Is the extracted job profile well-organized, clear, and professional?
- Additional Observations: Note any other strengths, weaknesses, or areas for improvement.

**Extracted Job Profile (JSON):**
```json
{job_profile}
```

Provide a comprehensive, structured review with specific examples and actionable feedback for each aspect. Assign a score (1-100) to each aspect and conclude the review with a final score (1-100).
"""


@pytest.mark.langsmith
@pytest.mark.job_profile
def test_job_profile(loaded_job_description):
    job_profile = extractor.extract(
        job_description=loaded_job_description, thread_id="test"
    )
    assert isinstance(
        job_profile, JobProfile
    ), "Return value is not an instance of `JobProfile`."
    score_result = score_content(
        system_message=system_message,
        prompt=prompt,
        job_description=loaded_job_description,
        job_profile=model_to_str(job_profile),
    )
    assert score_result.score > 50

# This file makes this directory a Python package.
from .job_profile import job_profile_prompts
from .resume_compile import resume_compiler_prompts
from .resume_refine_with_job import (
    resume_writer_prompts as resume_writer_with_job_prompts,
)
from .resume_refine_without_job import (
    resume_writer_prompts as resume_writer_without_job_prompts,
)
from .resume_edit import section_editor_prompts
from .cover_letter import cover_letter_prompts

resume_prompts = {
    "writer": {
        "refine_with_job": resume_writer_with_job_prompts,
        "refine_without_job": resume_writer_without_job_prompts,
    },
    "compiler": resume_compiler_prompts,
    "section_editor": section_editor_prompts,
}

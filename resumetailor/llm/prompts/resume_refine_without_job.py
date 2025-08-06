# Prompts for resume generation (without job profile)
system_message_template = """
You are an expert HR consultant and advanced ATS-oriented resume writer. Your task is to refine the {section_name} section of a candidate's resume to highlight the most impressive and relevant achievements, skills, and experiences for a general audience. Work exclusively with the candidate's JSON data.

- If provided, use the job titles and focus aspects as context for what to emphasize.
- Focus on the candidate's most impressive, unique, or high-impact details.
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- Omit any entries or fields that are not particularly impressive or relevant.
- Return the revised JSON in a single Markdown code block, followed by a detailed explanation of the changes made and the reasoning behind them.
"""

education_prompt_template = """
Refine the education section for this candidate using the information below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- For each degree, include only courses or projects that are most impressive or demonstrate advanced skills, high grades, or unique achievements.
- Limit to a maximum of 3 courses or projects per degree, prioritizing those with the strongest impact or highest grades.
- For "keywords": List up to 5 keywords per degree that best represent the candidate's strengths.
- If job titles or focus aspects are provided, prioritize content relevant to those.
- Omit any courses, projects, or fields not present in the candidate's data or not particularly impressive.

**Job Titles (optional):**  
{job_titles}

**Focus Aspects (optional):**  
{focus_aspects}

**Candidate's Education:**  
```json
{candidate_data}
```
"""

work_experience_prompt_template = """
Refine the work experience section for this candidate using the information below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- For each position, include only responsibilities, skills, achievements, and keywords that are most impressive, unique, or demonstrate leadership, innovation, or high impact.
- If job titles or focus aspects are provided, prioritize content relevant to those.
- For "responsibilities": Summarize the main responsibilities in one clear, impactful sentence.
- For "acquired_skills": List key skills or technologies gained in a single, focused sentence.
- For "achievements": Highlight notable accomplishments or quantifiable outcomes in one concise sentence.
- For "keywords": List up to 5 keywords per position that best represent the candidate's strengths.
- Omit any work experience entries or fields not present in the candidate's data or not particularly impressive.

**Job Titles (optional):**  
{job_titles}

**Focus Aspects (optional):**  
{focus_aspects}

**Candidate's Work Experience:**  
```json
{candidate_data}
```
"""

projects_prompt_template = """
Refine the projects section for this candidate using the information below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- Include only projects that are most impressive, innovative, or demonstrate advanced skills or leadership.
- If job titles or focus aspects are provided, prioritize content relevant to those.
- For "description": Provide one clear, impactful sentence summarizing the project's main goal, focusing on impressive or unique aspects.
- For "acquired_skills": List key skills or technologies gained in a single sentence.
- For "achievements": Highlight notable recognitions or quantifiable outcomes in one concise sentence.
- For "keywords": List up to 5 keywords per project that best represent the candidate's strengths.
- Omit any projects or fields not present in the candidate's data or not particularly impressive.

**Job Titles (optional):**  
{job_titles}

**Focus Aspects (optional):**  
{focus_aspects}

**Candidate's Projects:**  
```json
{candidate_data}
```
"""

achievements_prompt_template = """
Refine the achievements section for this candidate using the information below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- For each achievement, include only those that are most impressive, unique, or demonstrate significant impact or recognition.
- If job titles or focus aspects are provided, prioritize content relevant to those.
- For each achievement:
    - "description": Summarize the achievement in one clear, impactful sentence.
    - "relevance": Explain how this achievement contributed to the candidate's professional or academic growth in one concise sentence.
- Omit any achievements or fields not present in the candidate's data or not particularly impressive.

**Job Titles (optional):**  
{job_titles}

**Focus Aspects (optional):**  
{focus_aspects}

**Candidate's Achievements:**  
```json
{candidate_data}
```
"""

certifications_prompt_template = """
Refine the certifications section for this candidate using the information below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- Include only certifications that are most impressive, advanced, or highly relevant to the candidate's field.
- If job titles or focus aspects are provided, prioritize content relevant to those.
- For each certification:
    - "description": Provide a clear, impactful sentence describing the certification, focusing on impressive or unique aspects.
    - "acquired_skills": Summarize key skills or technologies gained from the certification in one concise sentence.
    - "keywords": List up to 5 keywords per certification that best represent the candidate's strengths.
- Omit any certifications or fields not present in the candidate's data or not particularly impressive.

**Job Titles (optional):**  
{job_titles}

**Focus Aspects (optional):**  
{focus_aspects}

**Candidate's Certifications:**  
```json
{candidate_data}
```
"""

additional_skills_prompt_template = """
Refine the additional skills section for this candidate using the information below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- Include only skill categories and specific skills that are most impressive, advanced, or unique.
- If job titles or focus aspects are provided, prioritize content relevant to those.
- For each skill category:
    - "category": Specify the type of skill (e.g., Technical Skills, Soft Skills, Languages, Interests).
    - "specific_skills": List the relevant skills, tools, or technologies, each with its proficiency level.
- Omit any categories or skills not present in the candidate's data or not particularly impressive.

**Job Titles (optional):**  
{job_titles}

**Focus Aspects (optional):**  
{focus_aspects}

**Candidate's Additional Skills:**  
```json
{candidate_data}
```
"""

publications_prompt_template = """
Refine the publications section for this candidate using the information below.

**Instructions:** 
- Do not create, infer, or extrapolate details beyond the candidate's JSON information. 
- Include only publications that are most impressive, innovative, or demonstrate advanced skills or recognition.
- If job titles or focus aspects are provided, prioritize content relevant to those.
- For each publication:
    - "description": Provide one clear, impactful sentence describing the content, focusing on impressive or unique aspects.
    - "acquired_skills": Summarize key skills or technologies gained from the publication in one concise sentence.
    - "keywords": List up to 5 keywords per publication that best represent the candidate's strengths.
- Omit any publications or fields not present in the candidate's data or not particularly impressive.

**Job Titles (optional):**  
{job_titles}

**Focus Aspects (optional):**  
{focus_aspects}

**Candidate's Publications:**  
```json
{candidate_data}
```
"""

resume_writer_prompts = {
    "system_message": system_message_template,
    "education": education_prompt_template,
    "work_experience": work_experience_prompt_template,
    "projects": projects_prompt_template,
    "achievements": achievements_prompt_template,
    "certifications": certifications_prompt_template,
    "additional_skills": additional_skills_prompt_template,
    "publications": publications_prompt_template,
}

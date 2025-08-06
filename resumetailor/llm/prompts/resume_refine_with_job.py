# Prompts for resume generation (with job profile)
system_message_template = """
You are an expert HR consultant and advanced ATS-oriented resume writer. Your task is to refine the {section_name} section of a candidate's resume, ensuring it aligns with the provided job profile. Work exclusively with the candidate's JSON data.

- Use the job profile as essential context.
- Focus only on candidate details directly relevant to the skills, requirements, and qualifications in the job profile.
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- Omit any entries or fields not pertinent to the job profile or lacking relevant data.
- Return the revised JSON in a single block, followed by a brief explanation of the changes made.
"""

education_prompt_template = """
Refine the education section for this candidate using the information and job profile below.

**Instructions:** 
- Do not create, infer, or extrapolate details beyond the candidate's JSON information. 
- For each degree, include only courses or projects highly relevant to the job profile.
- Limit to a maximum of 3 courses or projects per degree, prioritizing those with the strongest relevance and highest grades.
- For "keywords": List up to 5 keywords per degree that are relevant to the job profile.
- Omit any courses, projects, or fields not present in the candidate's data or not relevant to the job profile.

**Job Profile:**  
```json
{job_profile}
```

**Candidate's Education:**  
```json
{candidate_data}
```
"""

work_experience_prompt_template = """
Refine the work experience section for this candidate using the information and job profile below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- For each position, include only responsibilities, skills, achievements, and keywords directly relevant to the job profile.
- If information for "responsibilities", "acquired_skills", "achievements", or "keywords" is misplaced, use all available details for each position to accurately complete these fields.
- For "responsibilities": Summarize the main responsibilities in one clear, impactful sentence.
- For "acquired_skills": List key skills or technologies gained in a single, focused sentence.
- For "achievements": Highlight notable accomplishments or quantifiable outcomes in one concise sentence.
- For "keywords": List up to 5 keywords per position relevant to the job profile.
- Omit any work experience entries or fields not present in the candidate's data or not relevant to the job profile.

**Job Profile:**  
```json
{job_profile}
```

**Candidate's Work Experience:**  
```json
{candidate_data}
```
"""

projects_prompt_template = """
Refine the projects section for this candidate using the information and job profile below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- Include only projects directly relevant to the job profile.
- If information for "description", "acquired_skills", "achievements", or "keywords" is misplaced, use all available details for each project to accurately complete these fields.
- For "description": Provide one clear, impactful sentence summarizing the project's main goal, focusing on elements relevant to the job profile.
- For "acquired_skills": List key skills or technologies gained in a single sentence.
- For "achievements": Highlight notable recognitions or quantifiable outcomes in one concise sentence.
- For "keywords": List up to 5 keywords per project relevant to the job profile.
- Omit any projects or fields not present in the candidate's data or not relevant to the job profile.

**Job Profile:**  
```json
{job_profile}
```

**Candidate's Projects:**  
```json
{candidate_data}
```
"""

achievements_prompt_template = """
Refine the achievements section for this candidate using the information and job profile below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- If information for "description", "relevance", or "keywords" is misplaced, use all available details for each achievement to accurately complete these fields.
- For each achievement:
    - "description": Summarize the achievement in one clear, impactful sentence.
    - "relevance": Explain how this achievement contributed to the candidate's professional or academic growth in one concise sentence.
- Omit any achievements or fields not present in the candidate's data or not relevant to the job profile.

**Job Profile:**  
```json
{job_profile}
```

**Candidate's Achievements:**  
```json
{candidate_data}
```
"""

certifications_prompt_template = """
Refine the certifications section for this candidate using the information and job profile below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- Include only certifications directly relevant to the job profile.
- If information for "description", "acquired_skills", or "keywords" is misplaced, use all available details for each certification to accurately complete these fields.
- For each certification:
    - "description": Provide a clear, impactful sentence describing the certification, focusing on aspects relevant to the job profile.
    - "acquired_skills": Summarize key skills or technologies gained from the certification in one concise sentence.
    - "keywords": List up to 5 keywords per certification relevant to the job profile.
- Omit any certifications or fields not present in the candidate's data or not relevant to the job profile.

**Job Profile:**  
```json
{job_profile}
```

**Candidate's Certifications:**  
```json
{candidate_data}
```
"""

additional_skills_prompt_template = """
Refine the additional skills section for this candidate using the information and job profile below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- Include only skill categories and specific skills directly relevant to the job profile.
- For each skill category:
    - "category": Specify the type of skill (e.g., Technical Skills, Soft Skills, Languages, Interests).
    - "specific_skills": List the relevant skills, tools, or technologies, each with its proficiency level.
- Omit any categories or skills not present in the candidate's data or not relevant to the job profile.

**Job Profile:** 
```json 
{job_profile}
```

**Candidate's Additional Skills:**  
```json
{candidate_data}
```
"""

publications_prompt_template = """
Refine the publications section for this candidate using the information and job profile below.

**Instructions:**  
- Do not create, infer, or extrapolate details beyond the candidate's JSON information.
- Include only publications directly relevant to the job profile.
- If information for "description", "acquired_skills", or "keywords" is misplaced, use all available details for each publication to accurately complete these fields.
- For each publication:
    - "description": Provide one clear, impactful sentence describing the content, focusing on aspects relevant to the job profile.
    - "acquired_skills": Summarize key skills or technologies gained from the publication in one concise sentence.
    - "keywords": List up to 5 keywords per publication relevant to the job profile.
- Omit any publications or fields not present in the candidate's data or not relevant to the job profile.

**Job Profile:**  
```json
{job_profile}
```

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

from cv_engine.services.templateJsonDesc import Personal, SkillsList, ExperienceList, EducationList, ProjectList

SECTIONS = {
    "personal": {
        "schema": Personal,
        "rag_prompt": (
            "Contact information, full name, phone number, email address, "
            "LinkedIn profile URL, GitHub repository links, and professional bio summary."
            "Place 'description' INSIDE the 'info' object, NOT at root level"
            "Extract LinkedIn profile URL from the document and format it properly:"
            "Never include extra fields like 'skills' - that's a separate section"
        ),
        "model_prompt": (
            "DO NOT FORGET ABOUT LinkedIn link and label\n"
            "DO NOT PLACE DESCRIPTION FIELD OUTSIDE INFO, IT SHOULD BE IN IT\n"
            "DO NOT FORGET ABOUT description: str field"
        )
    },
    "skills": {
        "schema": SkillsList,
        "rag_prompt": (
            "Technical stack, programming languages like Python or Java, "
            "software technologies, frameworks, tools, and professional competencies."
        ),
        "model_prompt": (
            ""
        )
    },
    "education": {
        "schema": EducationList,
        "rag_prompt": (
            "Academic history, university degrees, higher education, "
            "graduation dates, GPA, honors, and relevant university courses."
        ),
        "model_prompt": (
            ""
        )
    },
    "experience": {
        "schema": ExperienceList,
        "rag_prompt": (
            "Professional work history, job titles, companies, employment dates, "
            "work responsibilities, professional achievements, and career path."
        ),
        "model_prompt": (
            ""
        )
    },
    "projects": {
        "schema": ProjectList,
        "rag_prompt": (
            "Technical projects, coding portfolio, applications built, "
            "project descriptions, and technologies used in development."
        ),
        "model_prompt": (
            ""
        )
    },
}

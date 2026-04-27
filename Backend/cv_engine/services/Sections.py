from cv_engine.services.templateJsonDesc import Personal, Skills, Education, Projects, Experience, Layout

SECTIONS = {
    "personal": {
        "schema": Personal,
        "prompt": (
            "Contact information, full name, phone number, email address, "
            "LinkedIn profile URL, GitHub repository links, and professional bio summary."
        )
    },
    "skills": {
        "schema": Skills,
        "prompt": (
            "Technical stack, programming languages like Python or Java, "
            "software technologies, frameworks, tools, and professional competencies."
        )
    },
    "education": {
        "schema": Education,
        "prompt": (
            "Academic history, university degrees, higher education, "
            "graduation dates, GPA, honors, and relevant university courses."
        )
    },
    "experience": {
        "schema": Experience,
        "prompt": (
            "Professional work history, job titles, companies, employment dates, "
            "work responsibilities, professional achievements, and career path."
        )
    },
    "projects": {
        "schema": Projects,
        "prompt": (
            "Technical projects, coding portfolio, applications built, "
            "project descriptions, and technologies used in development."
        )
    },
}

from cv_engine.services.templateJsonDesc import Personal, Skills, Education, Projects, Experience, Layout

SECTIONS = {
    "personal": {
        "schema": Personal.model_json_schema(),
        "prompt": (
            "Extract the user's identity and contact information. "
            "Ensure 'telephone_link' follows the 'tel:+48...' format and "
            "all URLs are absolute."
        )
    },
    "skills": {
        "schema": Skills.model_json_schema(),
        "prompt": (
            "Group the candidate's skills into logical categories (e.g., Languages, Programming, Tools). "
            "The 'items' field should be a comma-separated string of skills for that category."
        )
    },
    "education": {
        "schema": Education.model_json_schema(),
        "prompt": (
            "Extract the educational background. For 'highlights', focus on degree-specific "
            "achievements, high GPAs, or relevant certifications mentioned in the text."
        )
    },
    "experience": {
        "schema": Experience.model_json_schema(),
        "prompt": (
            "Extract professional experience. Rewrite the 'highlights' into action-oriented "
            "bullet points starting with strong verbs (e.g., 'Developed', 'Managed', 'Optimized')."
        )
    },
    "projects": {
        "schema": Projects.model_json_schema(),
        "prompt": (
            "Extract technical projects. In the 'tech' field, list the stack used "
            "(e.g., 'Python / Django / Docker'). In 'highlights', focus on the "
            "technical challenges solved."
        )
    },
}

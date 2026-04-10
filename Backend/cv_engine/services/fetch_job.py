mocked_job = {
    "title": "Financial Engineering - Internship",
    "company": "HSBC Service Delivery",
    "location": "Kapelanka 42A, Kraków",
    "work_type": "Hybrid",
    "seniority": "Junior / Internship",
    "salary": {
        "amount": 4500,
        "currency": "PLN",
        "type": "Gross monthly"
    },

    "description": (
        "Role in Global Risk Analytics (GRA) team responsible for development of risk models. "
        "Participate in development of quantitative library. Develop user interfaces using React. "
        "Build REST API for interaction with quantitative models. Work in Agile environment. "
        "Support creation of technical documentation. Collaborate with developers and data analysts."
    ),

    "requirements": {
        "tech_stack": {
            "Python": "regular",
            "React": "regular",
            "English": "B2"
        },
        "education": "M.Sc./B.S. in Physics, Mathematics, Computer Science or related",
        "skills": [
            "REST API",
            "Mathematical analysis",
            "Statistics",
            "Linear algebra",
            "Agile"
        ]
    },

    "search_query": (
        "Python React REST API development quantitative models "
        "mathematical analysis statistics linear algebra Financial Engineering "
        "technical documentation Agile"
    ),

    "metadata": {
        "source": "Just Join IT",
        "published_at": "2026-04-09",
        "application_deadline": "2026-04-12"
    }
}


def fetch_job():
    return mocked_job

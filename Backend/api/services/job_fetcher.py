import json
import urllib.request
from urllib.error import URLError

def fetch_jobs():

    mock_offers = [
        {
            "id": "python-dev-1",
            "title": "Junior Python Developer",
            "company": "Tech Solutions",
            "description": "We are looking for a developer with Python and Django knowledge to develop our backend.",
            "salary": 14000,
            "remote": True
        },
        {
            "id": "java-dev-1",
            "title": "Java Developer",
            "company": "Korp S.A.",
            "description": "Working with Java and Spring; we are looking for someone with 5 years of experience.",
            "salary": 15000,
            "remote": False
        },
        {
            "id": "frontend-dev-1",
            "title": "Frontend React Developer",
            "company": "Studio UI",
            "description": "Proficiency in React, HTML, and CSS.",
            "salary": 8000,
            "remote": True
        },
        {
            "id": "backend-api-1",
            "title": "Backend API Engineer",
            "company": "Super Startup",
            "description": "Building high-performance APIs. Knowledge of Python is highly desirable.",
            "salary": 16000,
            "remote": False
        }
    ]

    return mock_offers

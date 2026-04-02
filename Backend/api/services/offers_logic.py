
import json
import urllib.request
from urllib.error import URLError

def fetch_offers():

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


def is_good_offer(offer):
    title = str(offer.get('title', '')).lower()
    description = str(offer.get('description', '')).lower()
    salary = offer.get('salary', 0)
    remote = bool(offer.get('remote', False))

    positive_keywords = ['python', 'django', 'backend', 'api']
    has_keyword = any(word in title or word in description for word in positive_keywords)
    has_salary = isinstance(salary, (int, float)) and salary >= 12000

    return has_keyword and (has_salary or remote)


def filter_good_offers(offers):
    return [offer for offer in offers if isinstance(offer, dict) and is_good_offer(offer)]

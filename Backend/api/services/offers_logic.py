
import json
import urllib.request
from urllib.error import URLError

def is_good_offer(offer):
    title = str(offer.get('title', '')).lower()
    description = str(offer.get('body') or offer.get('description', '')).lower()
    salary = offer.get('salary', 0)
    remote = bool(offer.get('remote', False))
    required_skills = offer.get('required_skills', [])

    positive_keywords = ['python', 'django', 'backend', 'api', 'java', 'react', 'node', 'devops', 'ml', 'data']
    has_keyword = any(word in title or word in description for word in positive_keywords)
    has_salary = isinstance(salary, (int, float)) and salary >= 12000

    # Jeśli oferta pochodzi z bazy (ma required_skills) — akceptujemy bez filtra salary/remote
    from_db = bool(required_skills)
    return has_keyword and (from_db or has_salary or remote)


def filter_good_offers(offers):
    return [offer for offer in offers if isinstance(offer, dict) and is_good_offer(offer)]


def fetch_offers_from_db(limit: int = 50):
    """Serwisowa funkcja pobierająca oferty z lokalnej bazy PostgreSQL."""
    from api.models import JobOffer
    qs = (
        JobOffer.objects
        .order_by('-scraped_at')
        [:limit]
        .values('slug', 'title', 'body', 'required_skills', 'scraped_at')
    )
    return [dict(o) for o in qs]

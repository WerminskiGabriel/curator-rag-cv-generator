
import json
import urllib.request
from urllib.error import URLError


def _skill_name(skill) -> str:
    if isinstance(skill, dict):
        return skill.get('name', '') or skill.get('value', '')
    return str(skill)


def match_offers_by_skills(user_skills_text: str, limit: int = 20) -> list:
    """
    Returns offers ranked by how many of the user's skills overlap with required_skills.
    user_skills_text: comma/space separated string, e.g. "Python, Django, React"
    """
    from api.models import JobOffer

    raw_tokens = [t.strip().lower() for t in user_skills_text.replace(',', ' ').split() if t.strip()]
    if not raw_tokens:
        return []

    offers = list(
        JobOffer.objects
        .order_by('-scraped_at')
        .values('slug', 'title', 'body', 'required_skills', 'scraped_at')
    )

    scored = []
    for offer in offers:
        offer_skills = [_skill_name(s).lower() for s in (offer.get('required_skills') or [])]
        score = sum(
            1 for token in raw_tokens
            if any(token in skill or skill in token for skill in offer_skills)
        )
        if score > 0:
            scored.append({**offer, '_score': score})

    scored.sort(key=lambda o: o['_score'], reverse=True)

    results = []
    for o in scored[:limit]:
        o.pop('_score', None)
        o['required_skills'] = [_skill_name(s) for s in (o.get('required_skills') or [])]
        results.append(o)

    return results


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

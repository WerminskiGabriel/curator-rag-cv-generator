
# Rodziny umiejętności — jeśli użytkownik zna jedną, liczy jako znajomość pozostałych
SKILL_FAMILIES: dict[str, set[str]] = {
    'sql':        {'mysql', 'postgresql', 'postgres', 'sqlite', 'mssql', 'tsql', 'oracle', 'mariadb', 'plsql'},
    'javascript': {'js', 'typescript', 'ts', 'node', 'nodejs', 'node.js', 'react', 'react.js',
                   'vue', 'vue.js', 'angular', 'next.js', 'nextjs', 'nuxt'},
    'python':     {'django', 'flask', 'fastapi', 'pandas', 'numpy', 'scipy'},
    'java':       {'spring', 'spring boot', 'maven', 'gradle', 'hibernate', 'kotlin'},
    'cloud':      {'aws', 'azure', 'gcp', 'google cloud', 'ec2', 's3', 'lambda'},
    'docker':     {'kubernetes', 'k8s', 'containers', 'helm', 'docker compose'},
    'git':        {'github', 'gitlab', 'bitbucket', 'version control'},
    'linux':      {'unix', 'bash', 'shell', 'cli', 'terminal'},
    'rest':       {'api', 'rest api', 'restful', 'http', 'openapi', 'swagger'},
    'nosql':      {'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'couchdb'},
    'ci/cd':      {'jenkins', 'github actions', 'gitlab ci', 'circleci', 'travis', 'pipeline'},
    'agile':      {'scrum', 'kanban', 'jira', 'confluence', 'sprint'},
    'c':          {'c++', 'c#', 'cpp'},
    'testing':    {'pytest', 'junit', 'selenium', 'cypress', 'jest', 'tdd', 'bdd', 'qa'},
}

# Indeks odwrotny: każda umiejętność → jej rodzina
_SKILL_TO_FAMILY: dict[str, str] = {}
for _family, _members in SKILL_FAMILIES.items():
    for _m in _members:
        _SKILL_TO_FAMILY[_m] = _family
    _SKILL_TO_FAMILY[_family] = _family


def _skill_name(skill) -> str:
    if isinstance(skill, dict):
        return skill.get('name', '') or skill.get('value', '')
    return str(skill)


def _normalize(s: str) -> str:
    return s.strip().lower()


def _skills_match(user_skill: str, required_skill: str) -> bool:
    """Returns True if user_skill covers required_skill (exact, substring, or same family)."""
    u = _normalize(user_skill)
    r = _normalize(required_skill)
    if u == r or u in r or r in u:
        return True
    # Same skill family?
    return _SKILL_TO_FAMILY.get(u) is not None and _SKILL_TO_FAMILY.get(u) == _SKILL_TO_FAMILY.get(r)


def compute_match(user_skills: list[str], required_skills: list[str]) -> dict:
    """
    Returns {'score': int, 'pct': int, 'matched': [...], 'missing': [...]}.
    score  = number of required skills covered by the user.
    pct    = score / len(required_skills) * 100, clamped to 0-100.
    """
    if not required_skills:
        return {'score': 0, 'pct': 0, 'matched': [], 'missing': []}

    matched = []
    missing = []
    for req in required_skills:
        if any(_skills_match(u, req) for u in user_skills):
            matched.append(req)
        else:
            missing.append(req)

    pct = round(len(matched) / len(required_skills) * 100)
    return {'score': len(matched), 'pct': pct, 'matched': matched, 'missing': missing}


def match_offers_by_skills(user_skills_text: str, limit: int = 20) -> list:
    """
    Returns offers ranked by smart skill match score.
    Each offer includes match_pct, matched_skills, missing_skills.
    """
    from api.models import JobOffer

    user_tokens = [t.strip() for t in user_skills_text.replace(',', ' ').split() if t.strip()]
    if not user_tokens:
        return []

    offers = list(
        JobOffer.objects
        .order_by('-scraped_at')
        .values('slug', 'title', 'body', 'required_skills', 'scraped_at')
    )

    scored = []
    for offer in offers:
        req_skills = [_skill_name(s) for s in (offer.get('required_skills') or [])]
        match = compute_match(user_tokens, req_skills)
        if match['score'] > 0:
            scored.append({**offer, '_match': match})

    scored.sort(key=lambda o: o['_match']['pct'], reverse=True)

    results = []
    for o in scored[:limit]:
        match = o.pop('_match')
        o['required_skills'] = [_skill_name(s) for s in (o.get('required_skills') or [])]
        o['match_pct'] = match['pct']
        o['matched_skills'] = match['matched']
        o['missing_skills'] = match['missing']
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

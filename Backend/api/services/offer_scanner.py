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

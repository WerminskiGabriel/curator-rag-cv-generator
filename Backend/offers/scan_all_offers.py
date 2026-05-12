import time
import requests
import re
import html

MAX_RETRY = 3

def request_all_offers(offers_count: int = 100):
    all_offers_url = f"http://justjoin.it/api/candidate-api/offers?from=0&itemsCount={offers_count}&cityRadius=30&currency=pln&orderBy=descending&sortBy=publishedAt&keywordType=any&isPromoted=true"

    headers = {
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-site": "same-origin",
        "sec-fetch-dest": "empty",
        "referer": "https://justjoin.it/",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "pl-PL,pl;q=0.9",
        "priority": "u=1, i"
    }

    for _ in range(MAX_RETRY):
        try:
            r = requests.get(all_offers_url, headers=headers, timeout=10, verify=False)

            if r.status_code == requests.codes.ok:
                return r.json()
        except Exception as error:
            print("Error whilst get offers: ", error)
            time.sleep(5)

def parse_all_offers_link(response):
    offers = response.get("data", []) if isinstance(response, dict) else response
    return [offer["slug"] for offer in offers if "slug" in offer]

def request_specific_offer_data(slug: str):
    offer_url = f"http://justjoin.it/api/candidate-api/offers/{slug}"

    headers = {
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-site": "same-origin",
        "sec-fetch-dest": "empty",
        "referer": "https://justjoin.it/",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "pl-PL,pl;q=0.9",
        "priority": "u=1, i"
    }

    for _ in range(MAX_RETRY):
        try:
            r = requests.get(offer_url, headers=headers, verify=False)

            if r.status_code == requests.codes.ok:
                return r.json()
        except Exception as error:
            print("Error whilst get offers: ", error)
            time.sleep(5)

def parse_specific_offer_data(response):
    required_skills = response.get("requiredSkills", [])
    body_html = response.get("body", "")

    body_text = html.unescape(re.sub(r'<[^>]+>', ' ', body_html).strip())
    # Usunięcie wielokrotnych spacji
    body_text = re.sub(r'\s+', ' ', body_text)

    return {
        "slug": response.get("slug"),
        "title": response.get("title"),
        "required_skills": required_skills,
        "body": body_text
    }

def handler():
    data = request_all_offers(10)

    links = parse_all_offers_link(data)

    resp = request_specific_offer_data(links[0])
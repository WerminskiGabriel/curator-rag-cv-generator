from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..services.offers_logic import filter_good_offers, match_offers_by_skills
from ..services.scraper_service import scrape_and_save_offers
import threading
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_offers_from_db(request):
    """
    Zwraca najnowsze oferty pracy z lokalnej bazy PostgreSQL.

    Query params (opcjonalne):
        limit (int): liczba ofert do zwrócenia (domyślnie 50, max 100)

    Returns:
        200: lista ofert [{slug, title, body, required_skills, scraped_at}, ...]
    """
    from ..models import JobOffer

    try:
        limit = int(request.query_params.get('limit', 50))
    except (ValueError, TypeError):
        limit = 50

    limit = max(1, min(limit, 100))

    offers = (
        JobOffer.objects
        .order_by('-scraped_at')
        [:limit]
        .values('slug', 'title', 'body', 'required_skills', 'scraped_at')
    )

    return Response(list(offers), status=status.HTTP_200_OK)


@api_view(['POST'])
def scrape_offers(request):
    """
    Manualny trigger scrapowania ofert pracy z JustJoin.it
    i zapisu ich do lokalnej bazy danych PostgreSQL.

    Body (opcjonalne):
        count (int): liczba ofert do pobrania (1-100, domyślnie 50)
        background (bool): uruchom w tle i wróć natychmiast (domyślnie false)

    Returns:
        200: statystyki (saved, updated, failed, total_fetched)
        202: jeśli background=true - scrapowanie uruchomione w tle
        400: nieprawidłowe parametry
    """
    count = request.data.get('count', 50)
    run_in_background = request.data.get('background', False)

    if not isinstance(count, int) or count < 1 or count > 100:
        return Response(
            {'error': 'Parametr "count" musi być liczbą całkowitą od 1 do 100.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if run_in_background:
        thread = threading.Thread(
            target=scrape_and_save_offers,
            args=(count,),
            daemon=True,
        )
        thread.start()
        logger.info(f"[API] Scrapowanie uruchomione w tle (count={count}).")
        return Response(
            {'message': f'Scrapowanie uruchomione w tle. Pobieranie {count} ofert.'},
            status=status.HTTP_202_ACCEPTED
        )

    # Synchroniczne wykonanie
    logger.info(f"[API] Uruchamianie scrapowania synchronicznego (count={count}).")
    result = scrape_and_save_offers(count)

    if 'error' in result:
        return Response(result, status=status.HTTP_502_BAD_GATEWAY)

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
def match_offers(request):
    """
    Matches job offers to the user's skills.

    Body:
        skills (str): comma or space separated skill list, e.g. "Python, Django, React"
        limit  (int): max results to return (1-50, default 20)

    Returns:
        200: [{slug, title, required_skills, body, scraped_at}, ...] sorted by match score
        400: missing/invalid skills
    """
    skills_text = request.data.get('skills', '').strip()
    if not skills_text:
        return Response({'error': 'Podaj przynajmniej jedną umiejętność.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        limit = int(request.data.get('limit', 20))
        limit = max(1, min(limit, 50))
    except (ValueError, TypeError):
        limit = 20

    results = match_offers_by_skills(skills_text, limit=limit)
    return Response(results, status=status.HTTP_200_OK)

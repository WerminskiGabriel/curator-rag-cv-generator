import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..services.offers_logic import fetch_offers_from_db, filter_good_offers
from ..services.resume_generation import compile_json_to_pdf
from cv_engine.services.generate_cv_data_llm import generate_cv_data_llm

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_generate_cv(request):
    """
    Generuje spersonalizowane CV dla najlepszych ofert z bazy danych.

    Pipeline:
        1. Pobiera oferty z lokalnej bazy PostgreSQL
        2. Filtruje oferty pasujące do profilu
        3. Dla każdej oferty: RAG (wektorowe CV) + LLM (qwen2.5) → JSON
        4. Kompiluje JSON przez Typst → PDF

    Body (opcjonalne):
        limit (int): liczba ofert do przeskanowania (domyślnie 10, max 50)

    Returns:
        200: lista wygenerowanych CV z ścieżkami do plików
        401: brak autoryzacji
        500: błąd serwera
    """
    try:
        limit = int(request.data.get('limit', 10))
    except (ValueError, TypeError):
        limit = 10
    limit = max(1, min(limit, 50))

    profile_id = request.user.profile.id

    logger.info(f"[CV Gen] Uruchamianie pipeline dla profilu {profile_id}, limit={limit}")

    # 1. Pobierz oferty z bazy
    jobs = fetch_offers_from_db(limit=limit)
    if not jobs:
        return Response(
            {"message": "Brak ofert w bazie. Uruchom najpierw POST /api/offers/scrape/"},
            status=status.HTTP_200_OK
        )

    # 2. Filtruj dobre oferty
    good_offers = filter_good_offers(jobs)
    if not good_offers:
        return Response(
            {"message": "Żadna oferta nie spełnia kryteriów filtrowania.", "total_scanned": len(jobs)},
            status=status.HTTP_200_OK
        )

    logger.info(f"[CV Gen] Znaleziono {len(good_offers)}/{len(jobs)} pasujących ofert.")

    generated_files = []
    errors = []

    for offer in good_offers:
        slug = offer.get('slug', 'unknown')
        title = offer.get('title', 'Unknown')
        logger.info(f"[CV Gen] Generowanie CV dla: {title} ({slug})")

        try:
            # 3. RAG + LLM → spersonalizowany JSON CV
            resume_json = generate_cv_data_llm(profile_id=profile_id, offer=offer)

            # 4. Typst kompilacja → PDF
            pdf_path = compile_json_to_pdf(resume_json, slug=slug)

            generated_files.append({
                "slug": slug,
                "offer_title": title,
                "cv_path": pdf_path,
                "status": "ok"
            })
            logger.info(f"[CV Gen] OK: {pdf_path}")

        except Exception as e:
            logger.error(f"[CV Gen] Błąd dla {slug}: {e}")
            errors.append({"slug": slug, "offer_title": title, "error": str(e)})

    return Response(
        {
            "message": "Pipeline zakończony.",
            "total_scanned": len(jobs),
            "good_offers_found": len(good_offers),
            "generated_count": len(generated_files),
            "error_count": len(errors),
            "generated_cvs": generated_files,
            "errors": errors,
        },
        status=status.HTTP_200_OK
    )

import logging
from offers.scan_all_offers import (
    request_all_offers,
    parse_all_offers_link,
    request_specific_offer_data,
    parse_specific_offer_data,
)
from ..models import JobOffer

logger = logging.getLogger(__name__)


def scrape_and_save_offers(count: int = 50) -> dict:
    """
    Scrapuje oferty z JustJoin.it i zapisuje je do lokalnej bazy PostgreSQL.

    Args:
        count: Liczba ofert do pobrania (domyślnie 50, max 100).

    Returns:
        Słownik ze statystykami: saved, updated, failed, total_fetched.
    """
    count = max(1, min(count, 100))

    # 1. Pobierz listę ofert
    logger.info(f"[Scraper] Pobieranie {count} ofert z JustJoin.it...")
    raw_response = request_all_offers(count)

    if not raw_response:
        logger.error("[Scraper] Brak odpowiedzi z JustJoin.it.")
        return {"error": "Nie udało się pobrać listy ofert z JustJoin.it.", "saved": 0, "updated": 0, "failed": 0, "total_fetched": 0}

    slugs = parse_all_offers_link(raw_response)
    logger.info(f"[Scraper] Znaleziono {len(slugs)} slugów.")

    saved = 0
    updated = 0
    failed = 0

    for slug in slugs:
        try:
            # 2. Pobierz szczegóły każdej oferty
            detail = request_specific_offer_data(slug)
            if not detail:
                logger.warning(f"[Scraper] Brak danych dla slug: {slug}")
                failed += 1
                continue

            # 3. Przetwórz dane
            offer_data = parse_specific_offer_data(detail)

            # 4. Zapisz / zaktualizuj w lokalnej bazie przez Django ORM
            _, created = JobOffer.objects.update_or_create(
                slug=offer_data["slug"],
                defaults={
                    "title": offer_data.get("title", ""),
                    "body": offer_data.get("body", ""),
                    "required_skills": offer_data.get("required_skills", []),
                },
            )

            if created:
                saved += 1
                logger.info(f"[Scraper] Zapisano nową ofertę: {slug}")
            else:
                updated += 1
                logger.info(f"[Scraper] Zaktualizowano ofertę: {slug}")

        except Exception as exc:
            logger.error(f"[Scraper] Błąd przy ofercie {slug}: {exc}")
            failed += 1

    result = {
        "total_fetched": len(slugs),
        "saved": saved,
        "updated": updated,
        "failed": failed,
    }
    logger.info(f"[Scraper] Zakończono. Wyniki: {result}")
    return result

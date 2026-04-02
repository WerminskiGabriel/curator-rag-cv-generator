from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..services.offers_logic import fetch_offers
from ..services.offers_logic import filter_good_offers
from ..services.resume_generation import generate_cv_for_offer


@api_view(['GET', 'POST'])
def auto_generate_cv(request):
    try:
        jobs = fetch_offers()

        good_offers = filter_good_offers(jobs)

        if not good_offers:
            return Response({"message": "No offers found matching your criteria."}, status=status.HTTP_200_OK)

        generated_files = []

        # generate resumes in typst for each good offer
        for offer in good_offers:
            filepath = generate_cv_for_offer(offer)
            generated_files.append({
                "offer_title": offer.get("title"),
                "company": offer.get("company"),
                "cv_path": filepath
            })

        return Response({
            "message": "Success!",
            "total_jobs_scanned": len(jobs),
            "good_jobs_found": len(good_offers),
            "generated_cvs": generated_files
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

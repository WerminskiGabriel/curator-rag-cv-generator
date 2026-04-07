from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def match(request):
    jobs = request.data.get('jobs', [])
    skills = request.data.get('skills', [])

    job_store = {}
    for text, job_id in jobs:
        if True:  # TODO decide to add or not add this to job_store
            job_store[job_id] = text

    return Response({'matched_ids': list(job_store.keys())})


from rest_framework import status
from ..services.offers_logic import filter_good_offers
from ..services.supabase_client import extract_bearer_token, supabase_request


@api_view(['POST'])
def scan_and_save_offers(request):
    jwt_token = extract_bearer_token(request)
    if not jwt_token:
        return Response({'error': 'Missing Bearer JWT token.'}, status=status.HTTP_401_UNAUTHORIZED)

    offers = request.data.get('offers', [])
    table = request.data.get('table', 'offers')

    if not isinstance(offers, list):
        return Response({'error': 'Field "offers" must be a list.'}, status=status.HTTP_400_BAD_REQUEST)
    if not isinstance(table, str) or not table.strip():
        return Response({'error': 'Field "table" must be a non-empty string.'}, status=status.HTTP_400_BAD_REQUEST)

    good_offers = filter_good_offers(offers)
    if not good_offers:
        return Response({'saved_count': 0, 'saved': [], 'skipped_count': len(offers)})

    result = supabase_request('POST', table.strip(), jwt_token, {'select': '*'}, good_offers)
    if not result['ok']:
        return Response({'error': result['error']}, status=result['status'])

    saved = result.get('data') or []
    return Response(
        {
            'saved_count': len(saved),
            'saved': saved,
            'skipped_count': len(offers) - len(good_offers),
        },
        status=result['status'],
    )

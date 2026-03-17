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

from django.conf import settings
from rest_framework import status

def extract_bearer_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    parts = auth_header.split(' ', 1)
    if len(parts) != 2 or parts[0].lower() != 'bearer' or not parts[1].strip():
        return None
    return parts[1].strip()
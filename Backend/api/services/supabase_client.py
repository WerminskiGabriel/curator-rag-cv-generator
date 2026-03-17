import json
from urllib import error, parse, request as urllib_request

from django.conf import settings
from rest_framework import status
from api.services.tools import extract_bearer_token

def to_eq_filter_query(filters):
    params = {}
    if isinstance(filters, dict):
        for key, value in filters.items():
            params[key] = f'eq.{value}'
    return params


def supabase_request(method, table, jwt_token, query_params=None, payload=None):
    base_url = settings.SUPABASE_URL.rstrip('/')
    if not base_url or not settings.SUPABASE_ANON_KEY:
        return {
            'ok': False,
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'error': 'SUPABASE_URL or SUPABASE_ANON_KEY is not configured.',
        }

    endpoint = f"{base_url}/rest/v1/{table}"
    if query_params:
        query_string = parse.urlencode(query_params)
        endpoint = f"{endpoint}?{query_string}"

    headers = {
        'Content-Type': 'application/json',
        'apikey': settings.SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {jwt_token}',
    }

    body = None
    if payload is not None:
        body = json.dumps(payload).encode('utf-8')

    req = urllib_request.Request(endpoint, data=body, method=method, headers=headers)

    try:
        with urllib_request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode('utf-8')
            data = json.loads(raw) if raw else None
            return {'ok': True, 'status': resp.status, 'data': data}
    except error.HTTPError as exc:
        raw = exc.read().decode('utf-8')
        try:
            parsed = json.loads(raw) if raw else {'detail': str(exc)}
        except json.JSONDecodeError:
            parsed = {'detail': raw or str(exc)}
        return {'ok': False, 'status': exc.code, 'error': parsed}
    except error.URLError as exc:
        return {
            'ok': False,
            'status': status.HTTP_502_BAD_GATEWAY,
            'error': {'detail': f'Supabase connection error: {exc.reason}'},
        }

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..services.supabase_client import (
    extract_bearer_token,
    supabase_request,
    to_eq_filter_query,
)


def _require_table(request):
    table = request.data.get('table')
    if not table or not isinstance(table, str):
        return None, Response({'error': 'Field "table" is required.'}, status=status.HTTP_400_BAD_REQUEST)
    return table, None


@api_view(['POST'])
def supabase_select(request):
    jwt_token = extract_bearer_token(request)
    if not jwt_token:
        return Response({'error': 'Missing Bearer JWT token.'}, status=status.HTTP_401_UNAUTHORIZED)

    table, error_response = _require_table(request)
    if error_response:
        return error_response

    columns = request.data.get('columns', '*')
    filters = request.data.get('filters', {})

    params = {'select': columns if isinstance(columns, str) else '*'}
    params.update(to_eq_filter_query(filters))

    result = supabase_request('GET', table, jwt_token, params)
    if not result['ok']:
        return Response({'error': result['error']}, status=result['status'])
    return Response({'data': result['data']}, status=result['status'])


@api_view(['POST'])
def supabase_insert(request):
    jwt_token = extract_bearer_token(request)
    if not jwt_token:
        return Response({'error': 'Missing Bearer JWT token.'}, status=status.HTTP_401_UNAUTHORIZED)

    table, error_response = _require_table(request)
    if error_response:
        return error_response

    values = request.data.get('values')
    if values is None:
        return Response({'error': 'Field "values" is required.'}, status=status.HTTP_400_BAD_REQUEST)

    result = supabase_request('POST', table, jwt_token, {'select': '*'}, values)
    if not result['ok']:
        return Response({'error': result['error']}, status=result['status'])
    return Response({'data': result['data']}, status=result['status'])


@api_view(['POST'])
def supabase_update(request):
    jwt_token = extract_bearer_token(request)
    if not jwt_token:
        return Response({'error': 'Missing Bearer JWT token.'}, status=status.HTTP_401_UNAUTHORIZED)

    table, error_response = _require_table(request)
    if error_response:
        return error_response

    values = request.data.get('values')
    filters = request.data.get('filters', {})
    if values is None:
        return Response({'error': 'Field "values" is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if not isinstance(filters, dict) or not filters:
        return Response({'error': 'Field "filters" must be a non-empty object.'}, status=status.HTTP_400_BAD_REQUEST)

    params = {'select': '*'}
    params.update(to_eq_filter_query(filters))

    result = supabase_request('PATCH', table, jwt_token, params, values)
    if not result['ok']:
        return Response({'error': result['error']}, status=result['status'])
    return Response({'data': result['data']}, status=result['status'])


@api_view(['POST'])
def supabase_delete(request):
    jwt_token = extract_bearer_token(request)
    if not jwt_token:
        return Response({'error': 'Missing Bearer JWT token.'}, status=status.HTTP_401_UNAUTHORIZED)

    table, error_response = _require_table(request)
    if error_response:
        return error_response

    filters = request.data.get('filters', {})
    if not isinstance(filters, dict) or not filters:
        return Response({'error': 'Field "filters" must be a non-empty object.'}, status=status.HTTP_400_BAD_REQUEST)

    params = {'select': '*'}
    params.update(to_eq_filter_query(filters))

    result = supabase_request('DELETE', table, jwt_token, params)
    if not result['ok']:
        return Response({'error': result['error']}, status=result['status'])
    return Response({'data': result['data']}, status=result['status'])

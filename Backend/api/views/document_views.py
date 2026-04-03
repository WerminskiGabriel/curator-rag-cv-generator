from django.http import JsonResponse
from .. import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..services.documents_logic import document_to_dict
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny


# middleware.autologinMiddleware logged user
# receiver in models made sure model for that user is created
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@csrf_exempt
def import_file(request):
    if request.method == "POST":
        models.Documents.objects.create(profile=request.user.profile, file=request.FILES.get('file'))
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def import_txt(request):
    if request.method == "POST":
        models.Documents.objects.create(profile=request.user.profile, text=request.data.get('text'))
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_document_status(request, document_id):
    try:
        doc = models.Documents.objects.get(id=document_id)
        return JsonResponse({
            "id": doc.id,
            "processed": doc.processed,
            "uploadDate": doc.uploadDate,
            "hasText": bool(doc.text),
            "hasFile": bool(doc.file),
        })
    except models.Documents.DoesNotExist:
        return JsonResponse({"error": "Model not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_document(request, document_id):
    if request.method == "DELETE":
        try:
            models.Documents.objects.get(id=document_id).delete()
            return Response(status=status.HTTP_200_OK)
        except models.Documents.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_document_objects(request, document_id):
    if request.method == "GET":
        try:
            doc = models.Documents.objects.get(id=document_id)
            return JsonResponse(document_to_dict(doc))
        except models.Documents.DoesNotExist:
            return JsonResponse({"error": "Model not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_profile_document_objects(request, profile_id):
    if request.method == "GET":
        try:
            profile = models.Profile.objects.get(id=profile_id)
            docs = models.Documents.objects.filter(profile=profile)
            return JsonResponse([document_to_dict(doc) for doc in docs], safe=False, status=status.HTTP_200_OK)
        except models.Profile.DoesNotExist:
            return JsonResponse({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_400_BAD_REQUEST)

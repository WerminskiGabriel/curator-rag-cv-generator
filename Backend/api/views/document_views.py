from django.http import JsonResponse
from .. import models
from rest_framework.response import Response
from rest_framework import status
from ..services.documents_logic import document_to_dict
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_file(request):
    """
    Creates document Model for Profile model,
    Uses @receiver in signals.py to automatically parse files to string and save it to Documents model,
    sets processed to True
    :returns ducument_model_json, status_201_CREATED
    """
    uploadedFile = request.FILES.get('file')

    if not uploadedFile:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    doc = models.Documents.objects.create(profile=request.user.profile, file=uploadedFile)

    return Response(document_to_dict(doc), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_txt(request):
    uploadedText = request.data.get('text')

    if not uploadedText:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    doc = models.Documents.objects.create(profile=request.user.profile, text=uploadedText,
                                          processed=True)
    return Response(document_to_dict(doc), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_status(request, document_id):
    doc = get_object_or_404(models.Documents, id=document_id, profile=request.user.profile)

    return JsonResponse({
        "id": doc.id,
        "processed": doc.processed,
        "uploadDate": doc.uploadDate,
        "hasText": bool(doc.text),
        "hasFile": bool(doc.file),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_document_status(request):
    docs = models.Documents.objects.filter(profile=request.user.profile)
    return JsonResponse(list(docs.values('id', 'processed', 'uploadDate')),
                        safe=False,
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_objects(request, document_id):
    doc = get_object_or_404(models.Documents, id=document_id, profile=request.user.profile)
    return JsonResponse({"id": doc.id,
                         "processed": doc.processed,
                         "uploadDate": doc.uploadDate,
                         "text": doc.text,
                         "filePath": doc.file.url if doc.file else None})


# to delete ?
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_document_objects(request):
    docs = models.Documents.objects.filter(profile=request.user.profile)
    return JsonResponse([{"id": doc.id,
                          "processed": doc.processed,
                          "uploadDate": doc.uploadDate,
                          "text": doc.text,
                          "filePath": doc.file.url if doc.file else None} for doc in docs],
                        safe=False,
                        status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request, documents_id):
    doc = get_object_or_404(models.Documents, id=documents_id, profile=request.user.profile)
    doc.delete()
    return Response(status=status.HTTP_400_BAD_REQUEST)

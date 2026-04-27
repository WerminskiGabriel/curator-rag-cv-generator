from django.http import JsonResponse

from cv_engine.services.generate_save_cv import generate_save_cv
from api.models import Profile
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from cv_engine.services import generate_cv_data_llm
from cv_engine.models import GeneratedResume


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_cv(request, generatedResume_id):
    """
    from GeneratedResume.generatedResume_id creates pdf using existing resume_dict in typst
    :returns pdf_file_path, status_201_CREATED
    """
    typst_file_path = generate_save_cv(generatedResume_id)

    resume_instance = GeneratedResume.objects.get(id=generatedResume_id, user=request.user)

    return Response({"pdf_path": typst_file_path}, status=status.HTTP_201_CREATED)

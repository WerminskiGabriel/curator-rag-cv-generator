from django.http import JsonResponse
from ...api.models import Profile
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..services import fill_cv_data
from ..models import GeneratedResume


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_and_fill_cv_to_model(request, profile_id):
    profile = Profile.objects.get(id=profile_id, user=request.user)

    new_resume_base = fill_cv_data(profile_id)
    # TODO change user to job model
    doc = GeneratedResume.objects.create(user=request.user, generatedJson=new_resume_base)

    return Response({"resume":doc.generatedJson}, status=status.HTTP_201_CREATED)

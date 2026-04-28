from django.http import JsonResponse
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
def generate_and_fill_cv_to_model(request, profile_id):
    """
    verifies the user,
    creates a resume dict for typst generation and uploads it to the GeneratedResume model
    :returns resume dict, status_201_CREATED
    """
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    try:
        new_resume_base = generate_cv_data_llm.generate_cv_data_llm(profile_id)
        # TODO change user to job model
        doc = GeneratedResume.objects.create(user=request.user, generatedJson=new_resume_base)

        return Response( {doc.generatedJson}, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({"error": "resume error", "details": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

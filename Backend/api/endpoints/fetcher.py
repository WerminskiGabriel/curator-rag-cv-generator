from .. import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# middleware.autologinMiddleware logged user
# receiver in models made sure model for that user is created

@api_view(['POST'])
def import_file(request):
    if request.method == "POST":
        models.Documents.objects.create(profile=request.user.profile, file=request.FILES.get('file'))
        return Response(status.HTTP_200_OK)
    return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def import_txt(request):
    if request.method == "POST":
        models.Documents.objects.create(profile=request.user.profile, imported_text=request.data.get('text'))
        return Response(status.HTTP_200_OK)
    return Response(status.HTTP_400_BAD_REQUEST)

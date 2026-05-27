from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Profile

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile
        return Response({
            'username': user.username,
            'email': user.email,
            'profile_id': profile.id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'subtitle': profile.subtitle,
            'bio': profile.bio,
            'phone': profile.phone,
            'github_url': profile.github_url,
            'linkedin_url': profile.linkedin_url,
            'education': profile.education,
            'experience': profile.experience,
            'skills': profile.skills,
        })

    def put(self, request):
        profile = request.user.profile
        data = request.data
        for field in ('first_name', 'last_name', 'subtitle', 'bio', 'phone',
                      'github_url', 'linkedin_url'):
            if field in data:
                setattr(profile, field, data[field])
        for field in ('education', 'experience', 'skills'):
            if field in data:
                setattr(profile, field, data[field])
        profile.save()
        return Response({'status': 'saved'})

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Rejestracja nowego użytkownika.

    Body:
        username (str): unikalna nazwa użytkownika
        password (str): hasło (min. 8 znaków)
        email    (str): adres email (opcjonalny)

    Returns:
        201: {access, refresh, username}
        400: błąd walidacji
    """
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    email = request.data.get('email', '').strip()

    if not username or not password:
        return Response(
            {'error': 'Pola "username" i "password" są wymagane.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 8:
        return Response(
            {'error': 'Hasło musi mieć co najmniej 8 znaków.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': f'Użytkownik "{username}" już istnieje.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(username=username, password=password, email=email)
    Profile.objects.get_or_create(user=user)

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            'username': user.username,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
        status=status.HTTP_201_CREATED
    )

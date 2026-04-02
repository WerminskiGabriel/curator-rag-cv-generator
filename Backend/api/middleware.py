from django.contrib.auth.models import User


class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            user = User.objects.filter(is_superuser=True).first()
            if user:
                request.user = user
        return self.get_response(request)

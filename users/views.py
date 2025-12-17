from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import UserUpdateSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

class SigninView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop("refresh")
        access = response.data.pop("access")
        response.set_cookie(
            "refresh_token",
            str(refresh),
            httponly=True,
            secure=True,
            samesite='None',
            path="/",
            max_age=7 * 24 * 60 * 60,
        )

        # ADDED ACCESS TOKEN COOKIE TOO
        response.set_cookie(
            "access_token",
            str(access),
            httponly=True,
            secure=True,
            samesite='None',
            path="/",
            max_age=7 * 24 * 60 * 60,
        )
        return response

class RefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        request.data["refresh"] = request.COOKIES.get("refresh_token")
        return super().post(request, *args, **kwargs)

class SignoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "logged out"})
        response.delete_cookie("refresh_token")
        response.delete_cookie("access_token") # ADDED THIS LINE TO REMOVE ACCESS TOKEN ON SIGN OUT
        return response

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "is_staff": u.is_staff,
            "is_superuser": u.is_superuser,
            "groups": [g.name for g in u.groups.all()],
            "language": u.language,
            "theme": u.theme,
        })
    
    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        data = request.data

        if User.objects.filter(username=data["username"]).exists():
            return Response({"error": "Username taken"}, status=400)

        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
        )

        return Response({"id": user.id}, status=status.HTTP_201_CREATED)

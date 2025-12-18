from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

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
        # Get refresh token from cookies
        refresh_token = request.COOKIES.get("refresh_token", None)
        if not refresh_token:
            return Response('Missing refresh token', 401)
        request.data["refresh"] = refresh_token

        # Call the parent post method to get the token response
        response = super().post(request, *args, **kwargs)

        # If successful, set the access_token cookie
        response.data.pop('refresh')
        access = response.data.pop('access', None)
        if response.status_code == 200 and access:
            response.set_cookie(
                "access_token",
                str(access),
                httponly=True,
                secure=True,
                samesite="None",
                path="/",
                max_age=7 * 24 * 60 * 60,  # 7 days
            )

        return response

class SignoutView(APIView):

    def post(self, request):
        response = Response(
            {"detail": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )

        # IMPORTANT: attributes must match creation
        response.delete_cookie(
            key="access_token",
            path="/",
            samesite='None'
        )
        response.delete_cookie(
            key="refresh_token",
            path="/",
            samesite='None'
        )

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

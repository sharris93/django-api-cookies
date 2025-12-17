# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "language", "theme"]
        extra_kwargs = {
            "username": {"required": False}, # allow patch to omit username although required on the main model
            "email": {"required": False}, # allow patch to omit email although required on the main model
        }

from django.urls import path
from .views import S3PresignedURLView

urlpatterns = [
    path('signed-upload-url/', S3PresignedURLView.as_view())
]
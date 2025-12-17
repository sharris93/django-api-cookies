from django.urls import path, include

urlpatterns = [
    path("auth/", include('users.urls')),
    path("receipts/", include('receipts.urls')),
    path('s3/', include('s3.urls'))
]

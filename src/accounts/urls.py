from django.urls import path, include

app_name = "accounts"

urlpatterns = [
    path("auth/", include("dj_rest_auth.urls")),
]

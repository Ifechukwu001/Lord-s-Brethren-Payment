from django.urls import path, include

app_name = "register"

urlpatterns = [
    path("register/", include("dj_rest_auth.registration.urls")),
]

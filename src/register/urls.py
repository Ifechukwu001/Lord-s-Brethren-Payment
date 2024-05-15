from django.urls import path

from dj_rest_auth.registration.views import RegisterView

app_name = "register"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
]

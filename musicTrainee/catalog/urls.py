from django.urls import path

from .views import base_view

app_name = "catalog"

urlpatterns = [
    path("", base_view, name="base-page"),
]

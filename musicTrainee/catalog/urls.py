from django.urls import path

from .views import base_view
from .views import CourseView

app_name = "catalog"

urlpatterns = [
    path("", base_view, name="base-page"),
    # path("", CourseView.as_view(), name="base-page"),
]

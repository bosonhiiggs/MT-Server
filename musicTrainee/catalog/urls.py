from django.urls import path

from .views import base_view, CourseModules
from .views import CoursesListView, CourseDetails, CourseModuleDetails

app_name = "catalog"

urlpatterns = [
    path("", base_view, name="base-page"),
    path("catalog/", CoursesListView.as_view(), name="base-page"),
    path("catalog/<str:slug>", CourseDetails.as_view(), name="course-details"),
    path("catalog/<str:slug>/modules/", CourseModules.as_view(), name="course-modules"),
    path("catalog/<str:slug>/modules/<int:pk>", CourseModuleDetails.as_view(), name="course-modules-details"),
]

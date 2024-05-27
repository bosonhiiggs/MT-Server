from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
    AboutMeView,
    LogoutView,
    LoginView,
    CreateUserView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UpdateUserView,
    MyCoursesView,
    MyCourseDetailView,
    MyCourseModulesView,
    MyCourseContentView,
    CatalogCoursesView, CatalogCourseDetailView, MyCreationCoursesView,
)

app_name = 'musicApi'

urlpatterns = [
    # path('hello/', hello_world_view, name='hello_world'),
    path('aboutme/', AboutMeView.as_view(), name='about-me'),
    path('singup/', CreateUserView.as_view(), name='sing-up'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='logout'),
    path('reset-request/', PasswordResetRequestView.as_view(), name='reset-request-password'),
    path('reset-confirm/', PasswordResetConfirmView.as_view(), name='reset-confirm-password'),
    path('update/', UpdateUserView.as_view(), name='update-user'),

    path('mycourses/', MyCoursesView.as_view(), name='my-courses'),
    path('mycourses/<str:slug>/', MyCourseDetailView.as_view(), name='my-course-details'),
    path('mycourses/<str:slug>/modules/', MyCourseModulesView.as_view(), name='my-course-modules'),
    path('mycourses/<str:slug>/modules/<int:pk>/', MyCourseContentView.as_view(), name='my-course-content'),

    path('catalog/', CatalogCoursesView.as_view(), name='catalog'),
    path('catalog/<str:slug>', CatalogCourseDetailView.as_view(), name='catalog-detail'),

    path('mycreations/', MyCreationCoursesView.as_view(), name='my-creations'),
]

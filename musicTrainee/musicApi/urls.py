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
    CatalogCoursesView, CatalogCourseDetailView, MyCreationCoursesView, PaidCourseCreateView, FreeCourseCreateView,
    ModuleCreateView, MyLessonsView, LessonCreatedView, LessonContentCreateView,
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
    path('mycourses/<str:slug>/modules/<int:module_id>/', MyLessonsView.as_view(), name='my-course-modules'),
    path('mycourses/<str:slug>/modules/<int:module_id>/<int:lesson_id>/<int:content_id>/', MyCourseContentView.as_view(), name='my-course-content'),

    path('catalog/', CatalogCoursesView.as_view(), name='catalog'),
    path('catalog/<str:slug>', CatalogCourseDetailView.as_view(), name='catalog-detail'),

    path('mycreations/', MyCreationCoursesView.as_view(), name='my-creations'),
    path('mycreations/create/paid/', PaidCourseCreateView.as_view(), name='course-create-paid'),
    path('mycreations/create/free/', FreeCourseCreateView.as_view(), name='course-create-free'),
    path('mycreations/create/<str:slug>/modules/', ModuleCreateView.as_view(), name='course-create-modules'),
    path('mycreations/create/<str:slug>/modules/<int:module_id>', LessonCreatedView.as_view(), name='course-create-lessons'),
    path('mycreations/create/<str:slug>/modules/<int:module_id>/lessoncreate', LessonContentCreateView.as_view(), name='course-create-content'),
]

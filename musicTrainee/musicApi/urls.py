from django.urls import path

from .views import AboutMeView, LogoutView, LoginView, CreateUserView

app_name = 'musicApi'

urlpatterns = [
    # path('hello/', hello_world_view, name='hello_world'),
    path('aboutme/', AboutMeView.as_view(), name='about-me'),
    path('singup/', CreateUserView.as_view(), name='sing-up'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='logout'),
]

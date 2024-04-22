from django.urls import path

from .views import hello_world_view, ExampleView, LogoutView, LoginView

app_name = 'musicApi'

urlpatterns = [
    path('hello/', hello_world_view, name='hello_world'),
    path('example/', ExampleView.as_view(), name='example'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='logout'),
]

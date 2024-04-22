from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({'Hello': 'World!'})


class ExampleView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, format=None) -> Response:
        content = {
            'user': str(request.user),
            'auth': str(request.auth),
        }
        return Response(content)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, format=None) -> Response:
        logout(request)
        return Response(
            {
                'message': 'You have been logged out.'
            }
        )


class LoginView(APIView):
    def post(self, request: Request, format=None) -> Response:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            # Проверка передачи данных пользователем
            return Response({'error': 'Please provide both username and password'})

        # Возврат объекта пользователя
        user = authenticate(username=username, password=password)

        # Проверка успешность аутентификации
        if user is not None:
            # Вход
            login(request=request, user=user)
            return Response({'success': 'Login in successfully'})
        else:
            return Response({'error': 'Invalid username or password'})

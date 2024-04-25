from django.contrib.auth import logout, authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from rest_framework import generics, status

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.common import generate_reset_code, send_reset_code_email
from accounts.models import PasswordResetRequest, CustomAccount
from accounts.serializers import ProfileInfoSerializer, ProfileLoginSerializer, ProfileCreateSerializer, \
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer


# Представление для создания нового пользователя
class CreateUserView(CreateAPIView):
    serializer_class = ProfileCreateSerializer

    @extend_schema(
        summary='Create a new user',
        examples=[
            OpenApiExample(
                name='Account creation',
                value={
                    'username': 'username',
                    'email': 'useremail',
                    'password': 'password',
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.create(request, *args, **kwargs)
            user = authenticate(username=request.data['username'], password=request.data['password'])
            login(request=request, user=user)
            return Response({'detail': 'User created successfully.'})
        else:
            return Response({'detail': 'Bad request'})


# Представление для получения информации о текущем пользователе
@extend_schema(
    summary='About Me',
    examples=[
        OpenApiExample(
            name='Profile Information',
            value={
                'id': 0,
                'username': 'username',
                'avatar': 'path/to/avatar.png',
                'is_moderator': 'true'
            }
        )
    ]
)
class AboutMeView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileInfoSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# Представление для входа пользователя в систему
class LoginView(APIView):
    serializer_class = ProfileLoginSerializer

    @extend_schema(
        summary='Login to MusicTrainee',
        request=ProfileLoginSerializer,
        examples=[
            OpenApiExample(
                name='Example for Sing In',
                # description='Login to MusicTrainee',
                value={
                    'username': 'username',
                    'password': 'password',
                }
            )
        ]
    )
    def post(self, request: Request, format=None) -> Response:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Please provide both username and password'})

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request=request, user=user)
            return Response({'success': 'Login in successfully'})
        else:
            return Response({'error': 'Invalid username or password'})


# Представление для выхода пользователя из системы
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileInfoSerializer

    @extend_schema(
        summary='Logout from MusicTrainee',
        examples=[
            OpenApiExample(
                name='Example for Logout',
                value={
                    'message': 'You have been logged out.'
                }
            )
        ]
    )
    def get(self, request: Request, format=None) -> Response:
        logout(request)
        return Response(
            {
                'message': 'You have been logged out.'
            }
        )


# Представление для создания запроса на сброс пароля
class PasswordResetRequestView(CreateAPIView):
    serializer_class = PasswordResetRequestSerializer

    @extend_schema(
        request=PasswordResetRequest,
        examples=[
            OpenApiExample(
                name='Example for Password Reset',
                value={
                    'email': 'your_email@example.com',
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            reset_request = PasswordResetRequest.objects.create(
                email=serializer.validated_data['email'],
                reset_code=generate_reset_code()
            )
            # Отправить письмо с инструкцией по сбросу пароля
            send_reset_code_email(reset_request.email, reset_request.reset_code)
            return Response({'message': 'Password reset request sent.'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    @extend_schema(
        request=PasswordResetConfirmSerializer,
        examples=[
            OpenApiExample(
                name='Example for Password Reset Confirm',
                value={
                    'reset_code': 'your_reset_code',
                    'new_password': 'your_new_password',
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            reset_code = serializer.validated_data['reset_code']
            new_password = serializer.validated_data['new_password']

            try:
                reset_request: PasswordResetRequest = PasswordResetRequest.objects.get(reset_code=reset_code)
            except ObjectDoesNotExist:
                return Response({'message': 'Invalid reset code'})

            user: CustomAccount = CustomAccount.objects.get(email=reset_request.email)
            # print(type(new_password))
            print(user)
            user.password = new_password
            user.save()
            reset_request.delete()
            return Response({'message': f'Password reset successful.{new_password}'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


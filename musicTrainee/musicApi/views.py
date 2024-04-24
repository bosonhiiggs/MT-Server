from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from rest_framework import generics

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import ProfileInfoSerializer, ProfileLoginSerializer, ProfileCreateSerializer


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

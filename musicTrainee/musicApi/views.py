from django.contrib.auth import logout, authenticate, login
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from rest_framework import generics, status

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView, \
    get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.common import generate_reset_code, send_reset_code_email
from accounts.models import PasswordResetRequest, CustomAccount
from accounts.serializers import ProfileInfoSerializer, ProfileLoginSerializer, ProfileCreateSerializer, \
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer, UserPatchUpdateSerializer
from catalog.models import Course, Module, Content, Task, TaskSubmission, Lesson, TaskReview
from catalog.serializers import CourseDetailSerializer, ModuleSerializer, ContentSerializer, TextSerializer, \
    FileSerializer, ImageSerializer, VideoSerializer, QuestionSerializer, AnswerSerializer, TaskSerializer, \
    TaskSubmissionSerializer, PaidCourseCreateSerializer, FreeCourseCreateSerializer, ModuleCreateSerializer, \
    LessonSerializer, LessonCreateSerializer, ContentCreateSerializer, TaskReviewSerializer

from slugify import slugify


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
                    'email': 'user_email',
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


class UpdateUserView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPatchUpdateSerializer

    # queryset = CustomAccount.objects.all()

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully.'})
        else:
            return Response({'error': serializer.errors})


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
        summary='Password reset request',
        request=PasswordResetRequestSerializer,
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


# Представление для подтверждения кода для сброса и ввода нового пароля
class PasswordResetConfirmView(APIView):
    serializer_class = PasswordResetConfirmSerializer

    @extend_schema(
        summary='Password reset confirm',
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
            user.password = new_password
            user.save()
            reset_request.delete()
            return Response({'message': f'Password reset successful.{new_password}'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyCoursesView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.request.user
        courses = Course.objects.filter(owner=instance).all()
        serializer = self.get_serializer(courses, many=True)
        response_data = [
            obj
            if obj['approval']
            else {'title': obj['title'], 'message': 'Course is not approval'}
            for obj in serializer.data
        ]
        return Response(response_data)


class MyCourseDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.kwargs.get('slug')
        course = Course.objects.filter(slug=instance).first()
        if course.approval:
            serializer = self.get_serializer(course)
            return Response(serializer.data)
        else:
            return Response({'message': 'Course is not approval'})


class MyCourseModulesView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ModuleSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.kwargs.get('slug')
        course = get_object_or_404(Course.objects.prefetch_related('modules'), slug=instance)
        modules = course.modules.all()
        serializer = self.get_serializer(modules, many=True)
        return Response(serializer.data)


class MyLessonsView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        module_id = kwargs.get('module_id')

        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module.objects.prefetch_related('lessons'), id=module_id, course=course)

        lessons = module.lessons.all()
        serializer = self.get_serializer(lessons, many=True)
        return Response(serializer.data)


class MyCourseContentView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    # queryset = Content.objects.all()
    serializer_class = ContentSerializer

    # lookup_field = 'id'

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        module_id = self.kwargs.get('module_id')
        lesson_id = self.kwargs.get('lesson_id')

        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        lesson = get_object_or_404(Lesson, id=lesson_id, module=module)

        return Content.objects.filter(lesson=lesson)

    def get_object(self):
        queryset = self.get_queryset()
        content_id = self.kwargs.get('content_id')
        return get_object_or_404(queryset, id=content_id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        content_type = instance.item.__class__.__name__

        if content_type == 'Text':
            text_serializer = TextSerializer(instance.item)
            return Response(text_serializer.data)
        elif content_type == 'File':
            file_serializer = FileSerializer(instance.item)
            return Response(file_serializer.data)
        elif content_type == 'Image':
            image_serializer = ImageSerializer(instance.item)
            return Response(image_serializer.data)
        elif content_type == 'Video':
            video_serializer = VideoSerializer(instance.item)
            return Response(video_serializer.data)
        elif content_type == 'Question':
            question_serializer = QuestionSerializer(instance.item)
            return Response(question_serializer.data)
        elif content_type == 'Task':
            task_serializer = TaskSerializer(instance.item)
            response_data = task_serializer.data
            submissions = TaskSubmission.objects.filter(task=instance.item, student=request.user)
            if submissions.exists():
                submission = submissions.first()
                submission_serializer = TaskSubmissionSerializer(submission)
                response_data['submission'] = submission_serializer.data
                reviews = TaskReview.objects.filter(task_submission=submission.id)

                if reviews.exists():
                    review = reviews.first()
                    review_serializer = TaskReviewSerializer(review)
                    response_data['review'] = review_serializer.data
            return Response(response_data)
        return Response(serializer.data)

    @extend_schema(
        summary='Create a content object',
        request={
            'application/json': AnswerSerializer,
            'multipart/form-data': TaskSubmissionSerializer,
        },
        responses={
            200: OpenApiExample(
                name='Correct answer response',
                value={'message': 'Correct answer'}
            ),
        },
        examples=[
            OpenApiExample(
                'Example for post answer',
                value={
                    'answer': 'your_answer_text',  # Пример JSON запроса
                },
                media_type='application/json',
            ),
            OpenApiExample(
                'Example for post task submission',
                value={
                    'file': 'file content here',  # Пример multipart/form-data запроса
                },
                media_type='multipart/form-data',
            ),
        ]
    )
    def post(self, request: Request, *args, **kwargs):
        instance = self.get_object()

        if instance.item.__class__.__name__ == 'Question':
            user_answer = request.data.get('answer')
            correct_answer = instance.item.answer_set.filter(is_true=True).values_list('text', flat=True)
            if user_answer in correct_answer:
                return Response({'message': 'Correct answer'})
            else:
                return Response({'message': 'Incorrect answer'})
        elif instance.item.__class__.__name__ == 'Task':
            file = request.FILES.get('file')
            if not file:
                return Response({'message': 'Please upload a file'})

            try:
                submission = TaskSubmission.objects.create(task=instance.item, student=request.user, file=file)
                submission_serializer = TaskSubmissionSerializer(submission)
                return Response(submission_serializer.data)
            except IntegrityError:
                return Response({'message': 'Task already exists by your user'})
        else:
            return Response({'error': 'This content type dont support answering task'})


@extend_schema(
    summary='Catalog courses list',
)
class CatalogCoursesView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        courses = Course.objects.all()
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)


@extend_schema(
    summary='Catalog detail course',
)
class CatalogCourseDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.kwargs.get('slug')
        course = Course.objects.filter(slug=instance).first()
        serializer = self.get_serializer(course)
        return Response(serializer.data)


class MyCreationCoursesView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        my_creations = Course.objects.filter(creator=request.user).all()
        serializer = self.get_serializer(my_creations, many=True)
        return Response(serializer.data)


class PaidCourseCreateView(CreateAPIView):
    queryset = Course
    serializer_class = PaidCourseCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        title = serializer.validated_data['title']
        slug = slugify(title)
        serializer.save(creator=self.request.user, slug=slug)


class FreeCourseCreateView(CreateAPIView):
    queryset = Course
    serializer_class = FreeCourseCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        title = serializer.validated_data['title']
        slug = slugify(title)
        serializer.save(creator=self.request.user, slug=slug)


class ModuleCreateView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ModuleCreateSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.kwargs.get('slug')
        course = get_object_or_404(Course.objects.prefetch_related('modules'), slug=instance)
        modules = course.modules.all()
        serializer = self.get_serializer(modules, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        instance = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=instance)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LessonCreatedView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer

    def get_module(self):
        slug = self.kwargs.get('slug')
        module_id = self.kwargs.get('module_id')
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        return module

    def get_queryset(self):
        module = self.get_module()
        return Lesson.objects.filter(module=module)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset)
        return obj

    def retrieve(self, request, *args, **kwargs):
        module = self.get_module()
        lessons = self.get_queryset()
        serializer = self.get_serializer(lessons, many=True)
        response = [module.title, serializer.data]
        return Response(response)


class LessonContentCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_module(self):
        slug = self.kwargs.get('slug')
        module_id = self.kwargs.get('module_id')
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        return module

    def create(self, request, *args, **kwargs):
        module = self.get_module()

        lesson_data = request.data.get('lesson')
        lesson_serializer = LessonCreateSerializer(data=lesson_data, context={'module': module})
        if lesson_serializer.is_valid():
            lesson = lesson_serializer.save()
        else:
            return Response(lesson_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        contents_data = request.data.get('contents', [])
        created_contents = []

        for content_data in contents_data:
            content_type = content_data.get('content_type')

            if content_type == 'text':
                content_serializer = TextSerializer(data=content_data.get('text'))
            elif content_type == 'file':
                content_serializer = FileSerializer(data=content_data.get('file'))
            elif content_type == 'image':
                content_serializer = ImageSerializer(data=content_data.get('image'))
            elif content_type == 'video':
                content_serializer = VideoSerializer(data=content_data.get('video'))
            elif content_type == 'question':
                content_serializer = QuestionSerializer(data=content_data.get('question'))
            elif content_type == 'task':
                content_serializer = TaskSerializer(data=content_data.get('task'))
            else:
                raise ValidationError({'error': 'Invalid content type'})

            if content_serializer.is_valid():
                item = content_serializer.save()
                content_type_instance = ContentType.objects.get(model=content_type)
                created_content = Content.objects.create(lesson=lesson, content_type=content_type_instance, object_id=item.id)
                created_contents.append(created_content)
            else:
                return Response(content_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            'lesson': LessonCreateSerializer(lesson).data,
            'content': ContentSerializer(created_contents, many=True).data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class TaskSubmissionsForReviewView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSubmissionSerializer

    def get_queryset(self):
        return TaskSubmission.objects.annotate(
            has_review=Exists(TaskReview.objects.filter(task_submission_id=OuterRef('pk')))
        ).filter(has_review=False)


class TaskSubmissionReviewView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSubmissionSerializer

    def get_object(self):
        task_id = self.kwargs.get('task_id')
        return get_object_or_404(TaskSubmission, pk=task_id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    @extend_schema(
        summary='Submits a task for review',
        request=TaskReviewSerializer,
        examples=[
            OpenApiExample(
                name='Submits a task for review',
                value={
                    "review": {
                        "is_correct": True,
                        "comment": "Optional"
                    }
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        task_submission = self.get_object()

        review_data = request.data.get('review')
        review_data['task_submission'] = task_submission.id

        review_serializer = TaskReviewSerializer(data=review_data)
        if review_serializer.is_valid():
            review = review_serializer.save()
            return Response(review_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(review_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



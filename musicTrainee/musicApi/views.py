from django.contrib.auth import logout, authenticate, login
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, inline_serializer
from rest_framework import generics, status, serializers

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView, \
    get_object_or_404, ListAPIView, GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
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
@extend_schema(
    summary='Create a new user',
    request=ProfileCreateSerializer,
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
class CreateUserView(CreateAPIView):
    serializer_class = ProfileCreateSerializer

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
class LoginView(GenericAPIView):
    serializer_class = ProfileLoginSerializer

    def post(self, request, *args, **kwargs):
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
    request=ProfileInfoSerializer,
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


# Представление обновления личной информации
@extend_schema(
    summary='Update user information',
    request=UserPatchUpdateSerializer,
    examples=[
        OpenApiExample(
            name='Profile Information',
            value={
                "first_name": "string",
                "last_name": "string",
                "email": "user@example.com",
                "avatar": "string",
                "is_moderator": "true"
            }

        )
    ]
)
class UpdateUserView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPatchUpdateSerializer

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
class LogoutView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileInfoSerializer

    def retrieve(self, request, *args, **kwargs) -> Response:
        logout(request)
        return Response(
            {
                'message': 'You have been logged out.'
            }
        )


# Представление для создания запроса на сброс пароля
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
class PasswordResetRequestView(CreateAPIView):
    serializer_class = PasswordResetRequestSerializer

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
class PasswordResetConfirmView(APIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            reset_code = serializer.validated_data['reset_code']
            new_password = serializer.validated_data['new_password']

            try:
                reset_request: PasswordResetRequest = PasswordResetRequest.objects.get(reset_code=reset_code)
            except ObjectDoesNotExist:
                return Response({'message': 'Invalid reset code'})

            user = CustomAccount.objects.get(email=reset_request.email)
            user.password = new_password
            user.save()
            reset_request.delete()
            return Response({'message': f'Password reset successful.{new_password}'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Представление для просмотра курсов пользователя
@extend_schema(
    summary='Get my courses',
    request=CourseDetailSerializer,
    examples=[
        OpenApiExample(
            name='My Courses',
            value={
                "title": "course_title",
                "description": "course_description",
                "target_description": "Target description",
                "logo": "logo_path",
                "price": "course_price",
                "creator_username": "course_creator",
                "created_at_formatted": "DD.MM.YYYY HH:MM",
                "approval": 'true/false',
                "slug": "course_slug"
            }
        )
    ]
)
class MyCoursesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return Course.objects.filter(owner=user).order_by('id')


# Представление для просмотра информиации о курсе
@extend_schema(
    summary='Get course detail information',
    request=CourseDetailSerializer,
    examples=[
        OpenApiExample(
            name='My Course Detail',
            value={
                "title": "course_title",
                "description": "course_description",
                "target_description": "Target description",
                "logo": "logo_path",
                "price": "course_price",
                "creator_username": "course_creator",
                "created_at_formatted": "DD.MM.YYYY HH:MM",
                "approval": 'true/false',
                "slug": "course_slug"
            }
        )
    ]
)
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


# Представление для просмотра модулей курса
@extend_schema(
    summary='Get modules list',
    request=CourseDetailSerializer,
    examples=[
        OpenApiExample(
            name='Course modules',
            value={
                'title': 'module_title',
            }
        )
    ]
)
class MyCourseModulesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ModuleSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=slug)
        return Module.objects.filter(course=course)


# Представление для просмотра уроков модуля
@extend_schema(
    summary='Get lessons from modules list',
    request=LessonSerializer,
    examples=[
        OpenApiExample(
            name='Lessons module',
            value={
                "title": "Module title",
                "contents": [
                    {
                        "id": "content_id",
                        "type_content": "Content title"
                    }
                ]
            }
        )
    ]
)
class MyLessonsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        module_id = self.kwargs.get('module_id')

        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        return Lesson.objects.filter(module=module)


# Представление для просмотра контента урока
@extend_schema(
    summary='Get a content object',
    request=ContentSerializer,
    examples=[
        OpenApiExample(
            name='Content object',
            value={
                "title": "Content title",
                "type_content": "content"
            }
        )
    ]
)
class MyCourseContentView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContentSerializer

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


# Представление для просмотра каталога
@extend_schema(
    summary='Catalog courses list',
    request=CourseDetailSerializer,
    examples=[
        OpenApiExample(
            name='My Course Detail',
            value={
                "title": "course_title",
                "description": "course_description",
                "target_description": "Target description",
                "logo": "logo_path",
                "price": "course_price",
                "creator_username": "course_creator",
                "created_at_formatted": "DD.MM.YYYY HH:MM",
                "approval": 'true/false',
                "slug": "course_slug"
            }
        )
    ]
)
class CatalogCoursesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def get_queryset(self):
        return Course.objects.all()


# Представление для просмотра курса с каталога
@extend_schema(
    summary='Catalog detail course',
    request=CourseDetailSerializer,
    examples=[
        OpenApiExample(
            name='My Course Detail',
            value={
                "title": "course_title",
                "description": "course_description",
                "target_description": "Target description",
                "logo": "logo_path",
                "price": "course_price",
                "creator_username": "course_creator",
                "created_at_formatted": "DD.MM.YYYY HH:MM",
                "approval": 'true/false',
                "slug": "course_slug"
            }
        )
    ]
)
class CatalogCourseDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Course, slug=slug)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# Представление для просмотра курсов, созданных пользователем
@extend_schema(
    summary='Get user created courses',
    request=CourseDetailSerializer,
    examples=[
        OpenApiExample(
            name='My created courses',
            value={
                "title": "course_title",
                "description": "course_description",
                "target_description": "Target description",
                "logo": "logo_path",
                "price": "course_price",
                "creator_username": "course_creator",
                "created_at_formatted": "DD.MM.YYYY HH:MM",
                "approval": "true/false",
                "slug": "course_slug"
            }
        )
    ]
)
class MyCreationCoursesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return Course.objects.filter(creator=user).order_by('id')


# Представление для создания платного курса
@extend_schema(
    summary='Create new paid course',
    request=PaidCourseCreateSerializer,
    examples=[
        OpenApiExample(
            name='New course',
            value={
                "title": "course_title",
                "target_description": "target-description",
                "description": "course_description",
                "price": "course_price",
            }
        )
    ]
)
class PaidCourseCreateView(CreateAPIView):
    queryset = Course
    serializer_class = PaidCourseCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        title = serializer.validated_data['title']
        slug = slugify(title)
        serializer.save(creator=self.request.user, slug=slug)


# Представление для создания бесплатного курса
@extend_schema(
    summary='Create new free course',
    request=FreeCourseCreateSerializer,
    examples=[
        OpenApiExample(
            name='New course',
            value={
                "title": "course_title",
                "target_description": "target-description",
                "description": "course_description",
            }
        )
    ]
)
class FreeCourseCreateView(CreateAPIView):
    queryset = Course
    serializer_class = FreeCourseCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        title = serializer.validated_data['title']
        slug = slugify(title)
        serializer.save(creator=self.request.user, slug=slug)


# Представление для получения и создания новых модулей
@extend_schema(
    summary='Get a modules from course',
    request=ModuleCreateSerializer,
    examples=[
        OpenApiExample(
            name='Get a modules from course',
            value=[
                {
                    "title": "module_title",
                }
            ]
        )
    ]
)
class ModuleCreateView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ModuleCreateSerializer

    def get_course(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Course, slug=slug)

    def get_queryset(self):
        course = self.get_course()
        return Module.objects.filter(course=course)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Create new module',
        request=ModuleCreateSerializer,
        examples=[
            OpenApiExample(
                name='Post new module',
                value={
                    "title": "module_title",
                }

            )
        ]
    )
    def post(self, request, *args, **kwargs):
        course = self.get_course()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Представление для получения созданных уроков в модуле
@extend_schema(
    summary='Get lessons from module',
    request=LessonSerializer,
    examples=[
        OpenApiExample(
            name='Get lessons from module',
            value=[
                "module_title",
                [
                    {
                        "title": "lesson_title",
                        "contents": [
                            {
                                "id": "content_id",
                                "type_content": "content"
                            },
                        ]
                    },
                ]
            ]
        )
    ]
)
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


# Представление для создания уроков состоящий из модулей
@extend_schema(
    summary='Create contents to lesson',
    request=inline_serializer(
        name='LessonContentCreateRequest',
        fields={
            'lesson': LessonCreateSerializer(),
            'contents': serializers.ListField(
                child=inline_serializer(
                    name='ContentItem',
                    fields={
                        'content_type': serializers.ChoiceField(
                            choices=['text', 'file', 'image', 'video', 'question', 'task']),
                        'text': TextSerializer(required=False),
                        'file': FileSerializer(required=False),
                        'image': ImageSerializer(required=False),
                        'video': VideoSerializer(required=False),
                        'question': QuestionSerializer(required=False),
                        'task': TaskSerializer(required=False),
                    }
                )
            )
        }
    ),
    responses={
        201: inline_serializer(
            name='LessonContentCreateResponse',
            fields={
                'lesson': LessonCreateSerializer(),
                'content': ContentSerializer(many=True),
            }
        ),
        400: inline_serializer(
            name='LessonContentCreateErrorResponse',
            fields={
                'error': serializers.CharField()
            }
        ),
    },
)
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
                created_content = Content.objects.create(
                    lesson=lesson,
                    content_type=content_type_instance,
                    object_id=item.id
                )
                created_contents.append(created_content)
            else:
                return Response(content_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            'lesson': LessonCreateSerializer(lesson).data,
            'content': ContentSerializer(created_contents, many=True).data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


# Представление для получения списка домашнего задания на проверку
@extend_schema(
    summary='Get unchecked tasks',
    request=TaskSerializer,
    examples=[
        OpenApiExample(
            name='Get unchecked tasks',
            value={
                "task": "task_id",
                "student": "student_id",
                "file": "path/to/file",
                "submitted_at": ""
            }
        )
    ]
)
class TaskSubmissionsForReviewView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSubmissionSerializer

    def get_queryset(self):
        return TaskSubmission.objects.annotate(
            has_review=Exists(TaskReview.objects.filter(task_submission_id=OuterRef('pk')))
        ).filter(has_review=False)


# Представление для оценки домашнего задания
@extend_schema(
    summary='Get task for review',
    request=TaskReviewSerializer,
    examples=[
        OpenApiExample(
            name='Get task for review',
            value={
                "task": "task_id",
                "student": "student_id",
                "file": "path/to/file.txt",
                "submitted_at": ""
            }
        )
    ]
)
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
                        "is_correct": "true/false",
                        "comment": "optional"
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


# Представление для просмотра заявок на модерацию
@extend_schema(
    summary='Get moderate courses list',
    request=CourseDetailSerializer,
    examples=[
        OpenApiExample(
            name='Get moderate courses list',
            value={
                "title": "course_title",
                "description": "course_description",
                "target_description": "Target description",
                "logo": "logo_path",
                "price": "course_price",
                "creator_username": "course_creator",
                "created_at_formatted": "DD.MM.YYYY HH:MM",
                "approval": "true/false",
                "slug": "course_slug"
            }
        )
    ]
)
class ModerationCoursesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def get_queryset(self):
        user = self.request.user
        print(user.is_moderator)
        if user.is_moderator is True:
            return Course.objects.filter(approval=False).order_by('id')
        else:
            return []


# Представление для просмотра модулей курса и принятия решения
# @extend_schema(
#     summary='Get moderate modules list',
#     request=ModuleSerializer,
#     examples=[
#         OpenApiExample(
#             name='Get moderate modules list',
#             value={
#                 "title": "module_title"
#             }
#         )
#     ]
# )
# class ModerationModulesView(ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ModuleSerializer
#
#     def get_course(self):
#         slug = self.kwargs.get('slug')
#         return Course.objects.get(slug=slug, approval=False)
#
#     def get_queryset(self):
#         user = self.request.user
#         if user.is_moderator is True:
#             course = self.get_course()
#             return Module.objects.filter(course=course).order_by('id')
#         elif user.is_moderator is False:
#             return []
#
#     def patch(self, request, *args, **kwargs):
#         course = self.get_course()
#         serializer_approval_course = CourseDetailSerializer
#

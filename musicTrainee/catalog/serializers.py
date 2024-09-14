from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from catalog.models import Course, Module, Text, File, Image, Video, Question, Answer, Task, Content, TaskSubmission, \
    Lesson, TaskReview, CommentContent, CourseRating


class CourseRatingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отзыва курсов
    """
    class Meta:
        model = CourseRating
        fields = [
            'id',
            'course',
            'user',
            'rating',
            'review',
        ]
        read_only_fields = [
            'id',
            'user',
            'course',
        ]

        def create(self, validated_data):
            validated_data['user'] = self.context['request'].user
            return super().create(validated_data)


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course
    """
    ratings = CourseRatingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    creator_username = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'target_description',
            'logo',
            'price',
            'creator_username',
            'created_at_formatted',
            'approval',
            'slug',
            'average_rating',
            'ratings',
        ]

    @extend_schema_field(serializers.CharField())
    def get_creator_username(self, obj):
        if obj.creator.first_name and obj.creator.last_name:
            return f'{obj.creator.first_name} {obj.creator.last_name}'
        return obj.creator.username

    @extend_schema_field(serializers.DateTimeField())
    def get_created_at_formatted(self, obj):
        return obj.created.strftime('%d.%m.%Y %H:%M')

    @extend_schema_field(serializers.IntegerField())
    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_logo(self, obj):
        request = self.context.get('request')
        try:
            url = obj.logo.url
            if request:
                host: str = request.get_host()
                port: str = request.get_port()
                if settings.IS_DEV_SERVER:
                    if host.endswith(f':{port}'):
                        host = host[:-len(f':{port}')]
                    return f'http://{host}:{port}{url}'
                else:
                    return f'http://{host}:{port}{url}'

            return url
        except ValueError:
            return None


class PaidCourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title',
            'target_description',
            'description',
            'price',
            'logo',
        ]
        extra_kwargs = {
            'logo': {'required': False},
        }


class FreeCourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title',
            'target_description',
            'description',
            'logo',
        ]
        extra_kwargs = {
            'logo': {'required': False},
        }

    def validate(self, data):
        data['price'] = 0
        return data


class TextSerializer(serializers.ModelSerializer):
    # lesson = serializers.SerializerMethodField()
    """
    Сериализатор для модели Text
    """

    class Meta:
        model = Text
        fields = ['title', 'content']


class FileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели File
    """

    class Meta:
        model = File
        fields = ['title', 'file']


class ImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Image
    """

    class Meta:
        model = Image
        fields = ['title', 'file']


class VideoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Video
    """

    class Meta:
        model = Video
        fields = ['title', 'url']


class AnswerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Answer
    """

    class Meta:
        model = Answer
        fields = ['question', 'text', 'is_true']


class QuestionDisplaySerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания Question
    """
    class Meta:
        model = Question
        fields = ['title', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Question
    """
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'title', 'text', 'answers']

    def get_answers(self, question):
        # Получаем ответы к вопросу
        answers = question.answer_set.all()
        serializer = AnswerSerializer(answers, many=True)
        return serializer.data


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Task
    """

    class Meta:
        model = Task
        fields = ['title', 'description', ]


class TaskSubmissionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели TaskSubmission
    """

    class Meta:
        model = TaskSubmission
        fields = ['task', 'student', 'file', 'submitted_at']
        read_only_fields = ['task', 'student', 'submitted_at']


class TaskReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskReview
        fields = ['is_correct', 'comment']
        extra_kwargs = {
            'comment': {'required': False},
        }


class CommentContentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CommentContent
    """
    author = serializers.SerializerMethodField()

    class Meta:
        model = CommentContent
        fields = ['id', 'author', 'text']

    @extend_schema_field(serializers.CharField())
    def get_author(self, obj):
        if obj.author.first_name and obj.author.last_name:
            return f'{obj.author.first_name} {obj.author.last_name}'
        return obj.author.username

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ContentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Content
    """
    item = serializers.SerializerMethodField()
    comments = CommentContentSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = ['item', 'comments']

    def get_item(self, instance) -> dict:
        if instance.content_type.model == 'text':
            serializer = TextSerializer(instance.item)
        elif instance.content_type.model == 'file':
            serializer = FileSerializer(instance.item)
        elif instance.content_type.model == 'image':
            serializer = ImageSerializer(instance.item)
        elif instance.content_type.model == 'video':
            serializer = VideoSerializer(instance.item)
        elif instance.content_type.model == 'question':
            serializer = QuestionSerializer(instance.item)
        elif instance.content_type.model == 'task':
            serializer = TaskSerializer(instance.item)
        else:
            return {"error": "Item is not found"}
        return serializer.data


class ContentCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField()

    class Meta:
        model = Content
        fields = ['content_type', 'object_id']

    def validate_content_type(self, value):
        try:
            return ContentType.objects.get(model=value)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Invalid content type.")


class ModuleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Module
    """
    class Meta:
        model = Module
        fields = ['id', 'title']


class ModuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['title']


class LessonSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'contents']
        # fields = ['id', 'title']

    def get_contents(self, obj) -> list:
        contents_data = []
        for content in obj.contents.all():
            content_data = {'id': content.pk}
            if isinstance(content.item, Text):
                content_data['text_content'] = TextSerializer(content.item).data['title']
            elif isinstance(content.item, File):
                content_data['file_content'] = FileSerializer(content.item).data['title']
            elif isinstance(content.item, Image):
                content_data['image_content'] = ImageSerializer(content.item).data['title']
            elif isinstance(content.item, Video):
                content_data['video_content'] = VideoSerializer(content.item).data['title']
            elif isinstance(content.item, Question):
                content_data['question_content'] = QuestionSerializer(content.item).data['title']
            elif isinstance(content.item, Task):
                content_data['task_content'] = TaskSerializer(content.item).data['title']
            contents_data.append(content_data)
        return contents_data


class PostLessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title']


class LessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['title']

    def create(self, validated_data):
        module = self.context['module']
        return Lesson.objects.create(module=module, **validated_data)

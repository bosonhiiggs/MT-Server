from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from catalog.models import Course, Module, Text, File, Image, Video, Question, Answer, Task, Content


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course
    """
    creator_username = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['title', 'description', 'logo', 'price', 'creator_username', 'created_at_formatted', 'approval']

    @extend_schema_field(serializers.CharField())
    def get_creator_username(self, obj):
        if obj.creator.first_name and obj.creator.last_name:
            return f'{obj.first_name} {obj.last_name}'
        return obj.creator.username

    @extend_schema_field(serializers.DateTimeField())
    def get_created_at_formatted(self, obj):
        return obj.created.strftime('%d.%m.%Y %H:%M')


class TextSerializer(serializers.ModelSerializer):
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
        fields = ['text', 'is_true']


class QuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Question
    """
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['title', 'text', 'answers']

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
        fields = ['title', 'description', 'file']


class ContentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Content
    """
    text_content = TextSerializer(many=True, required=True, allow_null=False)
    file_content = FileSerializer(many=True, required=True, allow_null=False)
    image_content = ImageSerializer(many=True, required=True, allow_null=False)
    video_content = VideoSerializer(many=True, required=True, allow_null=False)
    question_content = QuestionSerializer(many=True, required=True, allow_null=False)
    answer_content = AnswerSerializer(many=True, required=True, allow_null=False)

    contents = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ['text_content', 'file_content', 'image_content', 'video_content', 'question_content', 'answer_content']
        # fields = ['contents']


class ModuleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Module
    """
    contents = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['title', 'contents']

    def get_contents(self, obj):
        contents_data = []
        for content in obj.contents.all():
            content_data = {}
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
            contents_data.append(content_data)
        return contents_data



from django.contrib import admin
from .models import Course, Content, Text, Module, File, Image, Video, Answer, Question, Task, TaskSubmission, ItemBase, \
    Lesson, CommentContent, CourseRating


class QuestionsInline(admin.TabularInline):
    model = Answer


class ModuleInline(admin.TabularInline):
    model = Module


class TextInline(admin.TabularInline):
    model = Text


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'description',
        'price',
        'created',
        'creator',
        'approval',
    ]
    list_filter = [
        'title',
        'price',
        'creator',
    ]
    inlines = [
        ModuleInline,
    ]
    search_fields = [
        'title',
        'description',
    ]
    prepopulated_fields = {'slug': ('title', )}


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'course',
        'title',
    ]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'module',
        'title',
    ]


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = [
        'lesson',
        'content_type',
        'item'
    ]


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'short_content',
    ]

    def short_content(self, obj):
        max_length = 50
        if len(obj.content) > max_length:
            return obj.content[:max_length] + '...'
        else:
            return obj.content


@admin.register(File)
class TextAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'file',
    ]


@admin.register(Image)
class TextAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'file',
    ]


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'url',
    ]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        QuestionsInline,
    ]
    list_display = [
        'title',
        'text',
    ]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = [
        'question',
        'text',
        'is_true'
    ]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'description',
    ]


@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "task",
        "student",
        "file",
        "submitted_at",

    ]


@admin.register(CommentContent)
class CommentContentAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "content",
        "text",
    ]


@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    list_display = [
        "course",
        "user",
        "rating",
        "review",
    ]

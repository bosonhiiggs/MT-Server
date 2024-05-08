from django.contrib import admin
from .models import Course, Content, Text, Module, File, Image, Video, Answer, Question, Task, ItemBase


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


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = [
        'module',
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


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'file',
    ]
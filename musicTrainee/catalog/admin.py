from django.contrib import admin
from .models import Course, Content, Text, Module, File, Image, Video, Answer, Question


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'description', 'price', 'created', 'creator']
    list_filter = ['title', 'price', 'creator']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title', )}


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['course', 'title',]


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['module', 'content_type', 'item']


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ['title', 'content',]


@admin.register(File)
class TextAdmin(admin.ModelAdmin):
    list_display = ['title', 'file',]


@admin.register(Image)
class TextAdmin(admin.ModelAdmin):
    list_display = ['title', 'file',]


@admin.register(Video)
class TextAdmin(admin.ModelAdmin):
    list_display = ['title', 'url',]


class QuestionsInline(admin.TabularInline):
    model = Answer

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'text']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'text']

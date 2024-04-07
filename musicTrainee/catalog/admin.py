from django.contrib import admin
from .models import Course, Content, Text, Module


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


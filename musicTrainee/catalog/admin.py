from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'price', 'create_date', 'owner']
    list_filter = ['title', 'price', 'create_date']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title', )}


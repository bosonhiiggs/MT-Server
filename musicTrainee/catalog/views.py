from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Course, Module


def base_view(request: HttpRequest):
    queryset = {
        "courses": Course.objects.select_related("creator").prefetch_related("owner").all(),
        "modules": Module.objects.select_related("course").all()
    }
    return render(request=request, template_name='catalog/base.html', context=queryset)
    # return HttpResponse("Какой-то каталог")


class CoursesListView(ListView):
    queryset = Course.objects.select_related("creator").all()
    context_object_name = "courses"
    template_name = "catalog/course-catalog.html"


class CourseDetails(DetailView):
    template_name = "catalog/course-details.html"
    queryset = Course.objects.select_related("creator")
    context_object_name = "course"


class CourseModules(ListView):
    def get_queryset(self):
        course_slug = self.request.path.split('/')[2]
        course_choice = Course.objects.filter(slug=course_slug)[0]
        queryset_module = Module.objects.select_related("course").filter(course=course_choice).all()
        queryset = {
            "course": course_choice,
            "modules": queryset_module,
        }
        return queryset

    context_object_name = "objects"
    template_name = "catalog/course-modules.html"


class CourseModuleDetails(DetailView):
    template_name = "catalog/course-modules-details.html"
    queryset = Module.objects.select_related("course")

﻿from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from .models import Course, Module, Content


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
        queryset_modules = Module.objects.select_related("course").filter(course=course_choice).all()

        queryset_modules_content = dict()
        # queryset_content = Content.objects.select_related("module").filter(module=queryset_modules).all()

        # queryset_content = dict()
        for module in queryset_modules:
            content_module = Content.objects.filter(module=module).all()
            queryset_modules_content[module] = content_module
            for content_object in content_module:
                print(content_object.item)

        # print(queryset_modules_content)

        queryset = {
            "course": course_choice,
            "content": queryset_modules_content,
        }
        return queryset

    context_object_name = "objects"
    template_name = "catalog/course-modules.html"


class CourseModuleDetails(DetailView):
    # model = Module
    context_object_name = "course"
    template_name = "catalog/course-modules-details.html"

    # def get_object(self, queryset=None):
    #     course_content_pk = self.request.path.split('/')[4]
    #     queryset = Content.objects.filter(pk=course_content_pk).all()
    #     return queryset

    def get_object(self, queryset=None):
        course = get_object_or_404(Course, slug=self.kwargs["slug"])
        # module = get_object_or_404(Module, pk=self.kwargs["pk"], course=course)
        return course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        content = get_object_or_404(Content, pk=self.kwargs['pk'], module__course=course)
        context['content'] = content
        return context




from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView

from .models import Course, Module


def base_view(request: HttpRequest):
    queryset = {
        "courses": Course.objects.select_related("creator").prefetch_related("owner").all(),
        "modules": Module.objects.select_related("course").all()
    }
    return render(request=request, template_name='catalog/course-catalog.html', context=queryset)
    # return HttpResponse("Какой-то каталог")


class CourseView(ListView):
    queryset = (
        Course.objects.all()
    )

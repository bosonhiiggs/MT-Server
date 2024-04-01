from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def base_view(request: HttpRequest):
    return HttpResponse("Какой-то каталог")

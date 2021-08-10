
from django.contrib import admin
from django.urls import path
from appConverterTool import views

urlpatterns = [
    path('', views.home.as_view()),
]

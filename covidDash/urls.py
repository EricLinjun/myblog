
from django.contrib import admin
from django.urls import path, re_path
from covidDash import views

urlpatterns = [
#    path('admin/', admin.site.urls),
    path('', views.covidDash),
    path('get-data/',views.get_data)
]
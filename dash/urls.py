
from django.contrib import admin
from django.urls import path, re_path
from dash import views

urlpatterns = [
#    path('admin/', admin.site.urls),
    path('dashMain/', views.dashMain),
#    path('login/', views.login),
    path('dataTable/', views.dataTable),
#    path('lookUp/', views.lookUp),
    path('mngTemp/', views.mngTemp),
    path('ajax_addData/', views.ajax_addData),
    path('ajax_deleteData/', views.ajax_deleteData),
    path('ajax_addCtg/', views.ajax_addCtg),
    path('ajax_delCtg/', views.ajax_delCtg),
    path('ajax_editCtg/', views.ajax_editCtg),
    re_path('editData/(\d+)/', views.editData),
]
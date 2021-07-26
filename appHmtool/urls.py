
from django.contrib import admin
from django.urls import path
from appHmtool import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home.as_view()),
    path('get_excel_p1/', views.get_excel_p1.as_view()),
    path('get_excel_p2/', views.get_excel_p2.as_view()),
    
    
]

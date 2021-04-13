
from django.contrib import admin
from django.urls import path, re_path
from appSalesReport import views

urlpatterns = [
#    path('admin/', admin.site.urls),
    path('', views.sales_report),
    path('get-company/', views.get_company),
    path('get-lineChart/', views.get_lineChart)
]
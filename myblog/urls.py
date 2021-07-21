"""myblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app01 import views
from dash import urls as dash_urls
from covidDash import urls as covidDash_urls
from appSalesReport import urls as salesReport_urls
from appHmtool import urls as hmtool_urls


urlpatterns = [
#    path('admin/', admin.site.urls),
    path('', views.home),
    path('project/', views.project),
    path('dash/',include(dash_urls)),
#    path('covid-dash/',include(covidDash_urls)),
    path('sales-report/',include(salesReport_urls)),
    path('hmtool/', include(hmtool_urls)),

    #    path('test/', views.test)
#    path('dash/', include('blog.urls')),
]

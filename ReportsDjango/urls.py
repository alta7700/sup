"""ReportsDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

admin.site.site_header = 'Система учета посещаемости'
admin.site.site_title = 'Администрирование'
admin.site.index_title = 'Интерфейс администратора'

urlpatterns = [
    path('admin_panel/', admin.site.urls),
    path('callback/', include('vk_bot.urls')),
    path('', include('reports.urls')),
    path('tables/', include('tables.urls')),
]

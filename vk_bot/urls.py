from django.urls import path
from . import views


urlpatterns = [
    path('', views.bot_event),
]

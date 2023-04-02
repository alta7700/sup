from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('stud_subj_report', views.stud_subj_report, name='stud_subj_report'),
    path('stud_report', views.stud_report, name='stud_report'),
    path('subj_report', views.subj_report, name='subj_report'),
    path('all_subj_report', views.all_subj_report, name='all_subj_report'),
    path('all_subj_hours_report', views.all_subj_hours_report, name='all_subj_hours_report'),
]

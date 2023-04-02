from django.urls import path
from . import views


urlpatterns = [
    path('', views.TablesListView.as_view(), name='tables'),
    path('<int:pk>/', views.ShowTable.as_view(), name='tables_show'),
    path('notify/<int:pk>/', views.NotifyView.as_view(), name='tables_notify'),
    path('export/<int:pk>/', views.ExportExcelView.as_view(), name='tables_export'),
    path('edit/<int:pk>/', views.UpdateTable.as_view(), name='tables_edit'),
    path('fill/<uuid:pk>/', views.FillTable.as_view(), name='tables_fill'),
    path('fill/success/<uuid:pk>/', views.fill_success, name='tables_fill_success'),
    path('create/', views.NewTable.as_view(), name='tables_create'),
]

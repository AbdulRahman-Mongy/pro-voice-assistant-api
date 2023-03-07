from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateScripts.as_view(), name='scripts'),
    path('list/', views.ListScripts.as_view(), name='list_scripts'),
    path('fork/', views.CopyScripts.as_view(), name='fork_scripts'),
    path('download/<str:pk>/', views.DownloadScripts.as_view(), name='script_download'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListCreateScripts.as_view(), name='scripts'),
    path('list/', views.ListScripts.as_view(), name='list_scripts'),
    path('copy/', views.CopyScripts.as_view(), name='copy_scripts'),
    path('<str:pk>/', views.DownloadScripts.as_view(), name='script_download'),
]

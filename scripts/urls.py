from django.urls import path
from .api import views

urlpatterns = [
    path('', views.ListCreateScripts.as_view(), name='scripts'),
    path('copy/', views.CopyScripts.as_view(), name='copy_scripts'),
]

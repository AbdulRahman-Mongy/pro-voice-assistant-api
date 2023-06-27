from django.urls import path
from . import views

urlpatterns = [
    path('', views.Commands.as_view(), name='commands'),
    path('<int:pk>/', views.CommandDetail.as_view(), name='command-detail'),

    path('<int:id>/fork/', views.ForkCommands.as_view(), name='fork_commands'),
    path('progress/<int:id>/', views.UpdateCommandAfterBuild.as_view(), name='exec'),
]

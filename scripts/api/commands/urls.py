from django.urls import path
from . import views

urlpatterns = [
    path('', views.Commands.as_view(), name='commands'),
    path('<int:pk>/', views.CommandDetail.as_view(), name='command_detail'),
    path('<int:pk>/install/', views.InstallCommand.as_view(), name='install_command'),
    path('<int:id>/fork/', views.ForkCommands.as_view(), name='fork_commands'),
    path('mine/', views.UserCommands.as_view(), name='user_commands'),
    path('public/', views.PublicCommands.as_view(), name='public_commands'),
    path('installed/', views.InstalledCommands.as_view(), name='installed_commands'),
    path('progress/<int:id>/', views.UpdateCommandAfterBuild.as_view(), name='exec'),
]

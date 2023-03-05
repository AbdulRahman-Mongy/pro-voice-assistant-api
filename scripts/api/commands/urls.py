from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateCommands.as_view(), name='commands'),
    path('<int:id>/', views.DetailCommands.as_view(), name='detail_commands'),
    path('list/', views.ListCommands.as_view(), name='list_commands'),
]

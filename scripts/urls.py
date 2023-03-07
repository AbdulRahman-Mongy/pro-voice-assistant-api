from django.urls import path, include

urlpatterns = [
    path('scripts/', include('scripts.api.scripts.urls')),
    path('commands/', include('scripts.api.commands.urls')),
]

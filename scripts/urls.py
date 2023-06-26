from django.urls import path, include

urlpatterns = [
    path('commands/', include('scripts.api.commands.urls')),
]

from django.urls import path, include

urlpatterns = [
    path('', include('scripts.api.urls')),
]

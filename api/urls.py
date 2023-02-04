from django.urls import include, path


urlpatterns = [
    path('users/', include('users.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/', include('dj_rest_auth.urls')),
]

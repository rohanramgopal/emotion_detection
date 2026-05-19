"""
URL configuration for emotion_detection project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home, analysis, dashboard, login_view, register
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls')),
    path('api/', include('emotion_detection.api.urls')), 
    path('', home, name='home'),
     path('analysis.html', analysis, name='analysis'),
    path('dashboard.html', dashboard, name='dashboard'),
    path('login.html', login_view, name='login'),
    path('register.html', register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

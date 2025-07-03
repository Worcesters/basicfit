"""
Configuration des URLs principales du projet BasicFit v2
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

def home_redirect(request):
    """Rediriger vers le tableau de bord si connecté, sinon vers la connexion"""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    return redirect('users:login')

def api_root(request):
    """Vue racine de l'API avec informations"""
    return HttpResponse("""
    <h1>🏋️ BasicFit v2 API</h1>
    <h2>Endpoints disponibles:</h2>
    <ul>
        <li><a href="/api/machines/">🏋️ Machines</a></li>
        <li><a href="/api/users/auth/register/">📝 Inscription</a></li>
        <li><a href="/api/users/auth/login/">🔑 Connexion</a></li>
        <li><a href="/admin/">⚙️ Administration</a></li>
        <li><a href="/api/docs/">📚 Documentation Swagger</a></li>
        <li><a href="/api/redoc/">📖 Documentation ReDoc</a></li>
    </ul>
    <p><a href="/users/login/">🌐 Interface web</a></p>
    """, content_type='text/html')

urlpatterns = [
    # Page d'accueil
    path('', home_redirect, name='home'),

    # Administration Django
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', api_root, name='api_root'),
    path('api/machines/', include('apps.machines.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/workouts/', include('apps.workouts.urls')),
    path('api/core/', include('apps.core.urls')),

    # Interface web utilisateurs
    path('users/', include('apps.users.urls')),
]

# Configuration pour le développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug Toolbar (si installé)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

    # Documentation API
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
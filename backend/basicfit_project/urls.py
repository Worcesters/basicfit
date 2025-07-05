"""
Configuration des URLs principales - API complète pour Android BasicFit
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home_view(request):
    """Page d'accueil avec informations API"""
    return HttpResponse("""
    <h1>💪 BasicFit v2 API - Railway</h1>
    <h2>Serveur Django actif !</h2>
    <ul>
        <li><a href="/admin/">🔧 Administration Django</a></li>
        <li><a href="/api/users/">👥 API Utilisateurs</a></li>
        <li><a href="/api/workouts/">🏋️ API Entraînements</a></li>
        <li><a href="/api/machines/">🏋️ API Machines</a></li>
    </ul>
    <h3>Endpoints Android:</h3>
    <ul>
        <li><strong>POST</strong> /api/users/android/login/ - Connexion</li>
        <li><strong>POST</strong> /api/users/android/register/ - Inscription</li>
        <li><strong>GET</strong> /api/users/android/profile/ - Profil utilisateur</li>
        <li><strong>POST</strong> /api/workouts/sauvegarder/ - Sauvegarder entraînement</li>
    </ul>
    <p>🌐 API déployée sur Railway</p>
    <p>📱 Compatible avec l'application Android BasicFit</p>
    """, content_type='text/html')

urlpatterns = [
    # Page d'accueil
    path('', home_view, name='home'),

    # Administration Django
    path('admin/', admin.site.urls),

    # API REST
    path('api/users/', include('apps.users.urls')),
    path('api/workouts/', include('apps.workouts.urls')),
    path('api/machines/', include('apps.machines.urls')),
    path('api/core/', include('apps.core.urls')),
]

# Servir les fichiers statiques et media en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

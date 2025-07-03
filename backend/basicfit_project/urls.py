"""
Configuration des URLs principales - VERSION BASIQUE pour Railway
Seulement admin Django et page d'accueil
"""
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home_view(request):
    """Page d'accueil basique"""
    return HttpResponse("""
    <h1> BasicFit v2 API - Railway</h1>
    <h2>Serveur Django actif !</h2>
    <ul>
        <li><a href="/admin/"> Administration Django</a></li>
    </ul>
    <p> API déployée sur Railway</p>
    <p> URL: https://basicfit-production.up.railway.app</p>
    """, content_type='text/html')

urlpatterns = [
    # Page d'accueil
    path('', home_view, name='home'),
    
    # Administration Django
    path('admin/', admin.site.urls),
]

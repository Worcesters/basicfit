"""
URLs pour l'API des entraînements
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'seances', views.SeanceEntrainementViewSet, basename='seances')
router.register(r'machines', views.MachineViewSet, basename='machines')

urlpatterns = [
    # API REST avec ViewSets
    path('', include(router.urls)),

    # Endpoints spéciaux
    path('sauvegarder/', views.sauvegarder_seance_simple, name='sauvegarder-seance'),

    # Compatibilité/démo
    path('info/', views.workouts_info, name='workouts-info'),
    path('seances-list/', views.seances_list, name='seances-list'),
]
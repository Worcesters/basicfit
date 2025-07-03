"""
URLs pour l'API core
"""
from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health-check'),

    # App info
    path('info/', views.api_info, name='api-info'),

    # Modes d'entraînement
    path('modes-entrainement/', views.modes_entrainement_list, name='modes-entrainement'),
]
"""
URLs pour l'API des entraînements - Version professionnelle refactorisée
"""
from django.urls import path, include
from . import views, views_refactored, api_seances_effectuees

urlpatterns = [
    # NOUVEAUX ENDPOINTS CALENDRIER SIMPLIFIÉS
    path('', include('apps.workouts.calendar_urls')),
    
    # Endpoints pour les séances d'entraînement (ANCIENS - Compatibilité)
    path('seances/', views_refactored.get_calendar_sessions_professional, name='get_seances'),
    path('seances/sauvegarder/', views_refactored.save_workout_professional, name='save_workout'),

    # Endpoints pour les recommandations - NOUVEAU SYSTÈME BASÉ SUR LA PROGRESSION
    path('recommendations/<int:machine_id>/', views.get_recommendation, name='get_recommendation'),
    path('recommendations/name/<str:machine_name>/', views.get_recommendation_by_name, name='get_recommendation_by_name'),
    path('recommendations/session/', views.get_session_recommendations, name='get_session_recommendations'),
    
    # Nouveaux endpoints pour l'analyse intelligente
    path('recommendations/<str:mode_entrainement>/', views.get_intelligent_recommendations, name='get_intelligent_recommendations'),
    path('progressions/', views.get_user_progressions, name='get_user_progressions'),

    # NOUVEAUX ENDPOINTS SÉANCES EFFECTUÉES (séparées du calendrier)
    path('seances-effectuees/', api_seances_effectuees.get_seances_effectuees, name='get_seances_effectuees'),
    path('progressions-effectuees/', api_seances_effectuees.get_progressions_effectuees, name='get_progressions_effectuees'),
    path('seance-effectuee/', api_seances_effectuees.save_seance_effectuee, name='save_seance_effectuee'),

    # Endpoints d'information
    path('info/', views_refactored.workouts_info, name='workouts_info'),
    path('seances-list/', views_refactored.seances_list, name='seances_list'),
]
"""
URLs pour l'API des entraînements - Version professionnelle refactorisée
"""
from django.urls import path, include
from . import views, views_refactored

urlpatterns = [
    # Endpoints pour les séances d'entraînement
    path('seances/', views_refactored.get_calendar_sessions_professional, name='get_seances'),
    path('seances/sauvegarder/', views_refactored.save_workout_professional, name='save_workout'),

    # Endpoints pour les recommandations - NOUVEAU SYSTÈME BASÉ SUR LA PROGRESSION
    path('recommendations/<int:machine_id>/', views.get_recommendation, name='get_recommendation'),
    path('recommendations/name/<str:machine_name>/', views.get_recommendation_by_name, name='get_recommendation_by_name'),
    path('recommendations/session/', views.get_session_recommendations, name='get_session_recommendations'),

    # Endpoints d'information
    path('info/', views_refactored.workouts_info, name='workouts_info'),
    path('seances-list/', views_refactored.seances_list, name='seances_list'),
]
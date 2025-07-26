"""
URLs pour l'API des entraînements - Version professionnelle refactorisée
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_refactored

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'seances', views_refactored.SeanceEntrainementViewSet, basename='seances')
router.register(r'machines', views_refactored.MachineViewSet, basename='machines')

urlpatterns = [
    # API REST avec ViewSets
    path('', include(router.urls)),

    # ===== ENDPOINTS PRINCIPAUX (Version professionnelle) =====
    
    # Sauvegarde des séances (remplace l'ancien endpoint)
    path('save/', views_refactored.save_workout_professional, name='save-workout-professional'),
    
    # Recommandations (nouveau système)
    path('recommendation/id/<int:machine_id>/', views_refactored.get_recommendation_professional, name='get-recommendation-by-id-pro'),
    path('recommendation/name/<str:machine_name>/', views_refactored.get_recommendation_by_name_professional, name='get-recommendation-by-name-pro'),
    
    # Calendrier (nouveau système)
    path('calendar/', views_refactored.get_calendar_sessions_professional, name='get-calendar-sessions-pro'),
    path('calendar/plan/', views_refactored.plan_session_professional, name='plan-session-pro'),
    
    # ===== ENDPOINTS DE COMPATIBILITÉ (Anciens endpoints maintenus) =====
    
    # Ancien endpoint (maintenu pour compatibilité, mais utilise le nouveau système)
    path('sauvegarder/', views_refactored.save_workout_professional, name='sauvegarder-seance-legacy'),
    path('recommendation/<int:machine_id>/', views_refactored.get_recommendation_professional, name='get-recommendation-by-id-legacy'),
    path('recommendation/<str:machine_name>/', views_refactored.get_recommendation_by_name_professional, name='get-recommendation-legacy'),

    # ===== ENDPOINTS D'INFORMATION =====
    
    path('info/', views_refactored.workouts_info, name='workouts-info'),
    path('seances-list/', views_refactored.seances_list, name='seances-list'),
    
    # ===== ENDPOINTS DE MAINTENANCE =====
    
    # Nettoyage des doublons (à utiliser une seule fois)
    path('cleanup/duplicates/', views_refactored.cleanup_duplicate_sessions, name='cleanup-duplicates'),
]
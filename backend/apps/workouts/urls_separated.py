"""
URLs pour l'API séparée de calendrier et séances effectuées
"""
from django.urls import path
from . import views_separated

urlpatterns = [
    # ===== CALENDRIER (PLANIFICATION) =====
    path('calendrier/', views_separated.list_calendrier, name='list_calendrier'),
    path('calendrier/create/', views_separated.create_seance_planifiee, name='create_seance_planifiee'),
    path('calendrier/import/', views_separated.import_csv_to_calendar, name='import_csv_to_calendar'),
    
    # ===== SÉANCES EFFECTUÉES (HISTORIQUE/ANALYSE) =====
    path('effectuees/', views_separated.list_seances_effectuees, name='list_seances_effectuees'),
    path('effectuees/save/', views_separated.save_seance_effectuee, name='save_seance_effectuee'),
    
    # ===== MIGRATION =====
    path('migrate/', views_separated.migrate_sessions_simples, name='migrate_sessions_simples'),
]
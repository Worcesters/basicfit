"""
URLs spécifiques pour l'API Calendrier BasicFit
Endpoints simplifiés et robustes + Nouveau système CSV
"""
from django.urls import path
from . import calendar_api, api_simple

urlpatterns = [
    # Endpoint principal pour l'historique (compatible Android)
    path('history/', calendar_api.get_workout_history, name='workout_history'),
    
    # Endpoint spécifique calendrier
    path('calendar/', calendar_api.get_calendar_data, name='calendar_data'),
    
    # Sauvegarde simplifiée
    path('save/', calendar_api.save_workout_simple, name='save_workout'),
    
    # Health check
    path('calendar/health/', calendar_api.calendar_health_check, name='calendar_health'),
    
    # NOUVEAU SYSTÈME SIMPLE CSV - 100% synchronisé avec BDD
    path('simple/', api_simple.get_seances_simples, name='get_seances_simples'),
    path('simple/import/', api_simple.import_csv_seances, name='import_csv_seances'), 
    path('simple/delete-all/', api_simple.delete_all_seances, name='delete_all_seances'),
    path('simple/summary/', api_simple.get_calendar_summary, name='get_calendar_summary'),
    path('simple/add/', api_simple.add_seance_simple, name='add_seance_simple'),
]
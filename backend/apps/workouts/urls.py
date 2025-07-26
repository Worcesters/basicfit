"""
URLs pour l'API des entraînements
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import calendar_views

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'seances', views.SeanceEntrainementViewSet, basename='seances')
router.register(r'machines', views.MachineViewSet, basename='machines')

urlpatterns = [
    # API REST avec ViewSets
    path('', include(router.urls)),

    # Endpoints spéciaux
    path('sauvegarder/', views.sauvegarder_seance_simple, name='sauvegarder-seance'),
    path('recommendation/<int:machine_id>/', views.get_recommendation_by_id, name='get-recommendation-by-id'),
    path('recommendation/<str:machine_name>/', views.get_recommendation, name='get-recommendation'),

    # Endpoints calendrier
    path('calendar/', calendar_views.get_calendar_sessions, name='get-calendar-sessions'),
    path('calendar/plan/', calendar_views.plan_session, name='plan-session'),

    # Compatibilité/démo
    path('info/', views.workouts_info, name='workouts-info'),
    path('seances-list/', views.seances_list, name='seances-list'),
]
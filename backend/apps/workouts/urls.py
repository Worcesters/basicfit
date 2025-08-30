"""
URLs principales pour l'API des entraînements BasicFit v2
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'seances', views.SeanceEntrainementViewSet, basename='seances')
router.register(r'machines', views.MachineViewSet)

urlpatterns = [
    # ViewSets via router
    path('', include(router.urls)),

    # Endpoints spécifiques pour Android
    path('sauvegarder/', views.sauvegarder_seance_simple, name='sauvegarder_seance'),
    path('import-csv/', views.import_csv_workouts, name='import_csv_workouts'),
    path('recommandations/<int:machine_id>/', views.get_recommendation, name='get_recommendation'),
    path('recommandations/nom/<str:machine_name>/', views.get_recommendation_by_name, name='get_recommendation_by_name'),
    path('recommandations/session/', views.get_session_recommendations, name='get_session_recommendations'),
    path('recommandations/<str:mode_entrainement>/', views.get_intelligent_recommendations, name='get_intelligent_recommendations'),
    path('progressions/', views.get_user_progressions, name='get_user_progressions'),

    # Vues de compatibilité
    path('info/', views.workouts_info, name='workouts_info'),
    path('list/', views.seances_list, name='seances_list'),
]
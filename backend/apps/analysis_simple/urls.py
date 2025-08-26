"""
URLs pour analyse intelligente simplifiée
"""
from django.urls import path
from . import views

app_name = 'analysis_simple'

urlpatterns = [
    # Analyse
    path('progressions/', views.get_progressions, name='progressions'),
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('performance/', views.get_performance_analysis, name='performance'),
]
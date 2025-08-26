"""
URLs pour sessions simplifiées
"""
from django.urls import path
from . import views

app_name = 'sessions_simple'

urlpatterns = [
    # Sessions
    path('', views.list_sessions, name='list_sessions'),
    path('save/', views.save_session, name='save_session'),
    path('clear/', views.delete_all_sessions, name='delete_all_sessions'),
    path('stats/', views.get_statistics, name='get_statistics'),
    
    # Import
    path('import/', views.import_csv, name='import_csv'),
]
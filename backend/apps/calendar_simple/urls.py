"""
URLs pour calendrier simplifié
"""
from django.urls import path
from . import views

app_name = 'calendar_simple'

urlpatterns = [
    # Calendrier
    path('', views.get_calendar_data, name='calendar_data'),
    path('overview/', views.get_calendar_overview, name='calendar_overview'),
    path('day/<str:date_str>/', views.get_day_details, name='day_details'),
]
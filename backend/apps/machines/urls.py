"""
URLs pour l'API des machines
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.machines_list, name='machines-list'),
    path('<int:pk>/', views.machine_detail, name='machine-detail'),
    path('groupes-musculaires/', views.groupes_musculaires_list, name='groupes-musculaires'),
    path('categories/', views.categories_machines_list, name='categories'),
]
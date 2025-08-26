"""
URLs propres pour l'API des entraînements - Version 100% BDD
Utilise uniquement les modèles unifiés : ExerciceEffectueUnifie et CalendrierEntrainementSimple
"""
from django.urls import path
from . import api_clean

urlpatterns = [
    # === IMPORT CSV CALENDRIER ===
    path('import-csv/', api_clean.import_csv_calendar, name='import_csv_calendar'),

    # === EXERCICES EFFECTUÉS ===
    path('exercice/', api_clean.enregistrer_exercice, name='enregistrer_exercice'),
    path('exercices/', api_clean.get_exercices_utilisateur, name='get_exercices_utilisateur'),

    # === HISTORIQUE ET STATISTIQUES ===
    path('historique/', api_clean.get_historique_utilisateur, name='get_historique_utilisateur'),
    path('stats/', api_clean.get_statistiques_utilisateur, name='get_statistiques_utilisateur'),

    # === RECOMMANDATIONS IA ===
    path('recommandations/', api_clean.get_recommandations_ia, name='get_recommandations_ia'),
    path('recommandations/machine/<int:machine_id>/', api_clean.get_recommandations_machine, name='get_recommandations_machine'),

    # === CALENDRIER ===
    path('calendrier/', api_clean.get_calendrier_utilisateur, name='get_calendrier_utilisateur'),
    path('calendrier/<str:date>/', api_clean.get_calendrier_date, name='get_calendrier_date'),

    # === GESTION DES DONNÉES ===
    path('nettoyer/', api_clean.nettoyer_donnees_utilisateur, name='nettoyer_donnees_utilisateur'),
    path('export/', api_clean.exporter_donnees_utilisateur, name='exporter_donnees_utilisateur'),
]

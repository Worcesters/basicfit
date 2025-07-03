"""
Vues simplifiées pour l'API core (modes d'entraînement, health check, etc.)
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection

from .models import ModeEntrainement


@api_view(['GET'])
@permission_classes([AllowAny])
def modes_entrainement_list(request):
    """Liste des modes d'entraînement"""
    try:
        modes = ModeEntrainement.objects.filter(is_active=True).order_by('nom')
        data = []
        for mode in modes:
            data.append({
                'id': mode.id,
                'nom': mode.nom,
                'description': mode.description,
                'series_defaut': mode.series_defaut,
                'repetitions_min': mode.repetitions_min,
                'repetitions_max': mode.repetitions_max,
                'temps_repos_defaut': mode.temps_repos_defaut,
                'progression_poids': float(mode.progression_poids),
                'couleur': mode.couleur,
                'icone': mode.icone
            })
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Endpoint de vérification de santé de l'API"""
    try:
        # Tester la connexion à la base de données
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        db_status = "OK"
    except Exception as e:
        db_status = f"Erreur: {str(e)}"

    return Response({
        'status': 'OK',
        'database': db_status,
        'api_version': '1.0.0',
        'service': 'BasicFit API'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """Informations générales sur l'API"""
    return Response({
        'name': 'BasicFit API',
        'version': '1.0.0',
        'description': 'API REST pour l\'application de suivi de performances en salle de sport',
        'endpoints': {
            'auth': '/api/auth/',
            'users': '/api/users/',
            'machines': '/api/machines/',
            'workouts': '/api/workouts/',
            'core': '/api/core/',
            'docs': '/api/docs/',
            'admin': '/admin/'
        },
        'features': [
            'Authentification JWT',
            'Gestion des utilisateurs',
            'Catalogue de machines',
            'Suivi des séances',
            'Calcul 1RM automatique',
            'Progression intelligente',
            'Modes d\'entraînement'
        ]
    })
"""
Vues simplifiées pour les recommandations avec gestion d'authentification robuste
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from .simple_recommendation import get_simple_recommendation, get_simple_recommendation_by_name

logger = logging.getLogger(__name__)

def handle_auth_error(request):
    """Gère les erreurs d'authentification et force la déconnexion si nécessaire"""
    try:
        user = request.user
        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Utilisateur non authentifié',
                'force_logout': True
            }, status=status.HTTP_401_UNAUTHORIZED)
        return None
    except Exception as e:
        logger.error(f"Erreur vérification authentification: {e}")
        return Response({
            'success': False,
            'error': 'Erreur authentification',
            'force_logout': True
        }, status=status.HTTP_401_UNAUTHORIZED)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendation_simple(request, machine_id):
    """
    Endpoint simplifié pour obtenir une recommandation par ID de machine
    """
    try:
        # Vérifier l'authentification
        auth_error = handle_auth_error(request)
        if auth_error:
            return auth_error
        
        logger.info(f"Demande recommandation pour machine {machine_id} par {request.user.email}")
        
        # Obtenir la recommandation
        result = get_simple_recommendation(request.user, machine_id)
        
        if result['success']:
            return Response(result['data'], status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Erreur endpoint recommandation: {e}")
        return Response({
            'success': False,
            'error': 'Erreur interne du serveur'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendation_by_name_simple(request, machine_name):
    """
    Endpoint simplifié pour obtenir une recommandation par nom de machine
    """
    try:
        # Vérifier l'authentification
        auth_error = handle_auth_error(request)
        if auth_error:
            return auth_error
        
        logger.info(f"Demande recommandation pour machine '{machine_name}' par {request.user.email}")
        
        # Obtenir la recommandation
        result = get_simple_recommendation_by_name(request.user, machine_name)
        
        if result['success']:
            return Response(result['data'], status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Erreur endpoint recommandation par nom: {e}")
        return Response({
            'success': False,
            'error': 'Erreur interne du serveur'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_recommendation_system(request):
    """
    Endpoint de test pour vérifier le système de recommandation
    """
    try:
        # Vérifier l'authentification
        auth_error = handle_auth_error(request)
        if auth_error:
            return auth_error
        
        user = request.user
        logger.info(f"Test système recommandation pour {user.email}")
        
        # Tester avec Supine Press
        result = get_simple_recommendation_by_name(user, "Supine Press")
        
        from django.utils import timezone
        
        response_data = {
            'user': user.email,
            'test_machine': 'Supine Press',
            'result': result,
            'timestamp': str(timezone.now())
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur test système: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
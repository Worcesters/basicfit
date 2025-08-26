"""
Système d'authentification simplifié et robuste
Endpoints unifiés pour l'app Android
"""
import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

# ===== UTILITAIRES =====
def create_tokens_for_user(user):
    """Créer les tokens JWT pour un utilisateur"""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }

def user_to_dict(user):
    """Convertir un utilisateur en dictionnaire"""
    return {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active
    }

# ===== ENDPOINTS =====

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Inscription utilisateur simplifiée
    POST /api/auth/register/
    
    Body: {
        "email": "user@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    try:
        data = request.data
        
        # Validation des données requises
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        if not email or not password:
            logger.warning(f"Tentative d'inscription avec données manquantes")
            return Response({
                'success': False,
                'message': 'Email et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 6:
            return Response({
                'success': False,
                'message': 'Le mot de passe doit contenir au moins 6 caractères'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(email=email).exists():
            logger.warning(f"Tentative d'inscription avec email existant: {email}")
            return Response({
                'success': False,
                'message': 'Un compte avec cet email existe déjà'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer l'utilisateur
        try:
            user = User.objects.create_user(
                username=email,  # Utiliser l'email comme username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            
            logger.info(f"✅ NOUVEL UTILISATEUR CRÉÉ - ID: {user.id}, Email: {email}")
            
            # Créer les tokens
            tokens = create_tokens_for_user(user)
            
            return Response({
                'success': True,
                'message': 'Compte créé avec succès',
                'user': user_to_dict(user),
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
            
        except IntegrityError as e:
            logger.error(f"Erreur création utilisateur: {e}")
            return Response({
                'success': False,
                'message': 'Erreur lors de la création du compte'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"💥 ERREUR INSCRIPTION: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur interne du serveur'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Connexion utilisateur simplifiée
    POST /api/auth/login/
    
    Body: {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.data
        
        # Validation des données
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            logger.warning(f"Tentative de connexion avec données manquantes")
            return Response({
                'success': False,
                'message': 'Email et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"🔐 TENTATIVE CONNEXION - Email: {email}")
        
        # Authentification
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                if not user.is_active:
                    logger.warning(f"Tentative de connexion avec compte inactif: {email}")
                    return Response({
                        'success': False,
                        'message': 'Compte désactivé'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Créer les tokens
                tokens = create_tokens_for_user(user)
                
                logger.info(f"✅ CONNEXION RÉUSSIE - ID: {user.id}, Email: {email}")
                
                return Response({
                    'success': True,
                    'message': 'Connexion réussie',
                    'user': user_to_dict(user),
                    'tokens': tokens
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Mot de passe incorrect pour: {email}")
                return Response({
                    'success': False,
                    'message': 'Email ou mot de passe incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            logger.warning(f"Tentative de connexion avec email inexistant: {email}")
            return Response({
                'success': False,
                'message': 'Email ou mot de passe incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"💥 ERREUR CONNEXION: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur interne du serveur'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Déconnexion utilisateur
    POST /api/auth/logout/
    """
    try:
        user = request.user
        logger.info(f"🚪 DÉCONNEXION - ID: {user.id}, Email: {user.email}")
        
        return Response({
            'success': True,
            'message': 'Déconnexion réussie'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR DÉCONNEXION: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur lors de la déconnexion'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Profil utilisateur
    GET /api/auth/profile/
    """
    try:
        user = request.user
        logger.debug(f"Récupération profil - ID: {user.id}")
        
        return Response({
            'success': True,
            'user': user_to_dict(user)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR PROFIL: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur récupération profil'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    """
    Test de connectivité
    GET /api/auth/ping/
    """
    return Response({
        'success': True,
        'message': 'Auth API opérationnelle',
        'authenticated': request.user.is_authenticated
    }, status=status.HTTP_200_OK)
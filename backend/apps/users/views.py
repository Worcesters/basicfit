"""
Vues pour l'authentification et la gestion des utilisateurs BasicFit
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

from .models import User, ProfilUtilisateur
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, CustomTokenObtainPairSerializer,
    UserProfileSerializer, ProfilUtilisateurSerializer, PasswordChangeSerializer
)


class UserRegistrationView(APIView):
    """API pour l'inscription des nouveaux utilisateurs"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Créer un nouveau compte utilisateur"""
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Générer des tokens JWT pour l'utilisateur
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Compte créé avec succès!',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'prenom': user.prenom,
                    'nom': user.nom,
                    'est_premium': user.est_premium
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            'message': 'Erreur lors de la création du compte',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """API pour la connexion des utilisateurs"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Connecter un utilisateur existant"""
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Générer des tokens JWT
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Connexion réussie!',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'prenom': user.prenom,
                    'nom': user.nom,
                    'est_premium': user.est_premium,
                    'objectif_sportif': user.objectif_sportif,
                    'niveau_experience': user.niveau_experience
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'message': 'Identifiants incorrects',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue personnalisée pour obtenir les tokens JWT avec email"""
    serializer_class = CustomTokenObtainPairSerializer


class UserLogoutView(APIView):
    """API pour la déconnexion des utilisateurs"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Déconnecter l'utilisateur en blacklistant le refresh token"""
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({
                'message': 'Déconnexion réussie!'
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                'message': 'Erreur lors de la déconnexion'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API pour voir et modifier le profil utilisateur"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retourner l'utilisateur connecté"""
        return self.request.user

    def update(self, request, *args, **kwargs):
        """Mettre à jour le profil utilisateur"""
        response = super().update(request, *args, **kwargs)

        if response.status_code == 200:
            response.data['message'] = 'Profil mis à jour avec succès!'

        return response


class ProfilUtilisateurView(generics.RetrieveUpdateAPIView):
    """API pour gérer le profil détaillé de l'utilisateur"""
    serializer_class = ProfilUtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Récupérer ou créer le profil utilisateur"""
        profil, created = ProfilUtilisateur.objects.get_or_create(
            utilisateur=self.request.user
        )
        return profil


class PasswordChangeView(APIView):
    """API pour changer le mot de passe"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Changer le mot de passe de l'utilisateur"""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Mot de passe modifié avec succès!'
            }, status=status.HTTP_200_OK)

        return Response({
            'message': 'Erreur lors du changement de mot de passe',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserStatsView(APIView):
    """API pour les statistiques de l'utilisateur"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Récupérer les statistiques de l'utilisateur"""
        user = request.user

        # Import conditionnel pour éviter les dépendances circulaires
        from apps.workouts.models import SeanceEntrainement
        from django.utils import timezone
        from datetime import timedelta

        # Calculer les statistiques
        now = timezone.now()
        seances_cette_semaine = SeanceEntrainement.objects.filter(
            utilisateur=user,
            date_debut__gte=now - timedelta(days=7),
            statut='TERMINEE'
        ).count()

        total_seances = SeanceEntrainement.objects.filter(
            utilisateur=user,
            statut='TERMINEE'
        ).count()

        derniere_seance = SeanceEntrainement.objects.filter(
            utilisateur=user,
            statut='TERMINEE'
        ).order_by('-date_debut').first()

        return Response({
            'seances_cette_semaine': seances_cette_semaine,
            'total_seances': total_seances,
            'derniere_seance': derniere_seance.date_debut if derniere_seance else None,
            'membre_depuis': user.date_joined.strftime('%d/%m/%Y'),
            'est_premium': user.est_premium,
            'objectif_sportif': user.objectif_sportif,
            'niveau_experience': user.niveau_experience
        }, status=status.HTTP_200_OK)


# ============= VUES WEB POUR L'INTERFACE HTML =============

def register_view(request):
    """Vue web pour l'inscription"""
    if request.method == 'POST':
        # Traiter les données du formulaire d'inscription
        email = request.POST.get('email')
        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Validation basique
        if password != password_confirm:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Un compte avec cet email existe déjà.')
        else:
            try:
                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    prenom=prenom,
                    nom=nom
                )

                # Créer le profil
                ProfilUtilisateur.objects.create(user=user)

                messages.success(request, 'Compte créé avec succès! Vous pouvez maintenant vous connecter.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Erreur lors de la création du compte: {str(e)}')

    return render(request, 'users/register.html')


def login_view(request):
    """Vue web pour la connexion"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                messages.success(request, f'Bienvenue {user.prenom}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Mot de passe incorrect.')
        except User.DoesNotExist:
            messages.error(request, 'Aucun compte trouvé avec cet email.')

    return render(request, 'users/login.html')


@login_required
def dashboard_view(request):
    """Vue du tableau de bord utilisateur"""
    from apps.workouts.models import SeanceEntrainement
    from django.utils import timezone
    from datetime import timedelta

    user = request.user
    now = timezone.now()

    # Statistiques
    seances_cette_semaine = SeanceEntrainement.objects.filter(
        utilisateur=user,
        date_debut__gte=now - timedelta(days=7),
        statut='TERMINEE'
    ).count()

    derniere_seance = SeanceEntrainement.objects.filter(
        utilisateur=user,
        statut='TERMINEE'
    ).order_by('-date_debut').first()

    context = {
        'user': user,
        'seances_cette_semaine': seances_cette_semaine,
        'derniere_seance': derniere_seance
    }

    return render(request, 'users/dashboard.html', context)


@login_required
def logout_view(request):
    """Vue pour la déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')


@login_required
def profile_view(request):
    """Vue pour gérer le profil utilisateur"""
    user = request.user
    profil, created = ProfilUtilisateur.objects.get_or_create(utilisateur=user)

    if request.method == 'POST':
        # Mettre à jour les informations de l'utilisateur
        user.prenom = request.POST.get('prenom', user.prenom)
        user.nom = request.POST.get('nom', user.nom)
        user.telephone = request.POST.get('telephone', user.telephone)
        user.poids = request.POST.get('poids') or user.poids
        user.taille = request.POST.get('taille') or user.taille
        user.objectif_sportif = request.POST.get('objectif_sportif', user.objectif_sportif)
        user.niveau_experience = request.POST.get('niveau_experience', user.niveau_experience)
        user.save()

        # Mettre à jour le profil
        profil.bio = request.POST.get('bio', profil.bio)
        profil.objectifs_personnels = request.POST.get('objectifs_personnels', profil.objectifs_personnels)
        profil.frequence_entrainement_semaine = request.POST.get('frequence_entrainement_semaine') or profil.frequence_entrainement_semaine
        profil.duree_entrainement_moyenne = request.POST.get('duree_entrainement_moyenne') or profil.duree_entrainement_moyenne
        profil.est_public = 'est_public' in request.POST
        profil.save()

        messages.success(request, 'Profil mis à jour avec succès!')
        return redirect('profile')

    context = {
        'user': user,
        'profil': profil
    }

    return render(request, 'users/profile.html', context)


# ============= API POUR L'APPLICATION MOBILE =============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info(request):
    """API pour récupérer les informations de l'utilisateur connecté"""
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def check_email_exists(request):
    """API pour vérifier si un email existe déjà"""
    email = request.data.get('email')
    exists = User.objects.filter(email=email).exists()
    return Response({'exists': exists})


# ====== VUES SPÉCIFIQUES ANDROID ======

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def android_login(request):
    """Connexion simplifiée pour l'application Android"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                'success': False,
                'message': 'Email et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier les identifiants
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            # Générer un token JWT
            refresh = RefreshToken.for_user(user)

            return Response({
                'success': True,
                'message': 'Connexion réussie',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nom': user.nom,
                    'prenom': user.prenom
                },
                'token': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Identifiants incorrects'
            }, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def android_register(request):
    """Inscription simplifiée pour l'application Android"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        nom = request.data.get('nom', '')
        prenom = request.data.get('prenom', '')

        if not email or not password:
            return Response({
                'success': False,
                'message': 'Email et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier si l'email existe déjà
        if User.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': 'Un compte avec cet email existe déjà'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Créer l'utilisateur
        user = User.objects.create_user(
            username=email,  # Utiliser email comme username
            email=email,
            password=password,
            nom=nom,
            prenom=prenom
        )

        # Générer un token JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            'success': True,
            'message': 'Compte créé avec succès',
            'user': {
                'id': user.id,
                'email': user.email,
                'nom': user.nom,
                'prenom': user.prenom
            },
            'token': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def android_profile(request):
    """
    API simplifiée pour récupérer le profil utilisateur depuis Android
    """
    try:
        user = request.user
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'nom': user.nom,
                'prenom': user.prenom,
                'poids': user.poids,
                'taille': user.taille,
                'objectif_sportif': user.objectif_sportif,
                'niveau_experience': user.niveau_experience,
                'date_naissance': user.date_naissance.isoformat() if user.date_naissance else None,
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors de la récupération du profil: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'HEAD'])
@permission_classes([permissions.AllowAny])
def android_ping(request):
    """
    Endpoint simple pour tester la connectivité depuis l'application Android
    """
    return Response({
        'success': True,
        'message': 'Serveur BasicFit accessible',
        'timestamp': timezone.now().isoformat()
    })
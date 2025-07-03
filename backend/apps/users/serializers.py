"""
Serializers pour l'API des utilisateurs
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, ProfilUtilisateur
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription des nouveaux utilisateurs"""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'prenom', 'nom', 'telephone', 'date_naissance',
            'poids', 'taille', 'objectif_sportif', 'niveau_experience',
            'password', 'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'prenom': {'required': True},
            'nom': {'required': True}
        }

    def validate(self, data):
        """Validation des mots de passe"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        return data

    def validate_email(self, value):
        """Vérifier que l'email n'existe pas déjà"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Un compte avec cet email existe déjà.'
            )
        return value

    def create(self, validated_data):
        """Créer un nouvel utilisateur"""
        # Retirer les champs non nécessaires pour la création
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        # Créer l'utilisateur
        user = User.objects.create_user(
            username=validated_data['email'],  # Utiliser l'email comme username
            password=password,
            **validated_data
        )

        # Créer le profil utilisateur associé
        ProfilUtilisateur.objects.create(utilisateur=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer pour la connexion des utilisateurs"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Valider les identifiants de connexion"""
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # Chercher l'utilisateur par email
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'Aucun compte trouvé avec cet email.'
                )

            # Authentifier avec le username
            user = authenticate(username=username, password=password)

            if not user:
                raise serializers.ValidationError(
                    'Email ou mot de passe incorrect.'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    'Ce compte a été désactivé.'
                )

            data['user'] = user
        else:
            raise serializers.ValidationError(
                'Email et mot de passe requis.'
            )

        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personnalisé pour les tokens JWT"""
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField()
        del self.fields['username']

    def validate(self, attrs):
        """Validation personnalisée avec email"""
        # Convertir email en username pour l'authentification
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
            attrs['username'] = user.username
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Aucun compte trouvé avec cet email.'
            )

        del attrs['email']
        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        """Personnaliser le contenu du token"""
        token = super().get_token(user)

        # Ajouter des informations supplémentaires au token
        token['user_id'] = user.id
        token['email'] = user.email
        token['prenom'] = user.prenom
        token['nom'] = user.nom
        token['est_premium'] = user.est_premium

        return token


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    profil = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'prenom', 'nom', 'telephone', 'date_naissance',
            'poids', 'taille', 'objectif_sportif', 'niveau_experience',
            'est_premium', 'photo_profil', 'date_inscription_salle',
            'salle_frequentee', 'profil'
        ]
        read_only_fields = ['id', 'email', 'est_premium']

    def get_profil(self, obj):
        """Récupérer les données du profil utilisateur"""
        try:
            profil = obj.profil
            return {
                'bio': profil.bio,
                'objectifs_personnels': profil.objectifs_personnels,
                'frequence_entrainement_semaine': profil.frequence_entrainement_semaine,
                'duree_entrainement_moyenne': profil.duree_entrainement_moyenne,
                'est_public': profil.est_public
            }
        except ProfilUtilisateur.DoesNotExist:
            return None


class UserSerializer(serializers.ModelSerializer):
    """Serializer principal pour les utilisateurs"""
    nom_complet = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    imc = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'prenom', 'nom', 'nom_complet',
            'telephone', 'date_naissance', 'age', 'poids', 'taille', 'imc',
            'objectif_sportif', 'niveau_experience', 'mode_entrainement_prefere',
            'photo_profil', 'est_premium', 'date_inscription_salle', 'salle_frequentee',
            'notifications_actives', 'notification_rappel_entrainement',
            'notification_progression', 'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'date_joined', 'last_login')

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value


class ProfilUtilisateurSerializer(serializers.ModelSerializer):
    """Serializer pour le profil détaillé de l'utilisateur"""

    class Meta:
        model = ProfilUtilisateur
        fields = [
            'bio', 'objectifs_personnels', 'blessures_actuelles',
            'medicaments', 'frequence_entrainement_semaine',
            'duree_entrainement_moyenne', 'est_public'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        """Vérifier l'ancien mot de passe"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Ancien mot de passe incorrect.'
            )
        return value

    def validate(self, data):
        """Vérifier que les nouveaux mots de passe correspondent"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Les nouveaux mots de passe ne correspondent pas.'
            })
        return data

    def save(self):
        """Sauvegarder le nouveau mot de passe"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    """Serializer pour la demande de réinitialisation de mot de passe"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Aucun utilisateur trouvé avec cet email.")
        return value
"""
URLs pour l'authentification et la gestion des utilisateurs BasicFit
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from . import views

app_name = 'users'

# URLs pour l'API REST
api_urlpatterns = [
    # Authentification JWT
    path('auth/register/', views.UserRegistrationView.as_view(), name='api_register'),
    path('auth/login/', views.UserLoginView.as_view(), name='api_login'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='api_logout'),
    path('auth/token/', views.CustomTokenObtainPairView.as_view(), name='api_token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),

    # Profil utilisateur
    path('profile/', views.UserProfileView.as_view(), name='api_profile'),
    path('profile/details/', views.ProfilUtilisateurView.as_view(), name='api_profile_details'),
    path('profile/stats/', views.UserStatsView.as_view(), name='api_user_stats'),
    path('profile/password/', views.PasswordChangeView.as_view(), name='api_password_change'),

    # Utilitaires
    path('info/', views.user_info, name='api_user_info'),
    path('check-email/', views.check_email_exists, name='api_check_email'),

    # Authentification simple pour Android
    path('android/login/', views.android_login, name='android-login'),
    path('android/register/', views.android_register, name='android-register'),
    path('android/profile/', views.android_profile, name='android-profile'),
]

# URLs pour l'interface web
web_urlpatterns = [
    # Authentification web
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Tableau de bord et profil
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
]

# Combiner toutes les URLs
urlpatterns = api_urlpatterns + web_urlpatterns
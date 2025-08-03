@echo off
echo ===========================================
echo    CREATION ADMIN DJANGO FLY.IO
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Creation du superuser admin...
flyctl ssh console --app basicfit-v2 -C "python manage.py shell -c \"
from django.contrib.auth import get_user_model
User = get_user_model()
# Supprimer l'admin existant s'il existe
User.objects.filter(username='admin').delete()
# Créer le nouvel admin
admin_user = User.objects.create_superuser('admin', 'admin@basicfit.com', 'admin')
print('✅ Superuser admin créé avec succès')
print(f'Username: {admin_user.username}')
print(f'Email: {admin_user.email}')
print(f'Is superuser: {admin_user.is_superuser}')
\""

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ ADMIN CREE AVEC SUCCES !
    echo.
    echo Identifiants:
    echo - URL: https://basicfit-v2.fly.dev/admin/
    echo - Username: admin
    echo - Email: admin@basicfit.com
    echo - Password: admin
    
) else (
    echo ❌ ERREUR lors de la creation
)

echo.
pause
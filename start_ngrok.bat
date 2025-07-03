@echo off
echo 🚀 Démarrage BasicFit avec ngrok...
echo.

REM Démarrer le serveur Django en arrière-plan
echo 📡 Démarrage du serveur Django...
start "Django Server" cmd /k "cd backend && python manage.py runserver"

REM Attendre 3 secondes
timeout /t 3 /nobreak >nul

REM Démarrer ngrok pour exposer le serveur
echo 🌐 Exposition du serveur avec ngrok...
echo.
echo ⚠️  IMPORTANT: Copiez l'URL https://xxxx.ngrok.io
echo    et mettez-la dans ApiService.kt (BASE_URL)
echo.
ngrok http 8000
@echo off
echo 🏠 Démarrage BasicFit sur réseau local...
echo.

REM Trouver l'IP locale
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
set IP=%IP: =%

echo 📡 Votre IP locale: %IP%
echo.
echo 📱 Dans ApiService.kt, utilisez:
echo    private const val BASE_URL = "http://%IP%:8000/"
echo.
echo ⚠️  Les appareils doivent être sur le même WiFi !
echo.

REM Démarrer le serveur Django accessible depuis l'extérieur
cd backend
python manage.py runserver 0.0.0.0:8000
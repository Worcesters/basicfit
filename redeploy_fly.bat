@echo off
echo ===========================================
echo    REDEPLOIEMENT FLY.IO OPTIMISE
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Verification de la configuration...
echo Configuration fly.toml mise a jour:
echo - Health checks: grace period 30s, timeout 10s
echo - Memoire augmentee: 512MB (au lieu de 256MB)
echo - Gunicorn: timeout 300s, log-level info
echo - Collectstatic retire du process de boot
echo.

echo 2. Verification statut actuel...
flyctl status --app basicfit-v2
echo.

echo 3. Deployment avec configuration optimisee...
flyctl deploy --app basicfit-v2 --verbose

if %ERRORLEVEL% EQU 0 (
    echo.
    echo DEPLOIEMENT REUSSI !
    echo.
    echo 4. Tests automatiques...
    echo.
    
    echo Test API:
    ping -n 4 127.0.0.1 >nul
    curl -s https://basicfit-v2.fly.dev/api/
    echo.
    
    echo Test Admin:
    ping -n 4 127.0.0.1 >nul
    curl -s -I https://basicfit-v2.fly.dev/admin/
    echo.
    
    echo Application disponible sur:
    echo https://basicfit-v2.fly.dev/
    echo.
    
) else (
    echo.
    echo ECHEC DU DEPLOIEMENT
    echo.
    echo Verification des logs:
    flyctl logs --app basicfit-v2
)

echo.
pause
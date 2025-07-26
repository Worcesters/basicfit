@echo off
echo ============================================
echo    AUTO-DEPLOY BASICFIT (Git + Railway)
echo ============================================
echo.

cd /d "%~dp0"

echo 1. Verification des changements Git...
git status

echo.
echo 2. Ajout des fichiers modifies...
git add .

echo.
echo 3. Creation du commit avec timestamp...
set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
set "timestamp=%timestamp: =0%"
git commit -m "🚀 Auto-deploy %timestamp% - Maj système professionnel

🔧 Modifications:
- Nouveau système de recommandation scientifique (1RM)
- Déduplication SHA256 des séances
- Messages de confirmation Android
- Refactorisation complète des vues
- Amélioration du service de sauvegarde

🎯 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

echo.
echo 4. Push vers le repository...
git push origin main

echo.
echo 5. Attente du redéploiement Railway...
echo Railway va automatiquement redéployer grâce aux fichiers:
echo - railway.json (configuration de build)
echo - Procfile (commande de démarrage)
echo - nixpacks.toml (configuration Nixpacks)
echo.

echo 6. Verification de l'API...
timeout /t 10 >nul
echo Test de l'API en cours...

echo.
echo ============================================
echo    DEPLOYMENT COMPLETE !
echo ============================================
echo 📱 APK Android: android/app/build/outputs/apk/debug/app-debug.apk
echo 🌐 API URL: https://basicfit-production.up.railway.app/api/
echo 📊 Nouveaux endpoints:
echo   - /api/workouts/save_professional/
echo   - /api/workouts/recommendation_professional/
echo ============================================
echo.
pause
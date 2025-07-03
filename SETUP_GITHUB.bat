@echo off
chcp 65001 >nul
color 0B
echo.
echo ===============================================
echo     📱 SETUP GITHUB POUR BASICFIT
echo ===============================================
echo.
echo 🎯 ÉTAPES À SUIVRE :
echo.
echo 1️⃣  Créer un repo GitHub :
echo     • Allez sur https://github.com
echo     • Cliquez "New repository"
echo     • Nom : basicfit-v2
echo     • Public ✅ (pour Railway gratuit)
echo     • Create repository
echo.
echo 2️⃣  Copier l'URL de votre repo
echo     Exemple : https://github.com/votre-nom/basicfit-v2.git
echo.
echo 3️⃣  Revenir ici et appuyer sur ENTER
echo.
pause
echo.
echo ===============================================
echo     🔧 INITIALISATION GIT
echo ===============================================
echo.

echo Initialisation du repository local...
git init

echo Ajout de tous les fichiers...
git add .

echo Commit initial...
git commit -m "Initial commit - BasicFit v2 avec API Django et Android"

echo.
echo ⚠️  ATTENTION : Maintenant vous devez ajouter votre remote !
echo.
echo Copiez/collez cette commande avec VOTRE URL :
echo git remote add origin https://github.com/VOTRE-NOM/basicfit-v2.git
echo.
echo Puis :
echo git branch -M main
echo git push -u origin main
echo.
echo ===============================================
echo   Appuyez sur une touche pour ouvrir GitHub
echo ===============================================
pause >nul
start https://github.com/new
echo.
echo GitHub ouvert ! Créez votre repo puis revenez ici.
pause
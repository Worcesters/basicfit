@echo off
echo 🚀 PUSH DES CHANGEMENTS VERS GIT
echo =================================

echo.
echo 📝 Ajout des fichiers modifiés...
git add .

echo.
echo 💬 Commit des changements...
git commit -m "🔧 Amélioration système recommandation - Synchronisation BDD - Poids logiques"

echo.
echo 🚀 Push vers le repository...
git push origin main

echo.
echo ✅ Changements poussés avec succès !
echo.
echo 📊 Résumé des améliorations :
echo   - ✅ Système de recommandation corrigé
echo   - ✅ Synchronisation avec la BDD
echo   - ✅ Poids logiques proposés
echo   - ✅ Gestion des cas spéciaux (cardio, etc.)
echo.

pause
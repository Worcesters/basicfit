#!/bin/bash

echo "🚀 Configuration de BasicFit v2..."

# Démarrer les conteneurs
echo "📦 Démarrage des conteneurs Docker..."
docker-compose up -d

# Attendre que le backend soit prêt
echo "⏳ Attente du démarrage du backend..."
sleep 15

# Exécuter les migrations
echo "🗄️ Exécution des migrations..."
docker-compose exec -T backend python manage.py migrate

# Charger les données d'exemple
echo "📊 Chargement des données d'exemple..."
docker-compose exec -T backend python manage.py loaddata fixtures/initial_data.json

# Créer un superutilisateur (optionnel)
echo "👤 Création d'un superutilisateur..."
docker-compose exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@basicfit.com', 'admin123')
    print('Superutilisateur créé: admin / admin123')
else:
    print('Superutilisateur existe déjà')
"

echo ""
echo "✅ Configuration terminée !"
echo ""
echo "🌐 Votre application est maintenant accessible sur :"
echo "   - Interface Web: http://localhost:3000"
echo "   - API Swagger: http://localhost:8000/api/docs/"
echo "   - Admin Django: http://localhost:8000/admin/"
echo ""
echo "👤 Compte admin: admin / admin123"
echo ""
echo "🎉 Profitez de votre application BasicFit v2 !"
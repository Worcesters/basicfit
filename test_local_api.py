#!/usr/bin/env python3
"""
Test local de l'API Django
"""
import os
import sys
import django
import requests
import time

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.machines.models import Machine
from apps.workouts.serializers import MachineSerializer
from rest_framework.test import APIRequestFactory

def test_local_machines():
    """Test local des machines"""
    print("🔧 TEST LOCAL DE L'API MACHINES")
    print("=" * 50)

    # Test direct du modèle
    print("📊 Vérification des machines en base...")
    machines = Machine.objects.all()
    print(f"✅ {machines.count()} machines trouvées en base")

    # Test du sérialiseur
    print("\n🔧 Test du sérialiseur...")
    factory = APIRequestFactory()
    request = factory.get('/api/workouts/machines/')

    try:
        for machine in machines[:3]:
            serializer = MachineSerializer(machine, context={'request': request})
            data = serializer.data
            print(f"  📱 {machine.nom}:")
            print(f"     - ID: {data.get('id')}")
            print(f"     - GIF: {data.get('image_gif', 'Aucun')}")
            if data.get('image_gif'):
                print(f"     - URL GIF: {data.get('image_gif')[:50]}...")

        print("✅ Sérialiseur fonctionne correctement")
        return True

    except Exception as e:
        print(f"❌ Erreur du sérialiseur: {e}")
        return False

def test_api_endpoint():
    """Test de l'endpoint API"""
    print("\n🌐 Test de l'endpoint API...")

    try:
        # Attendre que le serveur soit prêt
        time.sleep(5)

        response = requests.get('http://localhost:8000/api/workouts/machines/', timeout=10)

        if response.status_code == 200:
            machines = response.json()
            print(f"✅ API endpoint fonctionne: {len(machines)} machines")

            for machine in machines[:3]:
                nom = machine.get('nom', 'N/A')
                gif = machine.get('image_gif')
                print(f"  📱 {nom}: GIF = {'Oui' if gif else 'Non'}")

            return True
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   Réponse: {response.text[:200]}...")
            return False

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DU TEST LOCAL")
    print("=" * 50)

    # Test du modèle et sérialiseur
    model_ok = test_local_machines()

    if model_ok:
        # Test de l'endpoint
        api_ok = test_api_endpoint()

        print("\n" + "=" * 50)
        print("📋 RÉSUMÉ DU TEST LOCAL")
        print("=" * 50)

        if api_ok:
            print("✅ TOUT FONCTIONNE EN LOCAL !")
            print("   - Les modèles sont corrects")
            print("   - Le sérialiseur fonctionne")
            print("   - L'API endpoint fonctionne")
            print("   - Le problème est probablement sur Railway")
        else:
            print("⚠️ PROBLÈME LOCAL DÉTECTÉ")
            print("   - Les modèles sont corrects")
            print("   - Le sérialiseur fonctionne")
            print("   - L'API endpoint a un problème")
    else:
        print("❌ PROBLÈME AVEC LES MODÈLES/SÉRIALISEUR")
#!/usr/bin/env python3
"""
Script simple pour tester le serveur Django
"""

import requests

def test_server():
    """Teste si le serveur Django fonctionne"""
    try:
        response = requests.get('http://localhost:8000/api/machines/')
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Serveur Django fonctionne")
            data = response.json()
            print(f"Nombre de machines: {len(data.get('results', []))}")
        else:
            print(f"❌ Erreur serveur: {response.status_code}")
            print(f"Réponse: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_server()
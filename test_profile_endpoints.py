#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test des endpoints de profil pour l'application Android
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://basicfit-v2.fly.dev/api"
# BASE_URL = "http://localhost:8000/api"  # Pour test local

def test_register_with_profile():
    """Test d'inscription avec données de profil complètes"""
    print("[TEST] Inscription avec profil complet...")
    
    # Données de test
    test_data = {
        "email": f"test_profile_{int(datetime.now().timestamp())}@example.com",
        "password": "Test123456!",
        "nom": "Dupont",
        "prenom": "Jean",
        "date_naissance": "1990-05-15",
        "poids": 75.5,
        "taille": 180,
        "objectif_sportif": "PRISE_MASSE",
        "niveau_experience": "INTERMEDIAIRE"
    }
    
    response = requests.post(f"{BASE_URL}/users/android/register/", json=test_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("[OK] Inscription reussie!")
        print(f"User data: {json.dumps(data['user'], indent=2)}")
        
        token = data.get('token')
        if token:
            print(f"[TOKEN] Token recu: {token[:20]}...")
            return token, data['user']['id']
    else:
        print(f"[ERREUR] Erreur inscription: {response.text}")
        return None, None

def test_get_profile(token):
    """Test récupération du profil"""
    print("\n[TEST] Test récupération profil...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/android/profile/", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("[OK] Profil récupéré!")
        print(f"User data: {json.dumps(data['user'], indent=2)}")
    else:
        print(f"[ERREUR] Erreur profil: {response.text}")

def test_update_profile(token):
    """Test mise à jour du profil"""
    print("\n[TEST] Test mise à jour profil...")
    
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "poids": 77.0,
        "taille": 182.0,
        "objectif_sportif": "FORCE"
    }
    
    response = requests.put(f"{BASE_URL}/users/android/profile/update/", 
                           json=update_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("[OK] Profil mis à jour!")
        print(f"User data: {json.dumps(data['user'], indent=2)}")
    else:
        print(f"[ERREUR] Erreur mise à jour: {response.text}")

def test_get_stats(token):
    """Test récupération des statistiques"""
    print("\n[TEST] Test récupération statistiques...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/profile/stats/", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("[OK] Statistiques récupérées!")
        print(f"Stats data: {json.dumps(data, indent=2)}")
    else:
        print(f"[ERREUR] Erreur stats: {response.text}")

def main():
    print("TEST des endpoints de profil Android")
    print(f"URL de base: {BASE_URL}")
    print("=" * 50)
    
    # Test inscription avec profil complet
    token, user_id = test_register_with_profile()
    
    if token:
        # Test récupération profil
        test_get_profile(token)
        
        # Test mise à jour profil
        test_update_profile(token)
        
        # Test récupération statistiques
        test_get_stats(token)
        
        print("\n[FINI] Tests terminés!")
    else:
        print("\n[ERREUR] Tests interrompus - échec inscription")

if __name__ == "__main__":
    main()
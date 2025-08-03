#!/usr/bin/env python3
"""
Test complet de l'API pour vérifier les recommandations
"""
import requests
import json

def test_recommendations_complete():
    """Test des recommandations avec le vrai utilisateur"""
    print("=== TEST COMPLET DES RECOMMANDATIONS ===")
    
    base_url = "https://basicfit-v2.fly.dev/api"
    
    # Login avec le compte utilisateur réel
    print("1. Login utilisateur...")
    login_data = {
        "email": "jeremy.jouvenal@example.com",  # Email utilisateur réel
        "password": "monmotdepasse"
    }
    
    try:
        response = requests.post(f"{base_url}/users/android/login/", 
                               json=login_data, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        print(f"   Status login: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('token'):
                token = data['token']
                user_email = data.get('user', {}).get('email', 'unknown')
                print(f"   LOGIN REUSSI pour: {user_email}")
                
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Test recommandations pour différentes machines
                machines_to_test = [
                    {"id": 1, "name": "Chest Press"},
                    {"id": 2, "name": "Supine Press"}, 
                    {"id": 3, "name": "Leg Press"},
                    {"id": 4, "name": "Lat Pull Down"}
                ]
                
                print("\n2. Test des recommandations:")
                for machine in machines_to_test:
                    print(f"\n   Testing machine {machine['id']}: {machine['name']}")
                    
                    # Test recommandation par ID
                    response = requests.get(f"{base_url}/workouts/recommendation/id/{machine['id']}/", 
                                          headers=headers, 
                                          timeout=10)
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        rec_data = response.json()
                        if rec_data.get('success') and rec_data.get('data'):
                            data = rec_data['data']
                            weight = data.get('poids_recommande', 0)
                            source = data.get('source', 'unknown')
                            print(f"   Poids recommande: {weight}kg (source: {source})")
                            print(f"   Series: {data.get('series_recommandees', 0)}, Reps: {data.get('reps_recommandees', 0)}")
                            
                            # Le test principal: vérifier si on a les bonnes valeurs
                            if machine['name'] == 'Supine Press' and weight >= 60:
                                print(f"   PARFAIT! Supine Press montre {weight}kg (>=60kg comme attendu)")
                            elif machine['name'] == 'Supine Press':
                                print(f"   PROBLEME: Supine Press montre {weight}kg mais devrait être >=60kg")
                        else:
                            print(f"   Pas de donnees de recommandation: {rec_data}")
                    else:
                        print(f"   Erreur: {response.text[:200]}")
                
                # Test du système de progression
                print(f"\n3. Test de la progression:")
                response = requests.post(f"{base_url}/workouts/progressions/force-update/", 
                                       headers=headers, 
                                       timeout=10)
                print(f"   Status force-update: {response.status_code}")
                if response.status_code == 200:
                    print("   Mise a jour des progressions reussie")
                else:
                    print(f"   Probleme mise a jour: {response.text[:100]}")
                
                return True
            else:
                print(f"   Pas de token dans la reponse: {data}")
                return False
        else:
            print(f"   Echec login: {response.text}")
            
            # Essayer avec le compte de test
            print("\n   Essai avec compte de test...")
            login_data_test = {
                "email": "test@railway.com",
                "password": "testpass123"
            }
            
            response = requests.post(f"{base_url}/users/android/login/", 
                                   json=login_data_test, 
                                   headers={"Content-Type": "application/json"},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                token = data['token']
                print("   LOGIN REUSSI avec compte test")
                
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Test recommandation Supine Press
                response = requests.get(f"{base_url}/workouts/recommendation/id/2/", 
                                      headers=headers, 
                                      timeout=10)
                if response.status_code == 200:
                    rec_data = response.json()
                    if rec_data.get('success'):
                        weight = rec_data['data']['poids_recommande']
                        print(f"   Supine Press pour compte test: {weight}kg")
                return True
            else:
                return False
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == '__main__':
    success = test_recommendations_complete()
    if success:
        print("\nTEST TERMINE AVEC SUCCES!")
    else:
        print("\nTEST ECHOUE!")
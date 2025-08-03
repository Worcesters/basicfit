#!/usr/bin/env python3
"""
Tester les machines sans séances pour vérifier le nouveau message
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.machines.models import Machine
from apps.workouts.models import ExerciceSeance
from apps.workouts.simple_recommendation import get_generic_recommendation

def find_machines_without_sessions():
    print("=== RECHERCHE MACHINES SANS SEANCES ===")
    
    # Trouver toutes les machines
    all_machines = Machine.objects.all()
    machines_without_sessions = []
    
    for machine in all_machines:
        session_count = ExerciceSeance.objects.filter(
            machine=machine,
            seance__statut='TERMINEE'
        ).count()
        
        if session_count == 0:
            machines_without_sessions.append(machine)
            print(f"- {machine.nom} (ID: {machine.id}) : 0 seances")
    
    print(f"\nTrouve {len(machines_without_sessions)} machines sans seances")
    return machines_without_sessions

def test_no_session_recommendation():
    print("\n=== TEST RECOMMANDATION SANS SEANCES ===")
    
    machines_without_sessions = find_machines_without_sessions()
    
    if machines_without_sessions:
        # Tester avec la première machine sans séances
        machine = machines_without_sessions[0]
        print(f"\nTest avec machine: {machine.nom}")
        
        result = get_generic_recommendation(machine.id)
        
        print(f"Resultat:")
        print(f"  Success: {result.get('success')}")
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"  Machine: {data.get('machine_nom')}")
            print(f"  Poids: {data.get('poids_recommande')}")
            print(f"  Source: {data.get('source')}")
            print(f"  Message: {data.get('message')}")
            print(f"  Notes: {data.get('notes')}")
            
            if data.get('source') == 'no_data':
                print("  [SUCCESS] Retourne bien 'aucune recommandation'")
            else:
                print("  [ERROR] Devrait retourner 'no_data'")
        else:
            print(f"  Erreur: {result.get('error')}")
    else:
        print("Aucune machine sans seances trouvee - toutes ont des donnees")

if __name__ == "__main__":
    test_no_session_recommendation()
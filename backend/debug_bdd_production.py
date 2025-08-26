#!/usr/bin/env python3
"""
Debug BDD PRODUCTION - Vérifier la vraie base sur Fly.io
"""
import os
import django

# Setup Django en PRODUCTION pour accéder à la vraie BDD
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.flyio')
django.setup()

from apps.users.models import User
from apps.workouts.models_simple import SeanceSimple
from apps.workouts.models import SeanceEntrainement, ExerciceSeance, SeriExercice
from django.db import connection

def debug_bdd_production():
    print("=" * 60)
    print("DEBUG BDD PRODUCTION - Fly.io PostgreSQL")
    print("=" * 60)
    
    # 1. Vérifier la connexion DB
    try:
        from django.conf import settings
        db_config = settings.DATABASES['default']
        print(f"[SETTINGS] Configuration DB:")
        print(f"  - Engine: {db_config['ENGINE']}")
        print(f"  - Name: {db_config['NAME']}")
        if 'HOST' in db_config:
            print(f"  - Host: {db_config['HOST']}")
        
        # Test de connexion simple
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"[DB] Connexion OK: {result[0]}")
            
    except Exception as e:
        print(f"[ERROR] Problème connexion DB: {e}")
        print(f"[DEBUG] Tentative de connexion directe...")
        # Continuer quand même
    
    # 2. Compter tous les utilisateurs
    try:
        users = User.objects.all()
        print(f"\n[USERS] Total utilisateurs: {users.count()}")
        for user in users:
            print(f"  - ID: {user.id}, Email: {user.email}, Username: {user.username}")
    except Exception as e:
        print(f"[ERROR] Utilisateurs: {e}")
    
    # 3. Vérifier SeanceSimple (CSV)
    try:
        total_simple = SeanceSimple.objects.count()
        print(f"\n[SEANCE_SIMPLE] Total global: {total_simple}")
        
        # Par utilisateur
        for user in User.objects.all():
            count = SeanceSimple.objects.filter(utilisateur=user).count()
            if count > 0:
                print(f"  - User {user.id} ({user.email}): {count} séances")
                
                # Dernières séances de cet utilisateur
                seances = SeanceSimple.objects.filter(utilisateur=user).order_by('-created_at')[:5]
                for seance in seances:
                    print(f"    → ID: {seance.id}, Machine: {seance.machine_nom}, Date: {seance.date_seance}")
        
    except Exception as e:
        print(f"[ERROR] SeanceSimple: {e}")
    
    # 4. Vérifier SeanceEntrainement (Workouts)
    try:
        total_entrainement = SeanceEntrainement.objects.count()
        print(f"\n[SEANCE_ENTRAINEMENT] Total global: {total_entrainement}")
        
        # Par utilisateur
        for user in User.objects.all():
            count = SeanceEntrainement.objects.filter(utilisateur=user).count()
            if count > 0:
                print(f"  - User {user.id} ({user.email}): {count} séances")
                
                # Dernières séances de cet utilisateur
                seances = SeanceEntrainement.objects.filter(utilisateur=user).order_by('-created_at')[:5]
                for seance in seances:
                    print(f"    → ID: {seance.id}, Nom: {seance.nom}, Date: {seance.date_prevue}, Statut: {seance.statut}")
                    print(f"      Exercices: {seance.exercices.count()}")
        
    except Exception as e:
        print(f"[ERROR] SeanceEntrainement: {e}")
    
    # 5. Vérifier les toutes dernières insertions
    try:
        with connection.cursor() as cursor:
            print(f"\n[SQL] Dernières insertions (toutes tables confondues):")
            
            # Dernières insertions SeanceSimple
            cursor.execute("""
                SELECT id, machine_nom, date_seance, created_at, utilisateur_id 
                FROM workouts_seancesimple 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            recent_simple = cursor.fetchall()
            print(f"  - Dernières 10 SeanceSimple:")
            for row in recent_simple:
                print(f"    → ID: {row[0]}, Machine: {row[1]}, Date: {row[2]}, Created: {row[3]}, User: {row[4]}")
            
            # Dernières insertions SeanceEntrainement
            cursor.execute("""
                SELECT id, nom, date_prevue, statut, created_at, utilisateur_id 
                FROM workouts_seanceentrainement 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            recent_entrainement = cursor.fetchall()
            print(f"  - Dernières 10 SeanceEntrainement:")
            for row in recent_entrainement:
                print(f"    → ID: {row[0]}, Nom: {row[1]}, Date: {row[2]}, Statut: {row[3]}, Created: {row[4]}, User: {row[5]}")
                
    except Exception as e:
        print(f"[ERROR] Requêtes SQL: {e}")
    
    # 6. Test d'insertion en temps réel
    print(f"\n[TEST] Test d'insertion en temps réel...")
    try:
        # Trouver un utilisateur
        user = User.objects.first()
        if user:
            print(f"  - Utilisateur test: {user.email} (ID: {user.id})")
            
            # Test insertion SeanceSimple
            seance_test = SeanceSimple.objects.create(
                utilisateur=user,
                machine_nom="Test Machine Debug",
                date_seance="2025-01-17",
                type_exercice="AUTRE"
            )
            print(f"  - SeanceSimple créée: ID {seance_test.id}")
            
            # Vérifier qu'elle existe
            exists = SeanceSimple.objects.filter(id=seance_test.id).exists()
            print(f"  - Vérification existence: {exists}")
            
            # Nettoyer
            seance_test.delete()
            print(f"  - Test nettoyé")
        else:
            print(f"  - Aucun utilisateur trouvé pour le test")
            
    except Exception as e:
        print(f"[ERROR] Test insertion: {e}")
    
    print("\n" + "=" * 60)
    print("DEBUG PRODUCTION TERMINÉ")
    print("=" * 60)

if __name__ == '__main__':
    debug_bdd_production()
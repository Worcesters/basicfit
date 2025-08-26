#!/usr/bin/env python3
"""
Debug complet de la BDD - Vérifier toutes les tables
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.users.models import User
from apps.workouts.models_simple import SeanceSimple
from apps.workouts.models import SeanceEntrainement, ExerciceSeance, SeriExercice
from django.db import connection

def debug_bdd_complete():
    print("=" * 60)
    print("DEBUG COMPLET BDD - TOUTES LES TABLES")
    print("=" * 60)
    
    # 1. Vérifier la connexion DB
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()
            print(f"[DB] Base de données: {db_version[0]}")
            
            # Lister toutes les tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"[DB] Nombre de tables: {len(tables)}")
            
    except Exception as e:
        print(f"[ERROR] Problème connexion DB: {e}")
        return
    
    # 2. Compter tous les utilisateurs
    try:
        users = User.objects.all()
        print(f"\n[USERS] Total utilisateurs: {users.count()}")
        for user in users[:5]:  # Limiter à 5
            print(f"  - ID: {user.id}, Email: {user.email}")
    except Exception as e:
        print(f"[ERROR] Utilisateurs: {e}")
    
    # 3. Vérifier SeanceSimple (CSV)
    try:
        total_simple = SeanceSimple.objects.count()
        print(f"\n[SEANCE_SIMPLE] Total: {total_simple}")
        
        if total_simple > 0:
            # Par utilisateur
            for user in User.objects.all()[:3]:
                count = SeanceSimple.objects.filter(utilisateur=user).count()
                print(f"  - User {user.id} ({user.email}): {count} séances")
                
                # Exemples de séances
                seances = SeanceSimple.objects.filter(utilisateur=user)[:3]
                for seance in seances:
                    print(f"    → ID: {seance.id}, Machine: {seance.machine_nom}, Date: {seance.date_seance}")
        
    except Exception as e:
        print(f"[ERROR] SeanceSimple: {e}")
    
    # 4. Vérifier SeanceEntrainement (Workouts)
    try:
        total_entrainement = SeanceEntrainement.objects.count()
        print(f"\n[SEANCE_ENTRAINEMENT] Total: {total_entrainement}")
        
        if total_entrainement > 0:
            # Par utilisateur
            for user in User.objects.all()[:3]:
                count = SeanceEntrainement.objects.filter(utilisateur=user).count()
                print(f"  - User {user.id} ({user.email}): {count} séances")
                
                # Exemples de séances
                seances = SeanceEntrainement.objects.filter(utilisateur=user)[:3]
                for seance in seances:
                    print(f"    → ID: {seance.id}, Nom: {seance.nom}, Date: {seance.date_prevue}, Statut: {seance.statut}")
                    print(f"      Exercices: {seance.exercices.count()}")
        
    except Exception as e:
        print(f"[ERROR] SeanceEntrainement: {e}")
    
    # 5. Vérifier directement dans la BDD via SQL
    try:
        with connection.cursor() as cursor:
            print(f"\n[SQL] Vérification directe...")
            
            # Table SeanceSimple
            cursor.execute("SELECT COUNT(*) FROM workouts_seancesimple")
            count_simple_sql = cursor.fetchone()[0]
            print(f"  - workouts_seancesimple: {count_simple_sql} lignes")
            
            # Table SeanceEntrainement
            cursor.execute("SELECT COUNT(*) FROM workouts_seanceentrainement")
            count_entrainement_sql = cursor.fetchone()[0]
            print(f"  - workouts_seanceentrainement: {count_entrainement_sql} lignes")
            
            # Dernières insertions SeanceSimple
            cursor.execute("""
                SELECT id, machine_nom, date_seance, created_at, utilisateur_id 
                FROM workouts_seancesimple 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_simple = cursor.fetchall()
            print(f"  - Dernières SeanceSimple:")
            for row in recent_simple:
                print(f"    → ID: {row[0]}, Machine: {row[1]}, Date: {row[2]}, User: {row[4]}")
            
            # Dernières insertions SeanceEntrainement
            cursor.execute("""
                SELECT id, nom, date_prevue, statut, created_at, utilisateur_id 
                FROM workouts_seanceentrainement 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_entrainement = cursor.fetchall()
            print(f"  - Dernières SeanceEntrainement:")
            for row in recent_entrainement:
                print(f"    → ID: {row[0]}, Nom: {row[1]}, Date: {row[2]}, Statut: {row[3]}, User: {row[5]}")
                
    except Exception as e:
        print(f"[ERROR] Requêtes SQL: {e}")
    
    # 6. Vérifier les settings de BDD
    try:
        from django.conf import settings
        print(f"\n[SETTINGS] Base de données configurée:")
        db_config = settings.DATABASES['default']
        print(f"  - Engine: {db_config['ENGINE']}")
        print(f"  - Name: {db_config['NAME']}")
        if 'HOST' in db_config:
            print(f"  - Host: {db_config['HOST']}")
        if 'PORT' in db_config:
            print(f"  - Port: {db_config['PORT']}")
    except Exception as e:
        print(f"[ERROR] Settings: {e}")
    
    print("\n" + "=" * 60)
    print("DEBUG TERMINÉ")
    print("=" * 60)

if __name__ == '__main__':
    debug_bdd_complete()
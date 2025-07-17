#!/usr/bin/env python
"""
Script pour corriger manuellement la base de données SQLite
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.production')
django.setup()

from django.db import connection

def fix_database():
    """Corrige la taille du champ image_gif pour SQLite"""
    print("🔧 Correction de la base de données SQLite...")

    with connection.cursor() as cursor:
        try:
            # Vérifier la structure actuelle
            cursor.execute("PRAGMA table_info(machines_machine);")
            columns = cursor.fetchall()

            # Chercher le champ image_gif
            image_gif_column = None
            for column in columns:
                if column[1] == 'image_gif':
                    image_gif_column = column
                    break

            if image_gif_column:
                print(f"📊 Champ image_gif trouvé: {image_gif_column}")

                # SQLite ne peut pas modifier la taille d'une colonne directement
                # Nous devons recréer la table
                print("🔧 Recréation de la table avec la bonne structure...")

                # Créer une table temporaire avec la bonne structure
                cursor.execute("""
                    CREATE TABLE machines_machine_temp (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom VARCHAR(100) NOT NULL,
                        nom_anglais VARCHAR(100) NOT NULL,
                        description TEXT NOT NULL,
                        instructions TEXT NOT NULL,
                        type_exercice VARCHAR(15) NOT NULL,
                        categorie_id INTEGER NOT NULL,
                        increment_poids REAL NOT NULL,
                        poids_minimum REAL NOT NULL,
                        poids_maximum REAL NOT NULL,
                        niveau_difficulte VARCHAR(15) NOT NULL,
                        popularite INTEGER NOT NULL,
                        est_disponible BOOLEAN NOT NULL,
                        necessite_supervision BOOLEAN NOT NULL,
                        image_principale VARCHAR(100),
                        image_gif VARCHAR(500),
                        video_demonstration VARCHAR(200),
                        fabricant VARCHAR(50) NOT NULL,
                        modele VARCHAR(50) NOT NULL,
                        numero_serie VARCHAR(50) NOT NULL,
                        ordre_affichage INTEGER NOT NULL,
                        tags VARCHAR(200) NOT NULL,
                        nombre_utilisations INTEGER NOT NULL,
                        note_moyenne REAL NOT NULL,
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        deleted_at DATETIME,
                        is_deleted BOOLEAN NOT NULL
                    );
                """)

                # Copier les données
                cursor.execute("""
                    INSERT INTO machines_machine_temp
                    SELECT * FROM machines_machine;
                """)

                # Supprimer l'ancienne table
                cursor.execute("DROP TABLE machines_machine;")

                # Renommer la nouvelle table
                cursor.execute("ALTER TABLE machines_machine_temp RENAME TO machines_machine;")

                print("✅ Table recréée avec image_gif VARCHAR(500)")

            else:
                print("❌ Champ image_gif non trouvé")

        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    fix_database()
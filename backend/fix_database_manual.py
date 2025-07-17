#!/usr/bin/env python
"""
Script pour corriger manuellement la base de données PostgreSQL
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
    """Corrige la taille du champ image_gif pour PostgreSQL ou SQLite"""
    print("🔧 Correction de la base de données...")

    # Détecter le type de base de données
    db_engine = connection.vendor
    print(f"📊 Type de base de données: {db_engine}")

    with connection.cursor() as cursor:
        try:
            if db_engine == 'postgresql':
                # PostgreSQL
                print("🔧 Utilisation de PostgreSQL...")
                cursor.execute("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = 'machines_machine' AND column_name = 'image_gif';
                """)
                result = cursor.fetchone()

                if result:
                    column_name, data_type, max_length = result
                    print(f"📊 Structure actuelle: {result}")

                    if max_length and max_length < 500:
                        cursor.execute("""
                            ALTER TABLE machines_machine ALTER COLUMN image_gif TYPE VARCHAR(500);
                        """)
                        print("✅ Champ image_gif modifié vers VARCHAR(500)")
                    else:
                        print("✅ Le champ est déjà correct (taille >= 500)")
                else:
                    print("❌ Champ image_gif non trouvé")

            else:
                # SQLite
                print("🔧 Utilisation de SQLite...")
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
                    print("✅ SQLite n'a pas de limite de taille pour VARCHAR")
                    print("✅ Le champ peut accepter les URLs Cloudinary")
                else:
                    print("❌ Champ image_gif non trouvé")

        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    fix_database()
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
    """Corrige la taille du champ image_gif pour PostgreSQL"""
    print("🔧 Correction de la base de données PostgreSQL...")

    with connection.cursor() as cursor:
        try:
            # Vérifier la structure actuelle
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
                    # Modifier la taille du champ
                    print("🔧 Modification de la taille du champ...")
                    cursor.execute("""
                        ALTER TABLE machines_machine ALTER COLUMN image_gif TYPE VARCHAR(500);
                    """)
                    print("✅ Champ image_gif modifié vers VARCHAR(500)")

                    # Vérifier la modification
                    cursor.execute("""
                        SELECT column_name, data_type, character_maximum_length
                        FROM information_schema.columns
                        WHERE table_name = 'machines_machine' AND column_name = 'image_gif';
                    """)
                    result = cursor.fetchone()
                    print(f"📊 Nouvelle structure: {result}")
                else:
                    print("✅ Le champ est déjà correct (taille >= 500)")

            else:
                print("❌ Champ image_gif non trouvé")

        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    fix_database()
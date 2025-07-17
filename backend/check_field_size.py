#!/usr/bin/env python
"""
Script pour vérifier la taille du champ image_gif
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

def check_field_size():
    """Vérifie la taille du champ image_gif pour PostgreSQL ou SQLite"""
    print("🔍 Vérification de la taille du champ image_gif...")

    # Détecter le type de base de données
    db_engine = connection.vendor
    print(f"📊 Type de base de données: {db_engine}")

    with connection.cursor() as cursor:
        try:
            if db_engine == 'postgresql':
                # PostgreSQL
                cursor.execute("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = 'machines_machine' AND column_name = 'image_gif';
                """)
                result = cursor.fetchone()

                if result:
                    column_name, data_type, max_length = result
                    print(f"📊 Champ: {column_name}")
                    print(f"📊 Type: {data_type}")
                    print(f"📊 Taille max: {max_length} caractères")

                    if max_length and max_length >= 500:
                        print("✅ Le champ peut accepter les URLs Cloudinary !")
                    else:
                        print("❌ Le champ est trop petit pour les URLs Cloudinary")
                        print("💡 Il faut appliquer la migration")
                else:
                    print("❌ Champ image_gif non trouvé")

            else:
                # SQLite
                cursor.execute("PRAGMA table_info(machines_machine);")
                columns = cursor.fetchall()

                # Chercher le champ image_gif
                image_gif_column = None
                for column in columns:
                    if column[1] == 'image_gif':
                        image_gif_column = column
                        break

                if image_gif_column:
                    column_name = image_gif_column[1]
                    data_type = image_gif_column[2]
                    print(f"📊 Champ: {column_name}")
                    print(f"📊 Type: {data_type}")
                    print("✅ SQLite n'a pas de limite de taille pour VARCHAR")
                    print("✅ Le champ peut accepter les URLs Cloudinary !")
                else:
                    print("❌ Champ image_gif non trouvé")

        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    check_field_size()
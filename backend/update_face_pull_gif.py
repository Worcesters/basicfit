#!/usr/bin/env python3
"""
Script pour ajouter l'URL du GIF au Face Pull
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.machines.models import Machine

def update_face_pull_gif():
    """Met à jour le Face Pull avec l'URL du GIF"""
    try:
        # Chercher le Face Pull
        face_pull = Machine.objects.filter(nom__icontains='Face Pull').first()

        if face_pull:
            print(f"✅ Face Pull trouvé: {face_pull.nom}")

            # URL du GIF
            gif_url = "https://res.cloudinary.com/dnernoibr/image/upload/v1752739063/basicfit/machines/gifs/machine_pull-up.gif"

            # Mettre à jour
            face_pull.image_gif = gif_url
            face_pull.save()

            print(f"✅ URL GIF ajoutée: {gif_url}")
            print(f"✅ Machine mise à jour: {face_pull.nom}")

            # Vérifier
            face_pull.refresh_from_db()
            print(f"✅ Vérification - image_gif: {face_pull.image_gif}")

        else:
            print("❌ Face Pull non trouvé")

    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")

if __name__ == "__main__":
    update_face_pull_gif()
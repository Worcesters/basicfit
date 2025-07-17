from django.core.management.base import BaseCommand
from apps.machines.models import Machine
from apps.machines.services import CloudinaryService
from pathlib import Path
import os

class Command(BaseCommand):
    help = 'Migre les GIFs locaux vers Cloudinary'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Migration des GIFs vers Cloudinary...")

        # Récupérer toutes les machines avec des GIFs locaux
        machines_with_local_gifs = Machine.objects.filter(
            image_gif__startswith='machines/'
        ).exclude(image_gif='')

        self.stdout.write(f"📊 {machines_with_local_gifs.count()} machines à migrer")

        cloudinary_service = CloudinaryService()

        for machine in machines_with_local_gifs:
            try:
                # Chemin du fichier local
                local_path = Path('media') / machine.image_gif

                if local_path.exists():
                    self.stdout.write(f"📤 Migration de {machine.nom} ({machine.image_gif})")

                    # Upload vers Cloudinary
                    with open(local_path, 'rb') as f:
                        cloudinary_url = cloudinary_service.upload_image(f)

                    # Mise à jour de l'URL
                    machine.image_gif = cloudinary_url
                    machine.save()

                    self.stdout.write(
                        self.style.SUCCESS(f"✅ {machine.nom} migré vers: {cloudinary_url}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"❌ Fichier non trouvé: {local_path}")
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur pour {machine.nom}: {e}")
                )

        self.stdout.write(self.style.SUCCESS("🎉 Migration terminée!"))
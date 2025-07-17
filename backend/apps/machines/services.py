"""
Service pour uploader les images sur Cloudinary
"""
import os
import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

class CloudinaryService:
    """Service pour uploader des images sur Cloudinary"""

    def __init__(self):
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET')
        )

    def upload_image(self, image_file: UploadedFile) -> str:
        """
        Upload une image sur Cloudinary et retourne l'URL

        Args:
            image_file: Fichier image uploadé via Django

        Returns:
            str: URL de l'image sur Cloudinary
        """
        try:
            # Upload sur Cloudinary
            result = cloudinary.uploader.upload(
                image_file,
                folder="basicfit/machines/gifs",
                public_id=f"machine_{image_file.name.split('.')[0]}",
                overwrite=True
            )

            return result['secure_url']  # URL HTTPS de l'image

        except Exception as e:
            raise Exception(f"Erreur upload Cloudinary: {str(e)}")

    def delete_image(self, cloudinary_url: str) -> bool:
        """
        Supprime une image de Cloudinary (optionnel)

        Args:
            cloudinary_url: URL de l'image sur Cloudinary

        Returns:
            bool: True si supprimé avec succès
        """
        try:
            # Extraire le public_id depuis l'URL
            # Ex: https://res.cloudinary.com/basicfit-app/image/upload/v1234567890/basicfit/machines/gifs/machine_chin_assist.gif
            parts = cloudinary_url.split('/')
            public_id = '/'.join(parts[parts.index('upload')+2:]).split('.')[0]

            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'

        except Exception:
            return False
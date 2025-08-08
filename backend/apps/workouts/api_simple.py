"""
API Simple pour le calendrier - Version CSV uniquement
100% synchronisé avec la BDD, pas de stockage local
"""
import logging
import csv
import io
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models_simple import SeanceSimple

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seances_simples(request):
    """
    Récupérer toutes les séances simples de l'utilisateur
    GET /api/workouts/simple/
    """
    try:
        user = request.user
        
        # Récupérer toutes les séances de l'utilisateur
        seances = SeanceSimple.objects.filter(utilisateur=user).order_by('-date_seance', 'machine_nom')
        
        # Convertir en format simple pour Android
        seances_data = []
        for seance in seances:
            seances_data.append({
                'id': seance.id,
                'machine': seance.machine_nom,
                'date': seance.date_seance.isoformat(),
                'type': seance.type_exercice,
                'duree': seance.duree_minutes,
                'note': seance.note_ressenti,
                'commentaire': seance.commentaire,
                'created_at': seance.created_at.isoformat()
            })
        
        return Response({
            'success': True,
            'data': seances_data,
            'count': len(seances_data),
            'message': f'{len(seances_data)} séances récupérées'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur get_seances_simples: {e}")
        return Response({
            'success': False,
            'data': [],
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_csv_seances(request):
    """
    Importer des séances depuis un CSV
    POST /api/workouts/simple/import/
    
    Payload: {
        "csv_data": "machine,date,type\nTapis,2025-01-01,CARDIO\n..."
    }
    """
    try:
        user = request.user
        
        # Récupérer les données CSV
        csv_text = request.data.get('csv_data', '').strip()
        if not csv_text:
            return Response({
                'success': False,
                'message': 'Données CSV manquantes'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parser le CSV
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        csv_data = []
        
        # Validation des colonnes
        expected_columns = {'machine', 'date', 'type'}
        if not expected_columns.issubset(set(csv_reader.fieldnames or [])):
            return Response({
                'success': False,
                'message': f'Colonnes CSV invalides. Attendu: {expected_columns}, Reçu: {csv_reader.fieldnames}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Lire toutes les lignes
        for row in csv_reader:
            csv_data.append(row)
        
        if not csv_data:
            return Response({
                'success': False,
                'message': 'Aucune donnée trouvée dans le CSV'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Importer les données
        imported_count, errors = SeanceSimple.import_from_csv_data(user, csv_data)
        
        # Préparer la réponse
        response_data = {
            'success': True,
            'imported_count': imported_count,
            'total_lines': len(csv_data),
            'errors_count': len(errors),
            'message': f'{imported_count} séances importées avec succès'
        }
        
        if errors:
            response_data['errors'] = errors[:10]  # Limiter à 10 erreurs
            response_data['message'] += f' ({len(errors)} erreurs)'
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erreur import_csv_seances: {e}")
        return Response({
            'success': False,
            'message': f'Erreur import: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_seances(request):
    """
    Supprimer TOUTES les séances de l'utilisateur
    DELETE /api/workouts/simple/delete-all/
    """
    try:
        user = request.user
        
        # Supprimer toutes les séances
        deleted_count = SeanceSimple.delete_all_for_user(user)
        
        return Response({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'{deleted_count} séances supprimées'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur delete_all_seances: {e}")
        return Response({
            'success': False,
            'message': f'Erreur suppression: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar_summary(request):
    """
    Résumé du calendrier pour l'affichage
    GET /api/workouts/simple/summary/
    """
    try:
        user = request.user
        
        # Statistiques par date
        from django.db.models import Count
        from collections import defaultdict
        
        seances = SeanceSimple.objects.filter(utilisateur=user).order_by('-date_seance')
        
        # Regrouper par date
        calendar_data = defaultdict(list)
        total_seances = 0
        
        for seance in seances:
            date_str = seance.date_seance.isoformat()
            calendar_data[date_str].append({
                'id': seance.id,
                'machine': seance.machine_nom,
                'type': seance.type_exercice,
                'duree': seance.duree_minutes
            })
            total_seances += 1
        
        # Convertir en format final
        calendar_entries = []
        for date_str, seances_list in calendar_data.items():
            calendar_entries.append({
                'date': date_str,
                'seances_count': len(seances_list),
                'seances': seances_list,
                'types': list(set(s['type'] for s in seances_list))
            })
        
        # Trier par date décroissante
        calendar_entries.sort(key=lambda x: x['date'], reverse=True)
        
        return Response({
            'success': True,
            'data': {
                'calendar_entries': calendar_entries[:100],  # Limiter à 100 dates
                'total_seances': total_seances,
                'total_dates': len(calendar_entries),
                'derniere_seance': seances.first().date_seance.isoformat() if seances.exists() else None
            },
            'message': 'Résumé calendrier généré'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur get_calendar_summary: {e}")
        return Response({
            'success': False,
            'message': f'Erreur résumé: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_seance_simple(request):
    """
    Ajouter une séance simple manuellement
    POST /api/workouts/simple/add/
    
    Payload: {
        "machine": "Tapis de course",
        "date": "2025-01-01",
        "type": "CARDIO",
        "duree": 30,
        "note": 7,
        "commentaire": "Bonne séance"
    }
    """
    try:
        user = request.user
        data = request.data
        
        # Validation des données requises
        required_fields = ['machine', 'date', 'type']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'success': False,
                    'message': f'Champ manquant: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parser la date
        from datetime import datetime
        try:
            date_obj = datetime.fromisoformat(data['date']).date()
        except ValueError:
            return Response({
                'success': False,
                'message': 'Format de date invalide. Utilisez YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la séance
        seance = SeanceSimple.objects.create(
            utilisateur=user,
            machine_nom=data['machine'].strip(),
            date_seance=date_obj,
            type_exercice=data.get('type', 'AUTRE').upper(),
            duree_minutes=data.get('duree'),
            note_ressenti=data.get('note'),
            commentaire=data.get('commentaire', '').strip()
        )
        
        return Response({
            'success': True,
            'data': {
                'id': seance.id,
                'machine': seance.machine_nom,
                'date': seance.date_seance.isoformat(),
                'type': seance.type_exercice
            },
            'message': 'Séance ajoutée avec succès'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erreur add_seance_simple: {e}")
        return Response({
            'success': False,
            'message': f'Erreur ajout: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
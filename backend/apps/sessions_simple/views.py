"""
Endpoints simplifiés pour sessions d'entraînement
Robuste et avec logging complet
"""
import logging
import json
from datetime import datetime
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .models import SessionSimple, ExerciceSimple, ImportCSVLog

logger = logging.getLogger(__name__)

# ===== UTILITAIRES =====
def session_to_dict(session):
    """Convertir une session en dictionnaire"""
    return {
        'id': session.id,
        'nom': session.nom,
        'date': session.date.isoformat(),
        'duree': session.duree,
        'note_ressenti': session.note_ressenti,
        'commentaire': session.commentaire,
        'exercices_count': session.exercices.count(),
        'exercices': [exercice_to_dict(ex) for ex in session.exercices.all()]
    }

def exercice_to_dict(exercice):
    """Convertir un exercice en dictionnaire"""
    return {
        'id': exercice.id,
        'nom': exercice.nom,
        'series': exercice.series,
        'reps': exercice.reps,
        'poids': exercice.poids
    }

# ===== ENDPOINTS =====

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_sessions(request):
    """
    Liste des sessions pour l'utilisateur connecté
    GET /api/sessions/
    """
    try:
        user = request.user
        logger.info(f"📋 LISTE SESSIONS - User: {user.id} ({user.email})")
        
        sessions = SessionSimple.objects.filter(user=user).prefetch_related('exercices')
        
        data = [session_to_dict(session) for session in sessions]
        
        logger.info(f"✅ SESSIONS RÉCUPÉRÉES - Count: {len(data)}")
        
        return Response({
            'success': True,
            'data': data,
            'count': len(data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR LISTE SESSIONS: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur récupération sessions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_session(request):
    """
    Sauvegarder une nouvelle session
    POST /api/sessions/save/
    
    Body: {
        "nom": "Mon entraînement",
        "date": "2024-01-15T10:30:00",
        "duree": 60,
        "note_ressenti": 8,
        "commentaire": "Bon entraînement",
        "exercices": [
            {
                "nom": "Développé couché",
                "series": 3,
                "reps": 12,
                "poids": 80.0
            }
        ]
    }
    """
    try:
        user = request.user
        data = request.data
        
        logger.info(f"💾 SAUVEGARDE SESSION - User: {user.id} ({user.email})")
        logger.info(f"   Nom: {data.get('nom', 'N/A')}")
        logger.info(f"   Date: {data.get('date', 'N/A')}")
        logger.info(f"   Exercices: {len(data.get('exercices', []))}")
        
        # Validation des données
        required_fields = ['nom', 'date', 'duree', 'note_ressenti']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Champ manquant: {field}")
                return Response({
                    'success': False,
                    'message': f'Champ requis manquant: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parser la date
        try:
            date_session = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            logger.warning(f"Format de date invalide: {data.get('date')} - {e}")
            return Response({
                'success': False,
                'message': 'Format de date invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Transaction atomique
        with transaction.atomic():
            # Créer la session
            session = SessionSimple.objects.create(
                user=user,
                nom=data['nom'],
                date=date_session,
                duree=int(data['duree']),
                note_ressenti=int(data['note_ressenti']),
                commentaire=data.get('commentaire', '')
            )
            
            logger.info(f"✅ SESSION CRÉÉE - ID: {session.id}")
            
            # Ajouter les exercices
            exercices_data = data.get('exercices', [])
            exercices_created = 0
            
            for ex_data in exercices_data:
                if all(key in ex_data for key in ['nom', 'series', 'reps', 'poids']):
                    exercice = ExerciceSimple.objects.create(
                        session=session,
                        nom=ex_data['nom'],
                        series=int(ex_data['series']),
                        reps=int(ex_data['reps']),
                        poids=float(ex_data['poids'])
                    )
                    exercices_created += 1
                    logger.debug(f"   Exercice créé: {exercice.nom}")
                else:
                    logger.warning(f"Exercice incomplet ignoré: {ex_data}")
            
            logger.info(f"✅ EXERCICES CRÉÉS - Count: {exercices_created}")
            
            return Response({
                'success': True,
                'message': 'Session sauvegardée avec succès',
                'data': {
                    'session_id': session.id,
                    'exercices_count': exercices_created
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"💥 ERREUR SAUVEGARDE SESSION: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur sauvegarde session'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_csv(request):
    """
    Import CSV de sessions
    POST /api/sessions/import/
    
    Body: {
        "csv_data": "date,machine,type,duree\n2024-01-15,Développé couché,PRISE_MASSE,60"
    }
    """
    try:
        user = request.user
        csv_data = request.data.get('csv_data', '')
        
        logger.info(f"📁 IMPORT CSV - User: {user.id} ({user.email})")
        logger.info(f"   Taille données: {len(csv_data)} caractères")
        
        if not csv_data.strip():
            return Response({
                'success': False,
                'message': 'Données CSV vides'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parser le CSV
        lines = csv_data.strip().split('\n')
        total_lines = len(lines) - 1  # Exclure l'en-tête
        imported_count = 0
        errors_count = 0
        errors = []
        
        logger.info(f"   Lignes à traiter: {total_lines}")
        
        # Ignorer la première ligne (en-tête)
        for i, line in enumerate(lines[1:], 1):
            try:
                parts = line.split(',')
                if len(parts) >= 4:
                    date_str, machine, type_entrainement, duree_str = parts[:4]
                    
                    # Parser la date
                    try:
                        date_session = datetime.strptime(date_str.strip(), '%Y-%m-%d')
                    except ValueError:
                        try:
                            date_session = datetime.strptime(date_str.strip(), '%d/%m/%Y')
                        except ValueError:
                            raise ValueError(f"Format de date non reconnu: {date_str}")
                    
                    # Créer la session
                    with transaction.atomic():
                        session = SessionSimple.objects.create(
                            user=user,
                            nom=f"{machine.strip()} ({type_entrainement.strip()})",
                            date=date_session,
                            duree=int(duree_str.strip()) if duree_str.strip().isdigit() else 30,
                            note_ressenti=5,
                            commentaire=f"Importé depuis CSV - Type: {type_entrainement.strip()}"
                        )
                        
                        # Ajouter un exercice par défaut
                        ExerciceSimple.objects.create(
                            session=session,
                            nom=machine.strip(),
                            series=3,
                            reps=12,
                            poids=50.0
                        )
                    
                    imported_count += 1
                    logger.debug(f"   Ligne {i} importée: {machine.strip()}")
                else:
                    errors.append(f"Ligne {i}: Format incorrect")
                    errors_count += 1
                    
            except Exception as e:
                errors.append(f"Ligne {i}: {str(e)}")
                errors_count += 1
                logger.warning(f"Erreur ligne {i}: {e}")
        
        # Log de l'import
        ImportCSVLog.objects.create(
            user=user,
            total_lines=total_lines,
            imported_count=imported_count,
            errors_count=errors_count,
            errors_detail='\n'.join(errors)
        )
        
        logger.info(f"✅ IMPORT CSV TERMINÉ - Importées: {imported_count}/{total_lines}, Erreurs: {errors_count}")
        
        return Response({
            'success': True,
            'message': f'Import terminé: {imported_count} sessions importées',
            'imported_count': imported_count,
            'total_lines': total_lines,
            'errors_count': errors_count,
            'errors': errors[:10]  # Limiter les erreurs affichées
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR IMPORT CSV: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur import CSV'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_sessions(request):
    """
    Supprimer toutes les sessions de l'utilisateur
    DELETE /api/sessions/clear/
    """
    try:
        user = request.user
        logger.info(f"🗑️ SUPPRESSION TOUTES SESSIONS - User: {user.id} ({user.email})")
        
        count = SessionSimple.objects.filter(user=user).count()
        SessionSimple.objects.filter(user=user).delete()
        
        logger.info(f"✅ SESSIONS SUPPRIMÉES - Count: {count}")
        
        return Response({
            'success': True,
            'message': f'{count} sessions supprimées',
            'deleted_count': count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR SUPPRESSION SESSIONS: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur suppression sessions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_statistics(request):
    """
    Statistiques des sessions
    GET /api/sessions/stats/
    """
    try:
        user = request.user
        logger.debug(f"📊 STATISTIQUES - User: {user.id}")
        
        sessions = SessionSimple.objects.filter(user=user)
        total_sessions = sessions.count()
        
        if total_sessions > 0:
            total_duree = sum(s.duree for s in sessions)
            avg_duree = total_duree / total_sessions
            total_exercices = sum(s.exercices.count() for s in sessions)
        else:
            total_duree = 0
            avg_duree = 0
            total_exercices = 0
        
        stats = {
            'total_sessions': total_sessions,
            'total_duree_minutes': total_duree,
            'moyenne_duree_minutes': round(avg_duree, 1),
            'total_exercices': total_exercices
        }
        
        logger.debug(f"✅ STATISTIQUES CALCULÉES: {stats}")
        
        return Response({
            'success': True,
            'data': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR STATISTIQUES: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur calcul statistiques'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
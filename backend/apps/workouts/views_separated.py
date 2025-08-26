"""
API séparée pour calendrier et exercices effectués
Sépare la planification (calendrier) des séances réellement effectuées (analyse)
"""
import logging
from datetime import datetime, date
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from .models_refactored import (
    SeanceEffectuee, ExerciceEffectue, SerieEffectuee,
    CalendrierSeance, ExercicePlanifie
)
from apps.machines.models import Machine
from apps.core.models import ModeEntrainement

logger = logging.getLogger(__name__)

# ===== UTILITAIRES =====

def seance_effectuee_to_dict(seance):
    """Convertir une séance effectuée en dictionnaire"""
    return {
        'id': seance.id,
        'nom': seance.nom,
        'date_debut': seance.date_debut.isoformat(),
        'date_fin': seance.date_fin.isoformat(),
        'date_seance': seance.date_seance.isoformat(),
        'duree_minutes': seance.duree_minutes,
        'volume_total': seance.volume_total,
        'tonnage_total': seance.tonnage_total,
        'nombre_exercices': seance.nombre_exercices,
        'note_ressenti': seance.note_ressenti,
        'commentaire': seance.commentaire,
        'exercices': [exercice_effectue_to_dict(ex) for ex in seance.exercices.all()]
    }

def exercice_effectue_to_dict(exercice):
    """Convertir un exercice effectué en dictionnaire"""
    return {
        'id': exercice.id,
        'nom_exercice': exercice.nom_exercice,
        'machine_id': exercice.machine.id,
        'machine_nom': exercice.machine.nom,
        'ordre': exercice.ordre_dans_seance,
        'series_realisees': exercice.series_realisees,
        'repetitions_totales': exercice.repetitions_totales,
        'poids_moyen': exercice.poids_moyen,
        'volume_exercice': exercice.volume_exercice,
        'taux_reussite': exercice.taux_reussite,
        'series': [serie_effectuee_to_dict(serie) for serie in exercice.series.all()]
    }

def serie_effectuee_to_dict(serie):
    """Convertir une série effectuée en dictionnaire"""
    return {
        'numero': serie.numero_serie,
        'repetitions_prevues': serie.repetitions_prevues,
        'repetitions_realisees': serie.repetitions_realisees,
        'poids_utilise': serie.poids_utilise,
        'est_reussie': serie.est_reussie,
        'pourcentage_reussite': serie.pourcentage_reussite
    }

def calendrier_seance_to_dict(seance):
    """Convertir une séance planifiée en dictionnaire"""
    return {
        'id': seance.id,
        'nom': seance.nom,
        'date_prevue': seance.date_prevue.isoformat(),
        'duree_prevue': seance.duree_prevue,
        'statut': seance.statut,
        'mode_entrainement': seance.mode_entrainement.nom if seance.mode_entrainement else None,
        'description': seance.description,
        'seance_effectuee_id': seance.seance_effectuee.id if seance.seance_effectuee else None,
        'exercices_planifies': [exercice_planifie_to_dict(ex) for ex in seance.exercices_planifies.all()]
    }

def exercice_planifie_to_dict(exercice):
    """Convertir un exercice planifié en dictionnaire"""
    return {
        'id': exercice.id,
        'machine_id': exercice.machine.id,
        'machine_nom': exercice.machine.nom,
        'ordre_prevu': exercice.ordre_prevu,
        'series_prevues': exercice.series_prevues,
        'repetitions_prevues': exercice.repetitions_prevues,
        'poids_prevu': exercice.poids_prevu,
        'repos_prevu': exercice.repos_prevu
    }

# ===== API CALENDRIER (PLANIFICATION) =====

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_csv_to_calendar(request):
    """
    Importer des séances CSV dans le calendrier (planification)
    POST /api/workouts-v2/calendrier/import/
    """
    try:
        user = request.user
        csv_data = request.data.get('csv_data', '')
        
        logger.info(f"📁 IMPORT CSV CALENDRIER - User: {user.id}")
        
        if not csv_data.strip():
            return Response({
                'success': False,
                'message': 'Données CSV vides'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        lines = csv_data.strip().split('\n')
        total_lines = len(lines) - 1
        imported_count = 0
        errors_count = 0
        errors = []
        
        # Ignorer la première ligne (en-tête)
        for i, line in enumerate(lines[1:], 1):
            try:
                parts = line.split(',')
                if len(parts) >= 4:
                    date_str, machine_name, type_entrainement, duree_str = parts[:4]
                    
                    # Parser la date
                    try:
                        date_session = datetime.strptime(date_str.strip(), '%Y-%m-%d')
                    except ValueError:
                        try:
                            date_session = datetime.strptime(date_str.strip(), '%d/%m/%Y')
                        except ValueError:
                            raise ValueError(f"Format de date non reconnu: {date_str}")
                    
                    # Créer la séance planifiée dans le calendrier
                    with transaction.atomic():
                        calendrier_seance = CalendrierSeance.objects.create(
                            utilisateur=user,
                            nom=f"{machine_name.strip()} ({type_entrainement.strip()})",
                            date_prevue=date_session,
                            duree_prevue=int(duree_str.strip()) if duree_str.strip().isdigit() else 60,
                            statut='PLANIFIEE',
                            description=f"Importé depuis CSV - Type: {type_entrainement.strip()}"
                        )
                        
                        # Ajouter l'exercice planifié si on trouve la machine
                        try:
                            from apps.machines.models import Machine
                            machine = Machine.objects.filter(
                                nom__icontains=machine_name.strip().split()[0]
                            ).first()
                            
                            if machine:
                                ExercicePlanifie.objects.create(
                                    calendrier_seance=calendrier_seance,
                                    machine=machine,
                                    ordre_prevu=1,
                                    series_prevues=3,
                                    repetitions_prevues=12,
                                    poids_prevu=50.0,
                                    repos_prevu=90
                                )
                        except Exception:
                            # Continuer même si on ne trouve pas la machine
                            pass
                    
                    imported_count += 1
                    logger.debug(f"   Séance planifiée importée: {machine_name.strip()}")
                else:
                    errors.append(f"Ligne {i}: Format incorrect")
                    errors_count += 1
                    
            except Exception as e:
                errors.append(f"Ligne {i}: {str(e)}")
                errors_count += 1
                logger.warning(f"Erreur ligne {i}: {e}")
        
        logger.info(f"✅ IMPORT CSV CALENDRIER TERMINÉ - Importées: {imported_count}/{total_lines}")
        
        return Response({
            'success': True,
            'message': f'Import calendrier terminé: {imported_count} séances planifiées',
            'imported_count': imported_count,
            'total_lines': total_lines,
            'errors_count': errors_count,
            'errors': errors[:10]
        })
        
    except Exception as e:
        logger.error(f"💥 ERREUR IMPORT CSV CALENDRIER: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur import CSV calendrier'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===== API CALENDRIER (PLANIFICATION) =====

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_calendrier(request):
    """
    Liste des séances planifiées pour l'utilisateur
    GET /api/workouts/calendrier/
    """
    try:
        user = request.user
        logger.info(f"📅 LISTE CALENDRIER - User: {user.id}")
        
        seances = CalendrierSeance.objects.filter(
            utilisateur=user
        ).select_related(
            'mode_entrainement', 'seance_effectuee'
        ).prefetch_related('exercices_planifies__machine')
        
        data = [calendrier_seance_to_dict(seance) for seance in seances]
        
        logger.info(f"✅ CALENDRIER RÉCUPÉRÉ - Count: {len(data)}")
        return Response({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        logger.error(f"💥 ERREUR LISTE CALENDRIER: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur récupération calendrier'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_seance_planifiee(request):
    """
    Créer une nouvelle séance planifiée
    POST /api/workouts/calendrier/create/
    """
    try:
        user = request.user
        data = request.data
        
        logger.info(f"📝 CRÉATION SÉANCE PLANIFIÉE - User: {user.id}")
        
        with transaction.atomic():
            # Créer la séance planifiée
            seance = CalendrierSeance.objects.create(
                utilisateur=user,
                nom=data.get('nom', 'Entraînement'),
                date_prevue=datetime.fromisoformat(data['date_prevue']),
                duree_prevue=data.get('duree_prevue', 60),
                description=data.get('description', ''),
                statut='PLANIFIEE'
            )
            
            # Ajouter les exercices planifiés
            exercices_data = data.get('exercices', [])
            for i, ex_data in enumerate(exercices_data):
                machine = Machine.objects.get(id=ex_data['machine_id'])
                ExercicePlanifie.objects.create(
                    calendrier_seance=seance,
                    machine=machine,
                    ordre_prevu=i + 1,
                    series_prevues=ex_data.get('series_prevues', 3),
                    repetitions_prevues=ex_data.get('repetitions_prevues', 12),
                    poids_prevu=ex_data.get('poids_prevu', 50.0),
                    repos_prevu=ex_data.get('repos_prevu', 90)
                )
            
            logger.info(f"✅ SÉANCE PLANIFIÉE CRÉÉE - ID: {seance.id}")
            return Response({
                'success': True,
                'message': 'Séance planifiée créée',
                'data': {'seance_id': seance.id}
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"💥 ERREUR CRÉATION SÉANCE PLANIFIÉE: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur création séance planifiée'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===== API SÉANCES EFFECTUÉES (HISTORIQUE/ANALYSE) =====

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_seances_effectuees(request):
    """
    Liste des séances réellement effectuées pour l'utilisateur
    GET /api/workouts/effectuees/
    """
    try:
        user = request.user
        logger.info(f"🏋️ LISTE SÉANCES EFFECTUÉES - User: {user.id}")
        
        seances = SeanceEffectuee.objects.filter(
            utilisateur=user
        ).prefetch_related('exercices__machine', 'exercices__series')
        
        data = [seance_effectuee_to_dict(seance) for seance in seances]
        
        logger.info(f"✅ SÉANCES EFFECTUÉES RÉCUPÉRÉES - Count: {len(data)}")
        return Response({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        logger.error(f"💥 ERREUR LISTE SÉANCES EFFECTUÉES: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur récupération séances effectuées'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_seance_effectuee(request):
    """
    Sauvegarder une séance réellement effectuée
    POST /api/workouts/effectuees/save/
    
    Body: {
        "nom": "Mon entraînement",
        "date_debut": "2024-01-15T10:30:00",
        "date_fin": "2024-01-15T11:30:00",
        "note_ressenti": 8,
        "commentaire": "Excellent entraînement",
        "exercices": [
            {
                "nom_exercice": "Développé couché",
                "machine_id": 1,
                "series": [
                    {
                        "numero": 1,
                        "repetitions_prevues": 12,
                        "repetitions_realisees": 12,
                        "poids_utilise": 80.0
                    }
                ]
            }
        ]
    }
    """
    try:
        user = request.user
        data = request.data
        
        logger.info(f"💾 SAUVEGARDE SÉANCE EFFECTUÉE - User: {user.id}")
        
        with transaction.atomic():
            # Créer la séance effectuée
            seance = SeanceEffectuee.objects.create(
                utilisateur=user,
                nom=data['nom'],
                date_debut=datetime.fromisoformat(data['date_debut']),
                date_fin=datetime.fromisoformat(data['date_fin']),
                note_ressenti=data.get('note_ressenti', 5),
                commentaire=data.get('commentaire', '')
            )
            
            # Ajouter les exercices effectués
            exercices_data = data.get('exercices', [])
            for i, ex_data in enumerate(exercices_data):
                machine = Machine.objects.get(id=ex_data['machine_id'])
                
                # Calculer les métriques de l'exercice
                series_data = ex_data.get('series', [])
                total_reps = sum(serie['repetitions_realisees'] for serie in series_data)
                poids_moyen = sum(serie['poids_utilise'] for serie in series_data) / len(series_data) if series_data else 0
                series_reussies = sum(1 for serie in series_data if serie['repetitions_realisees'] >= serie['repetitions_prevues'])
                taux_reussite = (series_reussies / len(series_data) * 100) if series_data else 100
                
                exercice = ExerciceEffectue.objects.create(
                    seance=seance,
                    machine=machine,
                    nom_exercice=ex_data['nom_exercice'],
                    ordre_dans_seance=i + 1,
                    series_realisees=len(series_data),
                    repetitions_totales=total_reps,
                    poids_moyen=poids_moyen,
                    taux_reussite=taux_reussite
                )
                
                # Ajouter les séries effectuées
                for serie_data in series_data:
                    SerieEffectuee.objects.create(
                        exercice=exercice,
                        numero_serie=serie_data['numero'],
                        repetitions_prevues=serie_data['repetitions_prevues'],
                        repetitions_realisees=serie_data['repetitions_realisees'],
                        poids_utilise=serie_data['poids_utilise'],
                        repos_apres_serie=serie_data.get('repos_apres_serie')
                    )
            
            # Calculer les métriques globales de la séance
            exercices = seance.exercices.all()
            seance.nombre_exercices = exercices.count()
            seance.volume_total = sum(ex.volume_exercice for ex in exercices)
            seance.tonnage_total = sum(ex.tonnage_exercice for ex in exercices)
            seance.save()
            
            logger.info(f"✅ SÉANCE EFFECTUÉE SAUVEGARDÉE - ID: {seance.id}")
            return Response({
                'success': True,
                'message': 'Séance effectuée sauvegardée',
                'data': {'seance_id': seance.id}
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"💥 ERREUR SAUVEGARDE SÉANCE EFFECTUÉE: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur sauvegarde séance effectuée'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===== MIGRATION DES DONNÉES EXISTANTES =====

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def migrate_sessions_simples(request):
    """
    Migrer les SessionSimple existantes vers les nouveaux modèles
    POST /api/workouts/migrate/
    """
    try:
        from apps.sessions_simple.models import SessionSimple
        user = request.user
        
        logger.info(f"🔄 MIGRATION SESSIONS SIMPLES - User: {user.id}")
        
        sessions = SessionSimple.objects.filter(user=user)
        migrated_count = 0
        
        with transaction.atomic():
            for session in sessions:
                # Déterminer si c'est une séance effectuée (passée) ou planifiée (future)
                session_date = session.date.date()
                today = date.today()
                
                if session_date <= today and session.duree > 0:
                    # Séance effectuée (passée avec durée)
                    seance_effectuee = SeanceEffectuee.objects.create(
                        utilisateur=user,
                        nom=session.nom,
                        date_debut=session.date,
                        date_fin=session.date.replace(
                            hour=session.date.hour + (session.duree // 60),
                            minute=session.date.minute + (session.duree % 60)
                        ),
                        note_ressenti=session.note_ressenti,
                        commentaire=session.commentaire
                    )
                    
                    # Migrer les exercices
                    for i, exercice_simple in enumerate(session.exercices.all()):
                        try:
                            machine = Machine.objects.filter(
                                nom__icontains=exercice_simple.nom.split()[0]
                            ).first()
                            
                            if machine:
                                ExerciceEffectue.objects.create(
                                    seance=seance_effectuee,
                                    machine=machine,
                                    nom_exercice=exercice_simple.nom,
                                    ordre_dans_seance=i + 1,
                                    series_realisees=exercice_simple.series,
                                    repetitions_totales=exercice_simple.series * exercice_simple.reps,
                                    poids_moyen=exercice_simple.poids,
                                    taux_reussite=100.0  # Assumer 100% pour les données migrées
                                )
                        except Exception as ex_error:
                            logger.warning(f"Erreur migration exercice {exercice_simple.nom}: {ex_error}")
                    
                    migrated_count += 1
                
                else:
                    # Séance planifiée (future ou passée sans durée)
                    CalendrierSeance.objects.create(
                        utilisateur=user,
                        nom=session.nom,
                        date_prevue=session.date,
                        duree_prevue=session.duree if session.duree > 0 else 60,
                        statut='TERMINEE' if session_date < today else 'PLANIFIEE',
                        description=session.commentaire
                    )
                    migrated_count += 1
        
        logger.info(f"✅ MIGRATION TERMINÉE - Migrées: {migrated_count}")
        return Response({
            'success': True,
            'message': f'{migrated_count} sessions migrées',
            'migrated_count': migrated_count
        })
        
    except Exception as e:
        logger.error(f"💥 ERREUR MIGRATION: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur migration'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
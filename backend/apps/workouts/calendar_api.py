"""
API Calendrier BasicFit - Version complètement refaite
Endpoints simplifiés et robustes pour la synchronisation Android
"""
import logging
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone

from .models import SeanceEntrainement, ExerciceSeance, SeriExercice

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workout_history(request):
    """
    Endpoint principal pour récupérer l'historique des séances - Format Android
    GET /api/workouts/history/
    """
    try:
        user = request.user
        
        # Paramètres optionnels
        days_limit = request.query_params.get('days', 365)  # Par défaut, dernière année
        try:
            days_limit = int(days_limit)
        except (ValueError, TypeError):
            days_limit = 365
        
        # Date limite
        date_limit = timezone.now() - timedelta(days=days_limit)
        
        # Récupérer les séances terminées
        seances = SeanceEntrainement.objects.filter(
            utilisateur=user,
            statut='TERMINEE',
            date_prevue__gte=date_limit
        ).prefetch_related(
            'exercices__machine',
            'exercices__series'
        ).order_by('-date_prevue')[:200]  # Limite de sécurité
        
        # Convertir en format Android
        workout_entries = []
        for seance in seances:
            try:
                # Calculer les exercices
                exercises = []
                for exercice in seance.exercices.all():
                    if exercice.machine:
                        # Calculer les moyennes des séries
                        series = exercice.series.all()
                        if series:
                            avg_reps = sum(s.repetitions for s in series) / len(series)
                            total_weight = sum(s.poids * s.repetitions for s in series)
                            max_weight = max(s.poids for s in series) if series else 0
                        else:
                            avg_reps = 0
                            total_weight = 0
                            max_weight = 0
                        
                        exercises.append({
                            'name': exercice.machine.nom,
                            'sets': len(series),
                            'reps': int(avg_reps),
                            'weight': float(max_weight)
                        })
                
                # Créer l'entrée workout
                workout_entry = {
                    'id': seance.id,
                    'date': seance.date_prevue.date().isoformat(),
                    'nom': seance.nom or 'Séance',
                    'mode': seance.nom or 'Entraînement',
                    'duree': seance.duree_reelle or seance.duree_prevue or 0,
                    'exercices': exercises,
                    'totalWeight': sum(ex['weight'] * ex['reps'] for ex in exercises),
                    'status': seance.statut
                }
                
                workout_entries.append(workout_entry)
                
            except Exception as e:
                logger.warning(f"Erreur conversion séance {seance.id}: {e}")
                continue
        
        return Response({
            'success': True,
            'data': workout_entries,
            'message': f'{len(workout_entries)} séances récupérées',
            'count': len(workout_entries)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur get_workout_history: {e}")
        return Response({
            'success': False,
            'data': [],
            'message': f'Erreur récupération historique: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar_data(request):
    """
    Endpoint spécifique calendrier - Format simple
    GET /api/workouts/calendar/
    """
    try:
        user = request.user
        
        # Paramètres de date
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        # Construire la requête
        query = SeanceEntrainement.objects.filter(utilisateur=user)
        
        # Filtrer par dates si spécifiées
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                query = query.filter(date_prevue__gte=start_date)
            except ValueError:
                pass
                
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                query = query.filter(date_prevue__lte=end_date)
            except ValueError:
                pass
        
        # Récupérer les séances
        seances = query.order_by('date_prevue')[:100]
        
        # Format simple pour calendrier
        calendar_entries = []
        for seance in seances:
            calendar_entries.append({
                'id': seance.id,
                'date': seance.date_prevue.date().isoformat(),
                'title': seance.nom or 'Séance',
                'duration': seance.duree_reelle or seance.duree_prevue or 0,
                'status': seance.statut,
                'exercises_count': seance.exercices.count(),
                'note': seance.note_ressenti or 0
            })
        
        return Response({
            'success': True,
            'data': calendar_entries,
            'message': 'Données calendrier récupérées'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur get_calendar_data: {e}")
        return Response({
            'success': False,
            'data': [],
            'message': f'Erreur calendrier: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_workout_simple(request):
    """
    Endpoint simplifié pour sauvegarder une séance
    POST /api/workouts/save/
    """
    try:
        user = request.user
        data = request.data
        
        # Validation de base
        if not isinstance(data, dict):
            return Response({
                'success': False,
                'message': 'Format de données invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la séance
        duree_minutes = data.get('duree', 0)
        date_debut = timezone.now()
        date_fin = date_debut + timedelta(minutes=duree_minutes) if duree_minutes > 0 else None
        
        seance = SeanceEntrainement.objects.create(
            utilisateur=user,
            nom=data.get('nom', 'Séance'),
            date_prevue=date_debut,
            date_debut=date_debut,
            date_fin=date_fin,
            statut='TERMINEE',
            duree_prevue=duree_minutes,
            note_ressenti=data.get('note', 5),
            commentaire=data.get('commentaire', '')
        )
        
        # Traiter les exercices si fournis
        exercices_data = data.get('exercices', [])
        for ex_data in exercices_data:
            try:
                # Trouver la machine
                from apps.machines.models import Machine
                machine = Machine.objects.filter(nom=ex_data.get('nom')).first()
                
                if machine:
                    # Créer l'exercice
                    exercice = ExerciceSeance.objects.create(
                        seance=seance,
                        machine=machine,
                        poids_utilise=ex_data.get('poids', 0),
                        ordre_dans_seance=len(exercices_data)
                    )
                    
                    # Créer les séries
                    nb_series = ex_data.get('series', 1)
                    for i in range(nb_series):
                        SeriExercice.objects.create(
                            exercice=exercice,
                            numero_serie=i + 1,
                            repetitions=ex_data.get('reps', 0),
                            poids=ex_data.get('poids', 0),
                            repos_apres=90  # 90 secondes par défaut
                        )
                        
            except Exception as e:
                logger.warning(f"Erreur création exercice: {e}")
                continue
        
        return Response({
            'success': True,
            'message': 'Séance sauvegardée avec succès',
            'data': {
                'id': seance.id,
                'nom': seance.nom,
                'date': seance.date_prevue.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erreur save_workout_simple: {e}")
        return Response({
            'success': False,
            'message': f'Erreur sauvegarde: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calendar_health_check(request):
    """
    Endpoint de vérification santé pour le calendrier
    GET /api/workouts/calendar/health/
    """
    try:
        user = request.user
        
        # Compter les séances
        total_seances = SeanceEntrainement.objects.filter(utilisateur=user).count()
        seances_terminees = SeanceEntrainement.objects.filter(
            utilisateur=user, 
            statut='TERMINEE'
        ).count()
        
        # Dernière séance
        derniere_seance = SeanceEntrainement.objects.filter(
            utilisateur=user
        ).order_by('-date_prevue').first()
        
        return Response({
            'success': True,
            'data': {
                'user_id': user.id,
                'user_email': user.email,
                'total_seances': total_seances,
                'seances_terminees': seances_terminees,
                'derniere_seance': {
                    'id': derniere_seance.id if derniere_seance else None,
                    'date': derniere_seance.date_prevue.isoformat() if derniere_seance else None,
                    'nom': derniere_seance.nom if derniere_seance else None
                } if derniere_seance else None,
                'server_time': timezone.now().isoformat()
            },
            'message': 'Calendrier API opérationnel'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur calendar_health_check: {e}")
        return Response({
            'success': False,
            'message': f'Erreur health check: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
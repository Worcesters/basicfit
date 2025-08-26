"""
API pour les séances effectuées - Séparée du calendrier
"""
import logging
from django.db.models import Q, Avg, Count, Sum, Max
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta, date
from django.utils import timezone

# Import des nouveaux modèles refactorisés
from .models_refactored import SeanceEffectuee, ExerciceEffectue, SerieEffectuee
from apps.machines.models import Machine

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seances_effectuees(request):
    """
    Récupère uniquement les séances réellement effectuées (pas les planifiées)
    GET /api/workouts/seances-effectuees/
    """
    try:
        user = request.user
        
        # Paramètres optionnels
        days_limit = request.query_params.get('days', 365)
        try:
            days_limit = int(days_limit)
        except (ValueError, TypeError):
            days_limit = 365
        
        # Date limite
        date_limit = timezone.now() - timedelta(days=days_limit)
        
        # Récupérer les séances effectuées
        seances = SeanceEffectuee.objects.filter(
            utilisateur=user,
            date_debut__gte=date_limit
        ).prefetch_related(
            'exercices',
            'exercices__machine',
            'exercices__series'
        ).order_by('-date_debut')
        
        # Formater les données pour l'Android
        seances_data = []
        for seance in seances:
            exercices_data = []
            for exercice in seance.exercices.all():
                series_data = []
                for serie in exercice.series.all():
                    series_data.append({
                        'numero': serie.numero_serie,
                        'reps_realisees': serie.repetitions_realisees,
                        'reps_prevues': serie.repetitions_prevues,
                        'poids': serie.poids_utilise,
                        'repos': serie.repos_apres_serie or 90,
                        'reussie': serie.est_reussie,
                        'pourcentage_reussite': serie.pourcentage_reussite
                    })
                
                exercices_data.append({
                    'nom': exercice.nom_exercice,
                    'machine_id': exercice.machine.id,
                    'machine_nom': exercice.machine.nom,
                    'ordre': exercice.ordre_dans_seance,
                    'series_realisees': exercice.series_realisees,
                    'repetitions_totales': exercice.repetitions_totales,
                    'poids_moyen': exercice.poids_moyen,
                    'volume': exercice.volume_exercice,
                    'tonnage': exercice.tonnage_exercice,
                    'taux_reussite': exercice.taux_reussite,
                    'charge_max_estimee': exercice.charge_max_estimee,
                    'series': series_data
                })
            
            seances_data.append({
                'id': seance.id,
                'nom': seance.nom,
                'date_debut': seance.date_debut.isoformat(),
                'date_fin': seance.date_fin.isoformat(),
                'duree_minutes': seance.duree_minutes,
                'volume_total': seance.volume_total,
                'tonnage_total': seance.tonnage_total,
                'nombre_exercices': seance.nombre_exercices,
                'nombre_series_totales': seance.nombre_series_totales,
                'note_ressenti': seance.note_ressenti,
                'note_difficulte': seance.note_difficulte,
                'commentaire': seance.commentaire,
                'exercices': exercices_data
            })
        
        return Response({
            'success': True,
            'count': len(seances_data),
            'data': seances_data
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération séances effectuées: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_progressions_effectuees(request):
    """
    Calcule les progressions basées uniquement sur les séances effectuées
    GET /api/workouts/progressions-effectuees/
    """
    try:
        user = request.user
        
        # Paramètres
        days_limit = request.query_params.get('days', 90)  # 3 mois par défaut
        try:
            days_limit = int(days_limit)
        except (ValueError, TypeError):
            days_limit = 90
        
        date_limit = timezone.now() - timedelta(days=days_limit)
        
        # Récupérer les exercices effectués
        exercices = ExerciceEffectue.objects.filter(
            seance__utilisateur=user,
            seance__date_debut__gte=date_limit
        ).select_related('machine', 'seance').prefetch_related('series')
        
        # Grouper par machine
        progressions = {}
        for exercice in exercices:
            machine_nom = exercice.machine.nom
            
            if machine_nom not in progressions:
                progressions[machine_nom] = {
                    'machine_id': exercice.machine.id,
                    'machine_nom': machine_nom,
                    'seances': [],
                    'poids_max': 0,
                    'poids_actuel': 0,
                    'volume_total': 0,
                    'tonnage_total': 0,
                    'taux_reussite_global': 0,
                    'nombre_seances': 0,
                    'dernier_1rm': None,
                    'progression_totale': 0,
                    'premiere_seance': None,
                    'derniere_seance': None
                }
            
            progression = progressions[machine_nom]
            
            # Ajouter les données de cette séance
            progression['seances'].append({
                'date': exercice.seance.date_debut.date(),
                'poids_moyen': exercice.poids_moyen,
                'series': exercice.series_realisees,
                'repetitions': exercice.repetitions_totales,
                'taux_reussite': exercice.taux_reussite,
                'volume': exercice.volume_exercice,
                'tonnage': exercice.tonnage_exercice,
                '1rm_estime': exercice.charge_max_estimee
            })
            
            # Mettre à jour les statistiques globales
            progression['volume_total'] += exercice.volume_exercice
            progression['tonnage_total'] += exercice.tonnage_exercice
            progression['nombre_seances'] += 1
            
            # Poids maximum et actuel
            if exercice.poids_moyen > progression['poids_max']:
                progression['poids_max'] = exercice.poids_moyen
                progression['poids_actuel'] = exercice.poids_moyen
            
            # 1RM le plus élevé
            if exercice.charge_max_estimee:
                if not progression['dernier_1rm'] or exercice.charge_max_estimee > progression['dernier_1rm']:
                    progression['dernier_1rm'] = exercice.charge_max_estimee
            
            # Dates première et dernière séance
            date_seance = exercice.seance.date_debut.date()
            if not progression['premiere_seance'] or date_seance < progression['premiere_seance']:
                progression['premiere_seance'] = date_seance
            if not progression['derniere_seance'] or date_seance > progression['derniere_seance']:
                progression['derniere_seance'] = date_seance
        
        # Calculer les moyennes et progressions
        for machine_nom, progression in progressions.items():
            if progression['nombre_seances'] > 0:
                # Taux de réussite global (moyenne)
                taux_reussite_total = sum(s['taux_reussite'] for s in progression['seances'])
                progression['taux_reussite_global'] = taux_reussite_total / progression['nombre_seances']
                
                # Progression totale (différence entre premier et dernier poids)
                if len(progression['seances']) > 1:
                    seances_triees = sorted(progression['seances'], key=lambda x: x['date'])
                    poids_initial = seances_triees[0]['poids_moyen']
                    poids_final = seances_triees[-1]['poids_moyen']
                    progression['progression_totale'] = poids_final - poids_initial
                
                # Convertir les dates en string pour JSON
                if progression['premiere_seance']:
                    progression['premiere_seance'] = progression['premiere_seance'].isoformat()
                if progression['derniere_seance']:
                    progression['derniere_seance'] = progression['derniere_seance'].isoformat()
        
        # Convertir en liste pour l'API
        progressions_list = list(progressions.values())
        
        return Response({
            'success': True,
            'count': len(progressions_list),
            'data': progressions_list
        })
        
    except Exception as e:
        logger.error(f"Erreur calcul progressions effectuées: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_seance_effectuee(request):
    """
    Sauvegarde une séance réellement effectuée
    POST /api/workouts/seance-effectuee/
    """
    try:
        user = request.user
        data = request.data
        
        if not isinstance(data, dict):
            return Response({
                'success': False,
                'message': 'Format de données invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la séance effectuée
        duree_minutes = data.get('duree', 45)
        date_debut = timezone.now()
        date_fin = date_debut + timedelta(minutes=duree_minutes)
        
        seance = SeanceEffectuee.objects.create(
            utilisateur=user,
            nom=data.get('nom', 'Séance d\'entraînement'),
            date_debut=date_debut,
            date_fin=date_fin,
            note_ressenti=data.get('note_ressenti', 5),
            commentaire=data.get('commentaire', '')
        )
        
        # Traiter les exercices
        exercices_data = data.get('exercices', [])
        volume_total_seance = 0
        tonnage_total_seance = 0
        nombre_series_totales = 0
        
        for idx, ex_data in enumerate(exercices_data, 1):
            try:
                # Trouver la machine
                machine = None
                if 'machine_id' in ex_data:
                    machine = Machine.objects.get(id=ex_data['machine_id'])
                else:
                    # Recherche par nom
                    nom_machine = ex_data.get('nom', '').strip()
                    if nom_machine:
                        machine = Machine.objects.filter(nom__icontains=nom_machine).first()
                
                if not machine:
                    logger.warning(f"Machine non trouvée pour: {ex_data}")
                    continue
                
                # Créer l'exercice effectué
                exercice = ExerciceEffectue.objects.create(
                    seance=seance,
                    machine=machine,
                    nom_exercice=ex_data.get('nom', machine.nom),
                    ordre_dans_seance=idx,
                    series_realisees=ex_data.get('series', 3),
                    repetitions_totales=ex_data.get('repetitions', 10) * ex_data.get('series', 3),
                    poids_moyen=float(ex_data.get('poids', 0)),
                    taux_reussite=95.0  # Par défaut, assumé réussi
                )
                
                # Créer les séries (simulation basique)
                for serie_num in range(1, exercice.series_realisees + 1):
                    SerieEffectuee.objects.create(
                        exercice=exercice,
                        numero_serie=serie_num,
                        repetitions_realisees=ex_data.get('repetitions', 10),
                        repetitions_prevues=ex_data.get('repetitions', 10),
                        poids_utilise=exercice.poids_moyen,
                        repos_apres_serie=90
                    )
                
                # Accumuler les totaux
                volume_total_seance += exercice.volume_exercice
                tonnage_total_seance += exercice.tonnage_exercice
                nombre_series_totales += exercice.series_realisees
                
            except Exception as e:
                logger.error(f"Erreur traitement exercice {ex_data}: {e}")
                continue
        
        # Mettre à jour les totaux de la séance
        seance.volume_total = volume_total_seance
        seance.tonnage_total = tonnage_total_seance
        seance.nombre_exercices = len(exercices_data)
        seance.nombre_series_totales = nombre_series_totales
        seance.save()
        
        return Response({
            'success': True,
            'message': 'Séance effectuée sauvegardée avec succès',
            'data': {
                'id': seance.id,
                'nom': seance.nom,
                'date': seance.date_debut.isoformat(),
                'duree_minutes': seance.duree_minutes,
                'volume_total': seance.volume_total,
                'tonnage_total': seance.tonnage_total,
                'nombre_exercices': seance.nombre_exercices
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde séance effectuée: {e}")
        return Response({
            'success': False,
            'message': f'Erreur sauvegarde: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
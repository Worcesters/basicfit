"""
API propre pour BasicFit v2 - Version 100% BDD
Utilise uniquement les modèles unifiés : ExerciceEffectueUnifie et CalendrierEntrainementSimple
"""
import logging
import csv
import io
from datetime import datetime, date
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Avg, Max, Min
from django.utils import timezone

from .models_unified import ExerciceEffectueUnifie, CalendrierEntrainementSimple
from apps.machines.models import Machine

logger = logging.getLogger(__name__)


# === IMPORT CSV CALENDRIER ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_csv_calendar(request):
    """
    Import CSV dans le calendrier d'entraînement
    POST /api/workouts/import-csv/

    Format CSV attendu: machine,date,type,duree,poids,series,repetitions
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
        csv_data = list(csv_reader)

        if not csv_data:
            return Response({
                'success': False,
                'message': 'Aucune donnée trouvée dans le CSV'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validation des colonnes
        expected_columns = {'machine', 'date', 'type'}
        if not expected_columns.issubset(set(csv_reader.fieldnames or [])):
            return Response({
                'success': False,
                'message': f'Colonnes CSV invalides. Attendu: {expected_columns}, Reçu: {csv_reader.fieldnames}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Traitement des données
        imported_count = 0
        errors = []
        seances_crees = set()

        for row_num, row in enumerate(csv_data, 1):
            try:
                # Parse de la date
                date_str = row['date'].strip()
                date_obj = None

                for date_format in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        date_obj = datetime.strptime(date_str, date_format).date()
                        break
                    except ValueError:
                        continue

                if not date_obj:
                    errors.append(f"Ligne {row_num}: Format de date invalide: {date_str}")
                    continue

                # Créer ou récupérer la séance dans le calendrier
                nom_seance = f"Séance {date_obj.strftime('%d/%m/%Y')}"
                seance_key = (user.id, date_obj, nom_seance)

                if seance_key not in seances_crees:
                    seance, created = CalendrierEntrainementSimple.objects.get_or_create(
                        utilisateur=user,
                        date_entrainement=date_obj,
                        nom_seance=nom_seance,
                        defaults={
                            'duree_totale_minutes': 60,
                            'nombre_exercices': 0,
                            'volume_total_seance': 0.00,
                            'source_donnees': 'CSV_IMPORT'
                        }
                    )
                    seances_crees.add(seance_key)

                # Créer l'exercice effectué
                exercice = ExerciceEffectueUnifie.objects.create(
                    utilisateur=user,
                    source='CSV_IMPORT',
                    date_exercice=datetime.combine(date_obj, datetime.min.time()),
                    nom_seance=nom_seance,
                    nom_exercice=row['machine'].strip(),
                    machine=None,  # Pas de machine spécifique pour l'import CSV
                    series_effectuees=int(row.get('series', 3)),
                    repetitions_totales=int(row.get('repetitions', 12)),
                    poids_utilise=float(row.get('poids', 0.0)),
                    ligne_csv_originale=str(row),
                    taux_reussite=100.00,
                    duree_seance_minutes=60
                )

                imported_count += 1

            except Exception as e:
                errors.append(f"Ligne {row_num}: Erreur: {str(e)}")

        # Mettre à jour les métriques des séances
        for seance_key in seances_crees:
            user_id, date_obj, nom_seance = seance_key
            seance = CalendrierEntrainementSimple.objects.get(
                utilisateur_id=user_id,
                date_entrainement=date_obj,
                nom_seance=nom_seance
            )
            seance.mettre_a_jour_metriques()

        return Response({
            'success': True,
            'imported_count': imported_count,
            'seances_crees': len(seances_crees),
            'total_lines': len(csv_data),
            'errors_count': len(errors),
            'message': f'{imported_count} exercices importés dans {len(seances_crees)} séances'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Erreur import_csv_calendar: {e}")
        return Response({
            'success': False,
            'message': f'Erreur import: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# === EXERCICES EFFECTUÉS ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enregistrer_exercice(request):
    """
    Enregistrer un exercice effectué (manuel ou depuis l'app)
    POST /api/workouts/exercice/
    """
    try:
        user = request.user
        data = request.data

        # Validation des données requises
        required_fields = ['nom_exercice', 'poids', 'series', 'repetitions']
        for field in required_fields:
            if field not in data:
                return Response({
                    'success': False,
                    'message': f'Champ requis manquant: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Créer l'exercice effectué
        exercice = ExerciceEffectueUnifie.objects.create(
            utilisateur=user,
            source='MANUEL_TEMPS_REEL',
            date_exercice=data.get('date_exercice', timezone.now()),
            nom_seance=data.get('nom_seance', 'Séance manuelle'),
            duree_seance_minutes=data.get('duree_seance_minutes'),
            nom_exercice=data['nom_exercice'],
            machine_id=data.get('machine_id'),
            series_effectuees=int(data['series']),
            repetitions_totales=int(data['repetitions']),
            poids_utilise=float(data['poids']),
            taux_reussite=float(data.get('taux_reussite', 100.0)),
            temps_repos_seconde=data.get('temps_repos_seconde'),
            commentaire_utilisateur=data.get('commentaire')
        )

        # Mettre à jour ou créer la séance dans le calendrier
        date_exercice = exercice.date_exercice.date()
        seance, created = CalendrierEntrainementSimple.objects.get_or_create(
            utilisateur=user,
            date_entrainement=date_exercice,
            nom_seance=exercice.nom_seance,
            defaults={
                'duree_totale_minutes': exercice.duree_seance_minutes or 30,
                'nombre_exercices': 0,
                'volume_total_seance': 0.00,
                'source_donnees': 'MANUEL'
            }
        )

        if not created:
            seance.mettre_a_jour_metriques()

        return Response({
            'success': True,
            'exercice_id': exercice.id,
            'message': 'Exercice enregistré avec succès'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Erreur enregistrer_exercice: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exercices_utilisateur(request):
    """
    Récupérer tous les exercices d'un utilisateur
    GET /api/workouts/exercices/
    """
    try:
        user = request.user

        # Filtres optionnels
        machine_id = request.query_params.get('machine_id')
        date_debut = request.query_params.get('date_debut')
        date_fin = request.query_params.get('date_fin')
        source = request.query_params.get('source')

        queryset = ExerciceEffectueUnifie.objects.filter(utilisateur=user)

        if machine_id:
            queryset = queryset.filter(machine_id=machine_id)
        if date_debut:
            queryset = queryset.filter(date_exercice__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_exercice__date__lte=date_fin)
        if source:
            queryset = queryset.filter(source=source)

        exercices = queryset.order_by('-date_exercice')

        exercices_data = []
        for ex in exercices:
            exercices_data.append({
                'id': ex.id,
                'date': ex.date_exercice.isoformat(),
                'nom_exercice': ex.nom_exercice,
                'machine': ex.machine.nom if ex.machine else None,
                'poids': float(ex.poids_utilise),
                'series': ex.series_effectuees,
                'repetitions': ex.repetitions_totales,
                'volume': float(ex.volume_total),
                'source': ex.source,
                'nom_seance': ex.nom_seance
            })

        return Response({
            'success': True,
            'data': exercices_data,
            'count': len(exercices_data)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erreur get_exercices_utilisateur: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# === HISTORIQUE ET STATISTIQUES ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_historique_utilisateur(request):
    """
    Historique complet des exercices d'un utilisateur
    GET /api/workouts/historique/
    """
    try:
        user = request.user

        # Statistiques globales
        total_exercices = ExerciceEffectueUnifie.objects.filter(utilisateur=user).count()
        total_volume = ExerciceEffectueUnifie.objects.filter(utilisateur=user).aggregate(
            total=Sum('volume_total')
        )['total'] or 0.0

        # Top machines utilisées
        top_machines = ExerciceEffectueUnifie.objects.filter(
            utilisateur=user,
            machine__isnull=False
        ).values('machine__nom').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        # Progression par machine
        progression_machines = []
        machines_utilisees = Machine.objects.filter(
            exercices_effectues_unifies__utilisateur=user
        ).distinct()

        for machine in machines_utilisees:
            exercices = ExerciceEffectueUnifie.objects.filter(
                utilisateur=user,
                machine=machine
            ).order_by('date_exercice')

            if exercices.exists():
                premier = exercices.first()
                dernier = exercices.last()

                progression_machines.append({
                    'machine': machine.nom,
                    'poids_initial': float(premier.poids_utilise),
                    'poids_actuel': float(dernier.poids_utilise),
                    'progression': float(dernier.poids_utilise - premier.poids_utilise),
                    'exercices_count': exercices.count()
                })

        return Response({
            'success': True,
            'data': {
                'total_exercices': total_exercices,
                'total_volume': float(total_volume),
                'top_machines': list(top_machines),
                'progression_machines': progression_machines
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erreur get_historique_utilisateur: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_statistiques_utilisateur(request):
    """
    Statistiques détaillées de l'utilisateur
    GET /api/workouts/stats/
    """
    try:
        user = request.user

        # Période (défaut: 30 jours)
        jours = int(request.query_params.get('jours', 30))
        date_limite = timezone.now() - timezone.timedelta(days=jours)

        exercices_recent = ExerciceEffectueUnifie.objects.filter(
            utilisateur=user,
            date_exercice__gte=date_limite
        )

        # Statistiques de la période
        stats = {
            'periode_jours': jours,
            'exercices_count': exercices_recent.count(),
            'volume_total': float(exercices_recent.aggregate(
                total=Sum('volume_total')
            )['total'] or 0.0),
            'moyenne_poids': float(exercices_recent.aggregate(
                moyenne=Avg('poids_utilise')
            )['moyenne'] or 0.0),
            'moyenne_series': float(exercices_recent.aggregate(
                moyenne=Avg('series_effectuees')
            )['moyenne'] or 0.0),
            'moyenne_repetitions': float(exercices_recent.aggregate(
                moyenne=Avg('repetitions_totales')
            )['moyenne'] or 0.0)
        }

        # Séances par jour
        seances_par_jour = CalendrierEntrainementSimple.objects.filter(
            utilisateur=user,
            date_entrainement__gte=date_limite.date()
        ).count()

        stats['seances_count'] = seances_par_jour

        return Response({
            'success': True,
            'data': stats
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erreur get_statistiques_utilisateur: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# === RECOMMANDATIONS IA ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommandations_ia(request):
    """
    Recommandations intelligentes basées sur l'historique des exercices effectués
    GET /api/workouts/recommandations/
    """
    try:
        user = request.user

        # Analyser l'historique des exercices effectués
        exercices_recent = ExerciceEffectueUnifie.objects.filter(
            utilisateur=user
        ).order_by('-date_exercice')[:50]  # Derniers 50 exercices

        if not exercices_recent.exists():
            return Response({
                'success': True,
                'message': 'Pas assez d\'historique pour des recommandations',
                'data': []
            }, status=status.HTTP_200_OK)

        # Analyser les tendances
        recommandations = []

        # Recommandation basée sur la fréquence
        machines_frequentes = ExerciceEffectueUnifie.objects.filter(
            utilisateur=user
        ).values('machine__nom').annotate(
            count=Count('id')
        ).order_by('-count')[:3]

        for machine in machines_frequentes:
            if machine['machine__nom']:
                recommandations.append({
                    'type': 'frequence',
                    'machine': machine['machine__nom'],
                    'message': f'Machine fréquemment utilisée ({machine["count"]} fois)',
                    'priorite': 'haute'
                })

        # Recommandation basée sur la progression
        for machine in machines_frequentes:
            if machine['machine__nom']:
                machine_obj = Machine.objects.filter(nom=machine['machine__nom']).first()
                if machine_obj:
                    exercices_machine = ExerciceEffectueUnifie.objects.filter(
                        utilisateur=user,
                        machine=machine_obj
                    ).order_by('date_exercice')

                    if exercices_machine.count() >= 3:
                        premier = exercices_machine.first()
                        dernier = exercices_machine.last()

                        if dernier.poids_utilise > premier.poids_utilise:
                            recommandations.append({
                                'type': 'progression',
                                'machine': machine['machine__nom'],
                                'message': f'Progression détectée: {float(premier.poids_utilise)}kg → {float(dernier.poids_utilise)}kg',
                                'priorite': 'moyenne',
                                'suggestion': 'Continuez sur cette lancée !'
                            })

        return Response({
            'success': True,
            'data': recommandations,
            'count': len(recommandations)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erreur get_recommandations_ia: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommandations_machine(request, machine_id):
    """
    Recommandations spécifiques pour une machine
    GET /api/workouts/recommandations/machine/<machine_id>/
    """
    try:
        user = request.user

        machine = Machine.objects.get(id=machine_id)
        exercices_machine = ExerciceEffectueUnifie.objects.filter(
            utilisateur=user,
            machine=machine
        ).order_by('-date_exercice')

        if not exercices_machine.exists():
            return Response({
                'success': True,
                'message': 'Aucun exercice sur cette machine',
                'data': {}
            }, status=status.HTTP_200_OK)

        # Dernier exercice
        dernier = exercices_machine.first()

        # Calculer la recommandation
        poids_actuel = float(dernier.poids_utilise)
        series_actuelles = dernier.series_effectuees
        repetitions_actuelles = dernier.repetitions_totales

        # Recommandation basée sur la progression
        if exercices_machine.count() >= 2:
            avant_dernier = exercices_machine[1]

            if dernier.poids_utilise > avant_dernier.poids_utilise:
                # Progression en poids, maintenir
                recommandation = {
                    'poids': poids_actuel,
                    'series': series_actuelles,
                    'repetitions': repetitions_actuelles,
                    'message': 'Maintenez ce niveau, progression détectée',
                    'type': 'maintenance'
                }
            else:
                # Pas de progression, suggérer augmentation
                nouveau_poids = poids_actuel + machine.increment_poids
                recommandation = {
                    'poids': nouveau_poids,
                    'series': series_actuelles,
                    'repetitions': repetitions_actuelles,
                    'message': f'Suggéré: augmenter à {nouveau_poids}kg',
                    'type': 'progression'
                }
        else:
            # Premier exercice sur cette machine
            recommandation = {
                'poids': poids_actuel,
                'series': series_actuelles,
                'repetitions': repetitions_actuelles,
                'message': 'Premier exercice, maintenez ce niveau',
                'type': 'premier'
            }

        return Response({
            'success': True,
            'machine': machine.nom,
            'recommandation': recommandation
        }, status=status.HTTP_200_OK)

    except Machine.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Machine non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Erreur get_recommandations_machine: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# === CALENDRIER ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendrier_utilisateur(request):
    """
    Calendrier complet de l'utilisateur
    GET /api/workouts/calendrier/
    """
    try:
        user = request.user

        seances = CalendrierEntrainementSimple.objects.filter(
            utilisateur=user
        ).order_by('-date_entrainement')

        calendrier_data = []
        for seance in seances:
            calendrier_data.append({
                'id': seance.id,
                'date': seance.date_entrainement.isoformat(),
                'nom_seance': seance.nom_seance,
                'duree_minutes': seance.duree_totale_minutes,
                'nombre_exercices': seance.nombre_exercices,
                'volume_total': float(seance.volume_total_seance),
                'source': seance.source_donnees
            })

        return Response({
            'success': True,
            'data': calendrier_data,
            'count': len(calendrier_data)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erreur get_calendrier_utilisateur: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendrier_date(request, date_str):
    """
    Calendrier pour une date spécifique
    GET /api/workouts/calendrier/<date>/
    """
    try:
        user = request.user

        # Parse de la date
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'message': 'Format de date invalide. Utilisez YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer la séance et les exercices
        try:
            seance = CalendrierEntrainementSimple.objects.get(
                utilisateur=user,
                date_entrainement=date_obj
            )
        except CalendrierEntrainementSimple.DoesNotExist:
            return Response({
                'success': True,
                'message': 'Aucune séance pour cette date',
                'data': {}
            }, status=status.HTTP_200_OK)

        # Récupérer les exercices de cette séance
        exercices = ExerciceEffectueUnifie.objects.filter(
            utilisateur=user,
            date_exercice__date=date_obj,
            nom_seance=seance.nom_seance
        ).order_by('date_exercice')

        exercices_data = []
        for ex in exercices:
            exercices_data.append({
                'id': ex.id,
                'nom_exercice': ex.nom_exercice,
                'machine': ex.machine.nom if ex.machine else None,
                'poids': float(ex.poids_utilise),
                'series': ex.series_effectuees,
                'repetitions': ex.repetitions_totales,
                'volume': float(ex.volume_total),
                'heure': ex.date_exercice.strftime('%H:%M')
            })

        return Response({
            'success': True,
            'data': {
                'seance': {
                    'id': seance.id,
                    'date': seance.date_entrainement.isoformat(),
                    'nom_seance': seance.nom_seance,
                    'duree_minutes': seance.duree_totale_minutes,
                    'nombre_exercices': seance.nombre_exercices,
                    'volume_total': float(seance.volume_total_seance),
                    'source': seance.source_donnees
                },
                'exercices': exercices_data
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erreur get_calendrier_date: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# === GESTION DES DONNÉES ===
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def nettoyer_donnees_utilisateur(request):
    """
    Nettoyer toutes les données d'un utilisateur
    DELETE /api/workouts/nettoyer/
    """
    try:
        user = request.user

        # Compter avant suppression
        exercices_count = ExerciceEffectueUnifie.objects.filter(utilisateur=user).count()
        seances_count = CalendrierEntrainementSimple.objects.filter(utilisateur=user).count()

        # Supprimer
        ExerciceEffectueUnifie.objects.filter(utilisateur=user).delete()
        CalendrierEntrainementSimple.objects.filter(utilisateur=user).delete()

        return Response({
            'success': True,
            'message': f'Données nettoyées: {exercices_count} exercices, {seances_count} séances supprimés'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erreur nettoyer_donnees_utilisateur: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exporter_donnees_utilisateur(request):
    """
    Exporter toutes les données d'un utilisateur
    GET /api/workouts/export/
    """
    try:
        user = request.user

        # Récupérer toutes les données
        exercices = ExerciceEffectueUnifie.objects.filter(utilisateur=user).order_by('date_exercice')
        seances = CalendrierEntrainementSimple.objects.filter(utilisateur=user).order_by('date_entrainement')

        # Préparer l'export
        export_data = {
            'utilisateur': user.username,
            'date_export': timezone.now().isoformat(),
            'exercices': [],
            'seances': []
        }

        for ex in exercices:
            export_data['exercices'].append({
                'date': ex.date_exercice.isoformat(),
                'nom_exercice': ex.nom_exercice,
                'machine': ex.machine.nom if ex.machine else None,
                'poids': float(ex.poids_utilise),
                'series': ex.series_effectuees,
                'repetitions': ex.repetitions_totales,
                'volume': float(ex.volume_total),
                'source': ex.source
            })

        for seance in seances:
            export_data['seances'].append({
                'date': seance.date_entrainement.isoformat(),
                'nom_seance': seance.nom_seance,
                'duree_minutes': seance.duree_totale_minutes,
                'nombre_exercices': seance.nombre_exercices,
                'volume_total': float(seance.volume_total_seance),
                'source': seance.source_donnees
            })

        return Response({
            'success': True,
            'data': export_data,
            'count_exercices': len(export_data['exercices']),
            'count_seances': len(export_data['seances'])
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erreur exporter_donnees_utilisateur: {e}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""
API REST pour les séances d'entraînement
"""
from django.db.models import Sum, Count, Max, Avg
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta, datetime
from django.utils.dateparse import parse_datetime
import logging
import csv
import io

logger = logging.getLogger(__name__)

from .models import SeanceEntrainement, ExerciceSeance, SeriExercice, ProgressionMachine
from .serializers import (
    SeanceEntrainementSerializer, SeanceCreateSerializer,
    ExerciceSeanceSerializer, SeriExerciceSerializer,
    ProgressionMachineSerializer, WorkoutStatsSerializer,
    MachineSerializer
)
from apps.machines.models import Machine
from .new_recommendation_system import ProgressionBasedRecommendationSystem


class SeanceEntrainementViewSet(viewsets.ModelViewSet):
    """ViewSet pour les séances d'entraînement"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return SeanceCreateSerializer
        return SeanceEntrainementSerializer

    def get_queryset(self):
        return SeanceEntrainement.objects.filter(
            utilisateur=self.request.user
        ).prefetch_related('exercices__machine', 'exercices__series').order_by('-date_debut')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques de l'utilisateur"""
        user = request.user
        seances = SeanceEntrainement.objects.filter(utilisateur=user, statut='TERMINEE')

        # Calculs des stats
        total_seances = seances.count()
        total_minutes = seances.aggregate(
            total=Sum('duree_reelle')
        )['total'] or 0

        # Estimation calories (approximative : 5 cal/min)
        total_calories = int(total_minutes * 5)

        # Séances excellentes (plus de 80% des exercices réussis)
        seances_excellentes = 0
        for seance in seances:
            exercices = seance.exercices.all()
            if exercices.count() > 0:
                excellents = exercices.filter(note_ressenti__gte=8).count()
                if excellents / exercices.count() >= 0.8:
                    seances_excellentes += 1

        # Record de poids
        record_poids = ExerciceSeance.objects.filter(
            seance__utilisateur=user
        ).aggregate(Max('poids_utilise'))['poids_utilise__max'] or 0.0

        # Exercices favoris (top 3)
        exercices_favoris = list(
            ExerciceSeance.objects.filter(seance__utilisateur=user)
            .values('machine__nom')
            .annotate(count=Count('id'))
            .order_by('-count')[:3]
            .values_list('machine__nom', flat=True)
        )

        # Progression générale (moyenne des progressions)
        progression_generale = ProgressionMachine.objects.filter(
            utilisateur=user
        ).aggregate(Avg('progression_poids_total'))['progression_poids_total__avg'] or 0.0

        stats_data = {
            'total_seances': total_seances,
            'total_minutes': int(total_minutes),
            'total_calories': total_calories,
            'seances_excellentes': seances_excellentes,
            'record_poids': float(record_poids),
            'exercices_favoris': exercices_favoris,
            'progression_generale': float(progression_generale)
        }

        serializer = WorkoutStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Historique des séances avec pagination"""
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))

        seances = self.get_queryset()[offset:offset + limit]
        serializer = self.get_serializer(seances, many=True)

        return Response({
            'results': serializer.data,
            'count': len(serializer.data),
            'has_more': len(seances) == limit
        })

    @action(detail=True, methods=['post'])
    def commencer(self, request, pk=None):
        """Commencer une séance"""
        seance = self.get_object()
        seance.commencer_seance()
        serializer = self.get_serializer(seance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def terminer(self, request, pk=None):
        """Terminer une séance"""
        seance = self.get_object()
        seance.terminer_seance()
        serializer = self.get_serializer(seance)
        return Response(serializer.data)


class MachineViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les machines (lecture seule)"""
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        """Liste des machines avec format JSON correct"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # Retourner directement le tableau des machines
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def groupes_musculaires(self, request):
        """Liste des groupes musculaires disponibles"""
        groupes = Machine.objects.values_list('groupe_musculaire', flat=True).distinct()
        return Response({'groupes': list(groupes)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sauvegarder_seance_simple(request):
    """Endpoint simplifié pour sauvegarder une séance depuis l'app Android"""
    try:
        data = request.data
        user = request.user
        print(f"[DEBUG] Données reçues: {data}")

        # Gestion de la date
        raw_date = data.get('date', timezone.now().isoformat())
        try:
            if isinstance(raw_date, str):
                date_prevue = parse_datetime(raw_date) or timezone.now()
            else:
                date_prevue = raw_date or timezone.now()
        except:
            date_prevue = timezone.now()

        # Créer la séance
        seance = SeanceEntrainement.objects.create(
            utilisateur=user,
            nom=data.get('nom', f"Séance du {date_prevue.strftime('%d/%m/%Y')}"),
            date_prevue=date_prevue,
            date_debut=timezone.now() - timedelta(minutes=data.get('duree', 45)),
            date_fin=timezone.now(),
            duree_prevue=data.get('duree', 45),
            statut='TERMINEE',
            note_ressenti=data.get('note_ressenti', 7),
            commentaire=data.get('commentaire', '')
        )
        print(f"[DEBUG] Séance créée: {seance.id}")

        # Ajouter les exercices
        for idx, exercice_data in enumerate(data.get('exercices', [])):
            nom_exercice = exercice_data.get('nom', '')
            if not nom_exercice:
                continue

            # Chercher ou créer la machine
            try:
                machine = Machine.objects.filter(nom__icontains=nom_exercice).first()
                if not machine:
                    from apps.machines.models import CategorieMachine
                    categorie_defaut, _ = CategorieMachine.objects.get_or_create(
                        nom='MUSCULATION',
                        defaults={'description': 'Catégorie par défaut'}
                    )
                    machine = Machine.objects.create(
                        nom=nom_exercice,
                        description='Créé automatiquement',
                        instructions='',
                        increment_poids=2.5,
                        poids_minimum=0.0,
                        poids_maximum=200.0
                    )
                    machine.categories.add(categorie_defaut)

                print(f"[DEBUG] Machine trouvée/créée: {machine.nom}")

                # Créer l'exercice
                exercice = ExerciceSeance.objects.create(
                    seance=seance,
                    machine=machine,
                    ordre_dans_seance=idx + 1,
                    series_prevues=exercice_data.get('series', 3),
                    repetitions_prevues=exercice_data.get('reps', 10),
                    poids_prevu=float(exercice_data.get('poids', 20)),
                    nombre_series=exercice_data.get('series', 3),
                    repetitions_realisees=exercice_data.get('reps', 10),
                    poids_utilise=float(exercice_data.get('poids', 20)),
                    statut='TERMINE'
                )
                print(f"[DEBUG] Exercice créé: {exercice.id}")

                # Créer les séries
                for serie_num in range(exercice_data.get('series', 3)):
                    SeriExercice.objects.create(
                        exercice=exercice,
                        numero_serie=serie_num + 1,
                        repetitions_prevues=exercice_data.get('reps', 10),
                        poids_prevu=float(exercice_data.get('poids', 20)),
                        repetitions_realisees=exercice_data.get('reps', 10),
                        poids_utilise=float(exercice_data.get('poids', 20)),
                        statut='REUSSIE'
                    )
                print(f"[DEBUG] {exercice_data.get('series', 3)} séries créées")

            except Exception as e:
                print(f"[ERROR] Erreur création exercice {nom_exercice}: {e}")
                continue

        # Calculer les métriques
        seance.calculer_metriques()

        return Response({
            'id': seance.id,
            'nom': seance.nom,
            'statut': seance.statut,
            'message': 'Séance sauvegardée avec succès'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"[ERROR] Erreur sauvegarde séance: {e}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Vues de compatibilité (pour les tests)
@api_view(['GET'])
@permission_classes([AllowAny])
def workouts_info(request):
    """Informations sur les workouts (pour démo)"""
    try:
        total_seances = SeanceEntrainement.objects.count()
        total_exercices = ExerciceSeance.objects.count()
        total_series = SeriExercice.objects.count()

        return Response({
            'total_seances': total_seances,
            'total_exercices': total_exercices,
            'total_series': total_series,
            'message': 'API workouts fonctionnelle ✅'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def seances_list(request):
    """Liste des séances d'entraînement (pour démo)"""
    try:
        seances = SeanceEntrainement.objects.all().order_by('-date_debut')[:10]
        data = []

        for seance in seances:
            data.append({
                'id': seance.id,
                'nom': seance.nom,
                'date_debut': seance.date_debut.isoformat() if seance.date_debut else None,
                'date_fin': seance.date_fin.isoformat() if seance.date_fin else None,
                'statut': seance.statut,
                'duree_reelle': seance.duree_reelle,
                'nombre_exercices': seance.nombre_exercices
            })

        return Response({'results': data, 'count': len(data)})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendation(request, machine_id):
    """
    Système de recommandation basé sur le nouveau système de progression
    """
    try:
        user = request.user

        # Récupérer la machine
        try:
            machine = Machine.objects.get(id=machine_id)
        except Machine.DoesNotExist:
            return Response({
                'error': 'Machine non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)

        # Utiliser le nouveau système de recommandation
        recommendation_system = ProgressionBasedRecommendationSystem()
        recommendations = recommendation_system.get_recommendations_for_user(
            user, 'PRISE_MASSE', nb_machines=10
        )

        # Chercher la recommandation pour cette machine spécifique
        for rec in recommendations:
            if rec['machine_id'] == machine_id:
                return Response({
                    'machine': {
                        'id': machine.id,
                        'nom': machine.nom,
                        'description': machine.description
                    },
                    'recommendation': rec,
                    'premiere_utilisation': rec['recommandation_source'] == 'premiere_utilisation'
                }, status=status.HTTP_200_OK)

        # Si pas trouvé dans les recommandations, créer une recommandation par défaut
        default_rec = {
            'machine_id': machine.id,
            'machine_nom': machine.nom,
            'poids_recommande': machine.poids_minimum + machine.increment_poids,
            'series_recommandees': 3,
            'repetitions_recommandees': 10,
            'repos_recommande': 90,
            'notes': 'Recommandation par défaut - première utilisation',
            'recommandation_source': 'defaut',
            'progression_info': {
                'poids_actuel': 0,
                'taux_reussite': 0,
                'nombre_seances': 0,
                'dernier_1rm': None,
                'progression_totale': 0
            }
        }

        return Response({
            'machine': {
                'id': machine.id,
                'nom': machine.nom,
                'description': machine.description
            },
            'recommendation': default_rec,
            'premiere_utilisation': True
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erreur dans get_recommendation: {e}")
        return Response({
            'error': f'Erreur lors du calcul de la recommandation: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_recommendation_by_name(request, machine_name):
    """Endpoint pour obtenir la recommandation de poids basée sur le système professionnel"""
    try:
        user = request.user

        if not user.is_authenticated:
            return Response({'error': 'Authentification requise'}, status=status.HTTP_401_UNAUTHORIZED)

        # Utiliser le nouveau système de recommandation
        recommendation_system = ProgressionBasedRecommendationSystem()
        try:
            # Chercher une machine spécifique par nom
            machine = Machine.objects.filter(nom__icontains=machine_name).first()
            if not machine:
                return Response({'error': f'Machine "{machine_name}" non trouvée'}, status=status.HTTP_404_NOT_FOUND)

            # Pour une machine spécifique, utiliser PRISE_MASSE par défaut
            recommendations = recommendation_system.get_recommendations_for_user(
                user, 'PRISE_MASSE', nb_machines=6
            )

            # Chercher la recommandation pour cette machine spécifique
            for rec in recommendations:
                if rec['machine_nom'].lower() in machine_name.lower() or machine_name.lower() in rec['machine_nom'].lower():
                    return Response(rec, status=status.HTTP_200_OK)

            # Si pas trouvé, retourner une recommandation générique pour cette machine
            return Response({
                'machine_id': machine.id,
                'machine_nom': machine.nom,
                'poids_recommande': machine.poids_minimum + machine.increment_poids,
                'series_recommandees': 3,
                'repetitions_recommandees': 10,
                'repos_recommande': 90,
                'notes': 'Recommandation par défaut - première utilisation',
                'recommandation_source': 'defaut'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erreur système recommandation: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Erreur endpoint recommandation nom {machine_name}: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_recommendations(request):
    """
    Nouveau endpoint pour obtenir des recommandations basées sur le mode d'entraînement
    GET /api/workouts/recommendations/session/?mode=FORCE&nb_machines=6
    """
    try:
        user = request.user
        mode = request.GET.get('mode', 'PRISE_MASSE')  # Mode par défaut
        nb_machines = int(request.GET.get('nb_machines', 6))  # 6 machines par défaut

        # Vérifier que le mode est valide
        valid_modes = ['FORCE', 'PRISE_MASSE', 'ENDURANCE', 'SECHE']
        if mode not in valid_modes:
            return Response({
                'error': f'Mode invalide. Modes supportés: {valid_modes}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Utiliser le nouveau système de recommandation
        recommendation_system = ProgressionBasedRecommendationSystem()
        recommendations = recommendation_system.get_recommendations_for_user(
            user, mode, nb_machines
        )

        response_data = {
            'mode_entrainement': mode,
            'nb_machines_demandees': nb_machines,
            'nb_recommendations': len(recommendations),
            'recommendations': recommendations,
            'metadata': {
                'timestamp': timezone.now().isoformat(),
                'user_id': user.id,
                'system_version': '2.0_progression_based'
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({'error': f'Paramètre invalide: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erreur dans get_session_recommendations: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_intelligent_recommendations(request, mode_entrainement):
    """
    Endpoint pour récupérer les recommandations intelligentes basées sur les progressions
    Compatible avec l'application Android
    """
    try:
        user = request.user
        nb_machines = int(request.GET.get('nb_machines', 6))

        logger.info(f"Demande recommandations intelligentes: user={user.id}, mode={mode_entrainement}, nb={nb_machines}")

        # Créer le système de recommandation
        recommendation_system = ProgressionBasedRecommendationSystem()

        # Générer les recommandations
        recommendations = recommendation_system.get_recommendations_for_user(
            user=user,
            mode_entrainement=mode_entrainement.upper(),
            nb_machines=nb_machines
        )

        response_data = {
            'success': True,
            'data': recommendations,
            'message': f'Recommandations intelligentes générées pour {mode_entrainement}',
            'mode_entrainement': mode_entrainement,
            'count': len(recommendations)
        }

        logger.info(f"Recommandations intelligentes envoyées: {len(recommendations)} machines")
        return Response(response_data, status=status.HTTP_200_OK)

    except ValueError as e:
        logger.error(f"Erreur paramètre dans get_intelligent_recommendations: {e}")
        return Response({
            'success': False,
            'message': f'Paramètre invalide: {str(e)}',
            'data': [],
            'count': 0
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Erreur dans get_intelligent_recommendations: {e}")
        return Response({
            'success': False,
            'message': f'Erreur serveur: {str(e)}',
            'data': [],
            'count': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_progressions(request):
    """
    Endpoint pour récupérer les progressions d'un utilisateur
    Compatible avec l'application Android
    """
    try:
        user = request.user
        mode_entrainement = request.GET.get('mode_entrainement')

        logger.info(f"Demande progressions: user={user.id}, mode={mode_entrainement}")

        # Construire la requête
        queryset = ProgressionMachine.objects.filter(utilisateur=user).select_related('machine', 'mode_entrainement')

        if mode_entrainement:
            queryset = queryset.filter(mode_entrainement__nom=mode_entrainement.upper())

        progressions = queryset.order_by('-derniere_progression', '-taux_reussite')

        # Sérialiser les données
        progressions_data = []
        for progression in progressions:
            progressions_data.append({
                'id': progression.id,
                'machine_id': progression.machine.id,
                'machine_nom': progression.machine.nom,
                'mode_entrainement': progression.mode_entrainement.nom if progression.mode_entrainement else '',
                'poids_actuel': progression.poids_actuel,
                'taux_reussite': progression.taux_reussite,
                'nombre_seances_machine': progression.nombre_seances_machine,
                'dernier_1rm': progression.dernier_1rm,
                'progression_poids_total': progression.progression_poids_total,
                'derniere_progression': progression.derniere_progression.isoformat() if progression.derniere_progression else None,
                'derniere_seance': progression.derniere_seance.date_debut.isoformat() if progression.derniere_seance else None
            })

        response_data = {
            'success': True,
            'data': progressions_data,
            'message': f'Progressions récupérées pour l\'utilisateur',
            'count': len(progressions_data)
        }

        logger.info(f"Progressions envoyées: {len(progressions_data)} entrées")
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erreur dans get_user_progressions: {e}")
        return Response({
            'success': False,
            'message': f'Erreur serveur: {str(e)}',
            'data': [],
            'count': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_csv_workouts(request):
    """
    Endpoint pour importer des séances d'entraînement depuis un fichier CSV
    Compatible avec l'application Android - Upload de fichier
    """
    try:
        # Vérifier qu'un fichier CSV a été uploadé
        if 'csv_file' not in request.FILES:
            return Response({
                'success': False,
                'message': 'Aucun fichier CSV fourni. Utilisez le paramètre "csv_file"',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['csv_file']

        # Vérifier que c'est bien un fichier CSV
        if not csv_file.name.endswith('.csv'):
            return Response({
                'success': False,
                'message': 'Le fichier doit être au format CSV',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

        # Lire le contenu du fichier CSV
        try:
            # Décoder le contenu en UTF-8
            content = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))

            imported_seances = []
            errors = []

            for row_num, row in enumerate(csv_reader, start=2):  # Commencer à 2 car ligne 1 = headers
                try:
                    # Parser la date
                    date_str = row.get('date', '').strip()
                    if not date_str:
                        errors.append(f"Ligne {row_num}: Date manquante")
                        continue

                    try:
                        date_prevue = parse_datetime(date_str) or timezone.now()
                    except:
                        date_prevue = timezone.now()

                    # Créer la séance
                    seance = SeanceEntrainement.objects.create(
                        utilisateur=request.user,
                        nom=row.get('nom', f"Séance importée du {date_prevue.strftime('%d/%m/%Y')}"),
                        date_prevue=date_prevue,
                        date_debut=date_prevue,
                        date_fin=date_prevue + timedelta(minutes=int(row.get('duree', 45))),
                        duree_prevue=int(row.get('duree', 45)),
                        statut='TERMINEE',
                        note_ressenti=int(row.get('note_ressenti', 7)),
                        commentaire=row.get('commentaire', 'Importé depuis CSV')
                    )

                    # Ajouter les exercices si présents
                    exercices_str = row.get('exercices', '').strip()
                    if exercices_str:
                        exercices_list = [ex.strip() for ex in exercices_str.split(',')]
                        for idx, nom_exercice in enumerate(exercices_list):
                            if nom_exercice:
                                # Chercher ou créer la machine
                                machine, created = Machine.objects.get_or_create(
                                    nom=nom_exercice,
                                    defaults={
                                        'description': 'Créé lors de l\'import CSV',
                                        'instructions': '',
                                        'increment_poids': 2.5,
                                        'poids_minimum': 0.0,
                                        'poids_maximum': 200.0
                                    }
                                )

                                # Créer l'exercice
                                exercice = ExerciceSeance.objects.create(
                                    seance=seance,
                                    machine=machine,
                                    ordre_dans_seance=idx + 1,
                                    series_prevues=int(row.get('series', 3)),
                                    repetitions_prevues=int(row.get('reps', 10)),
                                    poids_prevu=float(row.get('poids', 20)),
                                    nombre_series=int(row.get('series', 3)),
                                    repetitions_realisees=int(row.get('reps', 10)),
                                    poids_utilise=float(row.get('poids', 20)),
                                    statut='TERMINE'
                                )

                    imported_seances.append({
                        'id': seance.id,
                        'nom': seance.nom,
                        'date': seance.date_prevue.isoformat(),
                        'exercices': exercices_list if 'exercices_list' in locals() else []
                    })

                except Exception as e:
                    errors.append(f"Ligne {row_num}: {str(e)}")
                    continue

            # Préparer la réponse
            response_data = {
                'success': True,
                'message': f'Import CSV réussi. {len(imported_seances)} séances importées.',
                'data': {
                    'imported_seances': imported_seances,
                    'total_imported': len(imported_seances),
                    'errors': errors
                }
            }

            if errors:
                response_data['message'] += f' {len(errors)} erreurs rencontrées.'

            logger.info(f"Import CSV réussi: {len(imported_seances)} séances importées pour user {request.user.id}")
            return Response(response_data, status=status.HTTP_200_OK)

        except UnicodeDecodeError:
            return Response({
                'success': False,
                'message': 'Erreur de décodage du fichier CSV. Assurez-vous qu\'il est encodé en UTF-8.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Erreur dans import_csv_workouts: {e}")
        return Response({
            'success': False,
            'message': f'Erreur serveur: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

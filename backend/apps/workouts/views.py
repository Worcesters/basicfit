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

        # ------ Gestion date prévue ------
        raw_date = data.get('date') or data.get('date_prevue') or data.get('date_seance')

        if isinstance(raw_date, str) and raw_date.strip():
            try:
                # Essayer différents formats de date
                parsed = None
                formats_to_try = [
                    raw_date,  # Format original
                    raw_date + 'T00:00:00' if 'T' not in raw_date else raw_date,  # Ajouter heure si manquante
                    raw_date.replace('Z', '+00:00'),  # Remplacer Z par +00:00
                ]

                for date_format in formats_to_try:
                    try:
                        parsed = parse_datetime(date_format)
                        if parsed:
                            break
                    except:
                        try:
                            parsed = datetime.fromisoformat(date_format)
                            break
                        except:
                            continue

                if parsed:
                    date_prevue = timezone.make_aware(parsed) if parsed.tzinfo is None else parsed
                else:
                    # Si impossible de parser, utiliser aujourd'hui
                    date_prevue = timezone.now()
                    print(f"[WARNING] Impossible de parser la date '{raw_date}', utilisation de la date actuelle")
            except Exception as e:
                print(f"[ERROR] Erreur parsing date '{raw_date}': {e}")
                date_prevue = timezone.now()
        else:
            date_prevue = raw_date or timezone.now()

        print(f"[DEBUG] Date prévue traitée: {date_prevue} (original: {raw_date})")

        # ------ DEDUPLICATION LOGIC IMPROVED ------
        # Check for exact duplicate sessions on the same date with same exercises
        workout_exercises = data.get('exercices', [])

        # Look for duplicate sessions on the same date first
        existing_seances = SeanceEntrainement.objects.filter(
            utilisateur=user,
            date_prevue__date=date_prevue.date(),
            statut='TERMINEE'
        ).prefetch_related('exercices__machine', 'exercices__series')

        for existing_seance in existing_seances:
            existing_exercises = list(existing_seance.exercices.all())

            # Compare if exercises match (same machines and similar weights)
            if len(existing_exercises) == len(workout_exercises):
                match_count = 0
                for new_ex in workout_exercises:
                    for existing_ex in existing_exercises:
                        if (existing_ex.machine.nom.lower() == new_ex.get('nom', '').lower() and
                            abs(float(existing_ex.poids_utilise or 0) - float(new_ex.get('poids', 0))) < 2.5):
                            match_count += 1
                            break

                # If 80% or more exercises match, consider it a duplicate
                if match_count >= len(workout_exercises) * 0.8:
                    serializer = SeanceEntrainementSerializer(existing_seance)
                    return Response({
                        'id': existing_seance.id,
                        'nom': existing_seance.nom,
                        'statut': existing_seance.statut,
                        'message': 'Séance similaire déjà existante (éviter doublon)',
                        'data': serializer.data
                    }, status=status.HTTP_200_OK)

        # Déterminer le statut selon le type d'action
        est_planification = data.get('est_planification', False) or data.get('action') == 'planifier'

        if est_planification:
            # Mode planification : séance future
            seance = SeanceEntrainement.objects.create(
                utilisateur=user,
                nom=data.get('nom', f"Séance du {date_prevue.strftime('%d/%m/%Y')}"),
                date_prevue=date_prevue,
                duree_prevue=data.get('duree', 45),
                statut='PLANIFIEE',
                commentaire=data.get('commentaire', '')
            )
            print(f"[DEBUG] Séance PLANIFIEE créée pour le {date_prevue}")
        else:
            # Mode sauvegarde : séance terminée
            seance = SeanceEntrainement.objects.create(
                utilisateur=user,
                nom=data.get('nom', f"Séance du {timezone.now().strftime('%d/%m/%Y')}"),
                date_prevue=date_prevue,
                date_debut=timezone.now() - timedelta(minutes=data.get('duree', 45)),
                date_fin=timezone.now(),
                duree_prevue=data.get('duree', 45),
                statut='TERMINEE',
                note_ressenti=data.get('note_ressenti', 7),
                commentaire=data.get('commentaire', '')
            )
            print(f"[DEBUG] Séance TERMINEE sauvegardée")

        # Les exercices ne sont ajoutés que pour les séances terminées
        if not est_planification:
            # Ajouter les exercices
            for idx, exercice_data in enumerate(data.get('exercices', [])):
                # Récupérer la machine par nom (recherche flexible)
                machine = None
                nom_exercice = exercice_data['nom']

                # Essayer différentes stratégies de recherche
                search_strategies = [
                    lambda: Machine.objects.get(nom__iexact=nom_exercice),
                    lambda: Machine.objects.get(nom__icontains=nom_exercice),
                    lambda: Machine.objects.filter(nom__icontains=nom_exercice).first(),
                    lambda: Machine.objects.get(nom__icontains=nom_exercice.replace('é', 'e').replace('è', 'e')),
                    lambda: Machine.objects.get(nom__icontains=nom_exercice.replace('e', 'é')),
                    lambda: Machine.objects.get(nom__icontains=nom_exercice.replace('e', 'è')),
                ]

                for strategy in search_strategies:
                    try:
                        machine = strategy()
                        if machine:
                            break
                    except (Machine.DoesNotExist, Machine.MultipleObjectsReturned):
                        continue

                if not machine:
                    # Créer la machine si elle n'existe pas
                    from apps.machines.models import CategorieMachine
                    categorie_defaut, _ = CategorieMachine.objects.get_or_create(nom='MUSCULATION', defaults={
                        'description': 'Catégorie auto générée',
                    })
                    machine = Machine.objects.create(
                        nom=nom_exercice,
                        description='Créée automatiquement depuis l\'app Android',
                        instructions='',
                        categorie=categorie_defaut,
                        increment_poids=2.5,
                        poids_minimum=0.0,
                        poids_maximum=200.0
                    )

                # Vérifier si c'est une machine cardio (basé sur la catégorie ou le type d'exercice envoyé)
                is_cardio = (
                    machine.categorie.nom == 'CARDIO' if machine.categorie else False or
                    exercice_data.get('type_exercice') == 'DUREE'
                )

            if is_cardio:
                # Pour les exercices cardio, les reps représentent la durée en minutes
                duree_minutes = exercice_data.get('reps', 20)  # Durée en minutes
                exercice = ExerciceSeance.objects.create(
                    seance=seance,
                    machine=machine,
                    ordre_dans_seance=idx + 1,
                    series_prevues=1,  # Une seule série pour cardio
                    repetitions_prevues=duree_minutes,
                    duree_prevue=duree_minutes * 60,  # Convertir en secondes
                    poids_prevu=0.0,  # Pas de poids pour cardio
                    nombre_series=1,
                    repetitions_realisees=duree_minutes,
                    duree_realisee=duree_minutes * 60,
                    poids_utilise=0.0,
                    statut='TERMINE'
                )

                # Créer une seule série pour cardio
                SeriExercice.objects.create(
                    exercice=exercice,
                    numero_serie=1,
                    repetitions_prevues=duree_minutes,
                    duree_prevue=duree_minutes * 60,
                    poids_prevu=0.0,
                    repetitions_realisees=duree_minutes,
                    duree_realisee=duree_minutes * 60,
                    poids_utilise=0.0,
                    statut='REUSSIE'
                )
            else:
                # Pour les exercices de musculation
                exercice = ExerciceSeance.objects.create(
                    seance=seance,
                    machine=machine,
                    ordre_dans_seance=idx + 1,
                    series_prevues=exercice_data.get('series', 3),
                    repetitions_prevues=exercice_data.get('reps', 10),
                    poids_prevu=exercice_data.get('poids', 20),
                    nombre_series=exercice_data.get('series', 3),
                    repetitions_realisees=exercice_data.get('reps', 10),
                    poids_utilise=exercice_data.get('poids', 20),
                    statut='TERMINE'
                )

                # Ajouter les séries pour musculation
                for serie_num in range(exercice_data.get('series', 3)):
                    # Log du contenu reçu pour debug
                    print(f"[DEBUG] Création série pour exercice: {exercice_data}")
                    SeriExercice.objects.create(
                        exercice=exercice,
                        numero_serie=serie_num + 1,
                        repetitions_prevues=exercice_data.get('reps', 10),
                        poids_prevu=exercice_data.get('poids', 20),
                        repetitions_realisees=exercice_data.get('reps', 10),
                        poids_utilise=exercice_data.get('poids', 20),
                        statut='REUSSIE'
                    )

            # --- MISE À JOUR DE LA PROGRESSION ---
            from .models import ProgressionMachine, ModeEntrainement

            # S'assurer qu'il y a au moins un mode d'entraînement
            mode = ModeEntrainement.objects.first()
            if not mode:
                # Créer un mode par défaut si aucun n'existe
                mode = ModeEntrainement.objects.create(
                    nom="Prise de masse",
                    description="Mode par défaut",
                    series_recommandees=3,
                    repetitions_min=8,
                    repetitions_max=12,
                    repos_entre_series=90
                )

            # Récupérer ou créer la progression avec le mode d'entraînement
            try:
                progression = ProgressionMachine.objects.get(
                    utilisateur=user,
                    machine=machine
                )
                created = False
            except ProgressionMachine.DoesNotExist:
                # Calculer le 1RM pour cette première séance
                premier_1rm = exercice.calculer_1rm_brzycki() if not is_cardio else None

                # Créer la progression avec le poids de la séance comme base
                progression = ProgressionMachine.objects.create(
                    utilisateur=user,
                    machine=machine,
                    mode_entrainement=mode,
                    poids_actuel=exercice.poids_utilise or exercice.poids_prevu or 0.0,
                    series_actuelles=exercice.nombre_series,
                    repetitions_actuelles=exercice.repetitions_realisees,
                    derniere_seance=seance,
                    dernier_1rm=premier_1rm,
                    nombre_seances_machine=1,
                    progression_poids_total=exercice.poids_utilise or exercice.poids_prevu or 0.0,
                    taux_reussite=100.0,
                    increment_automatique=True,
                    seuil_progression=90.0,
                    derniere_progression=timezone.now(),
                )

                # IMPORTANT: Pour la première séance, on démarre avec le poids utilisé
                # La recommandation sera calculée après cette première séance
                print(f"[DEBUG] Nouvelle progression créée pour {machine.nom}:")
                print(f"  Poids première séance: {exercice.poids_utilise}kg")
                print(f"  1RM calculé: {premier_1rm}kg")
                print(f"  Poids de départ stocké: {progression.poids_actuel}kg")

                created = True
            if not created:
                # Mise à jour des champs de progression
                if not is_cardio:
                    # Mettre à jour le 1RM avec le meilleur calculé
                    nouveau_1rm = exercice.calculer_1rm_brzycki()
                    if nouveau_1rm and (not progression.dernier_1rm or nouveau_1rm > progression.dernier_1rm):
                        progression.dernier_1rm = nouveau_1rm

                    # Ajouter au tonnage total
                    progression.progression_poids_total += exercice.poids_utilise or exercice.poids_prevu or 0.0
                else:
                    # Pour cardio, mettre à jour la durée
                    progression.repetitions_actuelles = exercice.repetitions_realisees

                # Mettre à jour les informations de base
                progression.series_actuelles = exercice.nombre_series
                progression.derniere_seance = seance
                progression.nombre_seances_machine += 1
                progression.derniere_progression = timezone.now()

                # CALCUL DU TAUX DE RÉUSSITE BASÉ SUR LES SÉRIES
                series_reussies = 0
                series_totales = exercice.series.count()
                if series_totales > 0:
                    for serie in exercice.series.all():
                        if serie.repetitions_realisees >= serie.repetitions_prevues * 0.8:  # 80% = réussite
                            series_reussies += 1
                    progression.taux_reussite = (series_reussies / series_totales) * 100
                else:
                    progression.taux_reussite = 100.0  # Par défaut si pas de séries détaillées

                # *** CALCUL DE LA NOUVELLE RECOMMANDATION POUR LA PROCHAINE SÉANCE ***
                ancien_poids = progression.poids_actuel

                # Pour éviter de bloquer à 17kg, utilisons directement le poids de la séance
                # si c'est supérieur à la recommandation actuelle
                poids_seance = exercice.poids_utilise or exercice.poids_prevu or 0.0
                nouvelle_recommandation = progression.calculer_recommandation_professionnelle()

                # Si le poids de la séance actuelle est supérieur à la recommandation,
                # utiliser le poids de la séance comme base pour la prochaine fois
                if poids_seance > nouvelle_recommandation:
                    # Le joueur progresse plus vite que prévu, suivre son rythme
                    progression.poids_actuel = poids_seance
                    print(f"[DEBUG] Progression accélérée détectée - utilisation du poids séance: {poids_seance}kg")
                else:
                    progression.poids_actuel = nouvelle_recommandation

                print(f"[DEBUG] Progression mise à jour pour {machine.nom}:")
                print(f"  Ancien poids: {ancien_poids}kg")
                print(f"  Poids de la séance: {poids_seance}kg")
                print(f"  Recommandation calculée: {nouvelle_recommandation}kg")
                print(f"  Nouveau poids retenu: {progression.poids_actuel}kg")
                print(f"  1RM: {progression.dernier_1rm}kg")
                print(f"  Taux réussite: {progression.taux_reussite}%")

                progression.save()

        # Calculer les métriques
        seance.calculer_metriques()

        try:
            serializer = SeanceEntrainementSerializer(seance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as serialization_error:
            # Si la sérialisation échoue, retourner une réponse simple mais valide
            return Response({
                'id': seance.id,
                'nom': seance.nom,
                'statut': seance.statut,
                'message': 'Séance sauvegardée avec succès',
                'warning': f'Erreur de sérialisation: {str(serialization_error)}'
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
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

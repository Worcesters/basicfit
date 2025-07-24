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

from .models import SeanceEntrainement, ExerciceSeance, SeriExercice, ProgressionMachine
from .serializers import (
    SeanceEntrainementSerializer, SeanceCreateSerializer,
    ExerciceSeanceSerializer, SeriExerciceSerializer,
    ProgressionMachineSerializer, WorkoutStatsSerializer,
    MachineSerializer
)
from apps.machines.models import Machine


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
        raw_date = data.get('date') or data.get('date_prevue')
        if isinstance(raw_date, str):
            # Support ISO 8601 ou formats courants
            parsed = parse_datetime(raw_date) or datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
            date_prevue = timezone.make_aware(parsed) if parsed.tzinfo is None else parsed
        else:
            date_prevue = raw_date or timezone.now()

        # Créer la séance
        seance = SeanceEntrainement.objects.create(
            utilisateur=user,
            nom=data.get('nom', f"Séance du {timezone.now().strftime('%d/%m/%Y')}"),
            date_prevue = date_prevue,
            date_debut  = timezone.now() - timedelta(minutes=data.get('duree', 45)),
            date_fin    = timezone.now(),
            duree_prevue= data.get('duree', 45),
            statut      = 'TERMINEE',
            note_ressenti = data.get('note_ressenti', 7),
            commentaire   = data.get('commentaire', '')
        )

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
                progression = ProgressionMachine.objects.create(
                    utilisateur=user,
                    machine=machine,
                    mode_entrainement=mode,
                    poids_actuel=exercice.poids_utilise or exercice.poids_prevu or 0.0,
                    series_actuelles=exercice.nombre_series,
                    repetitions_actuelles=exercice.repetitions_realisees,
                    derniere_seance=seance,
                    dernier_1rm=exercice.calculer_1rm_brzycki() if not is_cardio else None,
                    nombre_seances_machine=1,
                    progression_poids_total=exercice.poids_utilise or exercice.poids_prevu or 0.0,
                    taux_reussite=100.0,
                    increment_automatique=True,
                    seuil_progression=90.0,
                    derniere_progression=timezone.now(),
                )
                created = True
            if not created:
                # Mise à jour des champs
                if not is_cardio:
                    # Pour musculation, mettre à jour le poids et 1RM
                    progression.poids_actuel = exercice.poids_utilise or exercice.poids_prevu or progression.poids_actuel
                    progression.dernier_1rm = exercice.calculer_1rm_brzycki()
                    progression.progression_poids_total += exercice.poids_utilise or exercice.poids_prevu or 0.0
                else:
                    # Pour cardio, mettre à jour la durée
                    progression.repetitions_actuelles = exercice.repetitions_realisees

                progression.series_actuelles = exercice.nombre_series
                progression.derniere_seance = seance
                progression.nombre_seances_machine += 1
                progression.taux_reussite = 100.0
                progression.derniere_progression = timezone.now()
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
def get_recommendation_by_id(request, machine_id):
    """Endpoint pour obtenir la recommandation de poids basée sur ProgressionMachine avec ID"""
    try:
        user = request.user

        # Récupérer la machine par ID
        try:
            machine = Machine.objects.get(id=machine_id)
        except Machine.DoesNotExist:
            return Response({'error': f'Machine avec ID {machine_id} non trouvée'}, status=status.HTTP_404_NOT_FOUND)

        # Récupérer l'objectif de l'utilisateur (depuis le profil)
        objectif = getattr(user, 'objectif_sportif', 'PRISE_MASSE')  # Valeur par défaut

        # Récupérer la progression pour cette machine
        try:
            progression = ProgressionMachine.objects.get(
                utilisateur=user,
                machine=machine
            )

            # Calculer la recommandation basée sur la progression
            poids_recommande = progression.calculer_recommandation_professionnelle()
            series_recommandees = progression.series_actuelles
            reps_recommandees = progression.repetitions_actuelles

            # Ajuster selon l'objectif
            if objectif == "Force":
                reps_recommandees = 4
                repos_recommande = 180
            elif objectif == "Prise de masse":
                reps_recommandees = 10
                repos_recommande = 90
            elif objectif == "Endurance":
                reps_recommandees = 18
                repos_recommande = 60
            elif objectif == "Sèche":
                reps_recommandees = 12
                repos_recommande = 75
            else:
                repos_recommande = 90

            # Vérifier si on peut progresser
            peut_progresser = progression.evaluer_progression(None)

            recommendation = {
                'machine_id': machine.id,
                'machine_nom': machine.nom,
                'poids_recommande': poids_recommande,
                'series_recommandees': series_recommandees,
                'reps_recommandees': reps_recommandees,
                'repos_recommande': repos_recommande,
                'objectif': objectif,
                'peut_progresser': peut_progresser,
                'dernier_1rm': progression.dernier_1rm,
                'nombre_seances': progression.nombre_seances_machine,
                'progression_totale': progression.progression_poids_total,
                'taux_reussite': progression.taux_reussite,
                'derniere_progression': progression.derniere_progression.isoformat() if progression.derniere_progression else None,
                'source': 'progression_machine'
            }

        except ProgressionMachine.DoesNotExist:
            # Pas de progression trouvée, calculer une suggestion de départ
            from apps.machines.models import GroupeMusculaire

            # Détecter le groupe musculaire principal
            groupes_primaires = machine.groupes_musculaires_primaires.all()
            groupe_principal = groupes_primaires.first() if groupes_primaires.exists() else None

            # Poids de base selon le groupe musculaire
            if groupe_principal:
                if 'pectoraux' in groupe_principal.nom.lower():
                    poids_base = 30.0
                elif 'dos' in groupe_principal.nom.lower():
                    poids_base = 25.0
                elif 'jambes' in groupe_principal.nom.lower() or 'cuisses' in groupe_principal.nom.lower():
                    poids_base = 40.0
                elif 'epaules' in groupe_principal.nom.lower():
                    poids_base = 15.0
                elif 'bras' in groupe_principal.nom.lower():
                    poids_base = 10.0
                else:
                    poids_base = 20.0
            else:
                poids_base = 20.0

            # Ajuster selon l'objectif
            if objectif == "Force":
                poids_base *= 0.8
                reps_recommandees = 4
                repos_recommande = 180
            elif objectif == "Prise de masse":
                reps_recommandees = 10
                repos_recommande = 90
            elif objectif == "Endurance":
                poids_base *= 0.7
                reps_recommandees = 18
                repos_recommande = 60
            elif objectif == "Sèche":
                poids_base *= 0.9
                reps_recommandees = 12
                repos_recommande = 75
            else:
                reps_recommandees = 10
                repos_recommande = 90

            recommendation = {
                'machine_id': machine.id,
                'machine_nom': machine.nom,
                'poids_recommande': poids_base,
                'series_recommandees': 3,
                'reps_recommandees': reps_recommandees,
                'repos_recommande': repos_recommande,
                'objectif': objectif,
                'peut_progresser': False,
                'dernier_1rm': None,
                'nombre_seances': 0,
                'progression_totale': 0.0,
                'taux_reussite': 0.0,
                'derniere_progression': None,
                'source': 'suggestion_depart'
            }

        return Response(recommendation, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendation(request, machine_name):
    """Endpoint pour obtenir la recommandation de poids basée sur ProgressionMachine"""
    try:

        user = request.user

        # Récupérer la machine par nom (recherche flexible)
        try:
            # Essayer d'abord une correspondance exacte
            machine = Machine.objects.get(nom__iexact=machine_name)
        except Machine.DoesNotExist:
            try:
                # Essayer une recherche partielle
                machine = Machine.objects.get(nom__icontains=machine_name)
            except Machine.DoesNotExist:
                try:
                    # Essayer avec des variations courantes
                    variations = [
                        machine_name.replace('é', 'e').replace('è', 'e'),
                        machine_name.replace('e', 'é'),
                        machine_name.replace('e', 'è'),
                    ]
                    for variation in variations:
                        try:
                            machine = Machine.objects.get(nom__icontains=variation)
                            break
                        except Machine.DoesNotExist:
                            continue
                    else:
                        return Response({'error': f'Machine "{machine_name}" non trouvée'}, status=status.HTTP_404_NOT_FOUND)
                except:
                    return Response({'error': f'Machine "{machine_name}" non trouvée'}, status=status.HTTP_404_NOT_FOUND)

        # Récupérer l'objectif de l'utilisateur (depuis le profil)
        objectif = getattr(user, 'objectif_sportif', 'PRISE_MASSE')  # Valeur par défaut

        # Récupérer la progression pour cette machine
        try:
            progression = ProgressionMachine.objects.get(
                utilisateur=user,
                machine=machine
            )

            # Calculer la recommandation basée sur la progression
            poids_recommande = progression.calculer_recommandation_professionnelle()
            series_recommandees = progression.series_actuelles
            reps_recommandees = progression.repetitions_actuelles

            # Ajuster selon l'objectif
            if objectif == "Force":
                reps_recommandees = 4
                repos_recommande = 180
            elif objectif == "Prise de masse":
                reps_recommandees = 10
                repos_recommande = 90
            elif objectif == "Endurance":
                reps_recommandees = 18
                repos_recommande = 60
            elif objectif == "Sèche":
                reps_recommandees = 12
                repos_recommande = 75
            else:
                repos_recommande = 90

            # Vérifier si on peut progresser
            peut_progresser = progression.evaluer_progression(None)  # On passe None car on n'a pas l'exercice_seance ici

            recommendation = {
                'machine_id': machine.id,
                'machine_nom': machine.nom,
                'poids_recommande': poids_recommande,
                'series_recommandees': series_recommandees,
                'reps_recommandees': reps_recommandees,
                'repos_recommande': repos_recommande,
                'objectif': objectif,
                'peut_progresser': peut_progresser,
                'dernier_1rm': progression.dernier_1rm,
                'nombre_seances': progression.nombre_seances_machine,
                'progression_totale': progression.progression_poids_total,
                'taux_reussite': progression.taux_reussite,
                'derniere_progression': progression.derniere_progression.isoformat() if progression.derniere_progression else None,
                'source': 'progression_machine'
            }

        except ProgressionMachine.DoesNotExist:
            # Pas de progression trouvée, calculer une suggestion de départ
            from apps.machines.models import GroupeMusculaire

            # Détecter le groupe musculaire principal
            groupes_primaires = machine.groupes_musculaires_primaires.all()
            groupe_principal = groupes_primaires.first() if groupes_primaires.exists() else None

            # Poids de base selon le groupe musculaire
            if groupe_principal:
                if 'pectoraux' in groupe_principal.nom.lower():
                    poids_base = 30.0
                elif 'dos' in groupe_principal.nom.lower():
                    poids_base = 25.0
                elif 'jambes' in groupe_principal.nom.lower() or 'cuisses' in groupe_principal.nom.lower():
                    poids_base = 40.0
                elif 'epaules' in groupe_principal.nom.lower():
                    poids_base = 15.0
                elif 'bras' in groupe_principal.nom.lower():
                    poids_base = 10.0
                else:
                    poids_base = 20.0
            else:
                poids_base = 20.0

            # Ajuster selon l'objectif
            if objectif == "Force":
                poids_base *= 0.8
                reps_recommandees = 4
                repos_recommande = 180
            elif objectif == "Prise de masse":
                reps_recommandees = 10
                repos_recommande = 90
            elif objectif == "Endurance":
                poids_base *= 0.7
                reps_recommandees = 18
                repos_recommande = 60
            elif objectif == "Sèche":
                poids_base *= 0.9
                reps_recommandees = 12
                repos_recommande = 75
            else:
                reps_recommandees = 10
                repos_recommande = 90

            recommendation = {
                'machine_id': machine.id,
                'machine_nom': machine.nom,
                'poids_recommande': poids_base,
                'series_recommandees': 3,
                'reps_recommandees': reps_recommandees,
                'repos_recommande': repos_recommande,
                'objectif': objectif,
                'peut_progresser': False,
                'dernier_1rm': None,
                'nombre_seances': 0,
                'progression_totale': 0.0,
                'taux_reussite': 0.0,
                'derniere_progression': None,
                'source': 'suggestion_depart'
            }

        return Response(recommendation, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

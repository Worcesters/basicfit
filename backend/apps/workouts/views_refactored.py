"""
Vues refactorisées pour les entraînements - Version professionnelle
Elimination des bugs et amélioration de la robustesse
"""
import logging
from django.db.models import Sum, Count, Max, Avg
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta, datetime
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt

from .models import SeanceEntrainement, ExerciceSeance, SeriExercice, ProgressionMachine
from .workout_service import WorkoutSaveService
from .serializers import (
    SeanceEntrainementSerializer, SeanceCreateSerializer,
    ExerciceSeanceSerializer, SeriExerciceSerializer,
    ProgressionMachineSerializer, WorkoutStatsSerializer,
    MachineSerializer
)
from apps.machines.models import Machine
from .workout_service import WorkoutSaveService, CalendarService
from .new_recommendation_system import ProgressionBasedRecommendationSystem

logger = logging.getLogger(__name__)


class SeanceEntrainementViewSet(viewsets.ModelViewSet):
    """ViewSet refactorisé pour les séances d'entraînement"""
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
def save_workout_professional(request):
    """
    Endpoint professionnel pour sauvegarder les séances
    Remplace l'ancien système avec déduplication et gestion d'erreurs
    """
    try:
        user = request.user
        workout_data = request.data
        
        if not isinstance(workout_data, dict):
            return Response({
                'error': 'Format de données invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Utiliser le service professionnel
        save_service = WorkoutSaveService()
        session, created, message = save_service.save_workout(user, workout_data)
        
        # Mettre à jour les progressions si la séance est terminée
        if session and session.statut == 'TERMINEE':
            try:
                progression_system = ProgressionBasedRecommendationSystem()
                progression_system.update_progression_after_workout(session)
                logger.info(f"Progressions mises à jour pour la séance {session.id}")
            except Exception as e:
                logger.warning(f"Erreur mise à jour progressions: {e}")
                # Ne pas échouer la sauvegarde pour autant
        
        # Sérialiser la réponse
        try:
            serializer = SeanceEntrainementSerializer(session)
            response_data = {
                'success': True,
                'created': created,
                'message': message,
                'data': serializer.data
            }
            
            if created:
                logger.info(f"Nouvelle séance créée: {session.nom} (ID: {session.id})")
            else:
                logger.info(f"Séance existante retournée: {session.nom} (ID: {session.id})")
            
            return Response(response_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Exception as serialization_error:
            logger.error(f"Erreur sérialisation: {serialization_error}")
            # Réponse de secours
            return Response({
                'success': True,
                'created': created,
                'message': message,
                'session_id': session.id,
                'session_name': session.nom,
                'warning': 'Séance sauvegardée mais erreur de sérialisation'
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except ValueError as ve:
        logger.error(f"Erreur validation données: {ve}")
        return Response({
            'error': f'Données invalides: {str(ve)}'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde séance: {e}")
        return Response({
            'error': 'Erreur interne du serveur'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendation_professional(request, machine_id):
    """
    Endpoint professionnel pour les recommandations
    Utilise le nouveau système de recommandation
    """
    try:
        user = request.user
        
        # Récupérer la machine
        try:
            machine = Machine.objects.get(id=machine_id)
        except Machine.DoesNotExist:
            return Response({
                'error': f'Machine avec ID {machine_id} non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtenir la recommandation
        recommendation_result = RecommendationManager.get_recommendation_for_machine(user, machine)
        
        if recommendation_result['success']:
            return Response(recommendation_result['data'], status=status.HTTP_200_OK)
        else:
            return Response({
                'error': recommendation_result.get('error', 'Erreur génération recommandation'),
                'fallback_data': recommendation_result['data']
            }, status=status.HTTP_200_OK)  # On retourne quand même les données de secours
        
    except Exception as e:
        logger.error(f"Erreur endpoint recommandation: {e}")
        return Response({
            'error': 'Erreur interne du serveur'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendation_by_name_professional(request, machine_name):
    """
    Endpoint professionnel pour les recommandations par nom
    """
    try:
        user = request.user
        
        # Récupérer la machine par nom (recherche flexible)
        machine = None
        search_strategies = [
            lambda: Machine.objects.get(nom__iexact=machine_name),
            lambda: Machine.objects.filter(nom__icontains=machine_name).first(),
            lambda: Machine.objects.filter(
                nom__icontains=machine_name.replace('é', 'e').replace('è', 'e')
            ).first(),
        ]
        
        for strategy in search_strategies:
            try:
                machine = strategy()
                if machine:
                    break
            except Machine.DoesNotExist:
                continue
        
        if not machine:
            return Response({
                'error': f'Machine "{machine_name}" non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtenir la recommandation
        recommendation_result = RecommendationManager.get_recommendation_for_machine(user, machine)
        
        if recommendation_result['success']:
            return Response(recommendation_result['data'], status=status.HTTP_200_OK)
        else:
            return Response({
                'error': recommendation_result.get('error', 'Erreur génération recommandation'),
                'fallback_data': recommendation_result['data']
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur endpoint recommandation par nom: {e}")
        return Response({
            'error': 'Erreur interne du serveur'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar_sessions_professional(request):
    """Récupère les séances pour le calendrier"""
    try:
        user = request.user
        
        # Récupérer les paramètres de date
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Parser les dates si fournies
        parsed_start = None
        parsed_end = None
        
        if start_date:
            try:
                parsed_start = parse_datetime(start_date) or datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                pass
                
        if end_date:
            try:
                parsed_end = parse_datetime(end_date) or datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                pass
        
        # Utiliser le service calendrier
        sessions = CalendarService.get_calendar_sessions(user, parsed_start, parsed_end)
        
        # Format compatible avec ApiResponse attendu par Android
        return Response({
            'success': True,
            'data': sessions,
            'message': 'Séances récupérées avec succès'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur endpoint calendrier: {e}")
        return Response({
            'success': False,
            'data': [],
            'message': f'Erreur récupération du calendrier: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def plan_session_professional(request):
    """Planifie une nouvelle séance dans le calendrier"""
    try:
        user = request.user
        session_data = request.data
        
        if not isinstance(session_data, dict):
            return Response({
                'error': 'Format de données invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Utiliser le service calendrier
        session = CalendarService.plan_session(user, session_data)
        
        # Sérialiser la réponse
        serializer = SeanceEntrainementSerializer(session)
        
        return Response({
            'success': True,
            'message': 'Séance planifiée avec succès',
            'session': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as ve:
        return Response({
            'error': f'Erreur planification: {str(ve)}'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Erreur planification séance: {e}")
        return Response({
            'error': 'Erreur interne du serveur'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== ENDPOINTS DE COMPATIBILITÉ =====

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
            'message': 'API workouts fonctionnelle ✅',
            'version': '2.0_professional'
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

        return Response({
            'results': data, 
            'count': len(data),
            'version': '2.0_professional'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# ===== ENDPOINT DE MIGRATION (Pour nettoyer les anciennes données) =====

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_duplicate_sessions(request):
    """
    Endpoint pour nettoyer les séances dupliquées
    À utiliser une seule fois pour nettoyer les anciennes données
    """
    try:
        user = request.user
        
        # Récupérer toutes les séances de l'utilisateur
        sessions = SeanceEntrainement.objects.filter(
            utilisateur=user,
            statut='TERMINEE'
        ).order_by('date_prevue', 'created_at')
        
        duplicates_removed = 0
        seen_fingerprints = set()
        
        for session in sessions:
            # Générer un fingerprint pour cette séance
            exercises_data = []
            for exercice in session.exercices.all():
                exercises_data.append({
                    'nom': exercice.machine.nom,
                    'series': exercice.nombre_series,
                    'reps': exercice.repetitions_realisees,
                    'poids': exercice.poids_utilise or 0
                })
            
            if exercises_data:
                from .workout_service import WorkoutDeduplicationService
                fingerprint = WorkoutDeduplicationService.generate_workout_fingerprint(
                    user.id, session.date_prevue, exercises_data
                )
                
                if fingerprint in seen_fingerprints:
                    # Séance dupliquée, la supprimer
                    session.delete()
                    duplicates_removed += 1
                else:
                    seen_fingerprints.add(fingerprint)
        
        return Response({
            'success': True,
            'duplicates_removed': duplicates_removed,
            'message': f'{duplicates_removed} séances dupliquées supprimées'
        })
        
    except Exception as e:
        logger.error(f"Erreur nettoyage doublons: {e}")
        return Response({
            'error': 'Erreur lors du nettoyage'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def force_progression_update(request):
    """Force la mise à jour des progressions pour toutes les séances terminées de l'utilisateur"""
    try:
        user = request.user
        
        # Récupérer toutes les séances terminées récentes (7 derniers jours)
        from datetime import timedelta
        recent_sessions = SeanceEntrainement.objects.filter(
            utilisateur=user,
            statut='TERMINEE',
            date_debut__gte=timezone.now() - timedelta(days=7)
        ).prefetch_related('exercices')
        
        updated_count = 0
        save_service = WorkoutSaveService()
        
        for session in recent_sessions:
            # Convertir les exercices au format attendu
            exercises = []
            for exercice in session.exercices.all():
                if exercice.series.exists():
                    # Prendre les valeurs de la dernière série
                    last_serie = exercice.series.last()
                    exercises.append({
                        'nom': exercice.machine.nom,
                        'series': exercice.nombre_series,
                        'reps': last_serie.repetitions_realisees,
                        'poids': last_serie.poids_utilise
                    })
            
            if exercises:
                save_service._update_machine_progressions(user, exercises)
                updated_count += 1
        
        logger.info(f"Mise à jour forcée des progressions: {updated_count} séances traitées")
        
        return Response({
            'success': True,
            'updated_sessions': updated_count,
            'message': f'Progressions mises à jour pour {updated_count} séances'
        })
        
    except Exception as e:
        logger.error(f"Erreur mise à jour forcée: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
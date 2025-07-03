"""
API REST pour les séances d'entraînement
"""
from django.db.models import Sum, Count, Max, Avg
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

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
    permission_classes = [IsAuthenticated]

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

        # Créer la séance
        seance = SeanceEntrainement.objects.create(
            utilisateur=user,
            nom=data.get('nom', f"Séance du {timezone.now().strftime('%d/%m/%Y')}"),
            date_debut=timezone.now() - timedelta(minutes=data.get('duree', 45)),
            date_fin=timezone.now(),
            duree_prevue=data.get('duree', 45),
            statut='TERMINEE',
            note_ressenti=data.get('note_ressenti', 7),
            commentaire=data.get('commentaire', '')
        )

        # Ajouter les exercices
        for idx, exercice_data in enumerate(data.get('exercices', [])):
            # Récupérer la machine par nom
            try:
                machine = Machine.objects.get(nom__icontains=exercice_data['nom'])
            except Machine.DoesNotExist:
                # Créer une machine basique si elle n'existe pas
                machine = Machine.objects.create(
                    nom=exercice_data['nom'],
                    groupe_musculaire='Général'
                )

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

            # Ajouter les séries
            for serie_num in range(exercice_data.get('series', 3)):
                SeriExercice.objects.create(
                    exercice=exercice,
                    numero_serie=serie_num + 1,
                    repetitions_prevues=exercice_data.get('reps', 10),
                    poids_prevu=exercice_data.get('poids', 20),
                    repetitions_realisees=exercice_data.get('reps', 10),
                    poids_utilise=exercice_data.get('poids', 20),
                    statut='REUSSIE'
                )

        # Calculer les métriques
        seance.calculer_metriques()

        serializer = SeanceEntrainementSerializer(seance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
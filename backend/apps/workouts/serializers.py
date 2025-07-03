"""
Serializers pour l'API des entraînements
"""
from rest_framework import serializers
from .models import SeanceEntrainement, ExerciceSeance, SeriExercice, ProgressionMachine
from apps.machines.models import Machine, VarianteMachine
from apps.core.models import ModeEntrainement


class MachineSerializer(serializers.ModelSerializer):
    """Serializer pour les machines"""
    class Meta:
        model = Machine
        fields = ['id', 'nom', 'nom_technique', 'groupe_musculaire', 'description']


class VarianteMachineSerializer(serializers.ModelSerializer):
    """Serializer pour les variantes de machines"""
    class Meta:
        model = VarianteMachine
        fields = ['id', 'nom', 'description']


class ModeEntrainementSerializer(serializers.ModelSerializer):
    """Serializer pour les modes d'entraînement"""
    class Meta:
        model = ModeEntrainement
        fields = ['id', 'nom', 'description']


class SeriExerciceSerializer(serializers.ModelSerializer):
    """Serializer pour les séries d'exercices"""
    class Meta:
        model = SeriExercice
        fields = [
            'id', 'numero_serie', 'repetitions_prevues', 'poids_prevu',
            'repetitions_realisees', 'poids_utilise', 'repos_reel',
            'statut', 'duree_serie', 'note_effort', 'commentaire'
        ]


class ExerciceSeanceSerializer(serializers.ModelSerializer):
    """Serializer pour les exercices de séance"""
    machine = MachineSerializer(read_only=True)
    machine_id = serializers.IntegerField(write_only=True)
    variante = VarianteMachineSerializer(read_only=True)
    variante_id = serializers.IntegerField(write_only=True, required=False)
    series = SeriExerciceSerializer(many=True, read_only=True)

    class Meta:
        model = ExerciceSeance
        fields = [
            'id', 'machine', 'machine_id', 'variante', 'variante_id',
            'ordre_dans_seance', 'series_prevues', 'repetitions_prevues',
            'poids_prevu', 'repos_prevu', 'statut', 'nombre_series',
            'repetitions_realisees', 'poids_utilise', 'volume_total',
            'tonnage_total', 'duree_totale', 'note_ressenti',
            'commentaire', 'series'
        ]


class SeanceEntrainementSerializer(serializers.ModelSerializer):
    """Serializer pour les séances d'entraînement"""
    mode_entrainement = ModeEntrainementSerializer(read_only=True)
    mode_entrainement_id = serializers.IntegerField(write_only=True, required=False)
    exercices = ExerciceSeanceSerializer(many=True, read_only=True)
    duree_reelle = serializers.ReadOnlyField()

    class Meta:
        model = SeanceEntrainement
        fields = [
            'id', 'mode_entrainement', 'mode_entrainement_id', 'nom', 'description',
            'date_prevue', 'date_debut', 'date_fin', 'duree_prevue', 'duree_reelle',
            'statut', 'note_ressenti', 'note_difficulte', 'commentaire',
            'volume_total', 'tonnage_total', 'nombre_exercices',
            'nombre_series_totales', 'salle', 'exercices'
        ]


class SeanceCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une séance simple"""
    exercices_data = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = SeanceEntrainement
        fields = [
            'nom', 'description', 'date_prevue', 'date_debut', 'date_fin',
            'duree_prevue', 'statut', 'note_ressenti', 'note_difficulte',
            'commentaire', 'salle', 'exercices_data'
        ]

    def create(self, validated_data):
        exercices_data = validated_data.pop('exercices_data', [])
        validated_data['utilisateur'] = self.context['request'].user
        seance = SeanceEntrainement.objects.create(**validated_data)

        for exercice_data in exercices_data:
            series_data = exercice_data.pop('series', [])
            exercice = ExerciceSeance.objects.create(seance=seance, **exercice_data)

            for serie_data in series_data:
                SeriExercice.objects.create(exercice=exercice, **serie_data)

        seance.calculer_metriques()
        return seance


class ProgressionMachineSerializer(serializers.ModelSerializer):
    """Serializer pour la progression sur machines"""
    machine = MachineSerializer(read_only=True)

    class Meta:
        model = ProgressionMachine
        fields = [
            'id', 'machine', 'poids_actuel', 'series_actuelles',
            'repetitions_actuelles', 'dernier_1rm', 'nombre_seances_machine',
            'progression_poids_total', 'taux_reussite', 'premiere_utilisation',
            'derniere_progression'
        ]


class WorkoutStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques utilisateur"""
    total_seances = serializers.IntegerField()
    total_minutes = serializers.IntegerField()
    total_calories = serializers.IntegerField()
    seances_excellentes = serializers.IntegerField()
    record_poids = serializers.FloatField()
    exercices_favoris = serializers.ListField()
    progression_generale = serializers.FloatField()
"""
Service professionnel pour la gestion des séances d'entraînement
Refactorisation complète pour éliminer les doublons et améliorer la robustesse
"""
import logging
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta

from .models import SeanceEntrainement, ExerciceSeance, SeriExercice, ProgressionMachine, ModeEntrainement
from apps.machines.models import Machine, CategorieMachine
# Ancien système de recommandation supprimé

logger = logging.getLogger(__name__)


class WorkoutDeduplicationService:
    """Service de déduplication des séances"""
    
    @staticmethod
    def generate_workout_fingerprint(user_id: int, date: datetime, exercises: List[Dict]) -> str:
        """
        Génère une empreinte unique pour une séance
        """
        # Normaliser les exercices pour la comparaison
        normalized_exercises = []
        for ex in exercises:
            normalized_exercises.append({
                'nom': ex.get('nom', '').strip().lower(),
                'series': int(ex.get('series', 0)),
                'reps': int(ex.get('reps', 0)),
                'poids': float(ex.get('poids', 0))
            })
        
        # Trier les exercices par nom pour un hash cohérent
        normalized_exercises.sort(key=lambda x: x['nom'])
        
        # Créer l'empreinte
        fingerprint_data = {
            'user_id': user_id,
            'date': date.date().isoformat(),
            'exercises': normalized_exercises
        }
        
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:16]
    
    @staticmethod
    def check_duplicate_workout(user, date: datetime, exercises: List[Dict], 
                              time_window_minutes: int = 30) -> Optional[SeanceEntrainement]:
        """
        Vérifie s'il existe déjà une séance similaire dans une fenêtre de temps
        """
        fingerprint = WorkoutDeduplicationService.generate_workout_fingerprint(
            user.id, date, exercises
        )
        
        # Chercher dans une fenêtre de temps
        start_time = date - timedelta(minutes=time_window_minutes)
        end_time = date + timedelta(minutes=time_window_minutes)
        
        # Chercher d'abord par fingerprint exact
        existing = SeanceEntrainement.objects.filter(
            utilisateur=user,
            date_prevue__gte=start_time,
            date_prevue__lte=end_time,
            commentaire__contains=f"FP:{fingerprint}"
        ).first()
        
        if existing:
            logger.warning(f"Séance dupliquée détectée (fingerprint): {fingerprint}")
            return existing
        
        # Chercher par similarité d'exercices
        recent_sessions = SeanceEntrainement.objects.filter(
            utilisateur=user,
            date_prevue__gte=start_time,
            date_prevue__lte=end_time,
            statut='TERMINEE'
        ).prefetch_related('exercices__machine')
        
        for session in recent_sessions:
            if WorkoutDeduplicationService._sessions_are_similar(session, exercises):
                logger.warning(f"Séance similaire détectée: {session.id}")
                return session
        
        return None
    
    @staticmethod
    def _sessions_are_similar(session: SeanceEntrainement, new_exercises: List[Dict], 
                             similarity_threshold: float = 0.8) -> bool:
        """
        Compare une séance existante avec de nouveaux exercices
        """
        existing_exercises = list(session.exercices.all())
        
        if len(existing_exercises) == 0 or len(new_exercises) == 0:
            return False
        
        # Si le nombre d'exercices est très différent, pas similaire
        if abs(len(existing_exercises) - len(new_exercises)) > 2:
            return False
        
        match_count = 0
        for new_ex in new_exercises:
            for existing_ex in existing_exercises:
                if (existing_ex.machine.nom.lower() == new_ex.get('nom', '').strip().lower() and
                    abs(float(existing_ex.poids_utilise or 0) - float(new_ex.get('poids', 0))) < 5.0):
                    match_count += 1
                    break
        
        similarity = match_count / len(new_exercises)
        return similarity >= similarity_threshold


class WorkoutSaveService:
    """Service professionnel de sauvegarde des séances"""
    
    def __init__(self):
        self.dedup_service = WorkoutDeduplicationService()
    
    @transaction.atomic
    def save_workout(self, user, workout_data: Dict) -> Tuple[SeanceEntrainement, bool, str]:
        """
        Sauvegarde une séance avec déduplication et gestion d'erreurs
        
        Returns:
            (séance, created, message)
        """
        try:
            # 1. Validation des données
            validated_data = self._validate_workout_data(workout_data)
            
            # 2. Parsing de la date
            date_prevue = self._parse_workout_date(validated_data.get('date'))
            
            # 3. Déterminer le type de séance
            is_planning = validated_data.get('action') == 'planifier' or validated_data.get('est_planification', False)
            exercises = validated_data.get('exercices', [])
            
            # 4. Vérification de duplication (seulement pour les séances terminées)
            if not is_planning and exercises:
                existing_session = self.dedup_service.check_duplicate_workout(
                    user, date_prevue, exercises
                )
                if existing_session:
                    return existing_session, False, "Séance similaire déjà existante"
            
            # 5. Création de la séance
            session = self._create_workout_session(user, validated_data, date_prevue, is_planning)
            
            # 6. Ajout des exercices (seulement pour les séances terminées)
            if not is_planning and exercises:
                self._add_exercises_to_session(session, exercises)
                
                # 7. Calcul des métriques
                session.calculer_metriques()
                session.save()
                
                # 8. Mise à jour des progressions machine
                self._update_machine_progressions(user, exercises)
            
            logger.info(f"Séance sauvegardée: {session.nom} ({session.statut})")
            return session, True, "Séance sauvegardée avec succès"
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde séance: {e}")
            raise
    
    def _validate_workout_data(self, data: Dict) -> Dict:
        """Valide et nettoie les données d'entraînement"""
        if not isinstance(data, dict):
            raise ValueError("Les données d'entraînement doivent être un dictionnaire")
        
        # Valeurs par défaut
        validated = {
            'nom': data.get('nom', '').strip(),
            'duree': max(1, int(data.get('duree', 45))),
            'note_ressenti': max(1, min(10, int(data.get('note_ressenti', 7)))),
            'commentaire': data.get('commentaire', '').strip()[:500],  # Limite de 500 caractères
            'exercices': data.get('exercices', []),
            'action': data.get('action', '').strip().lower(),
            'est_planification': bool(data.get('est_planification', False)),
            'date': data.get('date') or data.get('date_prevue') or data.get('date_seance')
        }
        
        # Validation des exercices
        if validated['exercices']:
            validated_exercises = []
            for ex in validated['exercices']:
                if isinstance(ex, dict) and ex.get('nom'):
                    validated_exercises.append({
                        'nom': ex['nom'].strip(),
                        'series': max(1, int(ex.get('series', 3))),
                        'reps': max(1, int(ex.get('reps', 10))),
                        'poids': max(0.0, float(ex.get('poids', 0))),
                        'type_exercice': ex.get('type_exercice', 'REPETITIONS')
                    })
            validated['exercices'] = validated_exercises
        
        return validated
    
    def _parse_workout_date(self, raw_date) -> datetime:
        """Parse la date de la séance avec gestion d'erreurs robuste"""
        if not raw_date:
            return timezone.now()
        
        if isinstance(raw_date, datetime):
            return timezone.make_aware(raw_date) if raw_date.tzinfo is None else raw_date
        
        if isinstance(raw_date, str):
            # Essayer différents formats
            formats_to_try = [
                raw_date,
                raw_date + 'T00:00:00' if 'T' not in raw_date else raw_date,
                raw_date.replace('Z', '+00:00'),
                raw_date + 'Z' if not raw_date.endswith('Z') else raw_date
            ]
            
            for date_format in formats_to_try:
                try:
                    parsed = parse_datetime(date_format)
                    if parsed:
                        return timezone.make_aware(parsed) if parsed.tzinfo is None else parsed
                except:
                    try:
                        parsed = datetime.fromisoformat(date_format)
                        return timezone.make_aware(parsed) if parsed.tzinfo is None else parsed
                    except:
                        continue
        
        logger.warning(f"Impossible de parser la date '{raw_date}', utilisation de maintenant")
        return timezone.now()
    
    def _create_workout_session(self, user, data: Dict, date_prevue: datetime, 
                              is_planning: bool) -> SeanceEntrainement:
        """Crée la séance d'entraînement"""
        
        # Générer un nom si pas fourni
        if not data['nom']:
            data['nom'] = f"Séance du {date_prevue.strftime('%d/%m/%Y')}"
        
        # Générer le fingerprint pour déduplication
        fingerprint = ""
        if not is_planning and data['exercices']:
            fingerprint = self.dedup_service.generate_workout_fingerprint(
                user.id, date_prevue, data['exercices']
            )
        
        # Commentaire avec fingerprint
        commentaire = data['commentaire']
        if fingerprint:
            commentaire = f"{commentaire} [FP:{fingerprint}]".strip()
        
        if is_planning:
            # Séance planifiée
            session = SeanceEntrainement.objects.create(
                utilisateur=user,
                nom=data['nom'],
                date_prevue=date_prevue,
                duree_prevue=data['duree'],
                statut='PLANIFIEE',
                commentaire=commentaire
            )
        else:
            # Séance terminée
            now = timezone.now()
            session = SeanceEntrainement.objects.create(
                utilisateur=user,
                nom=data['nom'],
                date_prevue=date_prevue,
                date_debut=now - timedelta(minutes=data['duree']),
                date_fin=now,
                duree_prevue=data['duree'],
                statut='TERMINEE',
                note_ressenti=data['note_ressenti'],
                commentaire=commentaire
            )
        
        return session
    
    def _add_exercises_to_session(self, session: SeanceEntrainement, exercises: List[Dict]):
        """Ajoute les exercices à la séance"""
        for idx, exercise_data in enumerate(exercises):
            try:
                # Récupérer ou créer la machine
                machine = self._get_or_create_machine(exercise_data['nom'])
                
                # Déterminer si c'est du cardio
                is_cardio = self._is_cardio_exercise(machine, exercise_data)
                
                # Créer l'exercice
                if is_cardio:
                    exercice = self._create_cardio_exercise(session, machine, exercise_data, idx)
                else:
                    exercice = self._create_strength_exercise(session, machine, exercise_data, idx)
                
                # Créer les séries (UNE SEULE FOIS)
                self._create_exercise_sets(exercice, exercise_data, is_cardio)
                
            except Exception as e:
                logger.error(f"Erreur création exercice {exercise_data.get('nom', 'unknown')}: {e}")
                # Continuer avec les autres exercices
                continue
    
    def _get_or_create_machine(self, machine_name: str) -> Machine:
        """Récupère ou crée une machine"""
        # Essayer différentes stratégies de recherche
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
                    return machine
            except Machine.DoesNotExist:
                continue
        
        # Créer la machine si pas trouvée
        return self._create_new_machine(machine_name)
    
    def _create_new_machine(self, machine_name: str) -> Machine:
        """Crée une nouvelle machine automatiquement"""
        try:
            categorie_defaut, _ = CategorieMachine.objects.get_or_create(
                nom='MUSCULATION',
                defaults={'description': 'Catégorie auto-générée'}
            )
            
            machine = Machine.objects.create(
                nom=machine_name,
                description=f'Machine créée automatiquement: {machine_name}',
                instructions='Instructions à définir',
                categorie=categorie_defaut,
                increment_poids=2.5,
                poids_minimum=0.0,
                poids_maximum=200.0
            )
            
            logger.info(f"Nouvelle machine créée: {machine_name}")
            return machine
            
        except IntegrityError:
            # En cas de création concurrente, récupérer l'existante
            return Machine.objects.get(nom=machine_name)
    
    def _is_cardio_exercise(self, machine: Machine, exercise_data: Dict) -> bool:
        """Détermine si un exercice est du cardio"""
        return (
            (machine.categorie and machine.categorie.nom == 'CARDIO') or
            exercise_data.get('type_exercice') == 'DUREE' or
            any(keyword in machine.nom.lower() for keyword in ['tapis', 'vélo', 'rameur', 'elliptique'])
        )
    
    def _create_cardio_exercise(self, session: SeanceEntrainement, machine: Machine, 
                              exercise_data: Dict, order: int) -> ExerciceSeance:
        """Crée un exercice cardio"""
        duree_minutes = exercise_data['reps']  # Pour le cardio, 'reps' = durée en minutes
        
        return ExerciceSeance.objects.create(
            seance=session,
            machine=machine,
            ordre_dans_seance=order + 1,
            series_prevues=1,
            repetitions_prevues=duree_minutes,
            duree_prevue=duree_minutes * 60,
            poids_prevu=0.0,
            nombre_series=1,
            repetitions_realisees=duree_minutes,
            duree_realisee=duree_minutes * 60,
            poids_utilise=0.0,
            statut='TERMINE'
        )
    
    def _create_strength_exercise(self, session: SeanceEntrainement, machine: Machine,
                                exercise_data: Dict, order: int) -> ExerciceSeance:
        """Crée un exercice de musculation"""
        return ExerciceSeance.objects.create(
            seance=session,
            machine=machine,
            ordre_dans_seance=order + 1,
            series_prevues=exercise_data['series'],
            repetitions_prevues=exercise_data['reps'],
            poids_prevu=exercise_data['poids'],
            nombre_series=exercise_data['series'],
            repetitions_realisees=exercise_data['reps'],
            poids_utilise=exercise_data['poids'],
            statut='TERMINE'
        )
    
    def _create_exercise_sets(self, exercice: ExerciceSeance, exercise_data: Dict, is_cardio: bool):
        """Crée les séries pour un exercice (UNE SEULE FOIS)"""
        if is_cardio:
            # Une seule série pour le cardio
            SeriExercice.objects.create(
                exercice=exercice,
                numero_serie=1,
                repetitions_prevues=exercise_data['reps'],
                duree_prevue=exercise_data['reps'] * 60,
                poids_prevu=0.0,
                repetitions_realisees=exercise_data['reps'],
                duree_realisee=exercise_data['reps'] * 60,
                poids_utilise=0.0,
                statut='REUSSIE'
            )
        else:
            # Créer toutes les séries de musculation
            for serie_num in range(exercise_data['series']):
                SeriExercice.objects.create(
                    exercice=exercice,
                    numero_serie=serie_num + 1,
                    repetitions_prevues=exercise_data['reps'],
                    poids_prevu=exercise_data['poids'],
                    repetitions_realisees=exercise_data['reps'],
                    poids_utilise=exercise_data['poids'],
                    statut='REUSSIE'
                )
    
    def _update_machine_progressions(self, user, exercises: List[Dict]):
        """Met à jour les progressions machine après une séance"""
        from .models import ProgressionMachine, ModeEntrainement
        
        for exercise_data in exercises:
            try:
                # Récupérer la machine
                machine = self._get_or_create_machine(exercise_data['nom'])
                
                # Ignorer les exercices cardio pour la progression
                if self._is_cardio_exercise(machine, exercise_data):
                    continue
                
                # Récupérer ou créer le mode d'entraînement (par défaut "Force")
                mode_entrainement, _ = ModeEntrainement.objects.get_or_create(
                    nom="Force",
                    defaults={'description': 'Entraînement de force générale'}
                )
                
                # Récupérer ou créer la progression
                progression, created = ProgressionMachine.objects.get_or_create(
                    utilisateur=user,
                    machine=machine,
                    mode_entrainement=mode_entrainement,
                    defaults={
                        'poids_actuel': exercise_data['poids'],
                        'series_actuelles': exercise_data['series'],
                        'repetitions_actuelles': exercise_data['reps'],
                        'nombre_seances_machine': 1,
                        'dernier_1rm': exercise_data['poids'] * (1.0278 ** exercise_data['reps'])  # Formule de Brzycki
                    }
                )
                
                if not created:
                    # Mettre à jour la progression existante
                    progression.poids_actuel = exercise_data['poids']
                    progression.series_actuelles = exercise_data['series']
                    progression.repetitions_actuelles = exercise_data['reps']
                    progression.nombre_seances_machine += 1
                    
                    # Calculer le nouveau 1RM si c'est mieux
                    nouveau_1rm = exercise_data['poids'] * (1.0278 ** exercise_data['reps'])
                    if progression.dernier_1rm is None or nouveau_1rm > progression.dernier_1rm:
                        progression.dernier_1rm = nouveau_1rm
                    
                    progression.save()
                
                logger.info(f"Progression mise à jour: {machine.nom} - {exercise_data['poids']}kg x {exercise_data['reps']}")
                
            except Exception as e:
                logger.error(f"Erreur mise à jour progression {exercise_data.get('nom', 'unknown')}: {e}")
                continue


class CalendarService:
    """Service pour la gestion du calendrier"""
    
    @staticmethod
    def get_calendar_sessions(user, start_date=None, end_date=None) -> List[Dict]:
        """Récupère les séances pour le calendrier - Format compatible Android"""
        query = SeanceEntrainement.objects.filter(utilisateur=user)
        
        if start_date:
            query = query.filter(date_prevue__gte=start_date)
        if end_date:
            query = query.filter(date_prevue__lte=end_date)
        
        sessions = query.prefetch_related('exercices__machine', 'exercices__series').order_by('date_prevue')[:100]
        
        result = []
        for session in sessions:
            # Récupérer les exercices avec leurs détails
            exercices = []
            for exercice in session.exercices.all():
                # Calculer moyennes des séries
                series_data = exercice.series.all()
                avg_reps = sum(serie.repetitions for serie in series_data) / len(series_data) if series_data else 0
                avg_poids = sum(serie.poids for serie in series_data) / len(series_data) if series_data else 0
                
                exercices.append({
                    'nom': exercice.machine.nom if exercice.machine else 'Exercice',
                    'machine_nom': exercice.machine.nom if exercice.machine else 'Exercice',  
                    'series': len(series_data),
                    'repetitions': int(avg_reps),
                    'reps': int(avg_reps),
                    'poids': float(avg_poids),
                    'weight': float(avg_poids)
                })
            
            result.append({
                'id': session.id,
                'nom': session.nom,
                'title': session.nom,
                'date': session.date_prevue.date().isoformat(),
                'date_debut': session.date_prevue.isoformat(),
                'status': session.statut,
                'duree': session.duree_reelle or session.duree_prevue or 0,
                'duree_totale': session.duree_reelle or session.duree_prevue or 0,
                'duration': session.duree_reelle or session.duree_prevue or 0,
                'exercices': exercices,
                'exercises_count': len(exercices),
                'note': session.note_ressenti,
                'comment': session.commentaire
            })
        
        return result
    
    @staticmethod
    def plan_session(user, session_data: Dict) -> SeanceEntrainement:
        """Planifie une nouvelle séance"""
        session_data['action'] = 'planifier'
        
        save_service = WorkoutSaveService()
        session, created, message = save_service.save_workout(user, session_data)
        
        if not created:
            raise ValueError("Impossible de planifier la séance")
        
        return session
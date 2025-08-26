"""
Endpoints simplifiés pour analyse intelligente
Calculs de progression et recommandations basiques
"""
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from apps.sessions_simple.models import SessionSimple, ExerciceSimple

logger = logging.getLogger(__name__)

# ===== UTILITAIRES =====
def calculate_progression(exercices_history):
    """Calculer la progression pour un exercice"""
    if len(exercices_history) < 2:
        return {
            'progression_percentage': 0,
            'trend': 'stable',
            'volume_evolution': [],
            'recommended_weight': exercices_history[-1]['poids'] if exercices_history else 50.0
        }
    
    # Calculer volume (poids x series x reps) pour chaque occurrence
    volumes = []
    for ex in exercices_history:
        volume = ex['poids'] * ex['series'] * ex['reps']
        volumes.append({
            'date': ex['date'],
            'volume': volume,
            'poids': ex['poids']
        })
    
    # Tendance sur les 3 dernières sessions
    recent_volumes = volumes[-3:]
    if len(recent_volumes) >= 2:
        first_volume = recent_volumes[0]['volume']
        last_volume = recent_volumes[-1]['volume']
        progression_percentage = ((last_volume - first_volume) / first_volume) * 100 if first_volume > 0 else 0
        
        if progression_percentage > 5:
            trend = 'improvement'
            # Recommander +2.5kg ou +5%
            last_weight = recent_volumes[-1]['poids']
            recommended_weight = max(last_weight + 2.5, last_weight * 1.05)
        elif progression_percentage < -5:
            trend = 'decline'
            # Recommander -2.5kg ou maintenir
            last_weight = recent_volumes[-1]['poids']
            recommended_weight = max(last_weight - 2.5, last_weight * 0.95, 10.0)
        else:
            trend = 'stable'
            # Maintenir le poids ou +2.5kg léger
            last_weight = recent_volumes[-1]['poids']
            recommended_weight = last_weight + 1.25
    else:
        progression_percentage = 0
        trend = 'stable'
        recommended_weight = volumes[-1]['poids'] if volumes else 50.0
    
    return {
        'progression_percentage': round(progression_percentage, 1),
        'trend': trend,
        'volume_evolution': volumes[-5:],  # 5 dernières sessions
        'recommended_weight': round(recommended_weight, 1)
    }

def get_exercise_history(user, exercise_name):
    """Récupérer l'historique d'un exercice"""
    exercices = ExerciceSimple.objects.filter(
        session__user=user,
        nom__icontains=exercise_name
    ).select_related('session').order_by('session__date')
    
    history = []
    for ex in exercices:
        history.append({
            'date': ex.session.date.strftime('%Y-%m-%d'),
            'poids': ex.poids,
            'series': ex.series,
            'reps': ex.reps,
            'session_id': ex.session.id
        })
    
    return history

# ===== ENDPOINTS =====

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_progressions(request):
    """
    Analyse des progressions par exercice
    GET /api/analysis/progressions/
    """
    try:
        user = request.user
        logger.info(f"📈 ANALYSE PROGRESSIONS - User: {user.id}")
        
        # Récupérer tous les exercices uniques
        exercices_names = ExerciceSimple.objects.filter(
            session__user=user
        ).values_list('nom', flat=True).distinct()
        
        progressions = {}
        
        for exercise_name in exercices_names:
            history = get_exercise_history(user, exercise_name)
            if history:
                progression = calculate_progression(history)
                progressions[exercise_name] = {
                    'exercise_name': exercise_name,
                    'total_sessions': len(history),
                    'first_date': history[0]['date'],
                    'last_date': history[-1]['date'],
                    'current_weight': history[-1]['poids'],
                    **progression
                }
        
        logger.info(f"✅ PROGRESSIONS CALCULÉES - Exercices: {len(progressions)}")
        
        return Response({
            'success': True,
            'data': progressions,
            'exercises_count': len(progressions)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR PROGRESSIONS: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur calcul progressions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    """
    Recommandations intelligentes pour un exercice
    POST /api/analysis/recommendations/
    
    Body: {
        "exercise_name": "Développé couché",
        "current_weight": 80.0,
        "target_reps": 12,
        "target_series": 3
    }
    """
    try:
        user = request.user
        data = request.data
        
        exercise_name = data.get('exercise_name', '')
        current_weight = float(data.get('current_weight', 0))
        target_reps = int(data.get('target_reps', 12))
        target_series = int(data.get('target_series', 3))
        
        logger.info(f"🎯 RECOMMANDATIONS - User: {user.id}, Exercice: {exercise_name}")
        
        if not exercise_name:
            return Response({
                'success': False,
                'message': 'Nom d\'exercice requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupérer l'historique
        history = get_exercise_history(user, exercise_name)
        
        if not history:
            # Pas d'historique - recommandations de base
            recommendations = {
                'recommended_weight': current_weight if current_weight > 0 else 50.0,
                'confidence': 'low',
                'reason': 'Aucun historique disponible - recommandation de base',
                'weight_range': {
                    'min': max((current_weight if current_weight > 0 else 50.0) - 5, 10),
                    'max': (current_weight if current_weight > 0 else 50.0) + 5
                }
            }
        else:
            # Avec historique - calcul intelligent
            progression = calculate_progression(history)
            
            # Ajuster selon la progression
            base_weight = progression['recommended_weight']
            
            # Ajuster selon les objectifs
            if target_reps > 12:  # Endurance
                recommended_weight = base_weight * 0.9
                reason = f"Poids réduit pour {target_reps} répétitions (endurance)"
            elif target_reps < 8:  # Force
                recommended_weight = base_weight * 1.1
                reason = f"Poids augmenté pour {target_reps} répétitions (force)"
            else:  # Hypertrophie
                recommended_weight = base_weight
                reason = f"Poids optimal pour {target_reps} répétitions (hypertrophie)"
            
            # Confidence basée sur l'historique
            if len(history) >= 5:
                confidence = 'high'
            elif len(history) >= 3:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            recommendations = {
                'recommended_weight': round(recommended_weight, 1),
                'confidence': confidence,
                'reason': reason,
                'trend': progression['trend'],
                'progression_percentage': progression['progression_percentage'],
                'sessions_analyzed': len(history),
                'weight_range': {
                    'min': round(recommended_weight * 0.9, 1),
                    'max': round(recommended_weight * 1.1, 1)
                }
            }
        
        logger.info(f"✅ RECOMMANDATIONS CALCULÉES - Poids: {recommendations['recommended_weight']}kg")
        
        return Response({
            'success': True,
            'exercise_name': exercise_name,
            'data': recommendations
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR RECOMMANDATIONS: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur calcul recommandations'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_performance_analysis(request):
    """
    Analyse globale des performances
    GET /api/analysis/performance/
    """
    try:
        user = request.user
        logger.info(f"🏆 ANALYSE PERFORMANCE - User: {user.id}")
        
        # Récupérer les sessions récentes (30 derniers jours)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_sessions = SessionSimple.objects.filter(
            user=user,
            date__gte=thirty_days_ago
        ).prefetch_related('exercices')
        
        if not recent_sessions:
            return Response({
                'success': True,
                'data': {
                    'message': 'Aucune session récente pour l\'analyse',
                    'period_days': 30,
                    'sessions_count': 0
                }
            }, status=status.HTTP_200_OK)
        
        # Calculs d'analyse
        total_sessions = len(recent_sessions)
        total_exercices = sum(session.exercices.count() for session in recent_sessions)
        total_duree = sum(session.duree for session in recent_sessions)
        avg_duree = total_duree / total_sessions if total_sessions > 0 else 0
        
        # Analyse par exercice
        exercise_stats = defaultdict(list)
        for session in recent_sessions:
            for ex in session.exercices.all():
                volume = ex.poids * ex.series * ex.reps
                exercise_stats[ex.nom].append({
                    'date': session.date,
                    'volume': volume,
                    'poids': ex.poids
                })
        
        # Top exercices par volume
        top_exercises = []
        for exercise_name, data in exercise_stats.items():
            total_volume = sum(d['volume'] for d in data)
            avg_weight = sum(d['poids'] for d in data) / len(data)
            sessions_count = len(data)
            
            top_exercises.append({
                'name': exercise_name,
                'total_volume': round(total_volume, 1),
                'avg_weight': round(avg_weight, 1),
                'sessions_count': sessions_count
            })
        
        # Trier par volume total
        top_exercises.sort(key=lambda x: x['total_volume'], reverse=True)
        
        # Score de performance (basique)
        frequency_score = min(total_sessions / 8, 1) * 30  # 8 sessions/mois = 30 points max
        volume_score = min(total_exercices / 50, 1) * 30  # 50 exercices/mois = 30 points max
        consistency_score = min(len(exercise_stats) / 10, 1) * 20  # 10 exercices différents = 20 points max
        duration_score = min(avg_duree / 60, 1) * 20  # 60min moyenne = 20 points max
        
        performance_score = round(frequency_score + volume_score + consistency_score + duration_score)
        
        analysis = {
            'period_days': 30,
            'sessions_count': total_sessions,
            'total_exercices': total_exercices,
            'total_duree_minutes': total_duree,
            'moyenne_duree_minutes': round(avg_duree, 1),
            'exercices_differents': len(exercise_stats),
            'performance_score': performance_score,
            'top_exercises': top_exercises[:5],  # Top 5
            'scores_detail': {
                'frequency': round(frequency_score),
                'volume': round(volume_score),
                'consistency': round(consistency_score),
                'duration': round(duration_score)
            }
        }
        
        logger.info(f"✅ ANALYSE PERFORMANCE CALCULÉE - Score: {performance_score}/100")
        
        return Response({
            'success': True,
            'data': analysis
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR ANALYSE PERFORMANCE: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur analyse performance'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
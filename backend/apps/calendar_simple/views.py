"""
Endpoints simplifiés pour calendrier
Gère uniquement l'affichage calendar avec données sessions
"""
import logging
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from apps.sessions_simple.models import SessionSimple

logger = logging.getLogger(__name__)

# ===== UTILITAIRES =====
def session_to_calendar_dict(session):
    """Convertir une session pour l'affichage calendrier"""
    return {
        'id': session.id,
        'title': session.nom,
        'date': session.date.strftime('%Y-%m-%d'),
        'time': session.date.strftime('%H:%M'),
        'duree': session.duree,
        'note_ressenti': session.note_ressenti,
        'exercices_count': session.exercices.count(),
        'type': 'workout'
    }

# ===== ENDPOINTS =====

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar_data(request):
    """
    Données du calendrier pour l'utilisateur
    GET /api/calendar/
    
    Query params:
    - month: YYYY-MM (optionnel, défaut: mois actuel)
    """
    try:
        user = request.user
        
        # Paramètre mois optionnel
        month_param = request.GET.get('month')
        if month_param:
            try:
                year, month = map(int, month_param.split('-'))
                start_date = datetime(year, month, 1)
            except (ValueError, TypeError):
                start_date = datetime.now().replace(day=1)
        else:
            start_date = datetime.now().replace(day=1)
        
        # Fin du mois
        if start_date.month == 12:
            end_date = datetime(start_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
        
        logger.info(f"📅 CALENDRIER - User: {user.id}, Période: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
        
        # Récupérer les sessions du mois
        sessions = SessionSimple.objects.filter(
            user=user,
            date__date__gte=start_date.date(),
            date__date__lte=end_date.date()
        ).order_by('date')
        
        # Convertir pour le calendrier
        calendar_events = [session_to_calendar_dict(session) for session in sessions]
        
        # Statistiques du mois
        total_sessions = len(calendar_events)
        total_duree = sum(event['duree'] for event in calendar_events)
        
        logger.info(f"✅ CALENDRIER RÉCUPÉRÉ - Events: {total_sessions}, Durée totale: {total_duree}min")
        
        return Response({
            'success': True,
            'month': start_date.strftime('%Y-%m'),
            'events': calendar_events,
            'stats': {
                'total_sessions': total_sessions,
                'total_duree_minutes': total_duree,
                'days_with_workout': len(set(event['date'] for event in calendar_events))
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR CALENDRIER: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur récupération calendrier'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_day_details(request, date_str):
    """
    Détails d'une journée spécifique
    GET /api/calendar/day/YYYY-MM-DD/
    """
    try:
        user = request.user
        
        # Parser la date
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'message': 'Format de date invalide (attendu: YYYY-MM-DD)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"📆 DÉTAILS JOUR - User: {user.id}, Date: {date_str}")
        
        # Récupérer les sessions du jour
        sessions = SessionSimple.objects.filter(
            user=user,
            date__date=target_date
        ).order_by('date').prefetch_related('exercices')
        
        # Convertir en détails
        day_sessions = []
        for session in sessions:
            session_detail = {
                'id': session.id,
                'nom': session.nom,
                'time': session.date.strftime('%H:%M'),
                'duree': session.duree,
                'note_ressenti': session.note_ressenti,
                'commentaire': session.commentaire,
                'exercices': [
                    {
                        'nom': ex.nom,
                        'series': ex.series,
                        'reps': ex.reps,
                        'poids': ex.poids
                    } for ex in session.exercices.all()
                ]
            }
            day_sessions.append(session_detail)
        
        logger.info(f"✅ DÉTAILS JOUR RÉCUPÉRÉS - Sessions: {len(day_sessions)}")
        
        return Response({
            'success': True,
            'date': date_str,
            'sessions': day_sessions,
            'total_sessions': len(day_sessions),
            'total_duree': sum(s['duree'] for s in day_sessions)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR DÉTAILS JOUR: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur récupération détails jour'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar_overview(request):
    """
    Vue d'ensemble du calendrier (statistiques générales)
    GET /api/calendar/overview/
    """
    try:
        user = request.user
        logger.debug(f"📊 OVERVIEW CALENDRIER - User: {user.id}")
        
        # Toutes les sessions
        all_sessions = SessionSimple.objects.filter(user=user)
        total_sessions = all_sessions.count()
        
        if total_sessions > 0:
            # Statistiques générales
            total_duree = sum(s.duree for s in all_sessions)
            avg_duree = total_duree / total_sessions
            
            # Sessions ce mois
            now = datetime.now()
            this_month_sessions = all_sessions.filter(
                date__year=now.year,
                date__month=now.month
            ).count()
            
            # Sessions cette semaine
            start_of_week = now - timedelta(days=now.weekday())
            this_week_sessions = all_sessions.filter(
                date__date__gte=start_of_week.date()
            ).count()
            
            # Première et dernière session
            first_session = all_sessions.order_by('date').first()
            last_session = all_sessions.order_by('-date').first()
            
            overview = {
                'total_sessions': total_sessions,
                'total_duree_minutes': total_duree,
                'moyenne_duree_minutes': round(avg_duree, 1),
                'sessions_ce_mois': this_month_sessions,
                'sessions_cette_semaine': this_week_sessions,
                'premiere_session': first_session.date.strftime('%Y-%m-%d') if first_session else None,
                'derniere_session': last_session.date.strftime('%Y-%m-%d') if last_session else None
            }
        else:
            overview = {
                'total_sessions': 0,
                'total_duree_minutes': 0,
                'moyenne_duree_minutes': 0,
                'sessions_ce_mois': 0,
                'sessions_cette_semaine': 0,
                'premiere_session': None,
                'derniere_session': None
            }
        
        logger.debug(f"✅ OVERVIEW CALCULÉ: {overview}")
        
        return Response({
            'success': True,
            'data': overview
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"💥 ERREUR OVERVIEW CALENDRIER: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Erreur calcul overview calendrier'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
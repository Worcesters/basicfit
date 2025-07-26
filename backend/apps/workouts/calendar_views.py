"""
Vues spécifiques pour la gestion du calendrier des séances
"""
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from .models import SeanceEntrainement
from .serializers import SeanceEntrainementSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar_sessions(request):
    """Récupère les séances pour le calendrier"""
    try:
        user = request.user
        
        # Récupérer les paramètres de date (optionnels)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Query de base
        query = SeanceEntrainement.objects.filter(utilisateur=user)
        
        # Filtrer par dates si fournies
        if start_date:
            try:
                start_dt = parse_datetime(start_date) or datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(date_prevue__gte=start_dt)
            except:
                pass
                
        if end_date:
            try:
                end_dt = parse_datetime(end_date) or datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(date_prevue__lte=end_dt)
            except:
                pass
        
        # Récupérer les séances avec les détails
        seances = query.select_related().order_by('date_prevue')[:50]  # Limiter à 50
        
        calendar_data = []
        for seance in seances:
            calendar_data.append({
                'id': seance.id,
                'title': seance.nom or f"Séance du {seance.date_prevue.strftime('%d/%m/%Y')}",
                'date': seance.date_prevue.isoformat(),
                'status': seance.statut,
                'duration': seance.duree_reelle or seance.duree_prevue,
                'exercises_count': seance.nombre_exercices,
                'note': seance.note_ressenti,
                'comment': seance.commentaire
            })
        
        return Response({
            'sessions': calendar_data,
            'count': len(calendar_data),
            'message': 'Séances récupérées avec succès'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def plan_session(request):
    """Planifie une nouvelle séance dans le calendrier"""
    try:
        user = request.user
        data = request.data
        
        # Traitement de la date
        raw_date = data.get('date_prevue') or data.get('date')
        if not raw_date:
            return Response({'error': 'Date prévue requise'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Parser la date
        try:
            if isinstance(raw_date, str):
                date_prevue = parse_datetime(raw_date) or datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
            else:
                date_prevue = raw_date
        except:
            return Response({'error': 'Format de date invalide'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la séance planifiée
        seance = SeanceEntrainement.objects.create(
            utilisateur=user,
            nom=data.get('nom', f"Séance du {date_prevue.strftime('%d/%m/%Y')}"),
            date_prevue=date_prevue,
            duree_prevue=data.get('duree_prevue', 60),
            statut='PLANIFIEE',
            commentaire=data.get('commentaire', '')
        )
        
        serializer = SeanceEntrainementSerializer(seance)
        return Response({
            'session': serializer.data,
            'message': 'Séance planifiée avec succès'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
"""
Vues simplifiées pour l'API des machines
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import GroupeMusculaire, CategorieMachine, Machine, VarianteMachine


@api_view(['GET'])
@permission_classes([AllowAny])
def groupes_musculaires_list(request):
    """Liste des groupes musculaires"""
    try:
        groupes = GroupeMusculaire.objects.filter(is_active=True).order_by('nom')
        data = []
        for groupe in groupes:
            data.append({
                'id': groupe.id,
                'nom': groupe.nom,
                'description': groupe.description,
                'couleur': groupe.couleur,
                'icone': groupe.icone
            })
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def categories_machines_list(request):
    """Liste des catégories de machines"""
    try:
        categories = CategorieMachine.objects.filter(is_active=True).order_by('nom')
        data = []
        for cat in categories:
            data.append({
                'id': cat.id,
                'nom': cat.get_nom_display(),
                'nom_code': cat.nom,
                'description': cat.description,
                'couleur': cat.couleur,
                'icone': cat.icone
            })
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def machines_list(request):
    """Liste des machines disponibles"""
    try:
        machines = Machine.objects.filter(est_disponible=True, is_active=True).order_by('nom')
        data = []
        for machine in machines:
            # Récupérer les groupes musculaires primaires
            groupes_primaires = []
            for groupe in machine.groupes_musculaires_primaires.all():
                groupes_primaires.append({
                    'nom': groupe.nom,
                    'couleur': groupe.couleur,
                    'icone': groupe.icone
                })

            data.append({
                'id': machine.id,
                'nom': machine.nom,
                'nom_anglais': machine.nom_anglais or machine.nom,
                'categorie': machine.categorie.get_nom_display() if machine.categorie else None,
                'categorie_code': machine.categorie.nom if machine.categorie else None,
                'description': machine.description,
                'instructions': machine.instructions,
                'niveau_difficulte': machine.get_niveau_difficulte_display(),
                'niveau_code': machine.niveau_difficulte,
                'poids_minimum': float(machine.poids_minimum),
                'poids_maximum': float(machine.poids_maximum),
                'increment_poids': float(machine.increment_poids),
                'popularite': machine.popularite,
                'necessite_supervision': machine.necessite_supervision,
                'groupes_musculaires_primaires': groupes_primaires,
                'fabricant': machine.fabricant or '',
                'modele': machine.modele or ''
            })
        return Response({'results': data, 'count': len(data)})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def machine_detail(request, pk):
    """Détail d'une machine"""
    try:
        machine = Machine.objects.get(pk=pk, est_disponible=True, is_active=True)

        # Récupérer les groupes musculaires
        groupes_primaires = []
        for groupe in machine.groupes_musculaires_primaires.all():
            groupes_primaires.append({
                'nom': groupe.nom,
                'couleur': groupe.couleur,
                'icone': groupe.icone
            })

        groupes_secondaires = []
        for groupe in machine.groupes_musculaires_secondaires.all():
            groupes_secondaires.append({
                'nom': groupe.nom,
                'couleur': groupe.couleur,
                'icone': groupe.icone
            })

        # Récupérer les variantes
        variantes = VarianteMachine.objects.filter(machine=machine, is_active=True)
        variantes_data = []
        for variante in variantes:
            variantes_data.append({
                'id': variante.id,
                'nom': variante.nom,
                'description': variante.description,
                'niveau_difficulte': variante.get_niveau_difficulte_display()
            })

        data = {
            'id': machine.id,
            'nom': machine.nom,
            'nom_anglais': machine.nom_anglais or machine.nom,
            'categorie': machine.categorie.get_nom_display() if machine.categorie else None,
            'description': machine.description,
            'instructions': machine.instructions,
            'niveau_difficulte': machine.get_niveau_difficulte_display(),
            'poids_minimum': float(machine.poids_minimum),
            'poids_maximum': float(machine.poids_maximum),
            'increment_poids': float(machine.increment_poids),
            'popularite': machine.popularite,
            'necessite_supervision': machine.necessite_supervision,
            'groupes_musculaires_primaires': groupes_primaires,
            'groupes_musculaires_secondaires': groupes_secondaires,
            'variantes': variantes_data,
            'fabricant': machine.fabricant or '',
            'modele': machine.modele or '',
            'tags': machine.tags_liste if hasattr(machine, 'tags_liste') else []
        }
        return Response(data)
    except Machine.DoesNotExist:
        return Response({'error': 'Machine non trouvée'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
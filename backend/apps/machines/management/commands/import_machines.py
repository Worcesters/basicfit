from django.core.management.base import BaseCommand, CommandError
import json, os
from apps.machines.models import Machine, CategorieMachine, GroupeMusculaire

class Command(BaseCommand):
    help = "Importe des machines depuis un fichier JSON."

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str, help='Chemin vers le fichier JSON contenant la liste des machines')

    def handle(self, *args, **options):
        json_path = options['json_path']
        if not os.path.exists(json_path):
            raise CommandError(f"Fichier introuvable: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            machines_data = json.load(f)

        created, updated = 0, 0
        for m in machines_data:
            categorie_nom = m.get('categorie', 'MUSCULATION')
            categorie, _ = CategorieMachine.objects.get_or_create(nom=categorie_nom)

            machine, created_flag = Machine.objects.update_or_create(
                nom=m['nom'],
                defaults={
                    'nom_anglais': m.get('nom_anglais', ''),
                    'description': m.get('description', ''),
                    'instructions': m.get('instructions', ''),
                    'categorie': categorie,
                    'increment_poids': m.get('increment_poids', 2.5),
                    'poids_minimum': m.get('poids_minimum', 5.0),
                    'poids_maximum': m.get('poids_maximum', 200.0),
                    'niveau_difficulte': m.get('niveau_difficulte', 'DEBUTANT'),
                    'popularite': m.get('popularite', 0),
                    'est_disponible': m.get('est_disponible', True),
                    'necessite_supervision': m.get('necessite_supervision', False),
                    'tags': ','.join(m.get('tags', [])),
                    'ordre_affichage': m.get('ordre_affichage', 0),
                }
            )

            # Groupes musculaires primaires
            groupes_noms = m.get('groupes_musculaires', [m.get('groupeMusculairePrimaire', 'Général')])
            for g_nom in groupes_noms:
                groupe, _ = GroupeMusculaire.objects.get_or_create(nom=g_nom)
                machine.groupes_musculaires_primaires.add(groupe)

            if created_flag:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Machines importées. Créées: {created}, mises à jour: {updated}"))
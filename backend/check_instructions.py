#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.machines.models import Machine

def check_instructions():
    """Vérifie si les instructions sont présentes pour toutes les machines"""
    machines = Machine.objects.all()

    print(f"Nombre total de machines: {machines.count()}")
    print("\nMachines avec instructions:")

    machines_avec_instructions = 0
    machines_sans_instructions = 0

    for machine in machines:
        if machine.instructions and machine.instructions.strip():
            machines_avec_instructions += 1
            print(f"✅ {machine.nom}: {len(machine.instructions)} caractères")
        else:
            machines_sans_instructions += 1
            print(f"❌ {machine.nom}: PAS D'INSTRUCTIONS")

    print(f"\nRésumé:")
    print(f"- Machines avec instructions: {machines_avec_instructions}")
    print(f"- Machines sans instructions: {machines_sans_instructions}")

    if machines_sans_instructions > 0:
        print(f"\n⚠️  {machines_sans_instructions} machines n'ont pas d'instructions!")
        return False
    else:
        print(f"\n✅ Toutes les machines ont des instructions!")
        return True

if __name__ == "__main__":
    check_instructions()
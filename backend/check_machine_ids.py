#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.machines.models import Machine

print("=== IDs des machines disponibles ===")
machines = Machine.objects.all().order_by('id')
for machine in machines:
    print(f"ID {machine.id}: {machine.nom}")

print(f"\nTotal: {machines.count()} machines")
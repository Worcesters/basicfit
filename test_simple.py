#!/usr/bin/env python3
import requests

# Test simple de l'API
url = "http://127.0.0.1:8000/api/machines/"
print(f"Test de l'URL: {url}")

try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
except Exception as e:
    print(f"Erreur: {e}")
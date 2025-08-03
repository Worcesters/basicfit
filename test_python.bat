@echo off
echo ===========================================
echo    TEST PYTHON DJANGO
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Test avec Python requests...
flyctl ssh console --app basicfit-v2 -C "python -c \"
import requests
try:
    r = requests.get('http://localhost:8000/')
    print(f'Status: {r.status_code}')
    print(f'Response: {r.text[:200]}...')
except Exception as e:
    print(f'Erreur: {e}')
\""

echo.
pause
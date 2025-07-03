#!/usr/bin/env python3
"""
Serveur HTTP simple pour l'interface web BasicFit v2
Usage: python server.py
"""
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Ajouter les headers CORS pour permettre les appels API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def main():
    # Changer vers le répertoire frontend
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(frontend_dir)

    # Créer le serveur
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"""
🌐 Serveur web BasicFit v2 démarré !

📱 Interface web: http://localhost:{PORT}
🚀 API Backend: http://localhost:8000/api/

Ouvrez votre navigateur sur http://localhost:{PORT} pour voir votre application !

Appuyez sur Ctrl+C pour arrêter le serveur.
        """)

        # Ouvrir automatiquement le navigateur
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Serveur arrêté.")
            sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Script de test pour vérifier l'affichage des machines et GIFs
"""
import requests
import json
import time

def test_machines_api():
    """Test de l'API des machines"""
    print("🔧 TEST DE L'API MACHINES ET GIFS")
    print("=" * 50)

    # URL de l'API Railway
    base_url = "https://basicfit-production.up.railway.app/api"

    # Test de connexion
    print("🔗 Test de connexion à l'API...")
    try:
        response = requests.get(f"{base_url}/users/android/ping/", timeout=10)
        if response.status_code == 200:
            print("✅ API accessible")
        else:
            print(f"⚠️ API accessible mais statut: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

    # Test de l'endpoint des machines
    print("\n🏋️ Test de l'endpoint des machines...")
    try:
        response = requests.get(f"{base_url}/workouts/machines/", timeout=15)

        if response.status_code == 200:
            machines = response.json()
            print(f"✅ {len(machines)} machines récupérées")

            # Analyse des machines
            machines_avec_gifs = 0
            machines_sans_gifs = 0

            for machine in machines[:5]:  # Afficher les 5 premières
                nom = machine.get('nom', 'N/A')
                gif = machine.get('image_gif')

                if gif:
                    machines_avec_gifs += 1
                    print(f"  📱 {nom}: GIF présent ✅")
                    print(f"     URL: {gif[:50]}...")
                else:
                    machines_sans_gifs += 1
                    print(f"  📱 {nom}: Pas de GIF ❌")

            print(f"\n📊 Statistiques:")
            print(f"   - Machines avec GIFs: {machines_avec_gifs}")
            print(f"   - Machines sans GIFs: {machines_sans_gifs}")
            print(f"   - Total: {len(machines)}")

            return True

        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   Réponse: {response.text[:200]}...")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du test des machines: {e}")
        return False

def test_gif_accessibility():
    """Test de l'accessibilité des GIFs"""
    print("\n🎬 Test d'accessibilité des GIFs...")

    base_url = "https://basicfit-production.up.railway.app/api"

    try:
        response = requests.get(f"{base_url}/workouts/machines/", timeout=15)
        if response.status_code != 200:
            print("❌ Impossible de récupérer les machines")
            return False

        machines = response.json()
        gifs_testes = 0
        gifs_accessibles = 0

        for machine in machines[:3]:  # Tester les 3 premiers GIFs
            gif_url = machine.get('image_gif')
            if gif_url:
                gifs_testes += 1
                try:
                    gif_response = requests.head(gif_url, timeout=10)
                    if gif_response.status_code == 200:
                        gifs_accessibles += 1
                        print(f"  ✅ GIF accessible: {gif_url[:50]}...")
                    else:
                        print(f"  ❌ GIF inaccessible ({gif_response.status_code}): {gif_url[:50]}...")
                except Exception as e:
                    print(f"  ❌ Erreur d'accès au GIF: {e}")

        print(f"\n📊 Accessibilité des GIFs:")
        print(f"   - GIFs testés: {gifs_testes}")
        print(f"   - GIFs accessibles: {gifs_accessibles}")
        print(f"   - Taux de succès: {gifs_accessibles/gifs_testes*100:.1f}%" if gifs_testes > 0 else "   - Aucun GIF à tester")

        return gifs_accessibles > 0

    except Exception as e:
        print(f"❌ Erreur lors du test d'accessibilité: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE DU TEST COMPLET")
    print("=" * 50)

    # Attendre un peu que le déploiement soit terminé
    print("⏳ Attente de 30 secondes pour le déploiement...")
    time.sleep(30)

    # Test des machines
    machines_ok = test_machines_api()

    if machines_ok:
        # Test des GIFs
        gifs_ok = test_gif_accessibility()

        print("\n" + "=" * 50)
        print("📋 RÉSUMÉ DU TEST")
        print("=" * 50)

        if machines_ok and gifs_ok:
            print("✅ TOUT FONCTIONNE PARFAITEMENT !")
            print("   - L'API des machines est accessible")
            print("   - Les GIFs sont accessibles")
            print("   - Votre application Android devrait afficher les machines avec les GIFs")
        elif machines_ok:
            print("⚠️ PARTIEL: API OK mais problèmes avec les GIFs")
            print("   - L'API des machines fonctionne")
            print("   - Les GIFs ne sont pas accessibles")
            print("   - Vérifiez la configuration Cloudinary")
        else:
            print("❌ PROBLÈME: API non accessible")
            print("   - Le déploiement Railway n'est pas terminé")
            print("   - Attendez quelques minutes et relancez le test")
    else:
        print("\n❌ Impossible de tester les GIFs sans accès à l'API")

if __name__ == "__main__":
    main()
#!/bin/bash

# Script de déploiement automatisé pour BasicFit v2
# Usage: ./deploy.sh [dev|prod] [backend|android|all]

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Variables par défaut
ENVIRONMENT=${1:-dev}
COMPONENT=${2:-all}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_info "🚀 Démarrage du déploiement BasicFit v2"
log_info "Environnement: $ENVIRONMENT"
log_info "Composant: $COMPONENT"

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."

    # Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi

    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi

    log_success "Prérequis OK"
}

# Configuration de l'environnement
setup_environment() {
    log_info "Configuration de l'environnement $ENVIRONMENT..."

    cd "$PROJECT_ROOT"

    # Copier le bon fichier d'environnement
    if [ "$ENVIRONMENT" = "prod" ]; then
        if [ ! -f "backend/.env.prod" ]; then
            log_error "Fichier backend/.env.prod non trouvé"
            exit 1
        fi
        cp backend/.env.prod backend/.env
        COMPOSE_FILE="docker-compose.prod.yml"
    else
        if [ ! -f "backend/.env.dev" ]; then
            log_warning "Fichier backend/.env.dev non trouvé, création d'un exemple..."
            cat > backend/.env.dev << EOF
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DB_NAME=basicfit_db
DB_USER=basicfit_user
DB_PASSWORD=basicfit_password
DB_HOST=db
DB_PORT=5432
JWT_SECRET_KEY=jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF
        fi
        cp backend/.env.dev backend/.env
        COMPOSE_FILE="docker-compose.yml"
    fi

    log_success "Environnement configuré"
}

# Déploiement du backend
deploy_backend() {
    log_info "🐍 Déploiement du backend Django..."

    cd "$PROJECT_ROOT"

    # Construction et démarrage des services
    if [ "$ENVIRONMENT" = "prod" ]; then
        docker-compose -f $COMPOSE_FILE up -d --build db redis nginx backend
    else
        docker-compose -f $COMPOSE_FILE up -d --build db redis backend
    fi

    # Attendre que la base soit prête
    log_info "Attente de la base de données..."
    sleep 10

    # Migrations
    log_info "Exécution des migrations..."
    docker-compose -f $COMPOSE_FILE exec -T backend python manage.py migrate

    # Collecte des fichiers statiques
    log_info "Collecte des fichiers statiques..."
    docker-compose -f $COMPOSE_FILE exec -T backend python manage.py collectstatic --noinput

    # Chargement des données initiales
    if [ -f "backend/fixtures/initial_data.json" ]; then
        log_info "Chargement des données initiales..."
        docker-compose -f $COMPOSE_FILE exec -T backend python manage.py loaddata fixtures/initial_data.json || true
    fi

    # Création du superutilisateur en dev
    if [ "$ENVIRONMENT" = "dev" ]; then
        log_info "Création d'un superutilisateur (optionnel)..."
        echo "Voulez-vous créer un superutilisateur ? (y/N)"
        read -t 10 -r response || response="n"
        if [[ $response =~ ^[Yy]$ ]]; then
            docker-compose -f $COMPOSE_FILE exec backend python manage.py createsuperuser
        fi
    fi

    log_success "Backend déployé avec succès !"

    if [ "$ENVIRONMENT" = "dev" ]; then
        log_info "🌐 API disponible sur: http://localhost:8000/api/"
        log_info "📚 Documentation: http://localhost:8000/api/docs/"
        log_info "👨‍💼 Admin: http://localhost:8000/admin/"
    fi
}

# Compilation de l'application Android
build_android() {
    log_info "📱 Compilation de l'application Android..."

    cd "$PROJECT_ROOT/android"

    # Vérification de Gradle
    if [ ! -f "gradlew" ]; then
        log_error "Gradle wrapper non trouvé dans android/"
        exit 1
    fi

    # Nettoyage
    ./gradlew clean

    # Compilation selon l'environnement
    if [ "$ENVIRONMENT" = "prod" ]; then
        log_info "Compilation en mode production..."
        ./gradlew assembleRelease

        APK_PATH="app/build/outputs/apk/release/app-release.apk"
        if [ -f "$APK_PATH" ]; then
            log_success "APK produit: $APK_PATH"
            log_warning "⚠️  N'oubliez pas de signer l'APK pour le Play Store !"
        fi
    else
        log_info "Compilation en mode debug..."
        ./gradlew assembleDebug

        APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
        if [ -f "$APK_PATH" ]; then
            log_success "APK debug: $APK_PATH"
        fi
    fi
}

# Tests
run_tests() {
    log_info "🧪 Exécution des tests..."

    # Tests backend
    if [ "$COMPONENT" = "backend" ] || [ "$COMPONENT" = "all" ]; then
        log_info "Tests backend Django..."
        cd "$PROJECT_ROOT"
        docker-compose -f $COMPOSE_FILE exec -T backend python manage.py test
    fi

    # Tests Android
    if [ "$COMPONENT" = "android" ] || [ "$COMPONENT" = "all" ]; then
        log_info "Tests Android..."
        cd "$PROJECT_ROOT/android"
        ./gradlew test
    fi

    log_success "Tests terminés"
}

# Affichage des logs
show_logs() {
    log_info "📋 Affichage des logs..."
    cd "$PROJECT_ROOT"
    docker-compose -f $COMPOSE_FILE logs -f
}

# Nettoyage
cleanup() {
    log_info "🧹 Nettoyage..."
    cd "$PROJECT_ROOT"
    docker-compose -f $COMPOSE_FILE down --volumes --remove-orphans
    docker system prune -f
    log_success "Nettoyage terminé"
}

# Menu principal
case "$COMPONENT" in
    "backend")
        check_prerequisites
        setup_environment
        deploy_backend
        ;;
    "android")
        build_android
        ;;
    "all")
        check_prerequisites
        setup_environment
        deploy_backend
        build_android
        ;;
    "test")
        run_tests
        ;;
    "logs")
        show_logs
        ;;
    "clean")
        cleanup
        ;;
    *)
        log_error "Usage: $0 [dev|prod] [backend|android|all|test|logs|clean]"
        echo
        echo "Exemples:"
        echo "  $0 dev backend    # Déploie le backend en dev"
        echo "  $0 prod all       # Déploie tout en production"
        echo "  $0 dev test       # Lance les tests"
        echo "  $0 dev logs       # Affiche les logs"
        echo "  $0 dev clean      # Nettoie l'environnement"
        exit 1
        ;;
esac

log_success "🎉 Déploiement terminé avec succès !"
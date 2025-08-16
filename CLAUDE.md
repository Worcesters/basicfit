# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BasicFit v2 is a fitness tracking application with an Android mobile client and Django REST API backend. The app manages workout sessions, exercise machines, user profiles with calorie calculations, and provides detailed workout statistics.

## Architecture

### Backend (Django REST API)
- **Location**: `backend/`
- **Framework**: Django 4.2.7 with Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: JWT tokens via djangorestframework-simplejwt
- **Deployment**: Fly.io platform
- **API URL**: https://basicfit-v2.fly.dev/

### Android App
- **Location**: `android/`
- **Language**: Kotlin with Jetpack Compose
- **UI Framework**: Material Design 3
- **Networking**: Retrofit2 + OkHttp3
- **Minimum SDK**: Android 21 (5.0+)
- **Target SDK**: 34

### Core Django Apps Structure
The Django backend uses a modular app structure under `backend/apps/`:

- `apps.core`: Base models (TimeStampedModel, SoftDeletableModel, ModeEntrainement) and shared utilities. All models inherit from these base classes for consistent timestamps and soft deletion capabilities.
- `apps.users`: Custom User model with fitness profiles, calorie calculations using Mifflin-St Jeor formula, and fitness objectives (PRISE_MASSE, SECHE, FORCE, etc.)
- `apps.machines`: Exercise machines catalog with categories, muscle groups, GIF demonstrations, and exercise variants for different equipment types
- `apps.workouts`: Workout sessions (SeanceEntrainement), exercises, sets with progression tracking, and new recommendation system

### Settings Architecture
Settings are split across `backend/basicfit_project/settings/`:
- `base.py`: Common settings and app configuration
- `development.py`: Local development (SQLite, debug mode)
- `production.py`: Production settings (PostgreSQL, security)
- `flyio.py`: Fly.io-specific configuration
Default: `basicfit_project.settings.development`

## Development Commands

### Android Development
```bash
# Build debug APK (Windows)
android\build_apk.bat

# Build debug APK (Manual)
cd android
./gradlew assembleDebug

# Clean build
./gradlew clean

# APK location after build
android/app/build/outputs/apk/debug/app-debug.apk
```

### Backend Development
```bash
# Setup and run locally
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Data import and management
python manage.py import_machines

# Single test execution examples
python manage.py test apps.users.tests.TestUserModel
python manage.py test apps.workouts.tests
```

### Testing & Validation
```bash
cd backend

# Complete system testing
python test_systeme_complet.py

# Production API testing
python test_api_production.py

# Authentication flow testing
python test_authentification_android.py

# Recommendation system testing
python test_nouveau_systeme_recommandation.py
```

### Deployment Commands
```bash
# Quick API deployment to Fly.io
deploy_flyio.bat

# Deploy API to Fly.io (manual)
fly deploy

# Complete deployment workflow
final_deploy.bat
```

## Key Features & Models

### Recent Feature Updates (2025-08-16)
- **Intelligent Performance Analysis**: Real-time success rate calculation based on achieved vs target sets/reps with adaptive weight recommendations
- **Exercise Replacement Dialog**: In-workout exercise substitution targeting same muscle groups with searchable interface
- **Enhanced Calendar Interface**: Google Calendar-style current day indicators with mint color highlighting and improved visual feedback
- **Automatic Authentication Management**: Token validation with automatic logout on 401/403 responses
- **CSV Import Optimization**: Fixed coroutine scope management for reliable data import functionality

### Base Models Pattern
All Django models inherit from base classes in `apps.core.models`:
- `TimeStampedModel`: Auto-managed `created_at`/`updated_at` fields
- `SoftDeletableModel`: Soft deletion with `is_active`/`deleted_at` fields and custom managers
- `ModeEntrainement`: Training modes with rep/set/rest recommendations per training type

### User Management
- Custom User model extending AbstractUser with fitness profiles
- Objectives: PRISE_MASSE, SECHE, FORCE, ENDURANCE, POWERLIFTING
- Calorie calculation using Mifflin-St Jeor formula with activity multipliers
- Experience levels: DEBUTANT, INTERMEDIAIRE, AVANCE, EXPERT
- Profile updates through dedicated endpoints

### Machine & Exercise System
- Machine catalog with many-to-many category relationships
- Exercise variants linked to specific machine types
- GIF demonstrations stored in media directory
- Cardio vs. strength equipment differentiation with duration/tempo tracking
- Custom management commands for machine data import

### Workout Tracking Architecture
- `SeanceEntrainement`: Complete workout sessions with user/date tracking
- `SerieExercice`: Individual sets with reps, weight, rest periods, tempo
- Volume load calculations for progression tracking
- **Intelligent Recommendation System**: Advanced performance analysis with success rate calculations and adaptive weight recommendations
- **Exercise Replacement System**: Dynamic exercise substitution during workouts based on muscle groups
- **Automatic Token Management**: Automatic logout detection for invalid authentication tokens
- Calendar integration with enhanced visual indicators and workout scheduling

## API Architecture

### Authentication Flow
- JWT-based authentication via djangorestframework-simplejwt
- Login endpoint: `/api/auth/login/` returns access/refresh tokens  
- Android app stores tokens securely and includes in Authorization header
- Token refresh via `/api/auth/token/refresh/`
- API base URL configured in `android/app/src/main/java/com/basicfit/app/ApiService.kt`

### Key API Endpoints Structure
```
/api/auth/          # Authentication (login, register, refresh)
/api/users/         # User profiles and calorie management
/api/machines/      # Machine catalog and categories
/api/workouts/      # Workout sessions, exercises, recommendations
/api/calendar/      # Workout history and calendar integration
```

### Android-Backend Integration
- Retrofit2 client with OkHttp3 interceptors for authentication
- Gson serialization for API responses
- Automatic token refresh on 401 responses
- Network connectivity checking for offline handling

## Development Workflow

### Model Development Pattern
1. Create models inheriting from `TimeStampedModel` or `SoftDeletableModel`
2. Add to appropriate Django app (`users`, `machines`, `workouts`)
3. Create serializers in `serializers.py` 
4. Add API views and URL patterns
5. Update Android ApiService.kt with new endpoints
6. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Testing Strategy
- Backend unit tests via Django's test framework
- Integration tests using dedicated test scripts in `backend/`
- Production API validation via `test_api_production.py`
- Android authentication flow testing via `test_authentification_android.py`

## Deployment Architecture

### Fly.io Production Environment
- PostgreSQL database with connection pooling
- Cloudinary for media storage (GIFs, images)
- WhiteNoise for static file serving
- CORS configured for Android app access
- Environment-specific settings in `settings/flyio.py`

### Local Development Setup
- SQLite database for simplicity
- Local media storage in `backend/media/`
- Debug mode enabled
- Django admin available at `/admin/`

## Critical Application Behavior

### Online-Only Mode
- **IMPORTANT**: The application has been modified to be 100% online-only (commit: 0ceee9f7)
- All offline/local database functionality has been removed
- Always prioritize API authentication before any fallback logic

### Recent API Endpoint Fixes
Based on recent commits, ensure correct endpoint usage:
- `/api/machines/` (not `/workouts/machines/` - fixed in commit: 93f14613)
- `/api/recommendations/` (not `/recommendation/` - fixed in commit: 78cf38be)
- All workout entries must include `totalWeight` parameter (fixed in commit: 1aff7ad2)

## Android App Architecture

### Key Components
- **MainActivity.kt**: Main application entry with Jetpack Compose UI, navigation, intelligent recommendation system, and exercise replacement functionality
- **CalendarScreen.kt**: Enhanced workout history calendar with improved current day indicators and optimized CSV import functionality
- **ApiService.kt**: Retrofit client with JWT authentication, automatic token refresh, and automatic logout detection on invalid tokens
- **AuthManager.kt**: Handles user authentication and profile management
- **CommonData.kt**: Data models including ExercisePerformance, WeightRecommendation, and performance tracking structures

### UI Design System
- Material Design 3 with custom color palette (Mint: #00C9A7, SoftBlue: #6DD5ED)
- Gradient backgrounds and rounded corners throughout
- Responsive layouts for different screen sizes
- GIF support for exercise demonstrations via Coil image loader

### State Management
- Compose state management with MutableState and StateFlow
- SharedPreferences for token storage and user settings
- Reactive UI updates based on API responses

## Testing Infrastructure

### Backend Test Suite
Located in `backend/` directory:
- `test_systeme_complet.py`: Comprehensive system testing
- `test_api_production.py`: Production API validation  
- `test_authentification_android.py`: Android auth flow testing
- `test_nouveau_systeme_recommandation.py`: Recommendation system testing

### Running Specific Tests
```bash
# Test specific Django app
python manage.py test apps.users.tests

# Test specific model or class
python manage.py test apps.users.tests.TestUserModel

# Run production API tests
python test_api_production.py
```

## Deployment Workflow

### Automated Deployment Scripts
- `deploy_flyio.bat`: Complete Fly.io deployment with database setup
- `final_deploy.bat`: Full deployment workflow including testing
- `android/build_apk.bat`: Android APK build with Gradle wrapper

### Fly.io Configuration
- App name: `basicfit-v2`
- Database: `basicfit-v2-db` (PostgreSQL)
- Region: CDG (Paris)
- Environment variables set via `flyctl secrets`

## Development Best Practices

### Model Development Pattern
1. All models inherit from `TimeStampedModel` or `SoftDeletableModel` in `apps.core.models`
2. Use `active_objects` manager for soft-deleted models
3. Follow naming conventions: French model names, English field names
4. Add proper verbose_name and help_text for admin interface

### API Development Pattern
1. Create serializers in respective app's `serializers.py`
2. Use Django REST Framework viewsets and routers
3. Implement proper pagination for list endpoints
4. Add authentication and permission classes
5. Update Android `ApiService.kt` with new endpoint definitions

### Android Development Pattern
1. Follow Jetpack Compose best practices
2. Use sealed classes for navigation states
3. Implement proper error handling with user-friendly messages
4. Store sensitive data (tokens) in encrypted SharedPreferences
5. Use Retrofit interceptors for automatic authentication

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
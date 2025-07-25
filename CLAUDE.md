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
- **Deployment**: Railway platform
- **API URL**: https://basicfit-production.up.railway.app/

### Android App
- **Location**: `android/`
- **Language**: Kotlin with Jetpack Compose
- **UI Framework**: Material Design 3
- **Networking**: Retrofit2 + OkHttp3
- **Minimum SDK**: Android 21 (5.0+)
- **Target SDK**: 34

### Core Django Apps Structure
- `apps.core`: Base models (TimeStampedModel, SoftDeletableModel) and shared utilities
- `apps.users`: Custom User model with fitness profiles and calorie calculations
- `apps.machines`: Exercise machines, muscle groups, and equipment management
- `apps.workouts`: Workout sessions, exercises, sets, and progression tracking

## Development Commands

### Android Development
```bash
# Build debug APK
cd android
./gradlew assembleDebug

# Clean build
./gradlew clean

# Windows batch script for APK build
android/build_apk.bat
```

### Backend Development
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Import machine data
python manage.py import_machines

# Test the complete system
python test_systeme_complet.py
```

### Deployment Commands
```bash
# Deploy API to Railway
deploy_api_railway.bat

# Complete deployment (backend + Android)
deploy_complete.bat

# Quick API deployment
deploy_api_quick.bat
```

## Key Features & Models

### User Management
- Custom User model extending AbstractUser
- Fitness profiles with objectives (PRISE_MASSE, SECHE, FORCE, etc.)
- Calorie calculation using Mifflin-St Jeor formula
- Experience levels (DEBUTANT, INTERMEDIAIRE, AVANCE, EXPERT)

### Machine & Exercise System
- Machine catalog with categories and muscle groups
- Exercise variants for different machine types
- GIF support for exercise demonstrations
- Cardio vs. strength equipment differentiation

### Workout Tracking
- Complete workout sessions (SeanceEntrainement)
- Individual exercises with sets, reps, weights
- Rest periods and tempo tracking
- Progress monitoring and statistics

## Settings Configuration

The Django settings are split across multiple files in `backend/basicfit_project/settings/`:
- `base.py`: Common settings
- `development.py`: Local development
- `production.py`: Production on Railway
- `railway.py`: Railway-specific configuration

Default development setting: `basicfit_project.settings.development`

## API Authentication

- JWT-based authentication required for most endpoints
- Token obtained via `/api/auth/login/`
- Android app stores tokens in secure storage
- API base URL configured in Android's ApiClient.java

## Database Schema Highlights

- TimeStampedModel: Provides created_at/updated_at for all models
- SoftDeletableModel: Soft deletion with is_deleted field
- Machine categories use many-to-many relationships
- Workout progression calculated using volume load formulas

## Testing & Validation

Several test scripts are available in the backend directory:
- `test_systeme_complet.py`: End-to-end system testing
- `test_api_railway.py`: Railway API testing
- `test_authentification_android.py`: Android auth flow testing
- `validation_complete.py`: Complete data validation

## File Upload & Media

- Machine exercise GIFs stored in media directory
- Cloudinary integration for production media storage
- Image processing via Pillow

## Deployment Notes

- Railway deployment uses PostgreSQL
- Android APK built via Gradle
- CORS configured for cross-origin requests
- WhiteNoise handles static files in production
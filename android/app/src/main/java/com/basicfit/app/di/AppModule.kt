package com.basicfit.app.di

import com.basicfit.app.data.api.BasicFitApiService
import com.basicfit.app.data.repositories.*
import com.basicfit.app.presentation.profile.ProfileViewModel
import com.basicfit.app.presentation.machines.MachineViewModel
import com.basicfit.app.presentation.training.TrainingViewModel
import com.basicfit.app.presentation.calendar.CalendarViewModel
import com.basicfit.app.presentation.log.LogViewModel
import com.basicfit.app.utils.Logger

/**
 * Module de dépendances pour l'application BasicFit
 * Fournit les instances des repositories et ViewModels
 */
object AppModule {

    // Instance unique du logger
    val logger: Logger by lazy {
        Logger()
    }

    // API Service (sera configuré dans MainActivity)
    lateinit var apiService: BasicFitApiService

    // ==================== REPOSITORIES ====================

    val authRepository: AuthRepository by lazy {
        AuthRepository(apiService, logger)
    }

    val machineRepository: MachineRepository by lazy {
        MachineRepository(apiService, logger)
    }

    val workoutRepository: WorkoutRepository by lazy {
        WorkoutRepository(apiService, logger)
    }

    val calendarRepository: CalendarRepository by lazy {
        CalendarRepository(apiService, logger)
    }

    val logRepository: LogRepository by lazy {
        LogRepository(apiService, logger)
    }

    // ==================== VIEW MODELS ====================

    fun provideProfileViewModel(): ProfileViewModel {
        return ProfileViewModel(authRepository, apiService, logger)
    }

    fun provideMachineViewModel(): MachineViewModel {
        return MachineViewModel(machineRepository, logger)
    }

    fun provideTrainingViewModel(): TrainingViewModel {
        return TrainingViewModel(workoutRepository, machineRepository, logger)
    }

    fun provideCalendarViewModel(): CalendarViewModel {
        return CalendarViewModel(calendarRepository, logger)
    }

    fun provideLogViewModel(): LogViewModel {
        return LogViewModel(logRepository, logger)
    }

    // ==================== UTILITAIRES ====================

    /**
     * Initialiser le module avec l'API service
     */
    fun initialize(apiService: BasicFitApiService) {
        this.apiService = apiService
        logger.info("DI", "AppModule initialisé avec API service")
    }
}
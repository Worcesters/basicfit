package com.basicfit.app.data.repositories

import com.basicfit.app.data.api.BasicFitApiService
import com.basicfit.app.data.models.Machine
import com.basicfit.app.data.models.MachineCategory
import com.basicfit.app.data.models.MachineRecommendation
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Repository pour la gestion des machines d'exercice
 */
class MachineRepository(
    private val apiService: BasicFitApiService,
    private val logger: Logger
) {
    
    // Cache des machines
    private val _machines = MutableStateFlow<List<Machine>>(emptyList())
    val machines: StateFlow<List<Machine>> = _machines.asStateFlow()
    
    private val _categories = MutableStateFlow<List<MachineCategory>>(emptyList())
    val categories: StateFlow<List<MachineCategory>> = _categories.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    /**
     * Charger toutes les machines
     */
    suspend fun loadMachines(): Result<List<Machine>> {
        return try {
            _isLoading.value = true
            logger.info("MACHINE", "Chargement des machines...")
            
            val response = apiService.getMachines()
            
            if (response.isSuccessful) {
                val machineList = response.body() ?: emptyList()
                _machines.value = machineList
                logger.success("MACHINE", "Chargement réussi: ${machineList.size} machines")
                Result.success(machineList)
            } else {
                val errorMsg = "Erreur chargement machines: ${response.code()}"
                logger.error("MACHINE", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("MACHINE", "Erreur lors du chargement des machines", details = e.message)
            Result.failure(e)
        } finally {
            _isLoading.value = false
        }
    }
    
    /**
     * Charger les catégories de machines
     */
    suspend fun loadCategories(): Result<List<MachineCategory>> {
        return try {
            logger.info("MACHINE", "Chargement des catégories...")
            
            val response = apiService.getMachineCategories()
            
            if (response.isSuccessful) {
                val categoryList = response.body() ?: emptyList()
                _categories.value = categoryList
                logger.success("MACHINE", "Chargement réussi: ${categoryList.size} catégories")
                Result.success(categoryList)
            } else {
                val errorMsg = "Erreur chargement catégories: ${response.code()}"
                logger.error("MACHINE", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("MACHINE", "Erreur lors du chargement des catégories", details = e.message)
            Result.failure(e)
        }
    }
    
    /**
     * Obtenir la recommandation pour une machine
     */
    suspend fun getMachineRecommendation(machineId: Int): Result<MachineRecommendation> {
        return try {
            logger.info("MACHINE", "Récupération recommandation pour machine ID: $machineId")
            
            val response = apiService.getMachineRecommendation(machineId)
            
            if (response.isSuccessful) {
                val recommendation = response.body()
                if (recommendation != null) {
                    logger.success("MACHINE", "Recommandation obtenue: ${recommendation.poidsRecommande}kg")
                    Result.success(recommendation)
                } else {
                    logger.error("MACHINE", "Recommandation vide")
                    Result.failure(Exception("Recommandation introuvable"))
                }
            } else {
                val errorMsg = "Erreur recommandation: ${response.code()}"
                logger.error("MACHINE", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("MACHINE", "Erreur lors de la récupération de la recommandation", details = e.message)
            Result.failure(e)
        }
    }
    
    /**
     * Rechercher des machines par nom
     */
    fun searchMachines(query: String): List<Machine> {
        val currentMachines = _machines.value
        return if (query.isBlank()) {
            currentMachines
        } else {
            currentMachines.filter { machine ->
                machine.nom.contains(query, ignoreCase = true) ||
                machine.description.contains(query, ignoreCase = true) ||
                machine.groupeMusculaire.contains(query, ignoreCase = true) ||
                machine.getCategoriesNames().contains(query, ignoreCase = true)
            }
        }
    }
    
    /**
     * Filtrer les machines par catégorie
     */
    fun filterMachinesByCategory(categoryName: String): List<Machine> {
        val currentMachines = _machines.value
        return if (categoryName == "Toutes") {
            currentMachines
        } else {
            currentMachines.filter { machine ->
                machine.getMainCategory() == categoryName
            }
        }
    }
    
    /**
     * Filtrer les machines par groupe musculaire
     */
    fun filterMachinesByMuscleGroup(muscleGroup: String): List<Machine> {
        val currentMachines = _machines.value
        return if (muscleGroup == "Tous") {
            currentMachines
        } else {
            currentMachines.filter { machine ->
                machine.groupeMusculaire.contains(muscleGroup, ignoreCase = true)
            }
        }
    }
    
    /**
     * Obtenir les groupes musculaires disponibles
     */
    fun getAvailableMuscleGroups(): List<String> {
        val currentMachines = _machines.value
        val muscleGroups = currentMachines
            .map { it.groupeMusculaire }
            .filter { it.isNotBlank() }
            .distinct()
            .sorted()
        
        return listOf("Tous") + muscleGroups
    }
    
    /**
     * Obtenir les noms des catégories disponibles
     */
    fun getAvailableCategoryNames(): List<String> {
        val currentCategories = _categories.value
        val categoryNames = currentCategories.map { it.nom }.sorted()
        return listOf("Toutes") + categoryNames
    }
    
    /**
     * Exporter la liste des machines en format texte
     */
    fun exportMachineList(): String {
        val currentMachines = _machines.value
        val timestamp = java.time.LocalDateTime.now().format(
            java.time.format.DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm")
        )
        
        return buildString {
            appendLine("===== EXPORT MACHINES BASICFIT =====")
            appendLine("Date: $timestamp")
            appendLine("Total: ${currentMachines.size} machines")
            appendLine()
            
            currentMachines.sortedBy { it.nom }.forEach { machine ->
                appendLine("• ${machine.nom}")
                if (machine.description.isNotBlank()) {
                    appendLine("  Description: ${machine.description}")
                }
                if (machine.groupeMusculaire.isNotBlank()) {
                    appendLine("  Groupe musculaire: ${machine.groupeMusculaire}")
                }
                appendLine("  Catégorie: ${machine.getMainCategory()}")
                appendLine()
            }
        }
    }
    
    /**
     * Obtenir une machine par ID
     */
    fun getMachineById(id: Int): Machine? {
        return _machines.value.find { it.id == id }
    }
}
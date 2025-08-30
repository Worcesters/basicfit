package com.basicfit.app.presentation.machines

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.basicfit.app.data.models.Machine
import com.basicfit.app.data.models.MachineCategory
import com.basicfit.app.data.repositories.MachineRepository
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

/**
 * ViewModel pour l'onglet Machine
 * Gère l'affichage et la recherche des machines d'exercice
 */
class MachineViewModel(
    private val machineRepository: MachineRepository,
    private val logger: Logger
) : ViewModel() {

    // États des machines
    val machines = machineRepository.machines
    val categories = machineRepository.categories
    val isLoading = machineRepository.isLoading

    // État de recherche
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    private val _selectedCategory = MutableStateFlow("Toutes")
    val selectedCategory: StateFlow<String> = _selectedCategory.asStateFlow()

    private val _selectedMuscleGroup = MutableStateFlow("Tous")
    val selectedMuscleGroup: StateFlow<String> = _selectedMuscleGroup.asStateFlow()

    // Machines filtrées
    private val _filteredMachines = MutableStateFlow<List<Machine>>(emptyList())
    val filteredMachines: StateFlow<List<Machine>> = _filteredMachines.asStateFlow()

    // États d'erreur et succès
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _successMessage = MutableStateFlow<String?>(null)
    val successMessage: StateFlow<String?> = _successMessage.asStateFlow()

    // Groupes musculaires disponibles
    private val _availableMuscleGroups = MutableStateFlow<List<String>>(emptyList())
    val availableMuscleGroups: StateFlow<List<String>> = _availableMuscleGroups.asStateFlow()

    // Noms des catégories disponibles
    private val _availableCategoryNames = MutableStateFlow<List<String>>(emptyList())
    val availableCategoryNames: StateFlow<List<String>> = _availableCategoryNames.asStateFlow()

    init {
        logger.info("MACHINE", "Initialisation du MachineViewModel")

        // Observer les changements de machines pour mettre à jour les filtres
        viewModelScope.launch {
            machines.collect { machineList ->
                updateAvailableFilters()
                applyFilters()
            }
        }

        // Observer les changements de filtres
        viewModelScope.launch {
            combine(
                searchQuery,
                selectedCategory,
                selectedMuscleGroup
            ) { query: String, category: String, muscleGroup: String ->
                Triple(query, category, muscleGroup)
            }.collect {
                applyFilters()
            }
        }

        // Charger les données au démarrage
        loadData()
    }

    /**
     * Charger les machines et catégories
     */
    fun loadData() {
        viewModelScope.launch {
            logger.info("MACHINE", "Chargement des données machines...")

            // Charger les machines
            val machinesResult = machineRepository.loadMachines()
            if (machinesResult.isFailure) {
                val errorMsg = machinesResult.exceptionOrNull()?.message ?: "Erreur de chargement"
                logger.error("MACHINE", "Erreur chargement machines: $errorMsg")
                _errorMessage.value = errorMsg
            }

            // Charger les catégories
            val categoriesResult = machineRepository.loadCategories()
            if (categoriesResult.isFailure) {
                val errorMsg = categoriesResult.exceptionOrNull()?.message ?: "Erreur de chargement"
                logger.error("MACHINE", "Erreur chargement catégories: $errorMsg")
                _errorMessage.value = errorMsg
            }

            if (machinesResult.isSuccess && categoriesResult.isSuccess) {
                logger.success("MACHINE", "Données chargées avec succès")
                _successMessage.value = "Machines chargées: ${machinesResult.getOrNull()?.size ?: 0}"
            }
        }
    }

    /**
     * Mettre à jour la requête de recherche
     */
    fun updateSearchQuery(query: String) {
        logger.debug("MACHINE", "Recherche: '$query'")
        _searchQuery.value = query
    }

    /**
     * Sélectionner une catégorie
     */
    fun selectCategory(category: String) {
        logger.debug("MACHINE", "Catégorie sélectionnée: $category")
        _selectedCategory.value = category
    }

    /**
     * Sélectionner un groupe musculaire
     */
    fun selectMuscleGroup(muscleGroup: String) {
        logger.debug("MACHINE", "Groupe musculaire sélectionné: $muscleGroup")
        _selectedMuscleGroup.value = muscleGroup
    }

    /**
     * Réinitialiser les filtres
     */
    fun resetFilters() {
        logger.debug("MACHINE", "Réinitialisation des filtres")
        _searchQuery.value = ""
        _selectedCategory.value = "Toutes"
        _selectedMuscleGroup.value = "Tous"
    }

    /**
     * Exporter la liste des machines
     */
    fun exportMachines(): String {
        logger.info("MACHINE", "Export de la liste des machines")
        return machineRepository.exportMachineList().also {
            _successMessage.value = "Liste des machines exportée"
        }
    }

    /**
     * Obtenir une machine par ID
     */
    fun getMachineById(id: Int): Machine? {
        return machineRepository.getMachineById(id)
    }

    /**
     * Effacer les messages
     */
    fun clearMessages() {
        _errorMessage.value = null
        _successMessage.value = null
    }

    // ==================== MÉTHODES PRIVÉES ====================

    /**
     * Appliquer les filtres aux machines
     */
    private fun applyFilters() {
        val currentMachines = machines.value
        val query = searchQuery.value
        val category = selectedCategory.value
        val muscleGroup = selectedMuscleGroup.value

        var filtered = currentMachines

        // Appliquer la recherche textuelle
        if (query.isNotBlank()) {
            filtered = machineRepository.searchMachines(query)
        }

        // Appliquer le filtre de catégorie
        if (category != "Toutes") {
            filtered = filtered.filter { machine ->
                machine.getMainCategory() == category
            }
        }

        // Appliquer le filtre de groupe musculaire
        if (muscleGroup != "Tous") {
            filtered = filtered.filter { machine ->
                machine.groupeMusculaire.contains(muscleGroup, ignoreCase = true)
            }
        }

        _filteredMachines.value = filtered

        logger.debug("MACHINE", "Filtres appliqués: ${filtered.size} machines trouvées")
    }

    /**
     * Mettre à jour les options de filtres disponibles
     */
    private fun updateAvailableFilters() {
        val muscleGroups = machineRepository.getAvailableMuscleGroups()
        val categoryNames = machineRepository.getAvailableCategoryNames()

        _availableMuscleGroups.value = muscleGroups
        _availableCategoryNames.value = categoryNames

        logger.debug("MACHINE", "Filtres mis à jour: ${muscleGroups.size} groupes musculaires, ${categoryNames.size} catégories")
    }

    override fun onCleared() {
        super.onCleared()
        logger.debug("MACHINE", "MachineViewModel détruit")
    }
}
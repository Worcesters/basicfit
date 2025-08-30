package com.basicfit.app.data.api

import android.content.Context
import com.basicfit.app.data.repositories.AuthRepository
import com.basicfit.app.utils.Logger
import com.google.gson.GsonBuilder
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Configuration réseau pour l'application
 * Gère la création des services API avec authentification
 */
object NetworkModule {
    
    private const val BASE_URL = "https://basicfit-v2.fly.dev/"
    private const val TIMEOUT_SECONDS = 30L
    
    /**
     * Créer le service API avec authentification
     */
    fun createApiService(context: Context, logger: Logger): BasicFitApiService {
        val okHttpClient = createOkHttpClient(context, logger)
        val retrofit = createRetrofit(okHttpClient)
        return retrofit.create(BasicFitApiService::class.java)
    }
    
    /**
     * Créer le client OkHttp avec intercepteurs
     */
    private fun createOkHttpClient(context: Context, logger: Logger): OkHttpClient {
        val builder = OkHttpClient.Builder()
            .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        
        // Intercepteur d'authentification
        builder.addInterceptor(createAuthInterceptor(context))
        
        // Intercepteur de logging
        builder.addInterceptor(createLoggingInterceptor(logger))
        
        // Intercepteur pour les erreurs d'authentification
        builder.addInterceptor(createAuthErrorInterceptor(context, logger))
        
        return builder.build()
    }
    
    /**
     * Intercepteur d'authentification
     * Ajoute automatiquement le token aux requêtes
     */
    private fun createAuthInterceptor(context: Context): Interceptor {
        return Interceptor { chain ->
            val originalRequest = chain.request()
            
            // Récupérer le token depuis SharedPreferences
            val prefs = context.getSharedPreferences("BasicFitAuth", Context.MODE_PRIVATE)
            val token = prefs.getString("access_token", null)
            
            val requestBuilder = originalRequest.newBuilder()
            
            // Ajouter le token si disponible
            if (!token.isNullOrBlank()) {
                requestBuilder.addHeader("Authorization", "Bearer $token")
            }
            
            // Headers par défaut
            requestBuilder
                .addHeader("Content-Type", "application/json")
                .addHeader("Accept", "application/json")
            
            chain.proceed(requestBuilder.build())
        }
    }
    
    /**
     * Intercepteur de logging
     * Log les requêtes et réponses pour debug
     */
    private fun createLoggingInterceptor(logger: Logger): Interceptor {
        return Interceptor { chain ->
            val request = chain.request()
            val startTime = System.nanoTime()
            
            logger.debug("API", "→ ${request.method} ${request.url}")
            
            try {
                val response = chain.proceed(request)
                val endTime = System.nanoTime()
                val duration = (endTime - startTime) / 1_000_000 // Convert to milliseconds
                
                if (response.isSuccessful) {
                    logger.debug("API", "← ${response.code} ${request.url} (${duration}ms)")
                } else {
                    logger.warning("API", "← ${response.code} ${request.url} (${duration}ms)")
                }
                
                response
            } catch (e: Exception) {
                val endTime = System.nanoTime()
                val duration = (endTime - startTime) / 1_000_000
                logger.error("API", "✗ ${request.method} ${request.url} (${duration}ms)", exception = e)
                throw e
            }
        }
    }
    
    /**
     * Intercepteur pour gérer les erreurs d'authentification
     * Déconnecte automatiquement l'utilisateur en cas de token invalide
     */
    private fun createAuthErrorInterceptor(context: Context, logger: Logger): Interceptor {
        return Interceptor { chain ->
            val response = chain.proceed(chain.request())
            
            // Vérifier si l'erreur est liée à l'authentification
            if (response.code == 401 || response.code == 403) {
                logger.warning("API", "Token invalide détecté (${response.code}), déconnexion automatique")
                
                // Effacer les données d'authentification
                val prefs = context.getSharedPreferences("BasicFitAuth", Context.MODE_PRIVATE)
                prefs.edit().clear().apply()
                
                // Note: Ici on pourrait aussi envoyer un événement pour rediriger vers l'écran de connexion
                // mais cela nécessiterait une architecture plus complexe avec EventBus ou similar
            }
            
            response
        }
    }
    
    /**
     * Créer l'instance Retrofit
     */
    private fun createRetrofit(okHttpClient: OkHttpClient): Retrofit {
        val gson = GsonBuilder()
            .setDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")
            .create()
        
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }
}
package com.basicfit.app.data.api

import android.content.SharedPreferences
import com.basicfit.app.utils.Logger
import com.google.gson.GsonBuilder
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Configuration réseau pour l'API BasicFit
 * Gère la création du client Retrofit avec authentification JWT
 */
object NetworkConfig {

    private const val BASE_URL = "https://basicfit-v2.fly.dev/"

    /**
     * Créer le service API avec configuration Retrofit
     */
    fun createApiService(
        sharedPreferences: SharedPreferences,
        logger: Logger
    ): BasicFitApiService {

        // Configuration HTTP client
        val httpClient = OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor(sharedPreferences, logger))
            .addInterceptor(LoggingInterceptor())
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()

        // Configuration Gson
        val gson = GsonBuilder()
            .setLenient()
            .create()

        // Configuration Retrofit
        val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(httpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()

        logger.info("NETWORK", "API Service configuré: $BASE_URL")

        return retrofit.create(BasicFitApiService::class.java)
    }
}

/**
 * Intercepteur d'authentification JWT
 */
class AuthInterceptor(
    private val sharedPreferences: SharedPreferences,
    private val logger: Logger
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        // Récupérer le token d'authentification
        val token = sharedPreferences.getString("auth_token", null)

        val newRequest = if (token != null) {
            originalRequest.newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
        } else {
            originalRequest
        }

        val response = chain.proceed(newRequest)

        // Vérifier si le token a expiré
        if (response.code == 401 || response.code == 403) {
            logger.warning("NETWORK", "Token expiré ou invalide, nettoyage...")
            sharedPreferences.edit().clear().apply()
        }

        return response
    }
}

/**
 * Intercepteur de logging HTTP
 */
class LoggingInterceptor : Interceptor {
    private val httpLoggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    override fun intercept(chain: Interceptor.Chain): Response {
        return httpLoggingInterceptor.intercept(chain)
    }
}
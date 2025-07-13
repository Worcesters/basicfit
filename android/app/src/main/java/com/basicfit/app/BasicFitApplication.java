package com.basicfit.app;

import androidx.multidex.MultiDexApplication;
import android.app.Activity;
import android.app.Application;
import android.app.Application.ActivityLifecycleCallbacks;
import android.os.Bundle;
import android.util.Log;

public class BasicFitApplication extends MultiDexApplication {

    private static boolean isInBackground = false;
    private static Object dataManager; // On utilisera le DataManager de Kotlin

    @Override
    public void onCreate() {
        super.onCreate();
        // Initialisation de l application avec MultiDex

        // Gestion du cycle de vie de l'application
        registerActivityLifecycleCallbacks(new ActivityLifecycleCallbacks() {
            @Override
            public void onActivityCreated(Activity activity, Bundle savedInstanceState) {
                // Le DataManager sera initialisé dans MainActivity
            }

            @Override
            public void onActivityStarted(Activity activity) {
                // L'application passe au premier plan
                if (isInBackground) {
                    isInBackground = false;
                    Log.d("BasicFitApp", "Application repasse au premier plan");
                }
            }

            @Override
            public void onActivityResumed(Activity activity) {
                // Activité reprise
            }

            @Override
            public void onActivityPaused(Activity activity) {
                // Activité mise en pause
            }

                        @Override
            public void onActivityStopped(Activity activity) {
                // Vérifier si l'application passe en arrière-plan
                if (!activity.isChangingConfigurations()) {
                    // L'application passe en arrière-plan
                    isInBackground = true;
                    Log.d("BasicFitApp", "Application passe en arrière-plan");

                    // L'état sera automatiquement sauvegardé par LaunchedEffect dans MainActivity
                    Log.d("BasicFitApp", "Sauvegarde automatique de l'état d'entraînement");
                }
            }

            @Override
            public void onActivitySaveInstanceState(Activity activity, Bundle outState) {
                // Sauvegarder l'état de l'activité
            }

            @Override
            public void onActivityDestroyed(Activity activity) {
                // Activité détruite
            }
        });
    }

        public static boolean isInBackground() {
        return isInBackground;
    }
}

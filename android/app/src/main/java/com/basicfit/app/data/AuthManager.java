package com.basicfit.app.data;

import android.content.Context;
import android.content.SharedPreferences;

public class AuthManager {
    private static final String PREFS_NAME = "basicfit_auth";
    private static final String KEY_IS_LOGGED_IN = "is_logged_in";
    private static final String KEY_USER_EMAIL = "user_email";
    private static final String KEY_USER_NAME = "user_name";

    private SharedPreferences prefs;

    public AuthManager(Context context) {
        prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }

    public boolean login(String email, String password) {
        // Simulation d'une connexion (remplacez par votre API)
        if (email != null && password != null && email.contains("@")) {
            prefs.edit()
                .putBoolean(KEY_IS_LOGGED_IN, true)
                .putString(KEY_USER_EMAIL, email)
                .putString(KEY_USER_NAME, "Utilisateur BasicFit")
                .apply();
            return true;
        }
        return false;
    }

    public boolean register(String email, String password) {
        // Simulation d'une inscription (remplacez par votre API)
        if (email != null && password != null && email.contains("@")) {
            prefs.edit()
                .putBoolean(KEY_IS_LOGGED_IN, true)
                .putString(KEY_USER_EMAIL, email)
                .putString(KEY_USER_NAME, "Nouvel utilisateur")
                .apply();
            return true;
        }
        return false;
    }

    public void logout() {
        prefs.edit()
            .putBoolean(KEY_IS_LOGGED_IN, false)
            .remove(KEY_USER_EMAIL)
            .remove(KEY_USER_NAME)
            .apply();
    }

    public boolean isLoggedIn() {
        return prefs.getBoolean(KEY_IS_LOGGED_IN, false);
    }

    public String getUserInfo() {
        if (isLoggedIn()) {
            String email = prefs.getString(KEY_USER_EMAIL, "");
            String name = prefs.getString(KEY_USER_NAME, "");
            return "Bonjour " + name + "\nEmail: " + email;
        }
        return null;
    }
}
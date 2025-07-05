package com.basicfit.app.data;

import java.io.IOException;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class ApiClient {
    private static final String BASE_URL = "https://basicfit-production.up.railway.app/";
    private static final OkHttpClient client = new OkHttpClient();

    public static boolean testConnection() {
        try {
            Request request = new Request.Builder()
                .url(BASE_URL)
                .build();

            Response response = client.newCall(request).execute();
            boolean success = response.isSuccessful();
            response.close();
            return success;
        } catch (IOException e) {
            return false;
        }
    }

    public static boolean loginWithApi(String email, String password) {
        // TODO: Implémenter l'appel API réel
        // Pour l'instant, simulation simple
        return email != null && password != null && email.contains("@");
    }

    public static boolean registerWithApi(String email, String password) {
        // TODO: Implémenter l'appel API réel
        // Pour l'instant, simulation simple
        return email != null && password != null && email.contains("@");
    }
}
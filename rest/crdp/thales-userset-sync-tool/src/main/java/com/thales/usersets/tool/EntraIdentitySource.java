package com.thales.usersets.tool;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Set;
import java.util.TreeSet;

final class EntraIdentitySource implements IdentitySource {

    private final String tenantId;
    private final String clientId;
    private final String clientSecret;
    private final String groupId;
    private final String userIdAttribute;
    private final String graphBaseUrl;

    EntraIdentitySource(
        String tenantId,
        String clientId,
        String clientSecret,
        String groupId,
        String userIdAttribute,
        String graphBaseUrl) {
        this.tenantId = tenantId;
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.groupId = groupId;
        this.userIdAttribute = userIdAttribute;
        this.graphBaseUrl = graphBaseUrl;
    }

    @Override
    public Set<String> loadUsers() throws IOException {
        String accessToken = requestAccessToken();
        String nextUrl = graphBaseUrl
            + "/groups/"
            + urlEncode(groupId)
            + "/members/microsoft.graph.user?$select=id,userPrincipalName,mail,displayName&$top=999";

        Set<String> users = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
        while (nextUrl != null && !nextUrl.isBlank()) {
            JsonObject payload = executeJsonRequest(nextUrl, accessToken);
            JsonArray values = payload.getAsJsonArray("value");
            if (values != null) {
                for (JsonElement element : values) {
                    if (element != null && element.isJsonObject()) {
                        String user = resolveUserIdentifier(element.getAsJsonObject());
                        if (user != null && !user.isBlank()) {
                            users.add(user.trim());
                        }
                    }
                }
            }
            nextUrl = payload.has("@odata.nextLink") ? payload.get("@odata.nextLink").getAsString() : null;
        }
        return users;
    }

    @Override
    public String describe() {
        return "entra-group:" + groupId;
    }

    private String requestAccessToken() throws IOException {
        String tokenUrl = "https://login.microsoftonline.com/" + urlEncode(tenantId) + "/oauth2/v2.0/token";
        String body = "client_id=" + urlEncode(clientId)
            + "&client_secret=" + urlEncode(clientSecret)
            + "&scope=" + urlEncode("https://graph.microsoft.com/.default")
            + "&grant_type=client_credentials";

        HttpURLConnection connection = (HttpURLConnection) new URL(tokenUrl).openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
        connection.setDoOutput(true);
        try (OutputStream outputStream = connection.getOutputStream()) {
            outputStream.write(body.getBytes(StandardCharsets.UTF_8));
        }

        int responseCode = connection.getResponseCode();
        String responseBody = readBody(connection, responseCode);
        connection.disconnect();
        if (responseCode < 200 || responseCode >= 300) {
            throw new IOException("Entra token request failed: HTTP " + responseCode + " body=" + responseBody);
        }

        JsonObject json = JsonParser.parseString(responseBody).getAsJsonObject();
        if (!json.has("access_token")) {
            throw new IOException("Entra token response did not contain access_token");
        }
        return json.get("access_token").getAsString();
    }

    private JsonObject executeJsonRequest(String url, String accessToken) throws IOException {
        HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection();
        connection.setRequestMethod("GET");
        connection.setRequestProperty("Authorization", "Bearer " + accessToken);
        connection.setRequestProperty("Accept", "application/json");

        int responseCode = connection.getResponseCode();
        String responseBody = readBody(connection, responseCode);
        connection.disconnect();
        if (responseCode < 200 || responseCode >= 300) {
            throw new IOException("Entra Graph request failed: HTTP " + responseCode + " body=" + responseBody);
        }
        return JsonParser.parseString(responseBody).getAsJsonObject();
    }

    private String resolveUserIdentifier(JsonObject user) {
        if (userIdAttribute != null && user.has(userIdAttribute) && !user.get(userIdAttribute).isJsonNull()) {
            return user.get(userIdAttribute).getAsString();
        }
        String[] fallbacks = new String[] { "userPrincipalName", "mail", "displayName", "id" };
        for (String fallback : fallbacks) {
            if (user.has(fallback) && !user.get(fallback).isJsonNull()) {
                String value = user.get(fallback).getAsString();
                if (value != null && !value.isBlank()) {
                    return value;
                }
            }
        }
        return null;
    }

    private static String readBody(HttpURLConnection connection, int responseCode) throws IOException {
        InputStream stream = responseCode >= 200 && responseCode < 300 ? connection.getInputStream() : connection.getErrorStream();
        if (stream == null) {
            return "";
        }
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            return response.toString();
        }
    }

    private static String urlEncode(String input) throws IOException {
        return URLEncoder.encode(input, StandardCharsets.UTF_8.name());
    }
}

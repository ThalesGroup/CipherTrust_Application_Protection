package com.thales.usersets.tool;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

final class OktaIdentitySource implements IdentitySource {

    private final String baseUrl;
    private final String apiToken;
    private final String groupId;
    private final String userIdAttribute;
    private final boolean activeUsersOnly;
    private final int pageLimit;

    OktaIdentitySource(
        String baseUrl,
        String apiToken,
        String groupId,
        String userIdAttribute,
        boolean activeUsersOnly,
        int pageLimit) {
        this.baseUrl = stripTrailingSlash(baseUrl);
        this.apiToken = apiToken;
        this.groupId = groupId;
        this.userIdAttribute = userIdAttribute;
        this.activeUsersOnly = activeUsersOnly;
        this.pageLimit = pageLimit;
    }

    @Override
    public Set<String> loadUsers() throws IOException {
        Set<String> users = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
        String nextUrl = baseUrl + "/api/v1/groups/" + groupId + "/users?limit=" + pageLimit;

        while (nextUrl != null && !nextUrl.isBlank()) {
            HttpURLConnection connection = (HttpURLConnection) new URL(nextUrl).openConnection();
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Authorization", "SSWS " + apiToken);
            connection.setRequestProperty("Accept", "application/json");

            int responseCode = connection.getResponseCode();
            String responseBody = readBody(connection, responseCode);
            if (responseCode < 200 || responseCode >= 300) {
                connection.disconnect();
                throw new IOException("Okta request failed: HTTP " + responseCode + " body=" + responseBody);
            }

            JsonElement root = JsonParser.parseString(responseBody);
            if (root.isJsonArray()) {
                JsonArray array = root.getAsJsonArray();
                for (JsonElement element : array) {
                    if (element != null && element.isJsonObject()) {
                        JsonObject user = element.getAsJsonObject();
                        if (activeUsersOnly && isInactive(user)) {
                            continue;
                        }
                        String identifier = resolveUserIdentifier(user);
                        if (identifier != null && !identifier.isBlank()) {
                            users.add(identifier.trim());
                        }
                    }
                }
            }

            nextUrl = extractNextLink(connection.getHeaderFields());
            connection.disconnect();
        }

        return users;
    }

    @Override
    public String describe() {
        return "okta-group:" + groupId;
    }

    private boolean isInactive(JsonObject user) {
        if (!user.has("status") || user.get("status").isJsonNull()) {
            return false;
        }
        return !"ACTIVE".equalsIgnoreCase(user.get("status").getAsString());
    }

    private String resolveUserIdentifier(JsonObject user) {
        if ("id".equals(userIdAttribute) && user.has("id") && !user.get("id").isJsonNull()) {
            return user.get("id").getAsString();
        }

        if (userIdAttribute.startsWith("profile.")) {
            String profileKey = userIdAttribute.substring("profile.".length());
            if (user.has("profile") && user.get("profile").isJsonObject()) {
                JsonObject profile = user.getAsJsonObject("profile");
                if (profile.has(profileKey) && !profile.get(profileKey).isJsonNull()) {
                    return profile.get(profileKey).getAsString();
                }
            }
        }

        if (user.has("profile") && user.get("profile").isJsonObject()) {
            JsonObject profile = user.getAsJsonObject("profile");
            String[] fallbacks = new String[] { "login", "email" };
            for (String fallback : fallbacks) {
                if (profile.has(fallback) && !profile.get(fallback).isJsonNull()) {
                    String value = profile.get(fallback).getAsString();
                    if (value != null && !value.isBlank()) {
                        return value;
                    }
                }
            }
        }

        if (user.has("id") && !user.get("id").isJsonNull()) {
            return user.get("id").getAsString();
        }
        return null;
    }

    private static String extractNextLink(Map<String, List<String>> headers) {
        for (Map.Entry<String, List<String>> entry : headers.entrySet()) {
            if (entry.getKey() != null && "Link".equalsIgnoreCase(entry.getKey())) {
                for (String headerValue : entry.getValue()) {
                    String next = parseNextLink(headerValue);
                    if (next != null) {
                        return next;
                    }
                }
            }
        }
        return null;
    }

    private static String parseNextLink(String headerValue) {
        if (headerValue == null || headerValue.isBlank()) {
            return null;
        }
        String[] parts = headerValue.split(",");
        for (String part : parts) {
            String trimmed = part.trim();
            if (trimmed.contains("rel=\"next\"")) {
                int start = trimmed.indexOf('<');
                int end = trimmed.indexOf('>');
                if (start >= 0 && end > start) {
                    return trimmed.substring(start + 1, end);
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

    private static String stripTrailingSlash(String value) {
        if (value == null) {
            return null;
        }
        return value.endsWith("/") ? value.substring(0, value.length() - 1) : value;
    }
}

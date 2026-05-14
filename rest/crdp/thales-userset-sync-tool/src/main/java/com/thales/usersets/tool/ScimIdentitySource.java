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
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Set;
import java.util.TreeSet;

final class ScimIdentitySource implements IdentitySource {

    private final String baseUrl;
    private final String bearerToken;
    private final String groupId;
    private final String groupDisplayName;
    private final String userIdAttribute;
    private final int pageSize;

    ScimIdentitySource(
        String baseUrl,
        String bearerToken,
        String groupId,
        String groupDisplayName,
        String userIdAttribute,
        int pageSize) {
        this.baseUrl = stripTrailingSlash(baseUrl);
        this.bearerToken = bearerToken;
        this.groupId = groupId;
        this.groupDisplayName = groupDisplayName;
        this.userIdAttribute = userIdAttribute;
        this.pageSize = pageSize;
    }

    @Override
    public Set<String> loadUsers() throws IOException {
        JsonObject group = groupId != null && !groupId.isBlank() ? fetchGroupById(groupId) : fetchGroupByDisplayName(groupDisplayName);
        Set<String> users = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
        if (group == null) {
            return users;
        }

        JsonArray members = group.has("members") && group.get("members").isJsonArray() ? group.getAsJsonArray("members") : new JsonArray();
        for (JsonElement memberElement : members) {
            if (memberElement == null || !memberElement.isJsonObject()) {
                continue;
            }
            JsonObject member = memberElement.getAsJsonObject();
            String memberType = member.has("type") && !member.get("type").isJsonNull() ? member.get("type").getAsString() : null;
            if (memberType != null && "Group".equalsIgnoreCase(memberType)) {
                continue;
            }
            String identifier = resolveMemberIdentifier(member);
            if (identifier != null && !identifier.isBlank()) {
                users.add(identifier.trim());
            }
        }
        return users;
    }

    @Override
    public String describe() {
        return groupId != null && !groupId.isBlank() ? "scim-group-id:" + groupId : "scim-group-name:" + groupDisplayName;
    }

    private JsonObject fetchGroupById(String id) throws IOException {
        return executeObjectRequest(baseUrl + "/Groups/" + urlEncode(id));
    }

    private JsonObject fetchGroupByDisplayName(String displayName) throws IOException {
        String filter = "displayName eq \"" + escapeScimFilter(displayName) + "\"";
        int startIndex = 1;
        while (true) {
            String url = baseUrl + "/Groups?filter=" + urlEncode(filter) + "&startIndex=" + startIndex + "&count=" + pageSize;
            JsonObject payload = executeObjectRequest(url);
            JsonArray resources = findResources(payload);
            if (resources != null) {
                for (JsonElement resource : resources) {
                    if (resource != null && resource.isJsonObject()) {
                        JsonObject group = resource.getAsJsonObject();
                        if (group.has("displayName") && !group.get("displayName").isJsonNull()
                            && displayName.equalsIgnoreCase(group.get("displayName").getAsString())) {
                            return group;
                        }
                    }
                }
            }

            int itemsPerPage = payload.has("itemsPerPage") ? payload.get("itemsPerPage").getAsInt() : 0;
            int totalResults = payload.has("totalResults") ? payload.get("totalResults").getAsInt() : 0;
            if (itemsPerPage <= 0 || startIndex + itemsPerPage > totalResults) {
                return null;
            }
            startIndex += itemsPerPage;
        }
    }

    private String resolveMemberIdentifier(JsonObject member) {
        if ("display".equalsIgnoreCase(userIdAttribute) && member.has("display") && !member.get("display").isJsonNull()) {
            return member.get("display").getAsString();
        }
        if ("value".equalsIgnoreCase(userIdAttribute) && member.has("value") && !member.get("value").isJsonNull()) {
            return member.get("value").getAsString();
        }
        if (member.has("display") && !member.get("display").isJsonNull()) {
            return member.get("display").getAsString();
        }
        if (member.has("value") && !member.get("value").isJsonNull()) {
            return member.get("value").getAsString();
        }
        return null;
    }

    private JsonObject executeObjectRequest(String url) throws IOException {
        HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection();
        connection.setRequestMethod("GET");
        connection.setRequestProperty("Authorization", "Bearer " + bearerToken);
        connection.setRequestProperty("Accept", "application/scim+json, application/json");

        int responseCode = connection.getResponseCode();
        String responseBody = readBody(connection, responseCode);
        connection.disconnect();
        if (responseCode < 200 || responseCode >= 300) {
            throw new IOException("SCIM request failed: HTTP " + responseCode + " body=" + responseBody);
        }
        return JsonParser.parseString(responseBody).getAsJsonObject();
    }

    private JsonArray findResources(JsonObject payload) {
        if (payload.has("Resources") && payload.get("Resources").isJsonArray()) {
            return payload.getAsJsonArray("Resources");
        }
        if (payload.has("resources") && payload.get("resources").isJsonArray()) {
            return payload.getAsJsonArray("resources");
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

    private static String urlEncode(String value) throws IOException {
        return URLEncoder.encode(value, StandardCharsets.UTF_8.name());
    }

    private static String escapeScimFilter(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}

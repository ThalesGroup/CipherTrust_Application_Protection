package com.thales.usersets;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.RandomAccessFile;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

/*
 * This app provides a number of different helper methods dealing with CM Application Data Protection UserSets.  There is a method to find
 * a user in a userset and another method to populate the userset from a flat file.  Usersets are typically used within
 * an access policy but they are not restricted to that usage.
 * Was tested with CM 2.14
 * Note: This source code is only to be used for testing and proof of concepts.
 * @author mwarner
 *
 */
public class CMUserSetHelper {

    static String hostnamevalidate = "yourhostname";
    static boolean debug = true;
    static int CHUNKSIZEMAX = 100;

    private final boolean debugEnabled;
    private final String apiBaseUserSets;

    String usersetid = "716f01a6-5cab-4799-925a-6dc2d8712fc1";
    String cmIP = "yourip";
    String apiUrlGetUsers = "https://" + cmIP + "/api/v1/data-protection/user-sets/" + usersetid + "/users";
    String addusertouserset = "https://" + cmIP + "/api/v1/data-protection/user-sets/" + usersetid + "/users";
    String authUrl = "https://" + cmIP + "/api/v1/auth/tokens";

    int totalrecords = 0;
    int chunksize = 5;

    public CMUserSetHelper(String usersetid, String cmIP) {
        this(usersetid, cmIP, false);
    }

    public CMUserSetHelper(String usersetid, String cmIP, boolean debugEnabled) {
        this.usersetid = usersetid;
        this.cmIP = cmIP;
        this.apiBaseUserSets = "https://" + cmIP + "/api/v1/data-protection/user-sets";
        this.apiUrlGetUsers = apiBaseUserSets + "/" + usersetid + "/users";
        this.addusertouserset = apiUrlGetUsers;
        this.authUrl = "https://" + cmIP + "/api/v1/auth/tokens";
        this.debugEnabled = debugEnabled;
    }

    public static void main(String[] args) throws Exception {
        String username = args[0];
        String password = args[1];
        String cmip = args[2];
        String usersetid = args[3];
        String filePath = args[4];
        CMUserSetHelper cmusersetHelper = new CMUserSetHelper(usersetid, cmip);
        int totalrecords = 0;

        String jwthtoken = geAuthToken(cmusersetHelper.authUrl, username, password);
        String newtoken = "Bearer " + removeQuotes(jwthtoken);

        RandomAccessFile file = new RandomAccessFile(filePath, "r");
        if (cmusersetHelper.chunksize > CHUNKSIZEMAX) {
            cmusersetHelper.chunksize = CHUNKSIZEMAX;
        }
        int totalNumberOfRecords = numberOfLines(file);
        if (cmusersetHelper.chunksize > totalNumberOfRecords) {
            cmusersetHelper.chunksize = Math.max(1, totalNumberOfRecords / 2);
        }

        totalrecords = cmusersetHelper.addAUserToUserSetFromFile(cmusersetHelper.addusertouserset, newtoken, filePath);
        System.out.println("Totalrecords inserted into Userset  " + cmusersetHelper.usersetid + " = " + totalrecords);
    }

    public boolean findUserInUserSet(String user, String newtoken) throws CustomException {
        boolean found = false;
        try {
            Set<String> currentUsers = getUsersInUserSet(newtoken);
            String normalizedUser = normalizeUser(user);
            for (String currentUser : currentUsers) {
                if (normalizedUser.equalsIgnoreCase(currentUser)) {
                    found = true;
                    break;
                }
            }
        } catch (IOException e) {
            if (e.getMessage() != null && e.getMessage().contains("403")) {
                throw new CustomException("1002, User Not in Application Data Protection Clients ", 1002);
            }
            throw new CustomException(e.getMessage(), 1001);
        }
        return found;
    }

    public boolean findUserInUserSet(String user, String cmUser, String cmPassword) throws Exception {
        String jwtToken = geAuthToken(this.authUrl, cmUser, cmPassword);
        String bearerToken = "Bearer " + removeQuotes(jwtToken);
        return findUserInUserSet(user, bearerToken);
    }

    public String getBearerToken(String cmUser, String cmPassword) throws Exception {
        return "Bearer " + removeQuotes(geAuthToken(this.authUrl, cmUser, cmPassword));
    }

    public Set<String> getUsersInUserSet(String newtoken) throws IOException {
        String response = executeRequest("POST", this.apiUrlGetUsers, newtoken, null);
        if (debugEnabled) {
            System.out.println("userset response " + response);
        }
        return parseUsers(response);
    }

    public List<UserSetSummary> listUserSets(String newtoken) throws IOException {
        String response = executeRequest("GET", apiBaseUserSets, newtoken, null);
        if (debugEnabled) {
            System.out.println("list usersets response " + response);
        }
        return parseUserSetSummaries(response);
    }

    public UserSetSummary findUserSetByName(String userSetName, String newtoken) throws IOException {
        String normalizedName = normalizeName(userSetName);
        for (UserSetSummary summary : listUserSets(newtoken)) {
            if (normalizedName.equalsIgnoreCase(normalizeName(summary.getName()))) {
                return summary;
            }
        }
        return null;
    }

    public UserSetSummary createUserSet(String userSetName, String description, String newtoken) throws IOException {
        JsonObject payload = new JsonObject();
        payload.addProperty("name", userSetName);
        if (description != null && !description.isBlank()) {
            payload.addProperty("description", description);
        }
        String response = executeRequest("POST", apiBaseUserSets, newtoken, payload.toString());
        if (debugEnabled) {
            System.out.println("create userset response " + response);
        }

        UserSetSummary created = parseSingleUserSetSummary(response);
        if (created != null && created.getId() != null) {
            return created;
        }

        UserSetSummary lookedUp = findUserSetByName(userSetName, newtoken);
        if (lookedUp != null) {
            return lookedUp;
        }
        throw new IOException("Unable to resolve newly created user set: " + userSetName);
    }

    public UserSetSummary ensureUserSetExists(String userSetName, String description, String newtoken) throws IOException {
        UserSetSummary existing = findUserSetByName(userSetName, newtoken);
        if (existing != null) {
            return existing;
        }
        return createUserSet(userSetName, description, newtoken);
    }

    public UserSetSyncResult previewSyncUsers(Set<String> desiredUsers, String newtoken) throws IOException {
        Set<String> normalizedDesiredUsers = normalizeUsers(desiredUsers);
        Set<String> currentUsers = getUsersInUserSet(newtoken);

        Set<String> toAdd = new LinkedHashSet<>(normalizedDesiredUsers);
        toAdd.removeAll(currentUsers);

        Set<String> toRemove = new LinkedHashSet<>(currentUsers);
        toRemove.removeAll(normalizedDesiredUsers);

        return new UserSetSyncResult(this.usersetid, null, currentUsers, normalizedDesiredUsers, toAdd, toRemove, false, false);
    }

    public UserSetSyncResult syncUsers(Set<String> desiredUsers, String newtoken) throws IOException {
        UserSetSyncResult preview = previewSyncUsers(desiredUsers, newtoken);
        if (!preview.getUsersToRemove().isEmpty()) {
            removeUsersFromUserSet(preview.getUsersToRemove(), newtoken);
        }
        if (!preview.getUsersToAdd().isEmpty()) {
            addUsersToUserSet(preview.getUsersToAdd(), newtoken);
        }
        return new UserSetSyncResult(
            preview.getUserSetId(),
            preview.getUserSetName(),
            preview.getCurrentUsers(),
            preview.getDesiredUsers(),
            preview.getUsersToAdd(),
            preview.getUsersToRemove(),
            !preview.getUsersToAdd().isEmpty() || !preview.getUsersToRemove().isEmpty(),
            false
        );
    }

    public UserSetSyncResult syncUsersFromFile(String filePath, String newtoken) throws IOException {
        return syncUsers(readDistinctUsersFromFile(filePath), newtoken);
    }

    public UserSetSyncResult syncUsersToNamedUserSet(String userSetName, String description, Set<String> desiredUsers, String newtoken)
        throws IOException {
        UserSetSummary summary = ensureUserSetExists(userSetName, description, newtoken);
        CMUserSetHelper targetHelper = new CMUserSetHelper(summary.getId(), this.cmIP, this.debugEnabled);
        UserSetSyncResult result = targetHelper.syncUsers(desiredUsers, newtoken);
        return new UserSetSyncResult(
            summary.getId(),
            summary.getName(),
            result.getCurrentUsers(),
            result.getDesiredUsers(),
            result.getUsersToAdd(),
            result.getUsersToRemove(),
            result.isChanged(),
            result.isCreated()
        );
    }

    public UserSetSyncResult ensureAndSyncUsersToNamedUserSet(String userSetName, String description, Set<String> desiredUsers, String newtoken)
        throws IOException {
        UserSetSummary existing = findUserSetByName(userSetName, newtoken);
        boolean created = false;
        UserSetSummary summary = existing;
        if (summary == null) {
            summary = createUserSet(userSetName, description, newtoken);
            created = true;
        }
        CMUserSetHelper targetHelper = new CMUserSetHelper(summary.getId(), this.cmIP, this.debugEnabled);
        UserSetSyncResult result = targetHelper.syncUsers(desiredUsers, newtoken);
        return new UserSetSyncResult(
            summary.getId(),
            summary.getName(),
            result.getCurrentUsers(),
            result.getDesiredUsers(),
            result.getUsersToAdd(),
            result.getUsersToRemove(),
            result.isChanged(),
            created
        );
    }

    public int addAUserToUserSetFromFile(String url, String newtoken, String filePath) throws IOException {
        int totalNumberOfRecords = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            int count = 0;
            StringBuilder payloadBuilder = new StringBuilder();
            payloadBuilder.append("{\"users\": [");

            while ((line = br.readLine()) != null) {
                String normalizedLine = normalizeUser(line);
                if (normalizedLine.isBlank()) {
                    continue;
                }
                totalNumberOfRecords++;
                payloadBuilder.append("\"").append(escapeJson(normalizedLine)).append("\",");
                count++;

                if (count == chunksize) {
                    makeCMCall(payloadBuilder, newtoken, url);
                    payloadBuilder = new StringBuilder("{\"users\": [");
                    count = 0;
                }
            }

            if (count > 0) {
                payloadBuilder.deleteCharAt(payloadBuilder.length() - 1);
                payloadBuilder.append("}");
                makeCMCall(payloadBuilder, newtoken, url);
                if (debugEnabled) {
                    System.out.println(payloadBuilder.toString());
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        return totalNumberOfRecords;
    }

    public static int makeCMCall(StringBuilder payloadBuilder, String newtoken, String url) throws IOException {
        payloadBuilder.deleteCharAt(payloadBuilder.length() - 1);
        payloadBuilder.append("]}");
        if (debug) {
            System.out.println(payloadBuilder.toString());
        }
        String payload = payloadBuilder.toString();

        URL apiUrl = new URL(url);
        HttpURLConnection connection = (HttpURLConnection) apiUrl.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        connection.setRequestProperty("Authorization", newtoken);

        OutputStream outputStream = connection.getOutputStream();
        outputStream.write(payload.getBytes(StandardCharsets.UTF_8));
        outputStream.flush();
        outputStream.close();

        int responseCode = connection.getResponseCode();
        String responseBody = readResponseBody(connection, responseCode);

        if (debug) {
            System.out.println("Response Code: " + responseCode);
            System.out.println("Response Body: " + responseBody);
        }
        connection.disconnect();
        return responseCode;
    }

    public static int addAUserToUserSet(String url, String newtoken) throws IOException {
        String payload = "{\"users\": [\"akhip@company.com\",\"user2@company.com\"]}";

        URL apiUrl = new URL(url);
        HttpURLConnection connection = (HttpURLConnection) apiUrl.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        connection.setRequestProperty("Authorization", newtoken);

        OutputStream outputStream = connection.getOutputStream();
        outputStream.write(payload.getBytes(StandardCharsets.UTF_8));
        outputStream.flush();
        outputStream.close();

        int responseCode = connection.getResponseCode();
        String responseBody = readResponseBody(connection, responseCode);

        if (debug) {
            System.out.println("Response Code: " + responseCode);
            System.out.println("Response Body: " + responseBody);
        }
        connection.disconnect();
        return responseCode;
    }

    public static String removeQuotes(String input) {
        return input == null ? null : input.replace("\"", "");
    }

    private static int numberOfLines(RandomAccessFile file) throws IOException {
        int numberOfLines = 0;
        while (file.readLine() != null) {
            numberOfLines++;
        }
        file.seek(0);
        return numberOfLines;
    }

    public static String geAuthToken(String apiUrl, String usernb, String pwd) throws Exception {
        String jStr = "{\"username\":\"" + usernb + "\",\"password\":\"" + pwd + "\"}";
        disableCertValidation();

        String jwtstr = null;
        try {
            URL url = new URL(apiUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestProperty("Content-length", String.valueOf(jStr.length()));
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestMethod("POST");
            connection.setDoOutput(true);
            connection.setDoInput(true);
            DataOutputStream output = new DataOutputStream(connection.getOutputStream());
            output.writeBytes(jStr);
            output.close();

            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream(), StandardCharsets.UTF_8));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();

            JsonObject input = null;
            JsonElement jwt = null;
            JsonElement rootNode = JsonParser.parseString(response.toString()).getAsJsonObject();
            if (rootNode.isJsonObject()) {
                input = rootNode.getAsJsonObject();
                if (input.isJsonObject()) {
                    jwt = input.get("jwt");
                }
            }
            JsonPrimitive column = jwt.getAsJsonPrimitive();
            jwtstr = column.getAsJsonPrimitive().toString();
            connection.disconnect();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return jwtstr;
    }

    public static String geAuthToken(String apiUrl) throws Exception {
        String userName = System.getenv("CMUSER");
        String password = System.getenv("CMPWD");
        String jStr = "{\"username\":\"" + userName + "\",\"password\":\"" + password + "\"}";

        disableCertValidation();

        String jwtstr = null;
        try {
            URL url = new URL(apiUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestProperty("Content-length", String.valueOf(jStr.length()));
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestMethod("GET");
            connection.setDoOutput(true);
            connection.setDoInput(true);
            DataOutputStream output = new DataOutputStream(connection.getOutputStream());
            output.writeBytes(jStr);
            output.close();
            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream(), StandardCharsets.UTF_8));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();
            if (debug) {
                System.out.println("response " + response);
            }
            JsonObject input = null;
            JsonElement jwt = null;
            JsonElement rootNode = JsonParser.parseString(response.toString()).getAsJsonObject();
            if (rootNode.isJsonObject()) {
                input = rootNode.getAsJsonObject();
                if (input.isJsonObject()) {
                    jwt = input.get("jwt");
                }
            }
            JsonPrimitive column = jwt.getAsJsonPrimitive();
            jwtstr = column.getAsJsonPrimitive().toString();
            connection.disconnect();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return jwtstr;
    }

    public static void disableCertValidation() throws Exception {
        TrustManager[] trustAllCerts = new TrustManager[] { new X509TrustManager() {
            public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                return null;
            }

            public void checkClientTrusted(java.security.cert.X509Certificate[] certs, String authType) {
            }

            public void checkServerTrusted(java.security.cert.X509Certificate[] certs, String authType) {
            }
        } };

        try {
            SSLContext sc = SSLContext.getInstance("SSL");
            sc.init(null, trustAllCerts, new java.security.SecureRandom());
            HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
        } catch (Exception e) {
            e.printStackTrace();
        }

        HostnameVerifier allHostsValid = new HostnameVerifier() {
            public boolean verify(String hostname, SSLSession session) {
                return true;
            }
        };
        HttpsURLConnection.setDefaultHostnameVerifier(allHostsValid);
    }

    private void addUsersToUserSet(Set<String> usersToAdd, String newtoken) throws IOException {
        if (usersToAdd == null || usersToAdd.isEmpty()) {
            return;
        }
        for (List<String> batch : chunk(usersToAdd, Math.max(1, Math.min(this.chunksize, CHUNKSIZEMAX)))) {
            JsonObject payload = new JsonObject();
            JsonArray users = new JsonArray();
            for (String user : batch) {
                users.add(user);
            }
            payload.add("users", users);
            executeRequest("POST", this.addusertouserset, newtoken, payload.toString());
        }
    }

    private void removeUsersFromUserSet(Set<String> usersToRemove, String newtoken) throws IOException {
        if (usersToRemove == null || usersToRemove.isEmpty()) {
            return;
        }
        for (List<String> batch : chunk(usersToRemove, Math.max(1, Math.min(this.chunksize, CHUNKSIZEMAX)))) {
            JsonObject payload = new JsonObject();
            JsonArray users = new JsonArray();
            for (String user : batch) {
                users.add(user);
            }
            payload.add("users", users);
            executeRequest("DELETE", this.addusertouserset, newtoken, payload.toString());
        }
    }

    private String executeRequest(String method, String url, String newtoken, String payload) throws IOException {
        disableCertValidationSafely();
        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection) new URL(removeQuotes(url)).openConnection();
            connection.setRequestMethod(method);
            connection.setRequestProperty("Authorization", newtoken);
            connection.setRequestProperty("accept", "application/json");
            connection.setRequestProperty("Content-Type", "application/json");

            if (payload != null) {
                connection.setDoOutput(true);
                try (OutputStream outputStream = connection.getOutputStream()) {
                    outputStream.write(payload.getBytes(StandardCharsets.UTF_8));
                }
            }

            int responseCode = connection.getResponseCode();
            String responseBody = readResponseBody(connection, responseCode);
            if (debugEnabled) {
                System.out.println("CM " + method + " " + url + " -> " + responseCode);
                if (!responseBody.isBlank()) {
                    System.out.println(responseBody);
                }
            }
            if (responseCode < 200 || responseCode >= 300) {
                throw new IOException("HTTP " + responseCode + " calling " + url + " body=" + responseBody);
            }
            return responseBody;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    private static String readResponseBody(HttpURLConnection connection, int responseCode) throws IOException {
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

    private Set<String> parseUsers(String response) {
        if (response == null || response.isBlank()) {
            return Collections.emptySet();
        }
        JsonElement root = JsonParser.parseString(response);
        JsonArray users = findArray(root, "users", "items");
        if (users == null && root.isJsonArray()) {
            users = root.getAsJsonArray();
        }
        Set<String> parsedUsers = new LinkedHashSet<>();
        if (users == null) {
            return parsedUsers;
        }
        for (JsonElement userElement : users) {
            if (userElement == null || userElement.isJsonNull()) {
                continue;
            }
            if (userElement.isJsonPrimitive()) {
                String user = normalizeUser(userElement.getAsString());
                if (!user.isBlank()) {
                    parsedUsers.add(user);
                }
            } else if (userElement.isJsonObject()) {
                String user = firstNonBlank(
                    extractString(userElement.getAsJsonObject(), "user"),
                    extractString(userElement.getAsJsonObject(), "username"),
                    extractString(userElement.getAsJsonObject(), "name"),
                    extractString(userElement.getAsJsonObject(), "principal")
                );
                user = normalizeUser(user);
                if (!user.isBlank()) {
                    parsedUsers.add(user);
                }
            }
        }
        return parsedUsers;
    }

    private List<UserSetSummary> parseUserSetSummaries(String response) {
        if (response == null || response.isBlank()) {
            return Collections.emptyList();
        }
        JsonElement root = JsonParser.parseString(response);
        JsonArray items = findArray(root, "resources", "items", "user_sets");
        if (items == null && root.isJsonArray()) {
            items = root.getAsJsonArray();
        }
        List<UserSetSummary> summaries = new ArrayList<>();
        if (items == null) {
            UserSetSummary single = parseSingleUserSetSummary(response);
            if (single != null) {
                summaries.add(single);
            }
            return summaries;
        }
        for (JsonElement item : items) {
            if (item != null && item.isJsonObject()) {
                UserSetSummary summary = parseUserSetSummary(item.getAsJsonObject());
                if (summary != null) {
                    summaries.add(summary);
                }
            }
        }
        return summaries;
    }

    private UserSetSummary parseSingleUserSetSummary(String response) {
        if (response == null || response.isBlank()) {
            return null;
        }
        JsonElement root = JsonParser.parseString(response);
        if (root.isJsonObject()) {
            return parseUserSetSummary(root.getAsJsonObject());
        }
        return null;
    }

    private UserSetSummary parseUserSetSummary(JsonObject jsonObject) {
        if (jsonObject == null) {
            return null;
        }
        String id = firstNonBlank(
            extractString(jsonObject, "id"),
            extractString(jsonObject, "uuid")
        );
        String name = extractString(jsonObject, "name");
        String description = extractString(jsonObject, "description");
        if ((id == null || id.isBlank()) && (name == null || name.isBlank())) {
            return null;
        }
        return new UserSetSummary(id, name, description);
    }

    private JsonArray findArray(JsonElement root, String... candidateKeys) {
        if (root == null || root.isJsonNull()) {
            return null;
        }
        if (root.isJsonObject()) {
            JsonObject object = root.getAsJsonObject();
            for (String key : candidateKeys) {
                JsonElement value = object.get(key);
                if (value != null && value.isJsonArray()) {
                    return value.getAsJsonArray();
                }
            }
            for (String key : candidateKeys) {
                JsonElement value = object.get(key);
                if (value != null) {
                    JsonArray nested = findArray(value, candidateKeys);
                    if (nested != null) {
                        return nested;
                    }
                }
            }
        }
        return null;
    }

    private static String extractString(JsonObject object, String key) {
        if (object == null || key == null || !object.has(key) || object.get(key).isJsonNull()) {
            return null;
        }
        return object.get(key).getAsString();
    }

    private static Set<String> readDistinctUsersFromFile(String filePath) throws IOException {
        Set<String> users = new LinkedHashSet<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String normalized = normalizeUser(line);
                if (!normalized.isBlank()) {
                    users.add(normalized);
                }
            }
        }
        return users;
    }

    private static Set<String> normalizeUsers(Set<String> users) {
        Set<String> normalized = new LinkedHashSet<>();
        if (users == null) {
            return normalized;
        }
        for (String user : users) {
            String normalizedUser = normalizeUser(user);
            if (!normalizedUser.isBlank()) {
                normalized.add(normalizedUser);
            }
        }
        return normalized;
    }

    private static String normalizeUser(String user) {
        return user == null ? "" : user.trim();
    }

    private static String normalizeName(String name) {
        return name == null ? "" : name.trim();
    }

    private static String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }
        return null;
    }

    private static List<List<String>> chunk(Set<String> users, int chunkSize) {
        List<List<String>> chunks = new ArrayList<>();
        List<String> current = new ArrayList<>(chunkSize);
        for (String user : users) {
            current.add(user);
            if (current.size() == chunkSize) {
                chunks.add(new ArrayList<>(current));
                current.clear();
            }
        }
        if (!current.isEmpty()) {
            chunks.add(new ArrayList<>(current));
        }
        return chunks;
    }

    private static String escapeJson(String input) {
        return input
            .replace("\\", "\\\\")
            .replace("\"", "\\\"");
    }

    private static void disableCertValidationSafely() throws IOException {
        try {
            disableCertValidation();
        } catch (Exception e) {
            throw new IOException("Unable to initialize TLS configuration", e);
        }
    }

    public static final class UserSetSummary {
        private final String id;
        private final String name;
        private final String description;

        public UserSetSummary(String id, String name, String description) {
            this.id = id;
            this.name = name;
            this.description = description;
        }

        public String getId() {
            return id;
        }

        public String getName() {
            return name;
        }

        public String getDescription() {
            return description;
        }
    }

    public static final class UserSetSyncResult {
        private final String userSetId;
        private final String userSetName;
        private final Set<String> currentUsers;
        private final Set<String> desiredUsers;
        private final Set<String> usersToAdd;
        private final Set<String> usersToRemove;
        private final boolean changed;
        private final boolean created;

        public UserSetSyncResult(
            String userSetId,
            String userSetName,
            Set<String> currentUsers,
            Set<String> desiredUsers,
            Set<String> usersToAdd,
            Set<String> usersToRemove,
            boolean changed,
            boolean created) {
            this.userSetId = userSetId;
            this.userSetName = userSetName;
            this.currentUsers = Collections.unmodifiableSet(new LinkedHashSet<>(Objects.requireNonNullElse(currentUsers, Collections.emptySet())));
            this.desiredUsers = Collections.unmodifiableSet(new LinkedHashSet<>(Objects.requireNonNullElse(desiredUsers, Collections.emptySet())));
            this.usersToAdd = Collections.unmodifiableSet(new LinkedHashSet<>(Objects.requireNonNullElse(usersToAdd, Collections.emptySet())));
            this.usersToRemove = Collections.unmodifiableSet(new LinkedHashSet<>(Objects.requireNonNullElse(usersToRemove, Collections.emptySet())));
            this.changed = changed;
            this.created = created;
        }

        public String getUserSetId() {
            return userSetId;
        }

        public String getUserSetName() {
            return userSetName;
        }

        public Set<String> getCurrentUsers() {
            return currentUsers;
        }

        public Set<String> getDesiredUsers() {
            return desiredUsers;
        }

        public Set<String> getUsersToAdd() {
            return usersToAdd;
        }

        public Set<String> getUsersToRemove() {
            return usersToRemove;
        }

        public boolean isChanged() {
            return changed;
        }

        public boolean isCreated() {
            return created;
        }
    }
}

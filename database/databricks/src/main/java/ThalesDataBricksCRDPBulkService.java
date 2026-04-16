import java.io.IOException;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public final class ThalesDataBricksCRDPBulkService {

    private static final MediaType JSON = MediaType.parse("application/json");
    private static final Gson GSON = new Gson();
    private static final OkHttpClient CLIENT = new OkHttpClient.Builder().build();
    private static final Object REVEAL_CACHE_LOCK = new Object();
    private static Map<String, String> revealCache = new LinkedHashMap<>();
    private static int revealCacheMaxSize = -1;

    private final ThalesDataBricksUdfConfig config;

    /*
     * CRDP v1 protectbulk/revealbulk accepts a single protection policy per call,
     * so batching is done for values that share the same resolved column/profile.
     * It is not intended to send mixed-profile values from an entire row in one
     * request.
     */
    public ThalesDataBricksCRDPBulkService() {
        this(ThalesDataBricksUdfConfig.load());
    }

    public ThalesDataBricksCRDPBulkService(ThalesDataBricksUdfConfig config) {
        this.config = config;
    }

    public static void main(String[] args) throws Exception {
        ThalesDataBricksCRDPBulkService service = new ThalesDataBricksCRDPBulkService();

        List<String> values = List.of(
                "alice@example.com",
                "bob@example.com",
                "carol@example.com");

        List<String> protectedValues = service.protectValues(values, "char", "email");
        System.out.println("Protected values: " + protectedValues);

        List<String> revealedValues = service.revealValues(protectedValues, "char", "email");
        System.out.println("Revealed values: " + revealedValues);
        
        service.protectValues(values, "char");
        System.out.println("Protected values 2 part signature : " + protectedValues);
        
        service.revealValues(values, "char");
        System.out.println("Revealed values: 2 part signature " + revealedValues);
        
    }

    public String transformValue(String value, String mode, String dataType) throws Exception {
        return transformValue(value, mode, null, dataType);
    }

    public String transformValue(String value, String mode, String columnName, String dataType) throws Exception {
        return transformValue(value, mode, columnName, dataType, null);
    }

    public String transformValue(
            String value,
            String mode,
            String columnName,
            String dataType,
            String revealUser) throws Exception {
        List<String> results = transformValues(Collections.singletonList(value), mode, columnName, dataType, revealUser);
        return results.isEmpty() ? value : results.get(0);
    }

    public List<String> transformValues(List<String> values, String mode, String columnName, String dataType) throws Exception {
        return transformValues(values, mode, columnName, dataType, null);
    }

    public List<String> transformValues(
            List<String> values,
            String mode,
            String columnName,
            String dataType,
            String revealUser) throws Exception {
        if (values == null || values.isEmpty()) {
            return List.of();
        }

        String normalizedMode = normalizeMode(mode);
        ColumnRuntimeConfig runtimeConfig = resolveColumnConfig(columnName, dataType, normalizedMode, revealUser);
        List<String> results = new ArrayList<>(values.size());
        int batchSize = this.config.getBatchSize();

        for (int start = 0; start < values.size(); start += batchSize) {
            int end = Math.min(start + batchSize, values.size());
            processChunk(values.subList(start, end), results, normalizedMode, runtimeConfig, dataType);
        }
        return results;
    }

    public List<String> protectValues(List<String> values, String dataType) throws Exception {
        return protectValues(values, dataType, null);
    }

    public List<String> protectValues(List<String> values, String dataType, String columnName) throws Exception {
        return transformValues(values, "protect", columnName, dataType);
    }

    public List<String> revealValues(List<String> values, String dataType) throws Exception {
        return revealValues(values, dataType, null);
    }

    public List<String> revealValues(List<String> values, String dataType, String columnName) throws Exception {
        return transformValues(values, "reveal", columnName, dataType);
    }

    public List<String> revealValues(List<String> values, String dataType, String columnName, String revealUser) throws Exception {
        return transformValues(values, "reveal", columnName, dataType, revealUser);
    }

    private void processChunk(
            List<String> rawChunk,
            List<String> destination,
            String mode,
            ColumnRuntimeConfig runtimeConfig,
            String dataType) throws Exception {

        List<String> requestPayload = new ArrayList<>();
        List<Integer> requestIndexes = new ArrayList<>();

        for (String originalValue : rawChunk) {
            if (!shouldCallApi(originalValue, dataType)) {
                destination.add(originalValue);
                continue;
            }

            requestIndexes.add(destination.size());
            destination.add(originalValue);
            requestPayload.add(originalValue);
        }

        if (requestPayload.isEmpty()) {
            return;
        }

        List<String> transformedValues;
        try {
            transformedValues = "reveal".equals(mode)
                    ? revealChunk(requestPayload, runtimeConfig)
                    : protectChunk(requestPayload, runtimeConfig);
        } catch (Exception ex) {
            if (shouldReturnOriginalValues(ex)) {
                return;
            }
            throw ex;
        }

        if (transformedValues.size() != requestIndexes.size()) {
            throw new IllegalStateException("Unexpected " + mode + "bulk response size. expected="
                    + requestIndexes.size() + " actual=" + transformedValues.size());
        }

        for (int i = 0; i < transformedValues.size(); i++) {
            destination.set(requestIndexes.get(i), transformedValues.get(i));
        }
    }

    private List<String> protectChunk(List<String> values, ColumnRuntimeConfig runtimeConfig) throws Exception {
        JsonObject payload = new JsonObject();
        payload.addProperty("protection_policy_name", runtimeConfig.policyName);

        JsonArray dataArray = new JsonArray();
        for (String value : values) {
            dataArray.add(value);
        }
        payload.add("data_array", dataArray);

        JsonObject response = execute("/v1/protectbulk", payload);
        JsonArray protectedDataArray = response.getAsJsonArray("protected_data_array");
        if (protectedDataArray == null) {
            throw new IllegalStateException("protectbulk response did not include protected_data_array.");
        }

        List<String> protectedValues = new ArrayList<>(protectedDataArray.size());
        for (JsonElement element : protectedDataArray) {
            JsonObject item = element.getAsJsonObject();
            String protectedValue = getRequiredString(item, "protected_data");
            if ("external".equals(runtimeConfig.policyType) && item.has("external_version")) {
                runtimeConfig.metadata = item.get("external_version").getAsString();
            }
            protectedValues.add(protectedValue);
        }
        return protectedValues;
    }

    private List<String> revealChunk(List<String> values, ColumnRuntimeConfig runtimeConfig) throws Exception {
        if (this.config.isRevealCacheEnabled()) {
            return revealChunkWithCache(values, runtimeConfig);
        }

        JsonObject payload = new JsonObject();
        payload.addProperty("protection_policy_name", runtimeConfig.policyName);
        payload.addProperty("username", runtimeConfig.revealUser);

        JsonArray protectedDataArray = new JsonArray();
        for (String value : values) {
            JsonObject item = new JsonObject();
            item.addProperty("protected_data", value);
            if ("external".equals(runtimeConfig.policyType)) {
                item.addProperty("external_version", runtimeConfig.metadata);
            }
            protectedDataArray.add(item);
        }
        payload.add("protected_data_array", protectedDataArray);

        JsonObject response = execute("/v1/revealbulk", payload);
        JsonArray dataArray = response.getAsJsonArray("data_array");
        if (dataArray == null) {
            throw new IllegalStateException("revealbulk response did not include data_array.");
        }

        List<String> revealedValues = new ArrayList<>(dataArray.size());
        for (JsonElement element : dataArray) {
            JsonObject item = element.getAsJsonObject();
            revealedValues.add(getRequiredString(item, "data"));
        }
        return revealedValues;
    }

    private List<String> revealChunkWithCache(List<String> values, ColumnRuntimeConfig runtimeConfig) throws Exception {
        ensureRevealCacheConfigured();

        List<String> revealedValues = new ArrayList<>(Collections.nCopies(values.size(), null));
        List<String> uncachedValues = new ArrayList<>();
        List<Integer> uncachedIndexes = new ArrayList<>();

        for (int i = 0; i < values.size(); i++) {
            String value = values.get(i);
            String cacheKey = buildRevealCacheKey(value, runtimeConfig);
            String cachedValue = getCachedReveal(cacheKey);
            if (cachedValue != null) {
                revealedValues.set(i, cachedValue);
            } else {
                uncachedValues.add(value);
                uncachedIndexes.add(i);
            }
        }

        if (!uncachedValues.isEmpty()) {
            List<String> uncachedResults = revealChunkWithoutCache(uncachedValues, runtimeConfig);
            for (int i = 0; i < uncachedResults.size(); i++) {
                int targetIndex = uncachedIndexes.get(i);
                String cipherText = uncachedValues.get(i);
                String plainText = uncachedResults.get(i);
                revealedValues.set(targetIndex, plainText);
                putCachedReveal(buildRevealCacheKey(cipherText, runtimeConfig), plainText);
            }
        }

        return revealedValues;
    }

    private List<String> revealChunkWithoutCache(List<String> values, ColumnRuntimeConfig runtimeConfig) throws Exception {
        JsonObject payload = new JsonObject();
        payload.addProperty("protection_policy_name", runtimeConfig.policyName);
        payload.addProperty("username", runtimeConfig.revealUser);

        JsonArray protectedDataArray = new JsonArray();
        for (String value : values) {
            JsonObject item = new JsonObject();
            item.addProperty("protected_data", value);
            if ("external".equals(runtimeConfig.policyType)) {
                item.addProperty("external_version", runtimeConfig.metadata);
            }
            protectedDataArray.add(item);
        }
        payload.add("protected_data_array", protectedDataArray);

        JsonObject response = execute("/v1/revealbulk", payload);
        JsonArray dataArray = response.getAsJsonArray("data_array");
        if (dataArray == null) {
            throw new IllegalStateException("revealbulk response did not include data_array.");
        }

        List<String> revealedValues = new ArrayList<>(dataArray.size());
        for (JsonElement element : dataArray) {
            JsonObject item = element.getAsJsonObject();
            revealedValues.add(getRequiredString(item, "data"));
        }
        return revealedValues;
    }

    private JsonObject execute(String path, JsonObject payload) throws Exception {
        String url = buildUrl(path);
        Request request = new Request.Builder()
                .url(url)
                .method("POST", RequestBody.create(JSON, payload.toString()))
                .addHeader("Content-Type", "application/json")
                .build();

        try (Response response = CLIENT.newCall(request).execute()) {
            String responseBody = response.body() == null ? "" : response.body().string();
            if (!response.isSuccessful()) {
                throw new RuntimeException("CRDP request failed. url=" + url
                        + ", status=" + response.code()
                        + ", body=" + responseBody);
            }
            return GSON.fromJson(responseBody, JsonObject.class);
        } catch (IOException ex) {
            if (this.config.isReturnCiphertextForUnauthorizedEnabled()
                    && containsAny(ex.getMessage(), "1401", "1001", "1002")) {
                throw new RuntimeException("CRDP authorization failed.", ex);
            }
            throw ex;
        }
    }

    private ColumnRuntimeConfig resolveColumnConfig(String columnName, String dataType, String mode, String revealUser) {
        return new ColumnRuntimeConfig(
                columnName,
                this.config.resolvePolicyName(columnName, dataType, mode),
                this.config.resolvePolicyType(columnName, dataType, mode),
                this.config.resolveMetadata(columnName),
                this.config.resolveRevealUser(columnName, revealUser));
    }

    private boolean shouldCallApi(String value, String dataType) {
        if (value == null || value.trim().isEmpty() || value.trim().length() < 2) {
            return false;
        }

        String normalizedType = dataType == null ? "char" : dataType.trim().toLowerCase(Locale.ROOT);
        if ("char".equals(normalizedType)) {
            return true;
        }

        String normalizedValue = normalizeNumericCandidate(value);
        if (normalizedValue == null) {
            return false;
        }

        try {
            BigInteger number = new BigInteger(normalizedValue);
            return number.compareTo(BigInteger.valueOf(-9)) < 0 || number.compareTo(BigInteger.valueOf(-1)) > 0;
        } catch (NumberFormatException ex) {
            return false;
        }
    }

    private String buildUrl(String path) {
        String host = this.config.getCrdpIp();
        if (host.startsWith("http://") || host.startsWith("https://")) {
            return host + ":" + this.config.getCrdpPort() + path;
        }
        return "http://" + host + ":" + this.config.getCrdpPort() + path;
    }

    private static String getRequiredString(JsonObject object, String key) {
        if (object == null || !object.has(key)) {
            throw new IllegalStateException("CRDP response item missing key: " + key);
        }
        return object.get(key).getAsString();
    }

    private static String normalizeMode(String mode) {
        if (mode == null || mode.isBlank()) {
            return "protect";
        }
        return "reveal".equalsIgnoreCase(mode.trim()) ? "reveal" : "protect";
    }

    private static boolean containsAny(String source, String... values) {
        if (source == null) {
            return false;
        }
        for (String value : values) {
            if (source.contains(value)) {
                return true;
            }
        }
        return false;
    }

    private static String normalizeNumericCandidate(String value) {
        if (value == null) {
            return null;
        }

        String trimmed = value.trim();
        if (trimmed.isEmpty()) {
            return null;
        }

        StringBuilder digits = new StringBuilder(trimmed.length());
        boolean seenDigit = false;
        for (int i = 0; i < trimmed.length(); i++) {
            char current = trimmed.charAt(i);
            if (Character.isDigit(current)) {
                digits.append(current);
                seenDigit = true;
            } else if (current == '-' && !seenDigit && digits.length() == 0) {
                digits.append(current);
            } else if (current == '+' && !seenDigit && digits.length() == 0) {
                continue;
            }
        }

        String normalized = digits.toString();
        if (normalized.isEmpty() || "-".equals(normalized)) {
            return null;
        }
        return normalized;
    }

    private void ensureRevealCacheConfigured() {
        int configuredSize = Math.max(this.config.getRevealCacheMaxSize(), 1);
        synchronized (REVEAL_CACHE_LOCK) {
            if (revealCacheMaxSize == configuredSize) {
                return;
            }
            revealCacheMaxSize = configuredSize;
            revealCache = new LinkedHashMap<String, String>(128, 0.75f, true) {
                private static final long serialVersionUID = 1L;

                @Override
                protected boolean removeEldestEntry(Map.Entry<String, String> eldest) {
                    return size() > revealCacheMaxSize;
                }
            };
        }
    }

    private String buildRevealCacheKey(String protectedValue, ColumnRuntimeConfig runtimeConfig) {
        return String.join("|",
                runtimeConfig.policyName == null ? "" : runtimeConfig.policyName,
                runtimeConfig.policyType == null ? "" : runtimeConfig.policyType,
                runtimeConfig.metadata == null ? "" : runtimeConfig.metadata,
                runtimeConfig.revealUser == null ? "" : runtimeConfig.revealUser,
                runtimeConfig.columnName == null ? "" : runtimeConfig.columnName,
                protectedValue == null ? "" : protectedValue);
    }

    private String getCachedReveal(String cacheKey) {
        synchronized (REVEAL_CACHE_LOCK) {
            return revealCache.get(cacheKey);
        }
    }

    private void putCachedReveal(String cacheKey, String plainText) {
        synchronized (REVEAL_CACHE_LOCK) {
            revealCache.put(cacheKey, plainText);
        }
    }

    private boolean shouldReturnOriginalValues(Exception ex) {
        if (!this.config.isReturnCiphertextForUnauthorizedEnabled()) {
            return false;
        }

        Throwable current = ex;
        while (current != null) {
            if (containsAny(current.getMessage(), "1401", "1001", "1002", "authorization failed")) {
                return true;
            }
            current = current.getCause();
        }
        return false;
    }

    private static final class ColumnRuntimeConfig {
        private final String columnName;
        private final String policyName;
        private final String policyType;
        private String metadata;
        private final String revealUser;

        private ColumnRuntimeConfig(
                String columnName,
                String policyName,
                String policyType,
                String metadata,
                String revealUser) {
            this.columnName = columnName;
            this.policyName = policyName;
            this.policyType = policyType == null ? "external" : policyType.toLowerCase(Locale.ROOT);
            this.metadata = metadata;
            this.revealUser = revealUser;
        }
    }
}

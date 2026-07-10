package com.thales.databricks.integration.service;

import java.io.InputStream;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.security.SecureRandom;
import java.security.cert.Certificate;
import java.security.cert.CertificateFactory;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLParameters;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.apache.spark.sql.internal.SQLConf;
import com.thales.databricks.integration.config.IntegrationConfig;

public final class JavaCrdpService {

    private static final Gson GSON = new Gson();
    private static final AtomicBoolean STARTUP_LOGGED = new AtomicBoolean(false);
    private static volatile JavaCrdpService instance;

    private final IntegrationConfig config;
    private final HttpClient httpClient;

    private JavaCrdpService(IntegrationConfig config) throws IOException {
        this.config = Objects.requireNonNull(config, "config");
        this.httpClient = buildHttpClient(config);
        logStartupSummary(config);
    }

    public static JavaCrdpService getInstance() throws IOException {
        JavaCrdpService local = instance;
        if (local == null) {
            synchronized (JavaCrdpService.class) {
                local = instance;
                if (local == null) {
                    local = new JavaCrdpService(IntegrationConfig.fromRuntime());
                    instance = local;
                }
            }
        }
        return local;
    }

    public String protectValue(String value, String datatype, String objectName, String columnName) throws Exception {
        if (value == null) {
            return null;
        }
        return protectValues(List.of(value), datatype, objectName, columnName).get(0);
    }

    public ProtectResult protectValueWithExternalHeader(
            String value,
            String datatype,
            String objectName,
            String columnName) throws Exception {
        if (value == null) {
            return new ProtectResult(null, null);
        }
        List<ProtectResult> results = protectValuesWithExternalHeaders(List.of(value), datatype, objectName, columnName);
        return results.isEmpty() ? new ProtectResult(value, null) : results.get(0);
    }

    public List<String> protectValues(
            List<String> values,
            String datatype,
            String objectName,
            String columnName) throws Exception {
        List<ProtectResult> results = protectValuesInternal(values, datatype, objectName, columnName, false);
        List<String> protectedValues = new ArrayList<>(results.size());
        for (ProtectResult result : results) {
            protectedValues.add(result.getProtectedValue());
        }
        return protectedValues;
    }

    public List<ProtectResult> protectValuesWithExternalHeaders(
            List<String> values,
            String datatype,
            String objectName,
            String columnName) throws Exception {
        return protectValuesInternal(values, datatype, objectName, columnName, true);
    }

    public String revealValue(
            String protectedValue,
            String datatype,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        if (protectedValue == null) {
            return null;
        }
        return revealValues(List.of(protectedValue), datatype, objectName, columnName, revealUser, null).get(0);
    }

    public String revealValueWithExternalHeader(
            String protectedValue,
            String externalHeader,
            String datatype,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        if (protectedValue == null) {
            return null;
        }
        return revealValues(
                List.of(protectedValue),
                datatype,
                objectName,
                columnName,
                revealUser,
                List.of(externalHeader)).get(0);
    }

    public List<String> revealValues(
            List<String> protectedValues,
            String datatype,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        return revealValues(protectedValues, datatype, objectName, columnName, revealUser, null);
    }

    public List<String> revealValuesWithExternalHeaders(
            List<String> protectedValues,
            String datatype,
            String objectName,
            String columnName,
            String revealUser,
            List<String> externalHeaders) throws Exception {
        return revealValues(protectedValues, datatype, objectName, columnName, revealUser, externalHeaders);
    }

    private List<ProtectResult> protectValuesInternal(
            List<String> values,
            String datatype,
            String objectName,
            String columnName,
            boolean includeExternalHeaders) throws Exception {
        String profileName = requireProfile(objectName, columnName, "protect");
        String policyType = config.resolvePolicyType(objectName, columnName, datatype, "protect");

        List<ProtectResult> results = new ArrayList<>(values.size());
        for (List<String> batchValues : chunkValues(values)) {
            JsonObject response = postJson(resolveProtectEndpoint(), buildProtectPayload(profileName, batchValues));
            throwIfCrdpReportedErrors(response, "protect");
            JsonArray protectedItems = readProtectItems(response);
            if (protectedItems.size() != batchValues.size()) {
                throw new IllegalStateException(
                        "CRDP protect response size did not match request size. "
                                + "expected=" + batchValues.size()
                                + ", actual=" + protectedItems.size()
                                + ", profile_name=" + profileName
                                + ", object_name=" + objectName
                                + ", column_name=" + columnName
                                + ", response=" + response);
            }

            for (JsonElement element : protectedItems) {
                JsonObject item = element.getAsJsonObject();
                String protectedData = requireString(item, "protected_data");
                String externalHeader = includeExternalHeaders && "external".equals(policyType)
                        ? optionalString(item, "external_version")
                        : null;
                results.add(new ProtectResult(protectedData, externalHeader));
            }
        }
        return results;
    }

    private List<String> revealValues(
            List<String> protectedValues,
            String datatype,
            String objectName,
            String columnName,
            String revealUser,
            List<String> externalHeaders) throws Exception {
        String profileName = requireProfile(objectName, columnName, "reveal");
        String policyType = config.resolvePolicyType(objectName, columnName, datatype, "reveal");

        List<String> results = new ArrayList<>(protectedValues.size());
        for (int start = 0; start < protectedValues.size(); start += effectiveBatchSize()) {
            int end = Math.min(start + effectiveBatchSize(), protectedValues.size());
            List<String> protectedBatch = new ArrayList<>(protectedValues.subList(start, end));
            List<String> externalHeaderBatch = sliceOptional(externalHeaders, start, end);
            try {
                JsonObject response = postJson(
                        resolveRevealEndpoint(),
                        buildRevealPayload(
                                profileName,
                                protectedBatch,
                                revealUser,
                                policyType,
                                objectName,
                                columnName,
                                externalHeaderBatch));
                throwIfCrdpReportedErrors(response, "reveal");
                JsonArray dataItems = readRevealItems(response);
                if (dataItems.size() != protectedBatch.size()) {
                    throw new IllegalStateException(
                            "CRDP reveal response size did not match request size. "
                                    + "expected=" + protectedBatch.size()
                                    + ", actual=" + dataItems.size()
                                    + ", response=" + response);
                }

                for (int i = 0; i < dataItems.size(); i++) {
                    JsonElement element = dataItems.get(i);
                    JsonObject item = element.getAsJsonObject();
                    results.add(extractRevealValue(item, protectedBatch.get(i), response));
                }
            } catch (Exception ex) {
                if (!config.isRevealFailOpenToCiphertext()) {
                    throw ex;
                }
                logRevealFailOpen(objectName, columnName, profileName, protectedBatch, ex);
                results.addAll(protectedBatch);
            }
        }
        return results;
    }

    private List<List<String>> chunkValues(List<String> values) {
        List<List<String>> chunks = new ArrayList<>();
        int batchSize = effectiveBatchSize();
        for (int start = 0; start < values.size(); start += batchSize) {
            int end = Math.min(start + batchSize, values.size());
            chunks.add(new ArrayList<>(values.subList(start, end)));
        }
        return chunks;
    }

    private int effectiveBatchSize() {
        Integer runtimeOverride = readRuntimeBatchSizeOverride();
        if (runtimeOverride != null) {
            return Math.max(runtimeOverride, 1);
        }
        return Math.max(config.getDefaultBatchSize(), 1);
    }

    private Integer readRuntimeBatchSizeOverride() {
        String configured = readSqlConf("thales.crdp.request.item.target.override");
        if (configured == null || configured.isBlank()) {
            configured = readSqlConf("thales.batch.size.override");
        }
        if (configured == null || configured.isBlank()) {
            return null;
        }
        try {
            int parsed = Integer.parseInt(configured.trim());
            return parsed > 0 ? parsed : null;
        } catch (NumberFormatException ex) {
            return null;
        }
    }

    private String readSqlConf(String key) {
        try {
            return SQLConf.get().getConfString(key, null);
        } catch (Exception ex) {
            return null;
        }
    }

    private List<String> sliceOptional(List<String> values, int start, int end) {
        if (values == null || start >= values.size()) {
            return null;
        }
        int boundedEnd = Math.min(end, values.size());
        return new ArrayList<>(values.subList(start, boundedEnd));
    }

    private String requireProfile(String objectName, String columnName, String mode) {
        String profileName = config.resolveProfile(objectName, columnName, mode);
        if (profileName == null || profileName.isBlank()) {
            throw new IllegalStateException(
                    "No protection profile resolved for object " + objectName + " column " + columnName + ".");
        }
        return profileName;
    }

    private String resolveProtectEndpoint() {
        return "v1".equalsIgnoreCase(config.getCrdpApiVersion()) ? "/v1/protectbulk" : "/v2/protectbulk";
    }

    private String resolveRevealEndpoint() {
        return "v1".equalsIgnoreCase(config.getCrdpApiVersion()) ? "/v1/revealbulk" : "/v2/revealbulk";
    }

    private JsonObject buildProtectPayload(String profileName, List<String> values) {
        if ("v1".equalsIgnoreCase(config.getCrdpApiVersion())) {
            JsonObject payload = new JsonObject();
            payload.addProperty("protection_policy_name", profileName);
            JsonArray dataArray = new JsonArray();
            values.forEach(dataArray::add);
            payload.add("data_array", dataArray);
            return payload;
        }

        JsonObject group = new JsonObject();
        group.addProperty("protection_policy_name", profileName);
        JsonArray dataArray = new JsonArray();
        values.forEach(dataArray::add);
        group.add("data_array", dataArray);

        JsonArray requestData = new JsonArray();
        requestData.add(group);

        JsonObject payload = new JsonObject();
        payload.add("request_data", requestData);
        return payload;
    }

    private JsonObject buildRevealPayload(
            String profileName,
            List<String> protectedValues,
            String revealUser,
            String policyType,
            String objectName,
            String columnName,
            List<String> externalHeaders) {
        String resolvedRevealUser = config.resolveRevealUser(objectName, columnName, revealUser);
        String fallbackExternalVersion = config.resolveMetadata(objectName, columnName);
        boolean isExternal = "external".equals(policyType);

        if ("v1".equalsIgnoreCase(config.getCrdpApiVersion())) {
            JsonArray protectedItems = new JsonArray();
            for (int i = 0; i < protectedValues.size(); i++) {
                JsonObject item = new JsonObject();
                item.addProperty("protected_data", protectedValues.get(i));
                if (isExternal) {
                    String externalVersion = resolveExternalVersion(externalHeaders, i, fallbackExternalVersion);
                    if (externalVersion != null && !externalVersion.isBlank()) {
                        item.addProperty("external_version", externalVersion);
                    }
                }
                protectedItems.add(item);
            }
            JsonObject payload = new JsonObject();
            payload.addProperty("protection_policy_name", profileName);
            payload.addProperty("username", resolvedRevealUser);
            payload.add("protected_data_array", protectedItems);
            return payload;
        }

        JsonArray protectedItems = new JsonArray();
        for (int i = 0; i < protectedValues.size(); i++) {
            JsonObject item = new JsonObject();
            item.addProperty("protected_data", protectedValues.get(i));
            if (isExternal) {
                String externalVersion = resolveExternalVersion(externalHeaders, i, fallbackExternalVersion);
                if (externalVersion != null && !externalVersion.isBlank()) {
                    item.addProperty("external_version", externalVersion);
                }
            }
            protectedItems.add(item);
        }

        JsonObject group = new JsonObject();
        group.addProperty("protection_policy_name", profileName);
        group.add("protected_data_array", protectedItems);

        JsonArray requestData = new JsonArray();
        requestData.add(group);

        JsonObject payload = new JsonObject();
        payload.addProperty("username", resolvedRevealUser);
        payload.add("request_data", requestData);
        return payload;
    }

    private String resolveExternalVersion(List<String> externalHeaders, int index, String fallback) {
        if (externalHeaders != null && index < externalHeaders.size()) {
            String value = externalHeaders.get(index);
            if (value != null && !value.isBlank()) {
                return value.trim();
            }
        }
        return fallback;
    }

    private JsonArray readProtectItems(JsonObject response) {
        if ("v1".equalsIgnoreCase(config.getCrdpApiVersion())) {
            JsonArray items = response.getAsJsonArray("protected_data_array");
            return items == null ? new JsonArray() : items;
        }

        JsonArray topLevelItems = response.getAsJsonArray("protected_data_array");
        if (topLevelItems != null) {
            return topLevelItems;
        }

        JsonArray responseData = response.getAsJsonArray("response_data");
        if (responseData == null || responseData.size() == 0) {
            return new JsonArray();
        }
        JsonObject group = responseData.get(0).getAsJsonObject();
        JsonArray items = group.getAsJsonArray("protected_data_array");
        return items == null ? new JsonArray() : items;
    }

    private JsonArray readRevealItems(JsonObject response) {
        if ("v1".equalsIgnoreCase(config.getCrdpApiVersion())) {
            JsonArray dataArray = response.getAsJsonArray("data_array");
            return dataArray == null ? new JsonArray() : dataArray;
        }

        JsonArray dataArray = response.getAsJsonArray("data_array");
        if (dataArray != null && dataArray.size() > 0) {
            JsonElement firstElement = dataArray.get(0);
            if (firstElement.isJsonArray()) {
                JsonArray firstGroup = firstElement.getAsJsonArray();
                return firstGroup == null ? new JsonArray() : firstGroup;
            }
            if (firstElement.isJsonObject()) {
                JsonObject firstGroup = firstElement.getAsJsonObject();
                JsonArray groupedItems = firstGroup.getAsJsonArray("data_array");
                return groupedItems == null ? new JsonArray() : groupedItems;
            }
        }

        JsonArray responseData = response.getAsJsonArray("response_data");
        if (responseData == null || responseData.size() == 0) {
            return new JsonArray();
        }
        JsonObject firstGroup = responseData.get(0).getAsJsonObject();
        JsonArray groupedItems = firstGroup.getAsJsonArray("data_array");
        return groupedItems == null ? new JsonArray() : groupedItems;
    }

    private static void throwIfCrdpReportedErrors(JsonObject response, String operation) {
        String status = optionalString(response, "status");
        int errorCount = response.has("error_count") && !response.get("error_count").isJsonNull()
                ? response.get("error_count").getAsInt()
                : 0;
        if ((status != null && "error".equalsIgnoreCase(status)) || errorCount > 0) {
            throw new IllegalStateException(
                    "CRDP " + operation + " response reported errors. "
                            + "status=" + status
                            + ", error_count=" + errorCount
                            + ", full_response=" + response);
        }
    }

    private JsonObject postJson(String endpoint, JsonObject payload)
            throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(buildUrl(endpoint)))
                .timeout(Duration.ofMillis(Math.max(config.getCrdpConnectTimeoutMs(), config.getCrdpReadTimeoutMs())))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(GSON.toJson(payload)))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() >= 400) {
            throw new IOException(
                    "CRDP request failed with HTTP status " + response.statusCode()
                            + ": " + response.body()
                            + debugPayloadSuffix(endpoint, payload));
        }
        JsonElement parsed = JsonParser.parseString(response.body());
        if (!parsed.isJsonObject()) {
            throw new IOException(
                    "CRDP response was not a JSON object."
                            + debugPayloadSuffix(endpoint, payload)
                            + ", raw_response=" + response.body());
        }
        return parsed.getAsJsonObject();
    }

    private String buildUrl(String endpoint) {
        String host = config.getCrdpIp().trim();
        if (host.startsWith("http://") || host.startsWith("https://")) {
            return host + ":" + config.getCrdpPort() + endpoint;
        }
        String scheme = config.isCrdpSslEnabled() ? "https" : "http";
        return scheme + "://" + host + ":" + config.getCrdpPort() + endpoint;
    }

    private static void logStartupSummary(IntegrationConfig config) {
        if (!STARTUP_LOGGED.compareAndSet(false, true)) {
            return;
        }
        String host = config.getCrdpIp() == null ? "" : config.getCrdpIp().trim();
        String baseUrl;
        if (host.startsWith("http://") || host.startsWith("https://")) {
            baseUrl = host + ":" + config.getCrdpPort();
        } else {
            String scheme = isHttpsRequested(config) ? "https" : "http";
            baseUrl = scheme + "://" + host + ":" + config.getCrdpPort();
        }
        System.out.println(
                "[thales-databricks-integration] Java CRDP client startup: "
                        + "base_url=" + baseUrl
                        + ", api_version=" + config.getCrdpApiVersion()
                        + ", transport_mode=" + config.getTransportMode()
                        + ", https_requested=" + isHttpsRequested(config)
                        + ", ssl_enabled_flag=" + config.isCrdpSslEnabled()
                        + ", verify_server=" + config.isCrdpSslVerifyServer()
                        + ", ca_cert_configured=" + hasText(config.getCrdpCaCertPath())
                        + ", client_pkcs12_configured=" + hasText(config.getCrdpClientPkcs12Path())
                        + ", debug_log_payload=" + config.isCrdpDebugLogPayload());
    }

    private static HttpClient buildHttpClient(IntegrationConfig config) throws IOException {
        HttpClient.Builder builder = HttpClient.newBuilder()
                .connectTimeout(Duration.ofMillis(config.getCrdpConnectTimeoutMs()));
        if (!isHttpsRequested(config)) {
            return builder.build();
        }
        try {
            X509TrustManager trustManager = buildTrustManager(config);
            SSLContext sslContext = SSLContext.getInstance("TLS");
            if (hasText(config.getCrdpClientPkcs12Path())) {
                KeyManagerFactory keyManagerFactory = buildKeyManagerFactory(config);
                sslContext.init(keyManagerFactory.getKeyManagers(), new TrustManager[] { trustManager }, new SecureRandom());
            } else {
                sslContext.init(null, new TrustManager[] { trustManager }, new SecureRandom());
            }
            SSLParameters sslParameters = new SSLParameters();
            if (!config.isCrdpSslVerifyServer()) {
                sslParameters.setEndpointIdentificationAlgorithm(null);
            }
            builder.sslContext(sslContext).sslParameters(sslParameters);
            return builder.build();
        } catch (Exception ex) {
            throw new IOException("Unable to build SSL context for CRDP client.", ex);
        }
    }

    private static X509TrustManager trustAllManager() {
        return new X509TrustManager() {
            @Override
            public void checkClientTrusted(java.security.cert.X509Certificate[] chain, String authType) {
            }

            @Override
            public void checkServerTrusted(java.security.cert.X509Certificate[] chain, String authType) {
            }

            @Override
            public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                return new java.security.cert.X509Certificate[0];
            }
        };
    }

    private static boolean isHttpsRequested(IntegrationConfig config) {
        String host = config.getCrdpIp() == null ? "" : config.getCrdpIp().trim().toLowerCase(Locale.ROOT);
        return config.isCrdpSslEnabled() || host.startsWith("https://");
    }

    private static KeyManagerFactory buildKeyManagerFactory(IntegrationConfig config) throws Exception {
        Path pkcs12Path = requireExistingPath(config.getCrdpClientPkcs12Path(), "CRDP_CLIENT_PKCS12_PATH");
        char[] password = config.getCrdpClientPkcs12Password().toCharArray();
        KeyStore keyStore = KeyStore.getInstance("PKCS12");
        try (InputStream input = Files.newInputStream(pkcs12Path)) {
            keyStore.load(input, password);
        }
        KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
        keyManagerFactory.init(keyStore, password);
        java.util.Arrays.fill(password, '\0');
        return keyManagerFactory;
    }

    private static X509TrustManager buildTrustManager(IntegrationConfig config) throws Exception {
        if (!config.isCrdpSslVerifyServer()) {
            return trustAllManager();
        }

        if (hasText(config.getCrdpCaCertPath())) {
            Path caCertPath = requireExistingPath(config.getCrdpCaCertPath(), "CRDP_CA_CERT_PATH");
            CertificateFactory certificateFactory = CertificateFactory.getInstance("X.509");
            Collection<? extends Certificate> certificates;
            try (InputStream input = Files.newInputStream(caCertPath)) {
                certificates = certificateFactory.generateCertificates(input);
            }
            if (certificates == null || certificates.isEmpty()) {
                throw new IllegalStateException("No certificates found in CRDP_CA_CERT_PATH: " + caCertPath);
            }

            KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
            trustStore.load(null, null);
            int index = 0;
            for (Certificate certificate : certificates) {
                trustStore.setCertificateEntry("crdp-ca-" + index, certificate);
                index++;
            }
            TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
            trustManagerFactory.init(trustStore);
            return extractTrustManager(trustManagerFactory);
        }

        TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        trustManagerFactory.init((KeyStore) null);
        return extractTrustManager(trustManagerFactory);
    }

    private static X509TrustManager extractTrustManager(TrustManagerFactory trustManagerFactory) {
        TrustManager[] managers = trustManagerFactory.getTrustManagers();
        if (managers.length != 1 || !(managers[0] instanceof X509TrustManager)) {
            throw new IllegalStateException("Unable to resolve X509TrustManager for CRDP HTTPS client.");
        }
        return (X509TrustManager) managers[0];
    }

    private static Path requireExistingPath(String value, String propertyName) {
        if (!hasText(value)) {
            throw new IllegalStateException("Missing required property: " + propertyName);
        }
        Path path = Paths.get(value.trim());
        if (Files.notExists(path)) {
            throw new IllegalStateException("File does not exist for " + propertyName + ": " + value);
        }
        return path;
    }

    private static boolean hasText(String value) {
        return value != null && !value.trim().isEmpty();
    }

    private static String requireString(JsonObject item, String key) {
        if (!item.has(key) || item.get(key).isJsonNull()) {
            throw new IllegalStateException("CRDP response item missing key: " + key);
        }
        return item.get(key).getAsString();
    }

    private static String extractRevealValue(
            JsonObject item,
            String originalProtectedValue,
            JsonObject fullResponse) {
        if (item.has("data") && !item.get("data").isJsonNull()) {
            return item.get("data").getAsString();
        }
        if (item.has("protected_data") && !item.get("protected_data").isJsonNull()) {
            return item.get("protected_data").getAsString();
        }
        throw new IllegalStateException(
                "CRDP reveal response item missing plaintext key. "
                        + "item=" + item
                        + ", original_protected_value=" + originalProtectedValue
                        + ", full_response=" + fullResponse);
    }

    private static String optionalString(JsonObject item, String key) {
        if (!item.has(key) || item.get(key).isJsonNull()) {
            return null;
        }
        String value = item.get(key).getAsString();
        return value == null || value.isBlank() ? null : value.trim();
    }

    private String debugPayloadSuffix(String endpoint, JsonObject payload) {
        if (!config.isCrdpDebugLogPayload()) {
            return "";
        }
        return ", endpoint=" + endpoint + ", request_payload=" + GSON.toJson(payload);
    }

    private void logRevealFailOpen(
            String objectName,
            String columnName,
            String profileName,
            List<String> protectedBatch,
            Exception ex) {
        String level = config.getRevealFailOpenLogLevel();
        String configVersion = blankOrDefault(config.getRawProperty("CONFIG_VERSION"), "<not set>");
        String configReleaseDate = blankOrDefault(config.getRawProperty("CONFIG_RELEASE_DATE"), "<not set>");
        String configChangeRef = blankOrDefault(config.getRawProperty("CONFIG_CHANGE_REF"), "<not set>");
        System.err.println(
                "[thales-databricks-integration] "
                        + level
                        + " Reveal failed open to ciphertext. "
                        + "object_name=" + objectName
                        + ", column_name=" + columnName
                        + ", profile_name=" + profileName
                        + ", api_version=" + config.getCrdpApiVersion()
                        + ", transport_mode=" + config.getTransportMode()
                        + ", batch_size=" + protectedBatch.size()
                        + ", config_version=" + configVersion
                        + ", config_release_date=" + configReleaseDate
                        + ", config_change_ref=" + configChangeRef
                        + ", error=" + ex);
    }

    private static String blankOrDefault(String value, String defaultValue) {
        return value == null || value.isBlank() ? defaultValue : value.trim();
    }
}

package com.thales.databricks.integration.config;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Properties;

public final class IntegrationConfig {

    private final Map<String, ObjectPolicyConfig> objects;
    private final Map<String, ObjectPolicyConfig> revealObjects;
    private final Map<String, String> globalColumnProfiles;
    private final Map<String, String> globalColumnTypes;
    private final Map<String, String> rawProperties;
    private final int defaultBatchSize;
    private final String crdpApiVersion;
    private final String transportMode;
    private final String crdpIp;
    private final int crdpPort;
    private final String crdpUser;
    private final boolean crdpSslEnabled;
    private final boolean crdpSslVerifyServer;
    private final String crdpCaCertPath;
    private final String crdpClientPkcs12Path;
    private final String crdpClientPkcs12Password;
    private final boolean crdpDebugLogPayload;
    private final int crdpConnectTimeoutMs;
    private final int crdpReadTimeoutMs;
    private final String defaultRevealUser;
    private final String defaultMetadata;
    private final String defaultMode;
    private final String externalTableHeaderValue;
    private final String externalTableHeaderDelimiter;
    private final int sparkGroupSize;
    private final int crdpV2MaxItemsPerRequest;
    private final int crdpV2MaxPolicyGroupsPerRequest;
    private final boolean crdpV2EnableMultiPolicy;
    private final boolean revealFailOpenToCiphertext;
    private final String revealFailOpenLogLevel;

    public IntegrationConfig() {
        this(
                Collections.emptyMap(),
                Collections.emptyMap(),
                Collections.emptyMap(),
                Collections.emptyMap(),
                Collections.emptyMap(),
                1000,
                "v2",
                "auto",
                "",
                0,
                "",
                false,
                true,
                "",
                "",
                "",
                false,
                10000,
                30000,
                "admin",
                "1001000",
                "internal",
                "header",
                "_",
                1000,
                1000,
                50,
                true,
                false,
                "ERROR");
    }

    public IntegrationConfig(
            Map<String, ObjectPolicyConfig> objects,
            Map<String, ObjectPolicyConfig> revealObjects,
            Map<String, String> globalColumnProfiles,
            Map<String, String> globalColumnTypes,
            Map<String, String> rawProperties,
            int defaultBatchSize,
            String crdpApiVersion,
            String transportMode,
            String crdpIp,
            int crdpPort,
            String crdpUser,
            boolean crdpSslEnabled,
            boolean crdpSslVerifyServer,
            String crdpCaCertPath,
            String crdpClientPkcs12Path,
            String crdpClientPkcs12Password,
            boolean crdpDebugLogPayload,
            int crdpConnectTimeoutMs,
            int crdpReadTimeoutMs,
            String defaultRevealUser,
            String defaultMetadata,
            String defaultMode,
            String externalTableHeaderValue,
            String externalTableHeaderDelimiter,
            int sparkGroupSize,
            int crdpV2MaxItemsPerRequest,
            int crdpV2MaxPolicyGroupsPerRequest,
            boolean crdpV2EnableMultiPolicy,
            boolean revealFailOpenToCiphertext,
            String revealFailOpenLogLevel) {
        this.objects = immutableObjectConfigs(objects);
        this.revealObjects = immutableObjectConfigs(revealObjects);
        this.globalColumnProfiles = globalColumnProfiles == null
                ? Collections.emptyMap()
                : Collections.unmodifiableMap(new LinkedHashMap<>(globalColumnProfiles));
        this.globalColumnTypes = globalColumnTypes == null
                ? Collections.emptyMap()
                : Collections.unmodifiableMap(new LinkedHashMap<>(globalColumnTypes));
        this.rawProperties = rawProperties == null
                ? Collections.emptyMap()
                : Collections.unmodifiableMap(new LinkedHashMap<>(rawProperties));
        this.defaultBatchSize = defaultBatchSize;
        this.crdpApiVersion = blankToDefault(crdpApiVersion, "v2");
        this.transportMode = blankToDefault(transportMode, "auto");
        this.crdpIp = blankToDefault(crdpIp, "");
        this.crdpPort = crdpPort;
        this.crdpUser = blankToDefault(crdpUser, "");
        this.crdpSslEnabled = crdpSslEnabled;
        this.crdpSslVerifyServer = crdpSslVerifyServer;
        this.crdpCaCertPath = blankToDefault(crdpCaCertPath, "");
        this.crdpClientPkcs12Path = blankToDefault(crdpClientPkcs12Path, "");
        this.crdpClientPkcs12Password = blankToDefault(crdpClientPkcs12Password, "");
        this.crdpDebugLogPayload = crdpDebugLogPayload;
        this.crdpConnectTimeoutMs = crdpConnectTimeoutMs;
        this.crdpReadTimeoutMs = crdpReadTimeoutMs;
        this.defaultRevealUser = blankToDefault(defaultRevealUser, "admin");
        this.defaultMetadata = blankToDefault(defaultMetadata, "1001000");
        this.defaultMode = blankToDefault(defaultMode, "internal");
        this.externalTableHeaderValue = blankToDefault(externalTableHeaderValue, "header");
        this.externalTableHeaderDelimiter = blankToDefault(externalTableHeaderDelimiter, "_");
        this.sparkGroupSize = sparkGroupSize;
        this.crdpV2MaxItemsPerRequest = crdpV2MaxItemsPerRequest;
        this.crdpV2MaxPolicyGroupsPerRequest = crdpV2MaxPolicyGroupsPerRequest;
        this.crdpV2EnableMultiPolicy = crdpV2EnableMultiPolicy;
        this.revealFailOpenToCiphertext = revealFailOpenToCiphertext;
        this.revealFailOpenLogLevel = blankToDefault(revealFailOpenLogLevel, "ERROR");
    }

    public static IntegrationConfig fromProperties(Path path) throws IOException {
        Properties properties = new Properties();
        try (InputStream input = Files.newInputStream(path)) {
            properties.load(input);
        }

        Map<String, String> rawProperties = new LinkedHashMap<>();
        for (String key : properties.stringPropertyNames()) {
            rawProperties.put(key, properties.getProperty(key));
        }

        Map<String, ObjectPolicyConfig> objects = parseObjectConfigs(properties, "protect.object.");
        Map<String, ObjectPolicyConfig> revealObjects = parseObjectConfigs(properties, "reveal.object.");
        Map<String, String> globalColumnProfiles = parseColumnProfiles(properties.getProperty("COLUMN_PROFILES", ""));
        Map<String, String> globalColumnTypes = inferColumnTypes(globalColumnProfiles);

        if (objects.isEmpty()) {
            if (!globalColumnProfiles.isEmpty()) {
                objects.put("default", new ObjectPolicyConfig(
                        "default",
                        globalColumnProfiles,
                        globalColumnTypes));
            }
        }

        return new IntegrationConfig(
                objects,
                revealObjects,
                globalColumnProfiles,
                globalColumnTypes,
                rawProperties,
                parsePositiveInt(firstNonBlank(
                        properties.getProperty("BATCH_SIZE"),
                        properties.getProperty("CRDP_REQUEST_ITEM_TARGET")),
                        1000,
                        "BATCH_SIZE/CRDP_REQUEST_ITEM_TARGET"),
                properties.getProperty("CRDP_API_VERSION", "v2"),
                properties.getProperty("CRDP_TRANSPORT_MODE", "auto"),
                properties.getProperty("CRDPIP", ""),
                parseInt(properties.getProperty("CRDPPORT"), 0),
                properties.getProperty("CRDPUSER", ""),
                parseBoolean(properties.getProperty("CRDP_SSL_ENABLED"), false),
                parseBoolean(properties.getProperty("CRDP_SSL_VERIFY_SERVER"), true),
                properties.getProperty("CRDP_CA_CERT_PATH", ""),
                properties.getProperty("CRDP_CLIENT_PKCS12_PATH", ""),
                properties.getProperty("CRDP_CLIENT_PKCS12_PASSWORD", ""),
                parseBoolean(properties.getProperty("CRDP_DEBUG_LOG_PAYLOAD"), false),
                parseInt(properties.getProperty("CRDP_CONNECT_TIMEOUT_MS"), 10000),
                parseInt(properties.getProperty("CRDP_READ_TIMEOUT_MS"), 30000),
                firstNonBlank(
                        properties.getProperty("DEFAULTREVEALUSER"),
                        properties.getProperty("CRDPUSER"),
                        properties.getProperty("databricksuser"),
                        "admin"),
                firstNonBlank(
                        properties.getProperty("DEFAULTMETADATA"),
                        properties.getProperty("keymetadata"),
                        "1001000"),
                firstNonBlank(
                        properties.getProperty("DEFAULTMODE"),
                        properties.getProperty("keymetadatalocation"),
                        "internal"),
                firstNonBlank(
                        properties.getProperty("external_table_header_value"),
                        properties.getProperty("EXTERNAL_TABLE_HEADER_VALUE"),
                        "header"),
                firstNonBlank(
                        properties.getProperty("external_table_header_delimiter"),
                        properties.getProperty("EXTERNAL_TABLE_HEADER_DELIMITER"),
                        "_"),
                parsePositiveInt(firstNonBlank(
                        properties.getProperty("SPARK_GROUP_SIZE"),
                        properties.getProperty("WORK_UNIT_ROW_COUNT")),
                        1000,
                        "SPARK_GROUP_SIZE/WORK_UNIT_ROW_COUNT"),
                parsePositiveInt(firstNonBlank(
                        properties.getProperty("CRDP_V2_MAX_ITEMS_PER_REQUEST"),
                        properties.getProperty("CRDP_REQUEST_ITEM_TARGET")),
                        1000,
                        "CRDP_V2_MAX_ITEMS_PER_REQUEST/CRDP_REQUEST_ITEM_TARGET"),
                parsePositiveInt(
                        properties.getProperty("CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST"),
                        50,
                        "CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST"),
                parseBoolean(firstNonBlank(
                        properties.getProperty("CRDP_V2_ENABLE_MULTI_POLICY"),
                        properties.getProperty("CRDP_MULTI_POLICY_ENABLED")),
                        true),
                parseBoolean(
                        properties.getProperty("REVEAL_FAIL_OPEN_TO_CIPHERTEXT"),
                        false),
                firstNonBlank(
                        properties.getProperty("REVEAL_FAIL_OPEN_LOG_LEVEL"),
                        "ERROR"));
    }

    public static IntegrationConfig fromRuntime() throws IOException {
        return fromProperties(resolveRuntimeConfigPath());
    }

    public List<String> getObjectColumns(String objectName) {
        ObjectPolicyConfig config = getObjectConfig(objectName, "protect");
        return config == null ? List.of() : List.copyOf(config.getColumnProfiles().keySet());
    }

    public String resolveProfile(String objectName, String columnName) {
        return resolveProfile(objectName, columnName, "protect");
    }

    public String resolveProfile(String objectName, String columnName, String mode) {
        String configuredProfile = getConfiguredProfile(objectName, columnName, mode);
        if (configuredProfile == null) {
            return null;
        }
        String alias = resolveAlias(configuredProfile);
        return alias == null ? configuredProfile : alias;
    }

    public String resolveDatatype(String objectName, String columnName) {
        ObjectPolicyConfig config = objects.get(objectName);
        if (config != null && config.getColumnTypes().containsKey(columnName)) {
            return config.getColumnTypes().getOrDefault(columnName, "char");
        }
        if (globalColumnTypes.containsKey(columnName)) {
            return globalColumnTypes.getOrDefault(columnName, "char");
        }
        ObjectPolicyConfig defaultConfig = objects.get("default");
        return defaultConfig == null ? "char" : defaultConfig.getColumnTypes().getOrDefault(columnName, "char");
    }

    public String resolvePolicyType(String objectName, String columnName, String datatype, String mode) {
        String configuredProfile = getConfiguredProfile(objectName, columnName, mode);
        String explicitPolicyType = firstNonBlank(
                getColumnProperty(columnName, "policyType"),
                getProfileProperty(configuredProfile, "policyType"));
        if (explicitPolicyType != null) {
            return explicitPolicyType.trim().toLowerCase(Locale.ROOT);
        }

        String inferred = inferPolicyType(configuredProfile);
        if (inferred != null) {
            return inferred;
        }
        inferred = inferPolicyType(resolveAlias(configuredProfile));
        if (inferred != null) {
            return inferred;
        }
        return defaultMode.trim().toLowerCase(Locale.ROOT);
    }

    public String resolveMetadata(String objectName, String columnName) {
        return firstNonBlank(getColumnProperty(columnName, "metadata"), defaultMetadata, "1001000");
    }

    public String resolveRevealUser(String objectName, String columnName, String runtimeRevealUser) {
        return firstNonBlank(
                runtimeRevealUser,
                getColumnProperty(columnName, "revealUser"),
                defaultRevealUser,
                "admin");
    }

    public String resolveExternalHeaderColumnName(String columnName) {
        if (columnName == null || columnName.isBlank()) {
            return null;
        }
        return columnName.trim().toLowerCase(Locale.ROOT) + externalTableHeaderDelimiter + externalTableHeaderValue;
    }

    public boolean shouldUseRealTransport() {
        String normalizedMode = transportMode.trim().toLowerCase(Locale.ROOT);
        if ("stub".equals(normalizedMode)) {
            return false;
        }
        if ("real".equals(normalizedMode)) {
            return true;
        }
        return hasCrdpEndpoint();
    }

    public boolean hasCrdpEndpoint() {
        if (crdpIp.isBlank() || crdpPort <= 0) {
            return false;
        }
        return !crdpIp.toLowerCase(Locale.ROOT).contains("your-crdp-ip");
    }

    public int getDefaultBatchSize() {
        return defaultBatchSize;
    }

    public String getCrdpApiVersion() {
        return crdpApiVersion;
    }

    public String getTransportMode() {
        return transportMode;
    }

    public String getCrdpIp() {
        return crdpIp;
    }

    public int getCrdpPort() {
        return crdpPort;
    }

    public String getCrdpUser() {
        return crdpUser;
    }

    public boolean isCrdpSslEnabled() {
        return crdpSslEnabled;
    }

    public boolean isCrdpSslVerifyServer() {
        return crdpSslVerifyServer;
    }

    public String getCrdpCaCertPath() {
        return crdpCaCertPath;
    }

    public String getCrdpClientPkcs12Path() {
        return crdpClientPkcs12Path;
    }

    public String getCrdpClientPkcs12Password() {
        return crdpClientPkcs12Password;
    }

    public boolean isCrdpDebugLogPayload() {
        return crdpDebugLogPayload;
    }

    public int getCrdpConnectTimeoutMs() {
        return crdpConnectTimeoutMs;
    }

    public int getCrdpReadTimeoutMs() {
        return crdpReadTimeoutMs;
    }

    public String getDefaultRevealUser() {
        return defaultRevealUser;
    }

    public String getDefaultMetadata() {
        return defaultMetadata;
    }

    public String getDefaultMode() {
        return defaultMode;
    }

    public int getSparkGroupSize() {
        return sparkGroupSize;
    }

    public int getCrdpV2MaxItemsPerRequest() {
        return crdpV2MaxItemsPerRequest;
    }

    public int getCrdpV2MaxPolicyGroupsPerRequest() {
        return crdpV2MaxPolicyGroupsPerRequest;
    }

    public boolean isCrdpV2EnableMultiPolicy() {
        return crdpV2EnableMultiPolicy;
    }

    public boolean isRevealFailOpenToCiphertext() {
        return revealFailOpenToCiphertext;
    }

    public String getRevealFailOpenLogLevel() {
        return revealFailOpenLogLevel;
    }

    public String getRawProperty(String key) {
        return rawProperties.get(key);
    }

    private ObjectPolicyConfig getObjectConfig(String objectName, String mode) {
        String normalizedMode = mode == null ? "protect" : mode.trim().toLowerCase(Locale.ROOT);
        if ("reveal".equals(normalizedMode) && !revealObjects.isEmpty()) {
            ObjectPolicyConfig config = revealObjects.get(objectName);
            return config != null ? config : revealObjects.get("default");
        }
        ObjectPolicyConfig config = objects.get(objectName);
        return config != null ? config : objects.get("default");
    }

    private String getConfiguredProfile(String objectName, String columnName, String mode) {
        ObjectPolicyConfig objectConfig = getObjectConfig(objectName, mode);
        if (objectConfig != null && objectConfig.getColumnProfiles().containsKey(columnName)) {
            return objectConfig.getColumnProfiles().get(columnName);
        }
        String structuredColumnProfile = getColumnProperty(columnName, "profile");
        if (structuredColumnProfile != null && !structuredColumnProfile.isBlank()) {
            return structuredColumnProfile.trim();
        }
        if (globalColumnProfiles.containsKey(columnName)) {
            return globalColumnProfiles.get(columnName);
        }
        ObjectPolicyConfig defaultConfig = getObjectConfig("default", mode);
        if (defaultConfig != null && defaultConfig.getColumnProfiles().containsKey(columnName)) {
            return defaultConfig.getColumnProfiles().get(columnName);
        }
        String legacyProfile = rawProperties.get("protection_profile");
        return legacyProfile == null || legacyProfile.isBlank() ? null : legacyProfile.trim();
    }

    private String resolveAlias(String configuredProfile) {
        if (configuredProfile == null || configuredProfile.isBlank()) {
            return null;
        }
        String normalizedTagKey = normalizeTagKey(configuredProfile);
        String alias = firstNonBlank(
                rawProperties.get(configuredProfile),
                normalizedTagKey == null ? null : rawProperties.get(normalizedTagKey),
                configuredProfile);
        return alias;
    }

    private String getColumnProperty(String columnName, String suffix) {
        if (columnName == null || columnName.isBlank()) {
            return null;
        }
        String normalizedColumn = columnName.trim().toLowerCase(Locale.ROOT);
        String camelKey = "column." + normalizedColumn + "." + suffix;
        String upperKey = "COLUMN." + normalizedColumn.toUpperCase(Locale.ROOT) + "." + suffix.toUpperCase(Locale.ROOT);
        return firstNonBlank(rawProperties.get(camelKey), rawProperties.get(upperKey));
    }

    private String getProfileProperty(String configuredProfile, String suffix) {
        if (configuredProfile == null || configuredProfile.isBlank()) {
            return null;
        }
        String normalizedTagKey = normalizeTagKey(configuredProfile);
        return firstNonBlank(
                rawProperties.get(configuredProfile + "." + suffix),
                normalizedTagKey == null ? null : rawProperties.get(normalizedTagKey + "." + suffix));
    }

    private static Map<String, ObjectPolicyConfig> immutableObjectConfigs(Map<String, ObjectPolicyConfig> source) {
        return source == null
                ? Collections.emptyMap()
                : Collections.unmodifiableMap(new LinkedHashMap<>(source));
    }

    private static Map<String, ObjectPolicyConfig> parseObjectConfigs(Properties properties, String prefix) {
        Map<String, ObjectPolicyConfig> parsed = new LinkedHashMap<>();
        for (String key : properties.stringPropertyNames()) {
            if (!key.startsWith(prefix)) {
                continue;
            }
            String objectName = key.substring(prefix.length()).trim();
            Map<String, String> profiles = parseColumnProfiles(properties.getProperty(key, ""));
            parsed.put(objectName, new ObjectPolicyConfig(
                    objectName,
                    profiles,
                    inferColumnTypes(profiles)));
        }
        return parsed;
    }

    private static Map<String, String> parseColumnProfiles(String rawValue) {
        Map<String, String> parsed = new LinkedHashMap<>();
        if (rawValue == null || rawValue.isBlank()) {
            return parsed;
        }
        for (String entry : rawValue.split(",")) {
            String item = entry.trim();
            if (item.isEmpty() || !item.contains("|")) {
                continue;
            }
            String[] parts = item.split("\\|", 2);
            parsed.put(parts[0].trim(), parts[1].trim());
        }
        return parsed;
    }

    private static Map<String, String> inferColumnTypes(Map<String, String> profiles) {
        Map<String, String> types = new LinkedHashMap<>();
        for (Map.Entry<String, String> entry : profiles.entrySet()) {
            types.put(entry.getKey(), inferDatatype(entry.getValue()));
        }
        return types;
    }

    private static String inferDatatype(String profileName) {
        String normalized = profileName == null ? "" : profileName.toLowerCase(Locale.ROOT);
        return normalized.contains("nbr") ? "nbr" : "char";
    }

    private static String inferPolicyType(String value) {
        String normalized = value == null ? "" : value.trim().toLowerCase(Locale.ROOT);
        if (normalized.isEmpty()) {
            return null;
        }
        if (normalized.contains("external")) {
            return "external";
        }
        if (normalized.contains("internal")) {
            return "internal";
        }
        if (normalized.contains("none")) {
            return "none";
        }
        return null;
    }

    private static int parseInt(String rawValue, int defaultValue) {
        try {
            return rawValue == null ? defaultValue : Integer.parseInt(rawValue.trim());
        } catch (NumberFormatException ex) {
            return defaultValue;
        }
    }

    private static int parsePositiveInt(String rawValue, int defaultValue, String propertyName) {
        int parsed = parseInt(rawValue, defaultValue);
        if (parsed <= 0) {
            throw new IllegalArgumentException(
                    propertyName + " must be a positive integer. Received: " + rawValue);
        }
        return parsed;
    }

    private static boolean parseBoolean(String rawValue, boolean defaultValue) {
        if (rawValue == null) {
            return defaultValue;
        }
        String normalized = rawValue.trim().toLowerCase(Locale.ROOT);
        if (normalized.equals("true") || normalized.equals("yes") || normalized.equals("1") || normalized.equals("on")) {
            return true;
        }
        if (normalized.equals("false") || normalized.equals("no") || normalized.equals("0") || normalized.equals("off")) {
            return false;
        }
        return defaultValue;
    }

    private static String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value.trim();
            }
        }
        return null;
    }

    private static String normalizeTagKey(String configuredProfile) {
        if (configuredProfile == null || configuredProfile.isBlank()) {
            return null;
        }
        String trimmed = configuredProfile.trim();
        if (trimmed.toLowerCase(Locale.ROOT).startsWith("tag.")) {
            return "TAG." + trimmed.substring(4);
        }
        return trimmed;
    }

    private static String blankToDefault(String value, String defaultValue) {
        return value == null || value.isBlank() ? defaultValue : value.trim();
    }

    private static Path resolveRuntimeConfigPath() throws IOException {
        String[] candidates = new String[] {
            System.getenv("UDF_CONFIG_VOLUME_PATH"),
            System.getenv("THALES_UDF_CONFIG_PATH"),
            "/tmp/thales_config/udfConfig.properties"
        };
        for (String candidate : candidates) {
            if (candidate == null || candidate.isBlank()) {
                continue;
            }
            Path path = Paths.get(candidate);
            if (Files.exists(path)) {
                return path;
            }
        }
        throw new IOException("Unable to locate udfConfig.properties from runtime environment.");
    }
}

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Properties;

public final class ThalesDataBricksUdfConfig {

    private static final String COLUMN_PROFILES_KEY = "COLUMN_PROFILES";
    private static final int DEFAULT_BATCH_SIZE = 1000;

    private final Properties properties;
    private final Map<String, String> columnProfiles;

    private ThalesDataBricksUdfConfig(Properties properties) {
        this.properties = properties;
        this.columnProfiles = parseColumnProfiles(properties.getProperty(COLUMN_PROFILES_KEY));
    }

    public static ThalesDataBricksUdfConfig load() {
        try {
            String volumePath = System.getenv("UDF_CONFIG_VOLUME_PATH");
            if (isBlank(volumePath)) {
                throw new IllegalStateException("Environment variable UDF_CONFIG_VOLUME_PATH is not set.");
            }

            Path path = Paths.get(volumePath);
            if (Files.notExists(path)) {
                throw new IllegalStateException("Unable to find udfConfig.properties at: " + volumePath);
            }

            Properties properties = new Properties();
            try (InputStream input = Files.newInputStream(path)) {
                properties.load(input);
            }
            return new ThalesDataBricksUdfConfig(properties);
        } catch (Exception ex) {
            throw new RuntimeException("Error loading udfConfig.properties from UDF_CONFIG_VOLUME_PATH.", ex);
        }
    }

    public String getCrdpIp() {
        return firstNonBlank(property("CRDPIP"), property("crdpip"), "http://thales-crdp-service.stuff.svc.spcs.internal");
    }

    public String getCrdpPort() {
        return firstNonBlank(property("CRDPIPPORT"), property("CRDPPORT"), property("crdpport"), "8090");
    }

    public int getBatchSize() {
        return parseInt(firstNonBlank(property("BATCH_SIZE"), property("BATCHSIZE")), DEFAULT_BATCH_SIZE);
    }

    public boolean isReturnCiphertextForUnauthorizedEnabled() {
        return parseBooleanFlag(firstNonBlank(
                property("RETURNCIPHERTEXTFORUSERWITHNOKEYACCESS"),
                property("returnciphertextforuserwithnokeyaccess"),
                "true"));
    }

    public boolean isRevealCacheEnabled() {
        return parseBooleanFlag(firstNonBlank(
                property("REVEAL_CACHE_ENABLED"),
                property("reveal.cache.enabled"),
                "false"));
    }

    public int getRevealCacheMaxSize() {
        return parseInt(firstNonBlank(
                property("REVEAL_CACHE_MAX_SIZE"),
                property("reveal.cache.maxSize"),
                "10000"), 10000);
    }

    public String getDefaultRevealUser() {
        return firstNonBlank(property("DEFAULTREVEALUSER"), property("CRDPUSER"), property("databricksuser"), "admin");
    }

    public String getDefaultMetadata() {
        return firstNonBlank(property("DEFAULTMETADATA"), property("keymetadata"), "1001000");
    }

    public String getDefaultMode() {
        return firstNonBlank(property("DEFAULTMODE"), property("keymetadatalocation"), "external");
    }

    public String resolvePolicyName(String columnName, String dataType, String mode) {
        String configuredProfile = firstNonBlank(
                getColumnProperty(columnName, "profile"),
                getColumnProfileAlias(columnName),
                getLegacyProfileAlias(dataType, mode),
                property("protection_profile"));
        if (isBlank(configuredProfile)) {
            throw new IllegalArgumentException("No protection profile configured for column="
                    + valueOrDefault(columnName, "<default>")
                    + ", datatype=" + valueOrDefault(dataType, "<unspecified>")
                    + ", mode=" + valueOrDefault(mode, "<unspecified>"));
        }
        String resolvedProfile = resolveAlias(configuredProfile);
        return isBlank(resolvedProfile) ? configuredProfile : resolvedProfile;
    }

    public String resolvePolicyType(String columnName, String dataType, String mode) {
        String configuredProfile = firstNonBlank(
                getColumnProperty(columnName, "profile"),
                getColumnProfileAlias(columnName),
                getLegacyProfileAlias(dataType, mode),
                property("protection_profile"));

        String explicitPolicyType = firstNonBlank(getColumnProperty(columnName, "policyType"), getProfileProperty(configuredProfile, "policyType"));
        if (!isBlank(explicitPolicyType)) {
            return explicitPolicyType.trim().toLowerCase(Locale.ROOT);
        }

        String inferredPolicyType = inferPolicyType(configuredProfile);
        if (!isBlank(inferredPolicyType)) {
            return inferredPolicyType;
        }
        inferredPolicyType = inferPolicyType(resolveAlias(configuredProfile));
        if (!isBlank(inferredPolicyType)) {
            return inferredPolicyType;
        }
        return normalizeLower(firstNonBlank(getColumnProperty(columnName, "mode"), property("POLICYTYPE"), getDefaultMode()));
    }

    public String resolveMetadata(String columnName) {
        return firstNonBlank(getColumnProperty(columnName, "metadata"), getDefaultMetadata());
    }

    public String resolveRevealUser(String columnName) {
        return firstNonBlank(getColumnProperty(columnName, "revealUser"), getDefaultRevealUser());
    }

    public String resolveRevealUser(String columnName, String runtimeRevealUser) {
        return firstNonBlank(runtimeRevealUser, getColumnProperty(columnName, "revealUser"), getDefaultRevealUser());
    }

    private String getLegacyProfileAlias(String dataType, String mode) {
        String normalizedType = normalizeToken(dataType);
        String normalizedMode = normalizeToken(mode);

        if ("char".equals(normalizedType)) {
            if ("protect".equals(normalizedMode) || "external".equals(normalizedMode)) {
                return firstNonBlank(property("DEFAULTEXTERNALCHARPOLICY"), property("protection_profile_alpha_ext"));
            }
            if ("reveal".equals(normalizedMode) || "internal".equals(normalizedMode)) {
                return firstNonBlank(property("DEFAULTINTERNALCHARPOLICY"), property("protection_profile_alpha_int"));
            }
        }

        if ("nbr".equals(normalizedType) || "nbrchar".equals(normalizedType) || "nbrnbr".equals(normalizedType)) {
            if ("protect".equals(normalizedMode) || "external".equals(normalizedMode)) {
                return firstNonBlank(property("DEFAULTEXTERNALNBRNBRPOLICY"), property("DEFAULTNBRNBRPOLICY"), property("protection_profile_nbr_ext"));
            }
            if ("reveal".equals(normalizedMode) || "internal".equals(normalizedMode)) {
                return firstNonBlank(property("DEFAULTINTERNALNBRNBRPOLICY"), property("DEFAULTNBRNBRPOLICY"), property("protection_profile_nbr_int"));
            }
        }
        return null;
    }

    private String getColumnProperty(String columnName, String suffix) {
        if (isBlank(columnName)) {
            return null;
        }
        String normalizedColumn = normalizeColumnKey(columnName);
        String camelKey = "column." + normalizedColumn + "." + suffix;
        String upperKey = "COLUMN." + normalizedColumn.toUpperCase(Locale.ROOT) + "." + suffix.toUpperCase(Locale.ROOT);
        return firstNonBlank(property(camelKey), property(upperKey));
    }

    private String getColumnProfileAlias(String columnName) {
        return isBlank(columnName) ? null : this.columnProfiles.get(normalizeColumnKey(columnName));
    }

    private String resolveAlias(String configuredProfile) {
        if (isBlank(configuredProfile)) {
            return null;
        }
        String value = firstNonBlank(property(configuredProfile), property(normalizeTagKey(configuredProfile)));
        return isBlank(value) ? configuredProfile : value;
    }

    private String getProfileProperty(String configuredProfile, String suffix) {
        if (isBlank(configuredProfile)) {
            return null;
        }
        return firstNonBlank(
                property(configuredProfile + "." + suffix),
                property(normalizeTagKey(configuredProfile) + "." + suffix));
    }

    private String property(String key) {
        return key == null ? null : trimToNull(this.properties.getProperty(key));
    }

    private static Map<String, String> parseColumnProfiles(String rawProfiles) {
        Map<String, String> profiles = new LinkedHashMap<>();
        if (isBlank(rawProfiles)) {
            return profiles;
        }
        for (String rawEntry : rawProfiles.split(",")) {
            String entry = trimToNull(rawEntry);
            if (entry == null) {
                continue;
            }
            String[] parts = entry.split("\\|", 2);
            String columnName = trimToNull(parts[0]);
            if (columnName == null) {
                continue;
            }
            String profileAlias = parts.length > 1 ? trimToNull(parts[1]) : null;
            profiles.put(normalizeColumnKey(columnName), profileAlias);
        }
        return profiles;
    }

    private static String normalizeTagKey(String configuredProfile) {
        String trimmed = trimToNull(configuredProfile);
        if (trimmed == null) {
            return null;
        }
        if (trimmed.regionMatches(true, 0, "tag.", 0, 4)) {
            return "TAG." + trimmed.substring(4);
        }
        return trimmed;
    }

    private static String inferPolicyType(String value) {
        String normalized = normalizeLower(value);
        if (normalized == null) {
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

    private static int parseInt(String value, int defaultValue) {
        try {
            return Math.max(Integer.parseInt(trimToNull(value)), 1);
        } catch (Exception ex) {
            return defaultValue;
        }
    }

    private static boolean parseBooleanFlag(String value) {
        String normalized = normalizeLower(value);
        if (normalized == null) {
            return false;
        }
        return "true".equals(normalized)
                || "yes".equals(normalized)
                || "y".equals(normalized)
                || "1".equals(normalized);
    }

    private static String normalizeColumnKey(String columnName) {
        return columnName.trim().toLowerCase(Locale.ROOT);
    }

    private static String normalizeToken(String value) {
        String trimmed = trimToNull(value);
        return trimmed == null ? null : trimmed.toLowerCase(Locale.ROOT);
    }

    private static String normalizeLower(String value) {
        String trimmed = trimToNull(value);
        return trimmed == null ? null : trimmed.toLowerCase(Locale.ROOT);
    }

    private static String firstNonBlank(String... values) {
        for (String value : values) {
            if (!isBlank(value)) {
                return value.trim();
            }
        }
        return null;
    }

    private static String valueOrDefault(String value, String defaultValue) {
        return isBlank(value) ? defaultValue : value;
    }

    private static String trimToNull(String value) {
        if (value == null) {
            return null;
        }
        String trimmed = value.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }

    private static boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }
}

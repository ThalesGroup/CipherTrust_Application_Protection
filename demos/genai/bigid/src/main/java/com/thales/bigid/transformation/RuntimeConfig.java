package com.thales.bigid.transformation;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Properties;

public class RuntimeConfig {

	public final String bigIdBaseUrl;
	public final String bigIdSystemToken;
	public final String bigIdUserToken;
	public final String bigIdCatalogFilter;
	public final int bigIdPageSize;
	public final List<String> bigIdClassificationHints;
	public final boolean bigIdDebugDumpAssets;
	public final Path bigIdDebugDumpFile;
	public final boolean bigIdDebugOnly;
	public final String sourceMode;
	public final String operationMode;
	public final String tagPrefix;
	public final Map<String, String> tagPolicyMap;
	public final Map<String, String> tagCodeMap;
	public final Map<String, String> piiPolicyMap;
	public final Path sourceRootDirectory;
	public final List<String> supportedExtensions;
	public final Path outputDirectory;
	public final boolean unstructuredWriteExtractedText;
	public final boolean unstructuredWriteProtectedText;
	public final boolean unstructuredWriteFindingsReport;
	public final String azureStorageConnectionString;
	public final String azureStorageTargetContainer;
	public final String azureStorageTargetPrefix;
	public final List<String> azureStorageQualifiedNamePrefixes;
	public final String s3Region;
	public final String s3AccessKey;
	public final String s3SecretKey;
	public final String s3SessionToken;
	public final String s3Endpoint;
	public final boolean s3PathStyleAccess;
	public final String s3TargetBucket;
	public final String s3TargetPrefix;
	public final List<String> s3QualifiedNamePrefixes;
	public final String gcsProjectId;
	public final Path gcsCredentialsPath;
	public final String gcsTargetBucket;
	public final String gcsTargetPrefix;
	public final List<String> gcsQualifiedNamePrefixes;
	public final boolean sqlEnabled;
	public final String sqlJdbcUrl;
	public final String sqlUser;
	public final String sqlPassword;
	public final List<String> sqlSourceTables;
	public final String sqlTargetSchema;
	public final String sqlTargetTableSuffix;
	public final String sqlWhereClause;
	public final String sqlWriteMode;
	public final String azureEndpoint;
	public final String azureApiKey;
	public final String azureLanguage;
	public final double azureConfidenceThreshold;
	public final String thalesKeyManagerHost;
	public final String thalesRegistrationToken;
	public final String thalesPolicyName;
	public final String thalesDefaultPolicy;
	public final String thalesPolicyType;
	public final String thalesRevealUser;
	public final boolean thalesShowMetadata;

	private RuntimeConfig(Properties properties) {
		this.bigIdBaseUrl = require(properties, "bigid.baseUrl");
		this.bigIdSystemToken = trimToNull(properties.getProperty("bigid.systemToken"));
		this.bigIdUserToken = trimToNull(properties.getProperty("bigid.userToken"));
		this.bigIdCatalogFilter = trimToNull(properties.getProperty("bigid.catalogFilter"));
		this.bigIdPageSize = Integer.parseInt(properties.getProperty("bigid.pageSize", "100"));
		this.bigIdClassificationHints = parseCsv(properties.getProperty("bigid.classificationHints"));
		this.bigIdDebugDumpAssets = Boolean.parseBoolean(properties.getProperty("bigid.debug.dumpAssets", "false"));
		this.bigIdDebugDumpFile = toPath(properties.getProperty("bigid.debug.dumpFile"));
		this.bigIdDebugOnly = Boolean.parseBoolean(properties.getProperty("bigid.debug.only", "false"));
		this.sourceMode = properties.getProperty("source.mode", "local").trim().toLowerCase();
		this.operationMode = normalizeOperationMode(
				properties.getProperty("mode", properties.getProperty("MODE", "protect")));
		this.tagPrefix = properties.getProperty("TAGPREFIX", "ENC").trim();
		this.tagPolicyMap = parsePrefixedProperties(properties, "TAG.");
		this.tagCodeMap = parsePrefixedProperties(properties, "TAGCODE.");
		this.piiPolicyMap = parsePiiMappings(properties, tagPolicyMap);
		this.sourceRootDirectory = toPath(properties.getProperty("source.rootDirectory"));
		this.supportedExtensions = parseCsv(properties.getProperty("source.supportedExtensions"));
		this.outputDirectory = toPath(properties.getProperty("output.directory"));
		this.unstructuredWriteExtractedText = Boolean
				.parseBoolean(properties.getProperty("unstructured.output.writeExtractedText", "false"));
		this.unstructuredWriteProtectedText = Boolean
				.parseBoolean(properties.getProperty("unstructured.output.writeProtectedText", "true"));
		this.unstructuredWriteFindingsReport = Boolean
				.parseBoolean(properties.getProperty("unstructured.output.writeFindingsReport", "false"));
		this.azureStorageConnectionString = trimToNull(properties.getProperty("azure.storage.connectionString"));
		this.azureStorageTargetContainer = trimToNull(properties.getProperty("azure.storage.targetContainer"));
		this.azureStorageTargetPrefix = trimToNull(properties.getProperty("azure.storage.targetPrefix"));
		this.azureStorageQualifiedNamePrefixes = parseCsv(properties.getProperty("azure.storage.qualifiedNamePrefixes"));
		this.s3Region = trimToNull(properties.getProperty("s3.region"));
		this.s3AccessKey = trimToNull(properties.getProperty("s3.accessKey"));
		this.s3SecretKey = trimToNull(properties.getProperty("s3.secretKey"));
		this.s3SessionToken = trimToNull(properties.getProperty("s3.sessionToken"));
		this.s3Endpoint = trimToNull(properties.getProperty("s3.endpoint"));
		this.s3PathStyleAccess = Boolean.parseBoolean(properties.getProperty("s3.pathStyleAccess", "false"));
		this.s3TargetBucket = trimToNull(properties.getProperty("s3.targetBucket"));
		this.s3TargetPrefix = trimToNull(properties.getProperty("s3.targetPrefix"));
		this.s3QualifiedNamePrefixes = parseCsv(properties.getProperty("s3.qualifiedNamePrefixes"));
		this.gcsProjectId = trimToNull(properties.getProperty("gcs.projectId"));
		this.gcsCredentialsPath = toPath(properties.getProperty("gcs.credentialsPath"));
		this.gcsTargetBucket = trimToNull(properties.getProperty("gcs.targetBucket"));
		this.gcsTargetPrefix = trimToNull(properties.getProperty("gcs.targetPrefix"));
		this.gcsQualifiedNamePrefixes = parseCsv(properties.getProperty("gcs.qualifiedNamePrefixes"));
		this.sqlEnabled = Boolean.parseBoolean(properties.getProperty("sql.enabled", "false"));
		this.sqlJdbcUrl = trimToNull(properties.getProperty("sql.jdbcUrl"));
		this.sqlUser = trimToNull(properties.getProperty("sql.user"));
		this.sqlPassword = trimToNull(properties.getProperty("sql.password"));
		this.sqlSourceTables = parseCsv(properties.getProperty("sql.sourceTables"));
		this.sqlTargetSchema = properties.getProperty("sql.targetSchema", "dbo").trim();
		this.sqlTargetTableSuffix = properties.getProperty("sql.targetTableSuffix", "_protected").trim();
		this.sqlWhereClause = trimToNull(properties.getProperty("sql.whereClause"));
		this.sqlWriteMode = properties.getProperty("sql.writeMode", "replace").trim();
		this.azureEndpoint = require(properties, "azure.textAnalytics.endpoint");
		this.azureApiKey = require(properties, "azure.textAnalytics.apiKey");
		this.azureLanguage = properties.getProperty("azure.textAnalytics.language", "en").trim();
		this.azureConfidenceThreshold = Double
				.parseDouble(properties.getProperty("azure.textAnalytics.confidenceThreshold", "0.80"));
		this.thalesKeyManagerHost = require(properties, "thales.keyManagerHost");
		this.thalesRegistrationToken = require(properties, "thales.registrationToken");
		this.thalesPolicyName = require(properties, "thales.policyName");
		this.thalesDefaultPolicy = require(properties, "thales.defaultPolicy");
		this.thalesPolicyType = properties.getProperty("thales.policyType", "external").trim();
		this.thalesRevealUser = require(properties, "thales.revealUser");
		this.thalesShowMetadata = Boolean.parseBoolean(properties.getProperty("thales.showMetadata", "true"));
		if (bigIdSystemToken == null && bigIdUserToken == null) {
			throw new IllegalArgumentException("Set either bigid.systemToken or bigid.userToken.");
		}
		if (!"local".equals(sourceMode) && !"azureblob".equals(sourceMode) && !"s3".equals(sourceMode)
				&& !"gcs".equals(sourceMode) && !"auto".equals(sourceMode)) {
			throw new IllegalArgumentException("source.mode must be one of: local, azureblob, s3, gcs, auto.");
		}
		if (!"protect".equals(operationMode) && !"reveal".equals(operationMode)) {
			throw new IllegalArgumentException("mode/MODE must be one of: protect, reveal, encrypt, decrypt.");
		}
		if (!bigIdDebugOnly && requiresLocalRoot()) {
			require(properties, "source.rootDirectory");
			require(properties, "output.directory");
		}
		if (!bigIdDebugOnly && requiresAzureBlob()) {
			require(properties, "azure.storage.connectionString");
			require(properties, "azure.storage.targetContainer");
		}
		if (!bigIdDebugOnly && requiresS3()) {
			require(properties, "s3.region");
			require(properties, "s3.targetBucket");
		}
		if (!bigIdDebugOnly && requiresGcs()) {
			require(properties, "gcs.targetBucket");
		}
		if (!bigIdDebugOnly && sqlEnabled) {
			require(properties, "sql.jdbcUrl");
			require(properties, "sql.user");
			require(properties, "sql.password");
		}
	}

	public boolean usesAzureBlob() {
		return "azureblob".equals(sourceMode) || ("auto".equals(sourceMode) && azureStorageConnectionString != null);
	}

	public boolean usesLocalFiles() {
		return "local".equals(sourceMode) || ("auto".equals(sourceMode) && sourceRootDirectory != null);
	}

	public boolean usesS3() {
		return "s3".equals(sourceMode) || ("auto".equals(sourceMode) && s3TargetBucket != null);
	}

	public boolean usesGcs() {
		return "gcs".equals(sourceMode) || ("auto".equals(sourceMode) && gcsTargetBucket != null);
	}

	private boolean requiresLocalRoot() {
		return "local".equals(sourceMode);
	}

	private boolean requiresAzureBlob() {
		return "azureblob".equals(sourceMode);
	}

	private boolean requiresS3() {
		return "s3".equals(sourceMode);
	}

	private boolean requiresGcs() {
		return "gcs".equals(sourceMode);
	}

	public static RuntimeConfig load(Path propertiesFile) throws IOException {
		Properties properties = new Properties();
		try (InputStream inputStream = Files.newInputStream(propertiesFile)) {
			properties.load(inputStream);
		}
		return new RuntimeConfig(properties);
	}

	private static String require(Properties properties, String key) {
		String value = trimToNull(properties.getProperty(key));
		if (value == null) {
			throw new IllegalArgumentException(key + " is required.");
		}
		return value;
	}

	private static String trimToNull(String value) {
		if (value == null) {
			return null;
		}
		String trimmed = value.trim();
		return trimmed.isEmpty() ? null : trimmed;
	}

	private static Path toPath(String value) {
		String trimmed = trimToNull(value);
		return trimmed == null ? null : Path.of(trimmed);
	}

	private static List<String> parseCsv(String value) {
		if (value == null || value.trim().isEmpty()) {
			return Collections.emptyList();
		}
		String[] parts = value.split(",");
		List<String> parsed = new ArrayList<>();
		for (String part : parts) {
			String trimmed = trimToNull(part);
			if (trimmed != null) {
				parsed.add(trimmed);
			}
		}
		return parsed;
	}

	private static String normalizeOperationMode(String value) {
		String normalized = trimToNull(value);
		if (normalized == null) {
			return "protect";
		}
		String lower = normalized.toLowerCase();
		if ("encrypt".equals(lower)) {
			return "protect";
		}
		if ("decrypt".equals(lower)) {
			return "reveal";
		}
		return lower;
	}

	private static Map<String, String> parsePrefixedProperties(Properties properties, String prefix) {
		Map<String, String> values = new HashMap<>();
		for (String key : properties.stringPropertyNames()) {
			if (key.startsWith(prefix)) {
				String normalizedKey = key.substring(prefix.length()).trim();
				String value = trimToNull(properties.getProperty(key));
				if (value != null) {
					values.put(normalizedKey, value);
				}
			}
		}
		return values;
	}

	private static Map<String, String> parsePiiMappings(Properties properties, Map<String, String> tagPolicyMap) {
		Map<String, String> values = new HashMap<>();
		for (String key : properties.stringPropertyNames()) {
			if (key.startsWith("PII.")) {
				String piiCategory = key.substring(4).trim();
				String mapping = trimToNull(properties.getProperty(key));
				if (mapping == null) {
					continue;
				}
				if (mapping.startsWith("TAG.")) {
					String tagName = mapping.substring(4).trim();
					String policy = tagPolicyMap.get(tagName);
					if (policy != null) {
						values.put(piiCategory, policy);
					}
				} else {
					values.put(piiCategory, mapping);
				}
			}
		}
		return values;
	}

	public String resolveTagCode(String tagName) {
		String configuredCode = tagCodeMap.get(tagName);
		if (configuredCode != null && !configuredCode.isBlank()) {
			return configuredCode.trim();
		}
		return java.util.Base64.getEncoder().encodeToString((tagPrefix + tagName).getBytes(java.nio.charset.StandardCharsets.UTF_8))
				+ "-";
	}
}

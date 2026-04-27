package com.example;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Properties;

/**
 * Holds configuration for the Purview-aware processing flow.
 */
public class PurviewConfig {

	public final String endpoint;
	public final String accessToken;
	public final String dataSourceName;
	public final String scanName;
	public final boolean runScan;
	public final boolean waitForScanCompletion;
	public final int scanPollSeconds;
	public final int searchLimit;
	public final List<String> classificationFilters;
	public final List<String> fileEntityHints;
	public final List<String> sqlColumnEntityHints;
	public final List<String> storageQualifiedNamePrefixes;
	public final String storageConnectionString;
	public final String storageTargetContainer;
	public final String storageTargetPrefix;
	public final String sqlSourceTable;
	public final String sqlTargetTable;
	public final String sqlJdbcUrl;
	public final String sqlUser;
	public final String sqlPassword;
	public final String sqlWhereClause;
	public final String sqlWriteMode;

	private PurviewConfig(Properties properties) {
		this.endpoint = trimToNull(properties.getProperty("PURVIEW_ENDPOINT"));
		this.accessToken = trimToNull(properties.getProperty("PURVIEW_ACCESS_TOKEN"));
		this.dataSourceName = trimToNull(properties.getProperty("PURVIEW_DATASOURCE_NAME"));
		this.scanName = trimToNull(properties.getProperty("PURVIEW_SCAN_NAME"));
		this.runScan = Boolean.parseBoolean(properties.getProperty("PURVIEW_RUN_SCAN", "false"));
		this.waitForScanCompletion = Boolean.parseBoolean(properties.getProperty("PURVIEW_WAIT_FOR_SCAN", "true"));
		this.scanPollSeconds = Integer.parseInt(properties.getProperty("PURVIEW_SCAN_POLL_SECONDS", "15"));
		this.searchLimit = Integer.parseInt(properties.getProperty("PURVIEW_SEARCH_LIMIT", "100"));
		this.classificationFilters = parseCsv(properties.getProperty("PURVIEW_CLASSIFICATIONS"));
		this.fileEntityHints = parseCsv(properties.getProperty("PURVIEW_FILE_ENTITY_HINTS",
				"file,path,blob,adls,azure storage,azure blob,adls gen2"));
		this.sqlColumnEntityHints = parseCsv(properties.getProperty("PURVIEW_SQL_COLUMN_ENTITY_HINTS",
				"column,azure sql column,mssql column,sql column"));
		this.storageQualifiedNamePrefixes = parseCsv(properties.getProperty("PURVIEW_STORAGE_QUALIFIED_NAME_PREFIXES"));
		this.storageConnectionString = trimToNull(properties.getProperty("AZURE_STORAGE_CONNECTION_STRING"));
		this.storageTargetContainer = trimToNull(properties.getProperty("PURVIEW_STORAGE_TARGET_CONTAINER"));
		this.storageTargetPrefix = trimToNull(properties.getProperty("PURVIEW_STORAGE_TARGET_PREFIX"));
		this.sqlSourceTable = trimToNull(properties.getProperty("PURVIEW_SQL_SOURCE_TABLE"));
		this.sqlTargetTable = trimToNull(properties.getProperty("PURVIEW_SQL_TARGET_TABLE"));
		this.sqlJdbcUrl = trimToNull(properties.getProperty("PURVIEW_SQL_JDBC_URL"));
		this.sqlUser = trimToNull(properties.getProperty("PURVIEW_SQL_USER"));
		this.sqlPassword = trimToNull(properties.getProperty("PURVIEW_SQL_PASSWORD"));
		this.sqlWhereClause = trimToNull(properties.getProperty("PURVIEW_SQL_WHERE_CLAUSE"));
		this.sqlWriteMode = properties.getProperty("PURVIEW_SQL_WRITE_MODE", "replace").trim();
	}

	public static PurviewConfig fromProperties(Properties properties) {
		return new PurviewConfig(properties);
	}

	public void validateForPurview() {
		require(endpoint, "PURVIEW_ENDPOINT");
		require(accessToken, "PURVIEW_ACCESS_TOKEN");
		if (classificationFilters.isEmpty()) {
			throw new IllegalArgumentException("PURVIEW_CLASSIFICATIONS must contain at least one classification name.");
		}
	}

	public void validateForSql() {
		require(sqlJdbcUrl, "PURVIEW_SQL_JDBC_URL");
		require(sqlUser, "PURVIEW_SQL_USER");
		require(sqlPassword, "PURVIEW_SQL_PASSWORD");
		require(sqlSourceTable, "PURVIEW_SQL_SOURCE_TABLE");
		require(sqlTargetTable, "PURVIEW_SQL_TARGET_TABLE");
	}

	public void validateForStorage() {
		require(storageConnectionString, "AZURE_STORAGE_CONNECTION_STRING");
		require(storageTargetContainer, "PURVIEW_STORAGE_TARGET_CONTAINER");
	}

	private static void require(String value, String propertyName) {
		if (value == null || value.isEmpty()) {
			throw new IllegalArgumentException(propertyName + " is required for this flow.");
		}
	}

	private static String trimToNull(String value) {
		if (value == null) {
			return null;
		}
		String trimmed = value.trim();
		return trimmed.isEmpty() ? null : trimmed;
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
}

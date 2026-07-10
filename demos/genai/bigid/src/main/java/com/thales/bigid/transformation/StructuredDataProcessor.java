package com.thales.bigid.transformation;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Types;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

public class StructuredDataProcessor {

	private final RuntimeConfig config;
	private final BigIdClient bigIdClient;
	private final ProtectionService protectionService;

	public StructuredDataProcessor(RuntimeConfig config, BigIdClient bigIdClient, ProtectionService protectionService) {
		this.config = config;
		this.bigIdClient = bigIdClient;
		this.protectionService = protectionService;
	}

	public StructuredProcessingSummary process() throws IOException, InterruptedException, SQLException {
		List<BigIdAsset> assets = bigIdClient.querySensitiveAssets();
		Map<String, Set<String>> sensitiveColumnsByTable = new LinkedHashMap<>();
		for (BigIdAsset asset : assets) {
			if (!asset.hasClassificationHint(config.bigIdClassificationHints) || !asset.looksLikeStructuredColumn()) {
				continue;
			}
			String tableName = normalizeIdentifier(asset.inferTableName());
			String columnName = normalizeIdentifier(asset.inferColumnName());
			if (tableName == null || columnName == null) {
				continue;
			}
			if (!config.sqlSourceTables.isEmpty() && !containsIgnoreCase(config.sqlSourceTables, tableName)) {
				continue;
			}
			sensitiveColumnsByTable.computeIfAbsent(tableName, ignored -> new LinkedHashSet<>()).add(columnName);
		}

		StructuredProcessingSummary summary = new StructuredProcessingSummary();
		if (sensitiveColumnsByTable.isEmpty()) {
			System.out.println("No BigID-classified structured columns matched the SQL configuration.");
			return summary;
		}

		try (Connection connection = DriverManager.getConnection(config.sqlJdbcUrl, config.sqlUser, config.sqlPassword)) {
			for (Map.Entry<String, Set<String>> entry : sensitiveColumnsByTable.entrySet()) {
				String sourceTable = resolveSourceTable(connection, entry.getKey());
				if (sourceTable == null) {
					continue;
				}

				List<String> sourceColumns = loadSourceColumns(connection, sourceTable);
				Set<String> matchedSensitiveColumns = new LinkedHashSet<>();
				for (String sourceColumn : sourceColumns) {
					if (containsIgnoreCase(entry.getValue(), sourceColumn)) {
						matchedSensitiveColumns.add(sourceColumn);
					}
				}
				if (matchedSensitiveColumns.isEmpty()) {
					continue;
				}

				String targetTable = buildTargetTableName(sourceTable);
				prepareTargetTable(connection, sourceTable, targetTable, sourceColumns);
				int processedRows = copyRows(connection, sourceTable, targetTable, sourceColumns, matchedSensitiveColumns,
						summary);
				if (processedRows > 0) {
					summary.processedTableCount++;
					summary.processedRowCount += processedRows;
				}
			}
		}

		return summary;
	}

	private int copyRows(Connection connection, String sourceTable, String targetTable, List<String> sourceColumns,
			Set<String> sensitiveColumns, StructuredProcessingSummary summary) throws SQLException {
		String selectSql = "SELECT * FROM " + bracket(sourceTable)
				+ (config.sqlWhereClause == null ? "" : " WHERE " + config.sqlWhereClause);
		String insertSql = buildInsertSql(targetTable, sourceColumns);
		int rowCount = 0;

		try (Statement selectStatement = connection.createStatement();
				ResultSet resultSet = selectStatement.executeQuery(selectSql);
				PreparedStatement insertStatement = connection.prepareStatement(insertSql)) {
			ResultSetMetaData metaData = resultSet.getMetaData();
			while (resultSet.next()) {
				for (int i = 1; i <= metaData.getColumnCount(); i++) {
					Object rawValue = resultSet.getObject(i);
					String columnName = metaData.getColumnLabel(i);
					String finalValue = convertValue(rawValue, metaData.getColumnType(i));
					if (finalValue != null && containsIgnoreCase(sensitiveColumns, columnName)) {
						String piiCategory = inferPiiCategory(columnName);
						if ("reveal".equals(config.operationMode)) {
							finalValue = protectionService.reveal(finalValue, piiCategory);
						} else {
							finalValue = protectionService.protect(finalValue, piiCategory);
						}
						summary.protectedFieldCount++;
					}
					insertStatement.setString(i, finalValue);
				}
				insertStatement.executeUpdate();
				rowCount++;
			}
		}

		System.out.println("Processed structured table " + sourceTable + " -> " + targetTable + " rows=" + rowCount
				+ " sensitiveColumns=" + sensitiveColumns);
		return rowCount;
	}

	private List<String> loadSourceColumns(Connection connection, String sourceTable) throws SQLException {
		List<String> columns = new ArrayList<>();
		try (Statement statement = connection.createStatement();
				ResultSet resultSet = statement.executeQuery("SELECT TOP 1 * FROM " + bracket(sourceTable))) {
			ResultSetMetaData metaData = resultSet.getMetaData();
			for (int i = 1; i <= metaData.getColumnCount(); i++) {
				columns.add(metaData.getColumnLabel(i));
			}
		}
		return columns;
	}

	private void prepareTargetTable(Connection connection, String sourceTable, String targetTable, List<String> sourceColumns)
			throws SQLException {
		String writeMode = config.sqlWriteMode.toLowerCase(Locale.ROOT);
		try (Statement statement = connection.createStatement()) {
			if ("replace".equals(writeMode)) {
				statement.execute("IF OBJECT_ID('" + escapeSqlLiteral(targetTable) + "', 'U') IS NOT NULL DROP TABLE "
						+ bracket(targetTable));
			}
			if (!tableExists(connection, targetTable)) {
				StringBuilder createSql = new StringBuilder("CREATE TABLE ").append(bracket(targetTable)).append(" (");
				for (int i = 0; i < sourceColumns.size(); i++) {
					if (i > 0) {
						createSql.append(", ");
					}
					createSql.append("[").append(sourceColumns.get(i)).append("] NVARCHAR(MAX) NULL");
				}
				createSql.append(")");
				statement.execute(createSql.toString());
			}
		}
	}

	private boolean tableExists(Connection connection, String tableName) throws SQLException {
		String schema = schemaOf(tableName);
		String simpleName = simpleTableName(tableName);
		DatabaseMetaData metaData = connection.getMetaData();
		try (ResultSet resultSet = metaData.getTables(null, schema, simpleName, new String[] { "TABLE" })) {
			return resultSet.next();
		}
	}

	private String resolveSourceTable(Connection connection, String requestedTable) throws SQLException {
		if (tableExists(connection, requestedTable)) {
			return requestedTable;
		}
		if (tableExists(connection, "dbo." + requestedTable)) {
			return "dbo." + requestedTable;
		}
		return null;
	}

	private String buildTargetTableName(String sourceTable) {
		return config.sqlTargetSchema + "." + simpleTableName(sourceTable) + config.sqlTargetTableSuffix;
	}

	private String buildInsertSql(String targetTable, List<String> columns) {
		StringBuilder sql = new StringBuilder("INSERT INTO ").append(bracket(targetTable)).append(" (");
		for (int i = 0; i < columns.size(); i++) {
			if (i > 0) {
				sql.append(", ");
			}
			sql.append("[").append(columns.get(i)).append("]");
		}
		sql.append(") VALUES (");
		for (int i = 0; i < columns.size(); i++) {
			if (i > 0) {
				sql.append(", ");
			}
			sql.append("?");
		}
		sql.append(")");
		return sql.toString();
	}

	private String convertValue(Object rawValue, int sqlType) {
		if (rawValue == null) {
			return null;
		}
		if (sqlType == Types.BINARY || sqlType == Types.VARBINARY || sqlType == Types.LONGVARBINARY) {
			return String.valueOf(rawValue);
		}
		return String.valueOf(rawValue);
	}

	private String inferPiiCategory(String columnName) {
		String normalized = columnName.toLowerCase(Locale.ROOT);
		if (normalized.contains("email")) {
			return "Email";
		}
		if (normalized.contains("phone")) {
			return "PhoneNumber";
		}
		if (normalized.contains("address")) {
			return "Address";
		}
		if (normalized.contains("ssn") || normalized.contains("social")) {
			return "USSocialSecurityNumber";
		}
		if (normalized.contains("url")) {
			return "URL";
		}
		return "Person";
	}

	private boolean containsIgnoreCase(Iterable<String> values, String candidate) {
		for (String value : values) {
			if (value.equalsIgnoreCase(candidate)) {
				return true;
			}
		}
		return false;
	}

	private String normalizeIdentifier(String value) {
		if (value == null || value.isBlank()) {
			return null;
		}
		return value.replace("[", "").replace("]", "").replace("\"", "").trim();
	}

	private String schemaOf(String tableName) {
		String[] parts = normalizeIdentifier(tableName).split("\\.");
		return parts.length > 1 ? parts[0] : "dbo";
	}

	private String simpleTableName(String tableName) {
		String[] parts = normalizeIdentifier(tableName).split("\\.");
		return parts.length > 1 ? parts[1] : parts[0];
	}

	private String bracket(String objectName) {
		String[] parts = normalizeIdentifier(objectName).split("\\.");
		if (parts.length == 1) {
			return "[" + parts[0] + "]";
		}
		return "[" + parts[0] + "].[" + parts[1] + "]";
	}

	private String escapeSqlLiteral(String value) {
		return value.replace("'", "''");
	}

	public static class StructuredProcessingSummary {
		public int processedTableCount;
		public int processedRowCount;
		public int protectedFieldCount;
	}
}

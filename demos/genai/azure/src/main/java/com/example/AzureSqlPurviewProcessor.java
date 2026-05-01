package com.example;

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
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Properties;
import java.util.Set;

/**
 * Protects only the SQL columns that Purview classified as sensitive.
 * The output table is created with NVARCHAR(MAX) columns so the protected
 * values can be stored safely even when ciphertext is longer than source data.
 */
public class AzureSqlPurviewProcessor extends ContentProcessor {

	private final PurviewConfig purviewConfig;

	public AzureSqlPurviewProcessor(Properties properties, PurviewConfig purviewConfig) {
		super(properties);
		this.purviewConfig = purviewConfig;
	}

	public int processSensitiveTable(Set<String> sensitiveColumns, ThalesProtectRevealHelper tprh, String mode)
			throws SQLException {
		if (sensitiveColumns.isEmpty()) {
			System.out.println("Purview did not mark any columns in " + purviewConfig.sqlSourceTable
					+ " as sensitive. Skipping SQL processing.");
			return 0;
		}

		try (Connection connection = DriverManager.getConnection(purviewConfig.sqlJdbcUrl, purviewConfig.sqlUser,
				purviewConfig.sqlPassword)) {
			String sourceTable = purviewConfig.sqlSourceTable;
			String targetTable = purviewConfig.sqlTargetTable;
			List<String> sourceColumns = loadSourceColumns(connection, sourceTable);
			List<String> matchedSensitiveColumns = new ArrayList<>();
			for (String column : sourceColumns) {
				if (containsIgnoreCase(sensitiveColumns, column)) {
					matchedSensitiveColumns.add(column);
				}
			}

			if (matchedSensitiveColumns.isEmpty()) {
				System.out.println("Purview classifications did not match any source columns in " + sourceTable
						+ ". Skipping SQL processing.");
				return 0;
			}

			System.out.println("Purview-sensitive SQL columns: " + matchedSensitiveColumns);
			prepareTargetTable(connection, sourceTable, targetTable);
			return copyRows(connection, sourceTable, targetTable, sourceColumns, new LinkedHashSet<>(matchedSensitiveColumns),
					tprh, mode);
		}
	}

	@Override
	public int processFile(java.io.File inputFile, java.io.File outputDir, String projectId, ThalesProtectRevealHelper tprh,
			String mode, boolean skiphdr) {
		throw new UnsupportedOperationException("AzureSqlPurviewProcessor does not process files.");
	}

	private List<String> loadSourceColumns(Connection connection, String sourceTable) throws SQLException {
		List<String> columns = new ArrayList<>();
		try (Statement statement = connection.createStatement();
				ResultSet resultSet = statement.executeQuery("SELECT TOP 1 * FROM " + sourceTable)) {
			ResultSetMetaData metaData = resultSet.getMetaData();
			for (int i = 1; i <= metaData.getColumnCount(); i++) {
				columns.add(metaData.getColumnLabel(i));
			}
		}
		return columns;
	}

	private void prepareTargetTable(Connection connection, String sourceTable, String targetTable) throws SQLException {
		List<String> sourceColumns = loadSourceColumns(connection, sourceTable);
		String writeMode = purviewConfig.sqlWriteMode.toLowerCase(Locale.ROOT);

		try (Statement statement = connection.createStatement()) {
			if ("replace".equals(writeMode)) {
				statement.execute("IF OBJECT_ID('" + escapeSqlLiteral(targetTable)
						+ "', 'U') IS NOT NULL DROP TABLE " + targetTable);
			}

			if (!tableExists(connection, targetTable)) {
				StringBuilder createSql = new StringBuilder("CREATE TABLE ").append(targetTable).append(" (");
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
		String cleanName = tableName;
		String schema = "dbo";
		String simpleName = cleanName;
		if (tableName.contains(".")) {
			String[] parts = tableName.split("\\.");
			if (parts.length == 2) {
				schema = parts[0];
				simpleName = parts[1];
			}
		}
		DatabaseMetaData metaData = connection.getMetaData();
		try (ResultSet resultSet = metaData.getTables(null, schema, simpleName, new String[] { "TABLE" })) {
			return resultSet.next();
		}
	}

	private int copyRows(Connection connection, String sourceTable, String targetTable, List<String> sourceColumns,
			Set<String> sensitiveColumns, ThalesProtectRevealHelper tprh, String mode) throws SQLException {
		String selectSql = "SELECT * FROM " + sourceTable
				+ (purviewConfig.sqlWhereClause == null ? "" : " WHERE " + purviewConfig.sqlWhereClause);
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
						total_entities_found++;
						String piiMapping = piiMap.getOrDefault(inferPiiKey(columnName), tprh.defaultPolicy);
						if ("protect".equalsIgnoreCase(mode)) {
							finalValue = encryptData(finalValue, tprh, piiMapping);
						} else {
							finalValue = decryptLine(finalValue, tprh);
						}
					}
					insertStatement.setString(i, finalValue);
				}
				insertStatement.executeUpdate();
				rowCount++;
			}
		}

		System.out.println("Processed " + rowCount + " SQL rows into " + targetTable);
		return rowCount;
	}

	private String buildInsertSql(String targetTable, List<String> columns) {
		StringBuilder sql = new StringBuilder("INSERT INTO ").append(targetTable).append(" (");
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
			total_skipped_entities++;
			return rawValue.toString();
		}
		return String.valueOf(rawValue);
	}

	private String inferPiiKey(String columnName) {
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
		return "Person";
	}

	private boolean containsIgnoreCase(Set<String> values, String candidate) {
		for (String value : values) {
			if (value.equalsIgnoreCase(candidate)) {
				return true;
			}
		}
		return false;
	}

	private String escapeSqlLiteral(String value) {
		return value.replace("'", "''");
	}
}

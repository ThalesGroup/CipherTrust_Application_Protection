package com.example;

import java.io.IOException;
import java.io.InputStream;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Properties;
import java.util.Set;

/**
 * Purview-aware batch processor that supports both storage and Azure SQL flows.
 * Storage files are read directly from the Purview-scanned source and then
 * processed with Text Analytics plus Thales protection. SQL columns are
 * filtered by Purview classifications and then protected directly.
 */
public class ThalesAzurePurviewBatchProcessor {

	private static Properties properties;

	static {
		try (InputStream input = ThalesAzurePurviewBatchProcessor.class.getClassLoader()
				.getResourceAsStream("thales-config.properties")) {
			properties = new Properties();
			if (input == null) {
				throw new RuntimeException("Unable to find thales-config.properties");
			}
			properties.load(input);
		} catch (Exception ex) {
			throw new RuntimeException("Error loading properties file", ex);
		}
	}

	public static void main(String[] args) throws IOException, SQLException, InterruptedException {
		if (args.length != 5) {
			System.err.println(
					"Usage: java ThalesAzurePurviewBatchProcessor <mode> <workload:storage|sql|both> <textAnalyticsEndpoint|-> <textAnalyticsApiKey|-> <fileExtension|->");
			System.exit(-1);
		}

		long startTime = System.nanoTime();
		String mode = args[0];
		String workload = args[1];
		String textAnalyticsEndpoint = normalizeOptionalArg(args[2]);
		String textAnalyticsApiKey = normalizeOptionalArg(args[3]);
		String fileExtension = normalizeOptionalArg(args[4]);

		PurviewConfig purviewConfig = PurviewConfig.fromProperties(properties);
		purviewConfig.validateForPurview();

		ThalesCADPProtectRevealHelper tprh = buildProtectRevealHelper();
		PurviewClient purviewClient = new PurviewClient(purviewConfig);
		purviewClient.runConfiguredScanAndWait();
		List<PurviewAsset> sensitiveAssets = purviewClient.searchSensitiveAssets();
		System.out.println("Purview returned " + sensitiveAssets.size() + " classified assets.");

		if (handlesStorage(workload)) {
			purviewConfig.validateForStorage();
			requireStorageArgs(textAnalyticsEndpoint, textAnalyticsApiKey);
			processStorage(mode, purviewConfig, textAnalyticsEndpoint, textAnalyticsApiKey, fileExtension,
					sensitiveAssets, tprh);
		}

		if (handlesSql(workload)) {
			purviewConfig.validateForSql();
			processSql(mode, purviewConfig, sensitiveAssets, tprh);
		}

		long endTime = System.nanoTime();
		double elapsedTimeSeconds = (double) (endTime - startTime) / 1_000_000_000.0;
		System.out.printf("Application execution time: %.6f seconds%n", elapsedTimeSeconds);
	}

	private static void processStorage(String mode, PurviewConfig purviewConfig, String textAnalyticsEndpoint,
			String textAnalyticsApiKey, String fileExtension, List<PurviewAsset> sensitiveAssets,
			ThalesCADPProtectRevealHelper tprh) throws IOException {
		AzureStoragePurviewProcessor storageProcessor = new AzureStoragePurviewProcessor(properties, purviewConfig);
		AzureStoragePurviewProcessor.ProcessingSummary summary = storageProcessor.processSensitiveAssets(sensitiveAssets,
				mode, textAnalyticsEndpoint, textAnalyticsApiKey, fileExtension, tprh);
		System.out.println("Number of Purview-selected storage assets = " + summary.processedAssetCount);
		System.out.println("Total nbr of file records = " + summary.processedRecordCount);
		System.out.println("Total skipped entities = " + summary.totalSkippedEntities);
		System.out.println("Total entities found = " + summary.totalEntitiesFound);
	}

	private static void processSql(String mode, PurviewConfig purviewConfig, List<PurviewAsset> sensitiveAssets,
			ThalesCADPProtectRevealHelper tprh) throws SQLException {
		AzureSqlPurviewProcessor sqlProcessor = new AzureSqlPurviewProcessor(properties, purviewConfig);
		Set<String> sensitiveColumns = extractSensitiveSqlColumns(sensitiveAssets, purviewConfig);
		int processedRows = sqlProcessor.processSensitiveTable(sensitiveColumns, tprh, mode);
		System.out.println("Total SQL rows processed = " + processedRows);
		System.out.println("Total skipped entities = " + sqlProcessor.total_skipped_entities);
		System.out.println("Total entities found = " + sqlProcessor.total_entities_found);
	}

	private static ThalesCADPProtectRevealHelper buildProtectRevealHelper() {
		String keymanagerhost = properties.getProperty("KEYMGRHOST");
		String crdptkn = properties.getProperty("CRDPTKN");
		String policyType = properties.getProperty("POLICYTYPE");
		String defaultpolicy = properties.getProperty("DEFAULTPOLICY");
		boolean showmeta = properties.getProperty("SHOWMETADATA", "true").equalsIgnoreCase("true");
		String revealuser = properties.getProperty("REVEALUSER");

		ThalesCADPProtectRevealHelper tprh = new ThalesCADPProtectRevealHelper(keymanagerhost, crdptkn, null,
				policyType, showmeta);
		tprh.revealUser = revealuser;
		tprh.policyType = policyType;
		tprh.policyName = properties.getProperty("POLICYNAME");
		tprh.defaultPolicy = defaultpolicy;
		return tprh;
	}

	private static Set<String> extractSensitiveSqlColumns(List<PurviewAsset> assets, PurviewConfig config) {
		Set<String> columnNames = new LinkedHashSet<>();
		for (PurviewAsset asset : assets) {
			if (!matchesAnyHint(asset, config.sqlColumnEntityHints)) {
				continue;
			}
			if (config.sqlSourceTable != null && !asset.referencesTable(config.sqlSourceTable)) {
				continue;
			}
			if (asset.getName() != null) {
				columnNames.add(asset.getName());
			}
		}
		return columnNames;
	}

	private static boolean matchesAnyHint(PurviewAsset asset, List<String> hints) {
		for (String hint : hints) {
			if (asset.matchesHint(hint)) {
				return true;
			}
		}
		return false;
	}

	private static boolean handlesStorage(String workload) {
		return "storage".equalsIgnoreCase(workload) || "both".equalsIgnoreCase(workload)
				|| "files".equalsIgnoreCase(workload);
	}

	private static boolean handlesSql(String workload) {
		return "sql".equalsIgnoreCase(workload) || "both".equalsIgnoreCase(workload);
	}

	private static String normalizeOptionalArg(String arg) {
		if (arg == null || arg.isBlank() || "-".equals(arg.trim())) {
			return null;
		}
		return arg;
	}

	private static void requireStorageArgs(String textAnalyticsEndpoint, String textAnalyticsApiKey) {
		List<String> missing = new ArrayList<>();
		if (textAnalyticsEndpoint == null) {
			missing.add("textAnalyticsEndpoint");
		}
		if (textAnalyticsApiKey == null) {
			missing.add("textAnalyticsApiKey");
		}
		if (!missing.isEmpty()) {
			throw new IllegalArgumentException("Missing required storage-flow arguments: " + missing);
		}
	}
}

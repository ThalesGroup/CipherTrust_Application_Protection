package com.thales.bigid.transformation;

import java.io.IOException;
import java.nio.file.Path;

public class BigidThalesTransformationApplication {

	public static void main(String[] args) throws Exception {
		Path configPath = resolveConfigPath(args);
		if (configPath == null) {
			System.err.println(
					"Usage: java BigidThalesTransformationApplication <propertiesFile> or set BIGID_CONFIG_FILE");
			System.exit(-1);
		}

		RuntimeConfig config = RuntimeConfig.load(configPath);
		BigIdClient bigIdClient = new BigIdClient(config);
		DocumentConversionService documentConversionService = new DocumentConversionService();
		AzureTextAnalyticsService azureService = new AzureTextAnalyticsService(config);
		ProtectionService unstructuredProtectionService = buildProtectionService(config, true);
		ProtectionService structuredProtectionService = buildProtectionService(config, false);

		SensitiveAssetProcessor processor = new SensitiveAssetProcessor(config, bigIdClient, documentConversionService,
				azureService, unstructuredProtectionService);
		SensitiveAssetProcessor.ProcessingSummary summary = processor.process();
		StructuredDataProcessor.StructuredProcessingSummary sqlSummary = null;
		if (!config.bigIdDebugOnly && config.sqlEnabled) {
			StructuredDataProcessor structuredDataProcessor = new StructuredDataProcessor(config, bigIdClient,
					structuredProtectionService);
			sqlSummary = structuredDataProcessor.process();
		}

		System.out.println("BigID assets returned = " + summary.returnedAssetCount);
		System.out.println("Assets matched to configured sources = " + summary.matchedAssetCount);
		System.out.println("Document assets processed = " + summary.processedAssetCount);
		System.out.println("Sensitive spans protected = " + summary.protectedSpanCount);
		if (sqlSummary != null) {
			System.out.println("Structured tables processed = " + sqlSummary.processedTableCount);
			System.out.println("Structured rows copied = " + sqlSummary.processedRowCount);
			System.out.println("Structured fields protected = " + sqlSummary.protectedFieldCount);
		}
	}

	private static Path resolveConfigPath(String[] args) {
		if (args.length == 1 && args[0] != null && !args[0].isBlank()) {
			return Path.of(args[0]);
		}
		String envConfig = System.getenv("BIGID_CONFIG_FILE");
		if (envConfig != null && !envConfig.isBlank()) {
			return Path.of(envConfig);
		}
		return null;
	}

	private static ProtectionService buildProtectionService(RuntimeConfig config, boolean prefixOutput)
			throws IOException {
		ThalesCADPProtectRevealHelper helper = new ThalesCADPProtectRevealHelper(config.thalesKeyManagerHost,
				config.thalesRegistrationToken, null, config.thalesPolicyType, config.thalesShowMetadata);
		helper.policyName = config.thalesPolicyName;
		helper.defaultPolicy = config.thalesDefaultPolicy;
		helper.revealUser = config.thalesRevealUser;
		return new CadpProtectionService(helper, config, prefixOutput);
	}
}

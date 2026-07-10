package com.thales.bigid.transformation;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileVisitOption;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.ArrayList;
import java.util.stream.Stream;

import org.json.JSONArray;
import org.json.JSONObject;

public class SensitiveAssetProcessor {

	private final RuntimeConfig config;
	private final BigIdClient bigIdClient;
	private final DocumentConversionService documentConversionService;
	private final AzureTextAnalyticsService azureTextAnalyticsService;
	private final ProtectionService protectionService;
	private final List<RemoteDocumentStore> remoteDocumentStores;

	public SensitiveAssetProcessor(RuntimeConfig config, BigIdClient bigIdClient,
			DocumentConversionService documentConversionService, AzureTextAnalyticsService azureTextAnalyticsService,
			ProtectionService protectionService) throws IOException {
		this.config = config;
		this.bigIdClient = bigIdClient;
		this.documentConversionService = documentConversionService;
		this.azureTextAnalyticsService = azureTextAnalyticsService;
		this.protectionService = protectionService;
		this.remoteDocumentStores = buildRemoteStores(config);
	}

	public ProcessingSummary process() throws IOException, InterruptedException {
		if (config.outputDirectory != null) {
			Files.createDirectories(config.outputDirectory);
		}
		List<BigIdAsset> assets = bigIdClient.querySensitiveAssets();
		dumpAssetsIfRequested(assets);
		ProcessingSummary summary = new ProcessingSummary();
		summary.returnedAssetCount = assets.size();
		if (config.bigIdDebugOnly) {
			System.out.println("BigID debug-only mode enabled. Asset dump completed; skipping document processing.");
			return summary;
		}

		for (BigIdAsset asset : assets) {
			if (!asset.hasClassificationHint(config.bigIdClassificationHints)) {
				continue;
			}

			ResolvedDocument resolved = resolveAsset(asset);
			if (resolved == null) {
				continue;
			}
			summary.matchedAssetCount++;

			String extractedText = resolved.loadText(documentConversionService);
			List<PiiEntityMatch> piiMatches = "protect".equals(config.operationMode)
					? azureTextAnalyticsService.findSensitiveSpans(extractedText)
					: Collections.emptyList();
			ProtectionResult protectionResult = applyProtection(extractedText, piiMatches);
			resolved.writeArtifacts(config, extractedText, protectionResult);

			summary.processedAssetCount++;
			summary.protectedSpanCount += piiMatches.size();
			System.out.println("Processed " + resolved.describe());
		}

		return summary;
	}

	private void dumpAssetsIfRequested(List<BigIdAsset> assets) throws IOException {
		if (!config.bigIdDebugDumpAssets) {
			return;
		}
		JSONArray array = new JSONArray();
		for (BigIdAsset asset : assets) {
			array.put(asset.toJson());
		}
		Path dumpFile = config.bigIdDebugDumpFile != null
				? config.bigIdDebugDumpFile
				: (config.outputDirectory != null
						? config.outputDirectory.resolve("bigid-asset-debug.json")
						: Path.of("bigid-asset-debug.json"));
		if (dumpFile.getParent() != null) {
			Files.createDirectories(dumpFile.getParent());
		}
		Files.writeString(dumpFile, array.toString(2), StandardCharsets.UTF_8);
		System.out.println("Wrote BigID asset debug dump to " + dumpFile);
	}

	private ProtectionResult applyProtection(String originalText, List<PiiEntityMatch> matches) {
		if ("reveal".equals(config.operationMode)) {
			return new ProtectionResult(protectionService.revealTaggedText(originalText), new JSONArray());
		}
		StringBuilder builder = new StringBuilder(originalText);
		JSONArray findings = new JSONArray();
		matches.stream()
				.sorted(Comparator.comparingInt((PiiEntityMatch match) -> match.offset).reversed())
				.forEach(match -> {
					int end = Math.min(builder.length(), match.offset + match.length);
					if (match.offset < 0 || match.offset >= end) {
						return;
					}
					String sourceValue = builder.substring(match.offset, end);
					String protectedValue = protectionService.protect(sourceValue, match.category);
					findings.put(createFinding(match, sourceValue, protectedValue));
					builder.replace(match.offset, end, protectedValue);
				});
		return new ProtectionResult(builder.toString(), findings);
	}

	private JSONObject createFinding(PiiEntityMatch match, String sourceValue, String protectedValue) {
		JSONObject finding = new JSONObject();
		finding.put("offset", match.offset);
		finding.put("length", match.length);
		finding.put("category", match.category);
		finding.put("confidence", match.confidence);
		finding.put("originalText", sourceValue);
		finding.put("protectedText", protectedValue);
		return finding;
	}

	private ResolvedDocument resolveAsset(BigIdAsset asset) throws IOException {
		if (config.usesLocalFiles()) {
			Optional<Path> local = resolveLocalAsset(asset);
			if (local.isPresent()) {
				return createLocalResolvedDocument(local.get());
			}
		}
		for (RemoteDocumentStore remoteStore : remoteDocumentStores) {
			if (remoteStore.matchesAsset(asset)
					&& remoteStore.matchesConfiguredPrefix(asset)
					&& supports(resolveRemoteFileName(asset, remoteStore))) {
				return createRemoteResolvedDocument(remoteStore, asset);
			}
		}
		return null;
	}

	private String resolveRemoteFileName(BigIdAsset asset, RemoteDocumentStore remoteStore) {
		if (asset.getName() != null) {
			return asset.getName();
		}
		if (remoteStore instanceof AzureBlobDocumentStore) {
			return asset.getStorageBlobName();
		}
		if (remoteStore instanceof S3DocumentStore) {
			return asset.getS3ObjectKey();
		}
		if (remoteStore instanceof GcsDocumentStore) {
			return asset.getGcsObjectName();
		}
		return null;
	}

	private Optional<Path> resolveLocalAsset(BigIdAsset asset) throws IOException {
		if (asset.getPath() != null) {
			try {
				Path directPath = normalizePath(asset.getPath());
				if (Files.exists(directPath) && Files.isRegularFile(directPath) && supports(directPath)) {
					return Optional.of(directPath);
				}
			} catch (Exception ignored) {
			}

			if (config.sourceRootDirectory != null) {
				Path relativePath = config.sourceRootDirectory.resolve(asset.getPath()).normalize();
				if (Files.exists(relativePath) && Files.isRegularFile(relativePath) && supports(relativePath)) {
					return Optional.of(relativePath);
				}
			}
		}

		if (asset.getName() == null || config.sourceRootDirectory == null) {
			return Optional.empty();
		}

		try (Stream<Path> stream = Files.walk(config.sourceRootDirectory, FileVisitOption.FOLLOW_LINKS)) {
			return stream.filter(Files::isRegularFile)
					.filter(this::supports)
					.filter(path -> path.getFileName().toString().equalsIgnoreCase(asset.getName()))
					.findFirst();
		}
	}

	private Path buildOutputPath(Path inputFile, String suffix) {
		String safeName = inputFile.getFileName().toString() + suffix;
		return config.outputDirectory.resolve(safeName);
	}

	private boolean supports(Path path) {
		return supports(path.getFileName().toString());
	}

	private boolean supports(String fileName) {
		if (fileName == null) {
			return false;
		}
		String lowerCaseName = fileName.toLowerCase(Locale.ROOT);
		for (String extension : config.supportedExtensions) {
			if (lowerCaseName.endsWith(extension.toLowerCase(Locale.ROOT))) {
				return true;
			}
		}
		return false;
	}

	private Path normalizePath(String rawPath) {
		String cleaned = rawPath.replace("file://", "").replace('\\', '/');
		return Path.of(cleaned);
	}

	public static class ProcessingSummary {
		public int returnedAssetCount;
		public int matchedAssetCount;
		public int processedAssetCount;
		public int protectedSpanCount;
	}

	private ResolvedDocument createLocalResolvedDocument(Path localPath) {
		return new ResolvedDocument(localPath, null, null);
	}

	private ResolvedDocument createRemoteResolvedDocument(RemoteDocumentStore remoteStore, BigIdAsset asset) {
		return new ResolvedDocument(null, remoteStore, asset);
	}

	private List<RemoteDocumentStore> buildRemoteStores(RuntimeConfig config) throws IOException {
		List<RemoteDocumentStore> stores = new ArrayList<>();
		if (config.usesAzureBlob()) {
			stores.add(new AzureBlobDocumentStore(config));
		}
		if (config.usesS3()) {
			stores.add(new S3DocumentStore(config));
		}
		if (config.usesGcs()) {
			stores.add(new GcsDocumentStore(config));
		}
		return stores;
	}

	private class ResolvedDocument {
		private final Path localPath;
		private final RemoteDocumentStore remoteStore;
		private final BigIdAsset remoteAsset;

		private ResolvedDocument(Path localPath, RemoteDocumentStore remoteStore, BigIdAsset remoteAsset) {
			this.localPath = localPath;
			this.remoteStore = remoteStore;
			this.remoteAsset = remoteAsset;
		}

		private String loadText(DocumentConversionService conversionService) throws IOException {
			if (localPath != null) {
				return conversionService.extractText(localPath.toFile());
			}
			Path tempFile = remoteStore.downloadToTempFile(remoteAsset);
			try {
				return conversionService.extractText(tempFile.toFile());
			} finally {
				Files.deleteIfExists(tempFile);
			}
		}

		private void writeArtifacts(RuntimeConfig config, String extractedText, ProtectionResult protectionResult)
				throws IOException {
			if (localPath != null) {
				if (config.unstructuredWriteExtractedText) {
					Files.writeString(buildOutputPath(localPath, ".extracted.txt"), extractedText, StandardCharsets.UTF_8);
				}
				if (config.unstructuredWriteProtectedText) {
					String suffix = "reveal".equals(config.operationMode) ? ".revealed.txt" : ".protected.txt";
					Files.writeString(buildOutputPath(localPath, suffix), protectionResult.outputText,
							StandardCharsets.UTF_8);
				}
				if (config.unstructuredWriteFindingsReport && "protect".equals(config.operationMode)) {
					Files.writeString(buildOutputPath(localPath, ".findings.json"), protectionResult.findings.toString(2),
							StandardCharsets.UTF_8);
				}
				return;
			}
			if (config.unstructuredWriteExtractedText) {
				remoteStore.writeExtractedText(remoteAsset, extractedText);
			}
			if (config.unstructuredWriteProtectedText) {
				remoteStore.writeProtectedText(remoteAsset, protectionResult.outputText);
			}
			if (config.unstructuredWriteFindingsReport && "protect".equals(config.operationMode)) {
				remoteStore.writeFindingsReport(remoteAsset, protectionResult.findings.toString(2));
			}
		}

		private String describe() {
			if (localPath != null) {
				String suffix = "reveal".equals(config.operationMode) ? ".revealed.txt" : ".protected.txt";
				return localPath.toString() + " -> " + buildOutputPath(localPath, suffix);
			}
			return remoteAsset.getPath() + " -> " + remoteStore.describeTarget(remoteAsset);
		}
	}

	private static class ProtectionResult {
		private final String outputText;
		private final JSONArray findings;

		private ProtectionResult(String outputText, JSONArray findings) {
			this.outputText = outputText;
			this.findings = findings;
		}
	}
}

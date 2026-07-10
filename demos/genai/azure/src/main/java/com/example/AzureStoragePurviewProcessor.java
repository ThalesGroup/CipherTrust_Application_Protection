package com.example;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import com.azure.core.util.BinaryData;
import com.azure.storage.blob.BlobClient;
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobServiceClient;
import com.azure.storage.blob.BlobServiceClientBuilder;
import com.azure.storage.blob.specialized.BlobInputStream;

/**
 * Reads the same blob/file assets Purview classified, protects their content,
 * and uploads the protected output back to Azure Storage.
 */
public class AzureStoragePurviewProcessor {

	private final Properties properties;
	private final PurviewConfig purviewConfig;
	private final BlobServiceClient blobServiceClient;
	private final DocumentConversionService documentConversionService;

	public AzureStoragePurviewProcessor(Properties properties, PurviewConfig purviewConfig) {
		this.properties = properties;
		this.purviewConfig = purviewConfig;
		this.documentConversionService = new DocumentConversionService();
		this.blobServiceClient = new BlobServiceClientBuilder()
				.connectionString(purviewConfig.storageConnectionString)
				.buildClient();
	}

	public ProcessingSummary processSensitiveAssets(List<PurviewAsset> sensitiveAssets, String mode,
			String textAnalyticsEndpoint, String textAnalyticsApiKey, String fileExtension,
			ThalesProtectRevealHelper tprh) throws IOException {
		AzureContentProcessor.cognitiveservices_endpoint = textAnalyticsEndpoint;
		AzureContentProcessor.cognitiveservices_apiKey = textAnalyticsApiKey;
		AzureContentProcessor fileProcessor = new AzureContentProcessor(properties);
		ProcessingSummary summary = new ProcessingSummary();
		List<PurviewAsset> blobAssets = selectBlobAssets(sensitiveAssets, fileExtension);

		for (PurviewAsset asset : blobAssets) {
			processBlobAsset(asset, fileProcessor, mode, tprh, summary);
		}

		summary.totalEntitiesFound = fileProcessor.total_entities_found;
		summary.totalSkippedEntities = fileProcessor.total_skipped_entities;
		return summary;
	}

	private List<PurviewAsset> selectBlobAssets(List<PurviewAsset> sensitiveAssets, String fileExtension) {
		List<PurviewAsset> blobAssets = new ArrayList<>();
		for (PurviewAsset asset : sensitiveAssets) {
			if (!asset.hasBlobLikeQualifiedName()) {
				continue;
			}
			if (!matchesAnyHint(asset, purviewConfig.fileEntityHints)) {
				continue;
			}
			if (!matchesQualifiedNamePrefix(asset)) {
				continue;
			}
			if (fileExtension != null && asset.getName() != null
					&& !asset.getName().toLowerCase().endsWith(fileExtension.toLowerCase())) {
				continue;
			}
			blobAssets.add(asset);
		}
		return blobAssets;
	}

	private void processBlobAsset(PurviewAsset asset, AzureContentProcessor fileProcessor, String mode,
			ThalesProtectRevealHelper tprh, ProcessingSummary summary) throws IOException {
		String sourceContainerName = asset.getStorageContainerName();
		String sourceBlobName = asset.getStorageBlobName();
		BlobContainerClient sourceContainer = blobServiceClient.getBlobContainerClient(sourceContainerName);
		BlobClient sourceBlob = sourceContainer.getBlobClient(sourceBlobName);

		String targetContainerName = purviewConfig.storageTargetContainer;
		String targetBlobName = buildTargetBlobName(sourceBlobName, mode);
		BlobContainerClient targetContainer = blobServiceClient.getBlobContainerClient(targetContainerName);
		if (!targetContainer.exists()) {
			targetContainer.create();
		}

		ProcessedContentArtifacts artifacts = documentConversionService.isTextLikeFileName(sourceBlobName)
				? processTextLikeBlob(sourceBlob, fileProcessor, asset, tprh, mode)
				: processDocumentBlob(sourceBlob, fileProcessor, asset, tprh, mode);
		writeBlobArtifact(targetContainer, targetBlobName, artifacts.outputText);
		if (shouldWriteExtractedText()) {
			writeBlobArtifact(targetContainer, buildArtifactBlobName(sourceBlobName, "extracted", null),
					artifacts.extractedText);
		}
		if (shouldWriteFindingsReport() && "protect".equalsIgnoreCase(mode)) {
			writeBlobArtifact(targetContainer, buildArtifactBlobName(sourceBlobName, "findings", ".json"),
					artifacts.findingsReport(mode, asset.getQualifiedName()));
		}
		summary.processedAssetCount++;
		summary.processedRecordCount += artifacts.recordCount;
		System.out.println("Processed Purview asset " + asset.getQualifiedName() + " -> " + targetBlobName);
	}

	private ProcessedContentArtifacts processTextLikeBlob(BlobClient sourceBlob, AzureContentProcessor fileProcessor,
			PurviewAsset asset, ThalesProtectRevealHelper tprh, String mode) throws IOException {
		try (BlobInputStream blobInputStream = sourceBlob.openInputStream()) {
			return fileProcessor.processStreamArtifacts(blobInputStream, asset.getQualifiedName(), tprh, mode, false);
		}
	}

	private ProcessedContentArtifacts processDocumentBlob(BlobClient sourceBlob, AzureContentProcessor fileProcessor,
			PurviewAsset asset, ThalesProtectRevealHelper tprh, String mode) throws IOException {
		String sourceBlobName = asset.getStorageBlobName();
		String fileName = sourceBlobName == null ? asset.getName() : sourceBlobName;
		String suffix = fileName != null && fileName.contains(".")
				? fileName.substring(fileName.lastIndexOf('.'))
				: ".tmp";
		Path tempFile = Files.createTempFile("purview-asset-", suffix);
		try {
			sourceBlob.downloadToFile(tempFile.toString(), true);
			String extractedText = documentConversionService.extractText(tempFile.toFile());
			return fileProcessor.processTextArtifacts(extractedText, asset.getQualifiedName(), tprh, mode, false);
		} finally {
			Files.deleteIfExists(tempFile);
		}
	}

	private String buildTargetBlobName(String sourceBlobName, String mode) {
		return buildArtifactBlobName(sourceBlobName, "protect".equalsIgnoreCase(mode) ? "protected" : "revealed", null);
	}

	private String buildArtifactBlobName(String sourceBlobName, String label, String forcedExtension) {
		String prefix = purviewConfig.storageTargetPrefix == null ? "" : purviewConfig.storageTargetPrefix.trim();
		if (!prefix.isEmpty() && !prefix.endsWith("/")) {
			prefix = prefix + "/";
		}
		String normalizedName = sourceBlobName.replace('\\', '/');
		String targetName = prefix + label + "-" + normalizedName;
		if (forcedExtension == null) {
			return targetName;
		}
		return targetName + forcedExtension;
	}

	private void writeBlobArtifact(BlobContainerClient targetContainer, String blobName, String content) {
		targetContainer.getBlobClient(blobName)
				.getBlockBlobClient()
				.upload(BinaryData.fromString(content), true);
	}

	private boolean shouldWriteExtractedText() {
		return Boolean.parseBoolean(properties.getProperty("UNSTRUCTURED_OUTPUT_WRITE_EXTRACTED_TEXT", "false"));
	}

	private boolean shouldWriteFindingsReport() {
		return Boolean.parseBoolean(properties.getProperty("UNSTRUCTURED_OUTPUT_WRITE_FINDINGS_REPORT", "false"));
	}

	private boolean matchesQualifiedNamePrefix(PurviewAsset asset) {
		if (purviewConfig.storageQualifiedNamePrefixes.isEmpty()) {
			return true;
		}
		for (String prefix : purviewConfig.storageQualifiedNamePrefixes) {
			if (asset.referencesQualifiedNamePrefix(prefix)) {
				return true;
			}
		}
		return false;
	}

	private boolean matchesAnyHint(PurviewAsset asset, List<String> hints) {
		for (String hint : hints) {
			if (asset.matchesHint(hint)) {
				return true;
			}
		}
		return false;
	}

	public static class ProcessingSummary {
		public int processedAssetCount;
		public int processedRecordCount;
		public int totalEntitiesFound;
		public int totalSkippedEntities;
	}
}

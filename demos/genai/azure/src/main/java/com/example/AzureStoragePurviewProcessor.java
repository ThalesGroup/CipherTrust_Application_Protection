package com.example;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import com.azure.storage.blob.BlobClient;
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobServiceClient;
import com.azure.storage.blob.BlobServiceClientBuilder;
import com.azure.storage.blob.specialized.BlobInputStream;
import com.azure.storage.blob.specialized.BlockBlobClient;

/**
 * Reads the same blob/file assets Purview classified, protects their content,
 * and uploads the protected output back to Azure Storage.
 */
public class AzureStoragePurviewProcessor {

	private final Properties properties;
	private final PurviewConfig purviewConfig;
	private final BlobServiceClient blobServiceClient;

	public AzureStoragePurviewProcessor(Properties properties, PurviewConfig purviewConfig) {
		this.properties = properties;
		this.purviewConfig = purviewConfig;
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
		BlobClient targetBlob = targetContainer.getBlobClient(targetBlobName);

		BlockBlobClient blockBlobClient = targetBlob.getBlockBlobClient();
		try (BlobInputStream blobInputStream = sourceBlob.openInputStream();
				OutputStream outputStream = blockBlobClient.getBlobOutputStream(true)) {
			int processedRecords = fileProcessor.processStream(blobInputStream, outputStream, asset.getQualifiedName(),
					tprh, mode, false);
			summary.processedAssetCount++;
			summary.processedRecordCount += processedRecords;
			System.out.println("Processed Purview asset " + asset.getQualifiedName() + " -> " + targetBlobName);
		}
	}

	private String buildTargetBlobName(String sourceBlobName, String mode) {
		String prefix = purviewConfig.storageTargetPrefix == null ? "" : purviewConfig.storageTargetPrefix.trim();
		if (!prefix.isEmpty() && !prefix.endsWith("/")) {
			prefix = prefix + "/";
		}
		return prefix + ("protect".equalsIgnoreCase(mode) ? "protected-" : "revealed-")
				+ sourceBlobName.replace('\\', '/');
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

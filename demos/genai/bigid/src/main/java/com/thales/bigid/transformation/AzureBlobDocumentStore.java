package com.thales.bigid.transformation;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import com.azure.core.util.BinaryData;
import com.azure.storage.blob.BlobClient;
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobServiceClient;
import com.azure.storage.blob.BlobServiceClientBuilder;

public class AzureBlobDocumentStore implements RemoteDocumentStore {

	private final RuntimeConfig config;
	private final BlobServiceClient blobServiceClient;

	public AzureBlobDocumentStore(RuntimeConfig config) {
		this.config = config;
		this.blobServiceClient = new BlobServiceClientBuilder()
				.connectionString(config.azureStorageConnectionString)
				.buildClient();
	}

	@Override
	public boolean matchesAsset(BigIdAsset asset) {
		return asset != null && asset.looksLikeBlobObject();
	}

	@Override
	public Path downloadToTempFile(BigIdAsset asset) throws IOException {
		String container = asset.getStorageContainerName();
		String blobName = asset.getStorageBlobName();
		if (container == null || blobName == null) {
			throw new IOException("Unable to resolve Azure Blob path from BigID asset: " + asset);
		}
		BlobClient blobClient = blobServiceClient.getBlobContainerClient(container).getBlobClient(blobName);
		String fileName = asset.getName() != null ? asset.getName() : Path.of(blobName).getFileName().toString();
		String suffix = fileName.contains(".") ? fileName.substring(fileName.lastIndexOf('.')) : ".tmp";
		Path tempFile = Files.createTempFile("bigid-asset-", suffix);
		BinaryData content = blobClient.downloadContent();
		Files.write(tempFile, content.toBytes());
		return tempFile;
	}

	@Override
	public void writeProtectedText(BigIdAsset asset, String protectedText) {
		writeTextArtifact(asset, protectedText, "protected", ".txt");
	}

	@Override
	public void writeExtractedText(BigIdAsset asset, String extractedText) {
		writeTextArtifact(asset, extractedText, "extracted", ".txt");
	}

	@Override
	public void writeFindingsReport(BigIdAsset asset, String findingsJson) {
		writeTextArtifact(asset, findingsJson, "findings", ".json");
	}

	private void writeTextArtifact(BigIdAsset asset, String content, String label, String extension) {
		BlobContainerClient targetContainer = blobServiceClient.getBlobContainerClient(config.azureStorageTargetContainer);
		if (!targetContainer.exists()) {
			targetContainer.create();
		}
		String targetBlobName = buildTargetBlobName(asset, label, extension);
		targetContainer.getBlobClient(targetBlobName)
				.getBlockBlobClient()
				.upload(BinaryData.fromString(content), true);
		System.out.println("Uploaded " + label + " blob -> " + targetBlobName);
	}

	@Override
	public boolean matchesConfiguredPrefix(BigIdAsset asset) {
		List<String> prefixes = config.azureStorageQualifiedNamePrefixes;
		if (prefixes.isEmpty()) {
			return true;
		}
		for (String prefix : prefixes) {
			if (asset.referencesQualifiedNamePrefix(prefix)) {
				return true;
			}
		}
		return false;
	}

	@Override
	public String describeTarget(BigIdAsset asset) {
		return "azure://" + config.azureStorageTargetContainer;
	}

	private String buildTargetBlobName(BigIdAsset asset, String label, String extension) {
		String sourceBlobName = asset.getStorageBlobName();
		String prefix = config.azureStorageTargetPrefix == null ? "" : config.azureStorageTargetPrefix.trim();
		if (!prefix.isEmpty() && !prefix.endsWith("/")) {
			prefix = prefix + "/";
		}
		String fileName = sourceBlobName == null ? asset.getName() : sourceBlobName.replace('\\', '/');
		return prefix + label + "-" + fileName + extension;
	}
}

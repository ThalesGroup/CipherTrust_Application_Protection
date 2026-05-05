package com.thales.bigid.transformation;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import com.google.auth.Credentials;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;

public class GcsDocumentStore implements RemoteDocumentStore {

	private final RuntimeConfig config;
	private final Storage storage;

	public GcsDocumentStore(RuntimeConfig config) throws IOException {
		this.config = config;
		this.storage = buildStorage(config);
	}

	@Override
	public boolean matchesAsset(BigIdAsset asset) {
		return asset != null && asset.looksLikeGcsObject();
	}

	@Override
	public boolean matchesConfiguredPrefix(BigIdAsset asset) {
		if (config.gcsQualifiedNamePrefixes.isEmpty()) {
			return true;
		}
		for (String prefix : config.gcsQualifiedNamePrefixes) {
			if (asset.referencesQualifiedNamePrefix(prefix)) {
				return true;
			}
		}
		return false;
	}

	@Override
	public Path downloadToTempFile(BigIdAsset asset) throws IOException {
		String bucket = asset.getGcsBucketName();
		String objectName = asset.getGcsObjectName();
		if (bucket == null || objectName == null) {
			throw new IOException("Unable to resolve GCS object path from BigID asset: " + asset);
		}
		String fileName = asset.getName() != null ? asset.getName() : Path.of(objectName).getFileName().toString();
		String suffix = fileName.contains(".") ? fileName.substring(fileName.lastIndexOf('.')) : ".tmp";
		Path tempFile = Files.createTempFile("bigid-gcs-asset-", suffix);
		Files.write(tempFile, storage.readAllBytes(bucket, objectName));
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

	@Override
	public String describeTarget(BigIdAsset asset) {
		return "gs://" + config.gcsTargetBucket;
	}

	private void writeTextArtifact(BigIdAsset asset, String content, String label, String extension) {
		String targetObject = buildTargetObject(asset, label, extension);
		BlobInfo blobInfo = BlobInfo.newBuilder(BlobId.of(config.gcsTargetBucket, targetObject))
				.setContentType(".json".equals(extension) ? "application/json" : "text/plain; charset=utf-8")
				.build();
		storage.create(blobInfo, content.getBytes(StandardCharsets.UTF_8));
		System.out.println("Uploaded " + label + " GCS object -> " + targetObject);
	}

	private String buildTargetObject(BigIdAsset asset, String label, String extension) {
		String prefix = config.gcsTargetPrefix == null ? "" : config.gcsTargetPrefix.trim();
		if (!prefix.isEmpty() && !prefix.endsWith("/")) {
			prefix = prefix + "/";
		}
		String objectName = asset.getGcsObjectName();
		String fileName = objectName == null ? asset.getName() : objectName.replace('\\', '/');
		return prefix + label + "-" + fileName + extension;
	}

	private Storage buildStorage(RuntimeConfig config) throws IOException {
		StorageOptions.Builder builder = StorageOptions.newBuilder();
		if (config.gcsProjectId != null) {
			builder.setProjectId(config.gcsProjectId);
		}
		if (config.gcsCredentialsPath != null) {
			try (java.io.InputStream inputStream = Files.newInputStream(config.gcsCredentialsPath)) {
				Credentials credentials = GoogleCredentials.fromStream(inputStream);
				builder.setCredentials(credentials);
			}
		}
		return builder.build().getService();
	}
}

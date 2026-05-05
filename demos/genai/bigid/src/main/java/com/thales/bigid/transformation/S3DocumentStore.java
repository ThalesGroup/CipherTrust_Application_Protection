package com.thales.bigid.transformation;

import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;

import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.auth.credentials.AwsSessionCredentials;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.S3Configuration;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

public class S3DocumentStore implements RemoteDocumentStore {

	private final RuntimeConfig config;
	private final S3Client s3Client;

	public S3DocumentStore(RuntimeConfig config) {
		this.config = config;
		this.s3Client = buildClient(config);
	}

	@Override
	public boolean matchesAsset(BigIdAsset asset) {
		return asset != null && asset.looksLikeS3Object();
	}

	@Override
	public boolean matchesConfiguredPrefix(BigIdAsset asset) {
		if (config.s3QualifiedNamePrefixes.isEmpty()) {
			return true;
		}
		for (String prefix : config.s3QualifiedNamePrefixes) {
			if (asset.referencesQualifiedNamePrefix(prefix)) {
				return true;
			}
		}
		return false;
	}

	@Override
	public Path downloadToTempFile(BigIdAsset asset) throws IOException {
		String bucket = asset.getS3BucketName();
		String key = asset.getS3ObjectKey();
		if (bucket == null || key == null) {
			throw new IOException("Unable to resolve S3 object path from BigID asset: " + asset);
		}
		String fileName = asset.getName() != null ? asset.getName() : Path.of(key).getFileName().toString();
		String suffix = fileName.contains(".") ? fileName.substring(fileName.lastIndexOf('.')) : ".tmp";
		Path tempFile = Files.createTempFile("bigid-s3-asset-", suffix);
		s3Client.getObject(GetObjectRequest.builder().bucket(bucket).key(key).build(), tempFile);
		return tempFile;
	}

	@Override
	public void writeProtectedText(BigIdAsset asset, String protectedText) throws IOException {
		writeTextArtifact(asset, protectedText, "protected", ".txt");
	}

	@Override
	public void writeExtractedText(BigIdAsset asset, String extractedText) throws IOException {
		writeTextArtifact(asset, extractedText, "extracted", ".txt");
	}

	@Override
	public void writeFindingsReport(BigIdAsset asset, String findingsJson) throws IOException {
		writeTextArtifact(asset, findingsJson, "findings", ".json");
	}

	@Override
	public String describeTarget(BigIdAsset asset) {
		return "s3://" + config.s3TargetBucket;
	}

	private void writeTextArtifact(BigIdAsset asset, String content, String label, String extension) {
		String targetKey = buildTargetKey(asset, label, extension);
		s3Client.putObject(PutObjectRequest.builder()
				.bucket(config.s3TargetBucket)
				.key(targetKey)
				.contentType(".json".equals(extension) ? "application/json" : "text/plain; charset=utf-8")
				.build(), RequestBody.fromString(content));
		System.out.println("Uploaded " + label + " S3 object -> " + targetKey);
	}

	private String buildTargetKey(BigIdAsset asset, String label, String extension) {
		String prefix = config.s3TargetPrefix == null ? "" : config.s3TargetPrefix.trim();
		if (!prefix.isEmpty() && !prefix.endsWith("/")) {
			prefix = prefix + "/";
		}
		String objectKey = asset.getS3ObjectKey();
		String fileName = objectKey == null ? asset.getName() : objectKey.replace('\\', '/');
		return prefix + label + "-" + fileName + extension;
	}

	private S3Client buildClient(RuntimeConfig config) {
		var builder = S3Client.builder().region(Region.of(config.s3Region))
				.serviceConfiguration(S3Configuration.builder()
						.pathStyleAccessEnabled(config.s3PathStyleAccess)
						.build())
				.credentialsProvider(resolveCredentials(config));
		if (config.s3Endpoint != null) {
			builder.endpointOverride(URI.create(config.s3Endpoint));
		}
		return builder.build();
	}

	private AwsCredentialsProvider resolveCredentials(RuntimeConfig config) {
		if (config.s3AccessKey != null && config.s3SecretKey != null && config.s3SessionToken != null) {
			return StaticCredentialsProvider.create(AwsSessionCredentials.create(config.s3AccessKey,
					config.s3SecretKey, config.s3SessionToken));
		}
		if (config.s3AccessKey != null && config.s3SecretKey != null) {
			return StaticCredentialsProvider.create(AwsBasicCredentials.create(config.s3AccessKey, config.s3SecretKey));
		}
		return DefaultCredentialsProvider.create();
	}
}

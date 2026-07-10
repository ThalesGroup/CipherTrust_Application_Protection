package com.example;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.Set;

/**
 * Represents a classified asset returned by Purview search.
 */
public class PurviewAsset {

	private final String id;
	private final String name;
	private final String qualifiedName;
	private final String entityType;
	private final String assetType;
	private final Set<String> classifications;

	public PurviewAsset(String id, String name, String qualifiedName, String entityType, String assetType,
			Set<String> classifications) {
		this.id = id;
		this.name = name;
		this.qualifiedName = qualifiedName;
		this.entityType = entityType;
		this.assetType = assetType;
		this.classifications = new LinkedHashSet<>(classifications);
	}

	public String getId() {
		return id;
	}

	public String getName() {
		return name;
	}

	public String getQualifiedName() {
		return qualifiedName;
	}

	public String getEntityType() {
		return entityType;
	}

	public String getAssetType() {
		return assetType;
	}

	public Set<String> getClassifications() {
		return Collections.unmodifiableSet(classifications);
	}

	public boolean matchesHint(String hint) {
		return containsIgnoreCase(assetType, hint) || containsIgnoreCase(entityType, hint)
				|| containsIgnoreCase(qualifiedName, hint);
	}

	public boolean referencesTable(String tableName) {
		return containsIgnoreCase(qualifiedName, tableName);
	}

	public boolean referencesQualifiedNamePrefix(String prefix) {
		return containsIgnoreCase(qualifiedName, prefix);
	}

	public String getNormalizedQualifiedName() {
		return qualifiedName == null ? null : qualifiedName.replace('\\', '/');
	}

	public String getStorageContainerName() {
		String[] parts = getStoragePathParts();
		return parts.length > 0 ? parts[0] : null;
	}

	public String getStorageBlobName() {
		String[] parts = getStoragePathParts();
		if (parts.length <= 1) {
			return null;
		}
		StringBuilder blobName = new StringBuilder();
		for (int i = 1; i < parts.length; i++) {
			if (i > 1) {
				blobName.append('/');
			}
			blobName.append(parts[i]);
		}
		return blobName.toString();
	}

	public boolean hasBlobLikeQualifiedName() {
		return getStorageContainerName() != null && getStorageBlobName() != null;
	}

	private String[] getStoragePathParts() {
		if (qualifiedName == null || qualifiedName.isBlank()) {
			return new String[0];
		}
		String normalized = qualifiedName.replace('\\', '/');
		try {
			URI uri = new URI(normalized);
			String path = uri.getPath();
			if (path == null || path.isBlank()) {
				return new String[0];
			}
			return trimEmptySegments(path.split("/"));
		} catch (URISyntaxException ex) {
			int schemeIndex = normalized.indexOf("://");
			String path = schemeIndex >= 0 ? normalized.substring(schemeIndex + 3) : normalized;
			int firstSlash = path.indexOf('/');
			if (firstSlash >= 0) {
				path = path.substring(firstSlash + 1);
			}
			return trimEmptySegments(path.split("/"));
		}
	}

	private String[] trimEmptySegments(String[] rawParts) {
		return java.util.Arrays.stream(rawParts).filter(part -> part != null && !part.isBlank()).toArray(String[]::new);
	}

	public static boolean containsIgnoreCase(String source, String fragment) {
		if (source == null || fragment == null) {
			return false;
		}
		return source.toLowerCase().contains(fragment.toLowerCase());
	}
}

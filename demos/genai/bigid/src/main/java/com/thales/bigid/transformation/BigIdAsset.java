package com.thales.bigid.transformation;

import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.Set;

import org.json.JSONArray;
import org.json.JSONObject;

public class BigIdAsset {

	private final String id;
	private final String name;
	private final String path;
	private final String type;
	private final Set<String> classifications;

	public BigIdAsset(String id, String name, String path, String type, Set<String> classifications) {
		this.id = id;
		this.name = name;
		this.path = path;
		this.type = type;
		this.classifications = classifications == null ? Collections.emptySet() : new LinkedHashSet<>(classifications);
	}

	public String getId() {
		return id;
	}

	public String getName() {
		return name;
	}

	public String getPath() {
		return path;
	}

	public String getType() {
		return type;
	}

	public Set<String> getClassifications() {
		return Collections.unmodifiableSet(classifications);
	}

	public boolean hasClassificationHint(Iterable<String> hints) {
		if (hints == null) {
			return true;
		}
		for (String hint : hints) {
			for (String classification : classifications) {
				if (classification.equalsIgnoreCase(hint) || classification.toLowerCase().contains(hint.toLowerCase())) {
					return true;
				}
			}
		}
		return classifications.isEmpty();
	}

	public boolean looksLikeStructuredColumn() {
		String combined = ((type == null ? "" : type) + " " + (path == null ? "" : path)).toLowerCase();
		return combined.contains("column") || combined.contains("field");
	}

	public String inferColumnName() {
		if (name != null && !name.isBlank()) {
			return stripQuotes(lastToken(name));
		}
		if (path != null) {
			return stripQuotes(lastToken(path));
		}
		return null;
	}

	public String inferTableName() {
		if (path == null || path.isBlank()) {
			return null;
		}
		String normalized = path.replace('\\', '/').replace(':', '/');
		String[] slashParts = normalized.split("/");
		if (slashParts.length >= 2) {
			String candidate = slashParts[slashParts.length - 2];
			if (!candidate.isBlank()) {
				return stripQuotes(candidate);
			}
		}
		String[] dotParts = normalized.split("\\.");
		if (dotParts.length >= 2) {
			return stripQuotes(dotParts[dotParts.length - 2]);
		}
		return null;
	}

	public boolean looksLikeBlobObject() {
		if (path == null) {
			return false;
		}
		String normalized = path.toLowerCase();
		return normalized.contains(".blob.core.windows.net/")
				|| normalized.contains(".dfs.core.windows.net/")
				|| normalized.startsWith("abfss://")
				|| normalized.startsWith("wasbs://");
	}

	public boolean looksLikeS3Object() {
		if (path == null) {
			return false;
		}
		String normalized = path.toLowerCase();
		return normalized.startsWith("s3://")
				|| normalized.startsWith("s3a://")
				|| normalized.startsWith("s3n://")
				|| normalized.startsWith("arn:aws:s3:::")
				|| normalized.contains(".s3.amazonaws.com/")
				|| normalized.contains("s3.amazonaws.com/");
	}

	public boolean looksLikeGcsObject() {
		if (path == null) {
			return false;
		}
		String normalized = path.toLowerCase();
		return normalized.startsWith("gs://")
				|| normalized.contains("storage.googleapis.com/")
				|| normalized.contains(".storage.googleapis.com/");
	}

	public String getStorageContainerName() {
		if (path == null) {
			return null;
		}
		String normalized = path.replace('\\', '/');
		String lower = normalized.toLowerCase();
		if (lower.startsWith("abfss://") || lower.startsWith("wasbs://")) {
			int schemeEnd = normalized.indexOf("://");
			int atIndex = normalized.indexOf('@', schemeEnd + 3);
			if (atIndex > schemeEnd) {
				return normalized.substring(schemeEnd + 3, atIndex);
			}
		}
		int hostMarker = lower.indexOf(".blob.core.windows.net/");
		if (hostMarker < 0) {
			hostMarker = lower.indexOf(".dfs.core.windows.net/");
		}
		if (hostMarker >= 0) {
			int slash = normalized.indexOf('/', normalized.indexOf("//") + 2);
			if (slash >= 0) {
				String remaining = normalized.substring(slash + 1);
				String[] parts = remaining.split("/", 2);
				return parts.length > 0 ? parts[0] : null;
			}
		}
		return null;
	}

	public String getStorageBlobName() {
		if (path == null) {
			return null;
		}
		String normalized = path.replace('\\', '/');
		String lower = normalized.toLowerCase();
		if (lower.startsWith("abfss://") || lower.startsWith("wasbs://")) {
			int slashAfterHost = normalized.indexOf('/', normalized.indexOf('@'));
			return slashAfterHost >= 0 ? normalized.substring(slashAfterHost + 1) : null;
		}
		int hostMarker = lower.indexOf(".blob.core.windows.net/");
		if (hostMarker < 0) {
			hostMarker = lower.indexOf(".dfs.core.windows.net/");
		}
		if (hostMarker >= 0) {
			int slash = normalized.indexOf('/', normalized.indexOf("//") + 2);
			if (slash >= 0) {
				String remaining = normalized.substring(slash + 1);
				String[] parts = remaining.split("/", 2);
				return parts.length == 2 ? parts[1] : null;
			}
		}
		return null;
	}

	public String getS3BucketName() {
		if (path == null) {
			return null;
		}
		String normalized = path.replace('\\', '/');
		String lower = normalized.toLowerCase();
		if (lower.startsWith("s3://") || lower.startsWith("s3a://") || lower.startsWith("s3n://")) {
			int schemeEnd = normalized.indexOf("://");
			int slash = normalized.indexOf('/', schemeEnd + 3);
			if (slash > schemeEnd) {
				return normalized.substring(schemeEnd + 3, slash);
			}
			return normalized.substring(schemeEnd + 3);
		}
		if (lower.startsWith("arn:aws:s3:::")) {
			String remaining = normalized.substring("arn:aws:s3:::".length());
			int slash = remaining.indexOf('/');
			return slash >= 0 ? remaining.substring(0, slash) : remaining;
		}
		int hostIndex = lower.indexOf(".s3.amazonaws.com/");
		if (hostIndex > 0) {
			int schemeIndex = normalized.indexOf("://");
			return normalized.substring(schemeIndex + 3, hostIndex);
		}
		int pathHostIndex = lower.indexOf("s3.amazonaws.com/");
		if (pathHostIndex >= 0) {
			int start = pathHostIndex + "s3.amazonaws.com/".length();
			String remaining = normalized.substring(start);
			int slash = remaining.indexOf('/');
			return slash >= 0 ? remaining.substring(0, slash) : remaining;
		}
		return null;
	}

	public String getS3ObjectKey() {
		if (path == null) {
			return null;
		}
		String normalized = path.replace('\\', '/');
		String lower = normalized.toLowerCase();
		if (lower.startsWith("s3://") || lower.startsWith("s3a://") || lower.startsWith("s3n://")) {
			int schemeEnd = normalized.indexOf("://");
			int slash = normalized.indexOf('/', schemeEnd + 3);
			return slash >= 0 ? normalized.substring(slash + 1) : null;
		}
		if (lower.startsWith("arn:aws:s3:::")) {
			String remaining = normalized.substring("arn:aws:s3:::".length());
			int slash = remaining.indexOf('/');
			return slash >= 0 ? remaining.substring(slash + 1) : null;
		}
		int hostIndex = lower.indexOf(".s3.amazonaws.com/");
		if (hostIndex > 0) {
			return normalized.substring(hostIndex + ".s3.amazonaws.com/".length());
		}
		int pathHostIndex = lower.indexOf("s3.amazonaws.com/");
		if (pathHostIndex >= 0) {
			String remaining = normalized.substring(pathHostIndex + "s3.amazonaws.com/".length());
			int slash = remaining.indexOf('/');
			return slash >= 0 ? remaining.substring(slash + 1) : null;
		}
		return null;
	}

	public String getGcsBucketName() {
		if (path == null) {
			return null;
		}
		String normalized = path.replace('\\', '/');
		String lower = normalized.toLowerCase();
		if (lower.startsWith("gs://")) {
			int slash = normalized.indexOf('/', "gs://".length());
			if (slash > 0) {
				return normalized.substring("gs://".length(), slash);
			}
			return normalized.substring("gs://".length());
		}
		int hostIndex = lower.indexOf(".storage.googleapis.com/");
		if (hostIndex > 0) {
			int schemeIndex = normalized.indexOf("://");
			return normalized.substring(schemeIndex + 3, hostIndex);
		}
		int pathHostIndex = lower.indexOf("storage.googleapis.com/");
		if (pathHostIndex >= 0) {
			String remaining = normalized.substring(pathHostIndex + "storage.googleapis.com/".length());
			int slash = remaining.indexOf('/');
			return slash >= 0 ? remaining.substring(0, slash) : remaining;
		}
		return null;
	}

	public String getGcsObjectName() {
		if (path == null) {
			return null;
		}
		String normalized = path.replace('\\', '/');
		String lower = normalized.toLowerCase();
		if (lower.startsWith("gs://")) {
			int slash = normalized.indexOf('/', "gs://".length());
			return slash >= 0 ? normalized.substring(slash + 1) : null;
		}
		int hostIndex = lower.indexOf(".storage.googleapis.com/");
		if (hostIndex > 0) {
			return normalized.substring(hostIndex + ".storage.googleapis.com/".length());
		}
		int pathHostIndex = lower.indexOf("storage.googleapis.com/");
		if (pathHostIndex >= 0) {
			String remaining = normalized.substring(pathHostIndex + "storage.googleapis.com/".length());
			int slash = remaining.indexOf('/');
			return slash >= 0 ? remaining.substring(slash + 1) : null;
		}
		return null;
	}

	public boolean referencesQualifiedNamePrefix(String prefix) {
		if (prefix == null || prefix.isBlank() || path == null) {
			return false;
		}
		return path.toLowerCase().startsWith(prefix.toLowerCase());
	}

	private String lastToken(String value) {
		String normalized = value.replace('\\', '/').replace(':', '/');
		String[] slashParts = normalized.split("/");
		String slashToken = slashParts[slashParts.length - 1];
		String[] dotParts = slashToken.split("\\.");
		return dotParts[dotParts.length - 1];
	}

	private String stripQuotes(String value) {
		return value == null ? null : value.replace("[", "").replace("]", "").replace("\"", "").trim();
	}

	@Override
	public String toString() {
		return "BigIdAsset{id='" + id + "', name='" + name + "', path='" + path + "', type='" + type
				+ "', classifications=" + classifications + "}";
	}

	public JSONObject toJson() {
		JSONObject json = new JSONObject();
		json.put("id", id);
		json.put("name", name);
		json.put("path", path);
		json.put("type", type);
		json.put("classifications", new JSONArray(classifications));
		json.put("looksLikeStructuredColumn", looksLikeStructuredColumn());
		json.put("inferredTableName", inferTableName());
		json.put("inferredColumnName", inferColumnName());
		json.put("looksLikeBlobObject", looksLikeBlobObject());
		json.put("storageContainerName", getStorageContainerName());
		json.put("storageBlobName", getStorageBlobName());
		json.put("looksLikeS3Object", looksLikeS3Object());
		json.put("s3BucketName", getS3BucketName());
		json.put("s3ObjectKey", getS3ObjectKey());
		json.put("looksLikeGcsObject", looksLikeGcsObject());
		json.put("gcsBucketName", getGcsBucketName());
		json.put("gcsObjectName", getGcsObjectName());
		return json;
	}
}

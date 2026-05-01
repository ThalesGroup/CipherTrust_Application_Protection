package com.example;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Small Purview REST client for kicking off scans and discovering classified assets.
 */
public class PurviewClient {

	private static final String DATA_MAP_API_VERSION = "2023-09-01";
	private static final String SCAN_API_VERSION = "2023-09-01";

	private final PurviewConfig config;
	private final HttpClient httpClient;

	public PurviewClient(PurviewConfig config) {
		this.config = config;
		this.httpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(30)).build();
	}

	public void runConfiguredScanAndWait() throws IOException, InterruptedException {
		if (!config.runScan) {
			return;
		}
		if (config.dataSourceName == null || config.scanName == null) {
			throw new IllegalArgumentException(
					"PURVIEW_DATASOURCE_NAME and PURVIEW_SCAN_NAME are required when PURVIEW_RUN_SCAN=true.");
		}

		String runId = UUID.randomUUID().toString();
		String path = String.format("/scan/datasources/%s/scans/%s:run?runId=%s&api-version=%s",
				urlEncode(config.dataSourceName), urlEncode(config.scanName), urlEncode(runId), SCAN_API_VERSION);
		send("POST", path, null);
		System.out.println("Started Purview scan run " + runId + " for " + config.dataSourceName + "/" + config.scanName);

		if (config.waitForScanCompletion) {
			waitForScan(runId);
		}
	}

	public List<PurviewAsset> searchSensitiveAssets() throws IOException, InterruptedException {
		List<PurviewAsset> assets = new ArrayList<>();
		String continuationToken = null;

		do {
			JSONObject requestBody = new JSONObject();
			requestBody.put("keywords", JSONObject.NULL);
			requestBody.put("limit", config.searchLimit);
			JSONObject filter = new JSONObject();
			filter.put("classification", new JSONArray(config.classificationFilters));
			requestBody.put("filter", filter);
			if (continuationToken != null) {
				requestBody.put("continuationToken", continuationToken);
			}

			JSONObject response = send("POST",
					"/datamap/api/search/query?api-version=" + DATA_MAP_API_VERSION, requestBody.toString());
			JSONArray values = response.optJSONArray("value");
			if (values != null) {
				for (int i = 0; i < values.length(); i++) {
					JSONObject assetJson = values.getJSONObject(i);
					assets.add(parseAsset(assetJson));
				}
			}

			continuationToken = emptyToNull(response.optString("continuationToken", null));
		} while (continuationToken != null);

		return assets;
	}

	private void waitForScan(String runId) throws IOException, InterruptedException {
		while (true) {
			String path = String.format("/scan/datasources/%s/scans/%s/runs/%s?api-version=%s",
					urlEncode(config.dataSourceName), urlEncode(config.scanName), urlEncode(runId), SCAN_API_VERSION);
			JSONObject response = send("GET", path, null);
			String status = response.optString("status",
					response.optJSONObject("properties") != null ? response.getJSONObject("properties").optString("status")
							: "Unknown");
			System.out.println("Purview scan status: " + status);
			if ("Succeeded".equalsIgnoreCase(status)) {
				return;
			}
			if ("Failed".equalsIgnoreCase(status) || "Canceled".equalsIgnoreCase(status)
					|| "TransientFailure".equalsIgnoreCase(status)) {
				throw new IllegalStateException("Purview scan did not succeed. Final status: " + status);
			}
			Thread.sleep(config.scanPollSeconds * 1000L);
		}
	}

	private PurviewAsset parseAsset(JSONObject assetJson) {
		String id = firstNonBlank(assetJson.optString("id", null), assetJson.optString("objectId", null),
				assetJson.optString("guid", null));
		String name = assetJson.optString("name", null);
		String qualifiedName = firstNonBlank(assetJson.optString("qualifiedName", null),
				assetJson.optString("fullyQualifiedName", null));
		String entityType = assetJson.optString("entityType", null);
		String assetType = assetJson.optString("assetType", null);
		Set<String> classifications = new LinkedHashSet<>();

		Object classificationObject = assetJson.opt("classification");
		if (classificationObject instanceof JSONArray) {
			JSONArray array = (JSONArray) classificationObject;
			for (int i = 0; i < array.length(); i++) {
				Object item = array.get(i);
				if (item instanceof JSONObject) {
					JSONObject classification = (JSONObject) item;
					String typeName = firstNonBlank(classification.optString("typeName", null),
							classification.optString("name", null));
					if (typeName != null) {
						classifications.add(typeName);
					}
				} else if (item != null) {
					classifications.add(String.valueOf(item));
				}
			}
		}

		return new PurviewAsset(id, name, qualifiedName, entityType, assetType, classifications);
	}

	private JSONObject send(String method, String path, String body) throws IOException, InterruptedException {
		HttpRequest.Builder builder = HttpRequest.newBuilder().uri(URI.create(config.endpoint + path))
				.timeout(Duration.ofMinutes(2)).header("Authorization", "Bearer " + config.accessToken)
				.header("Content-Type", "application/json");

		if ("POST".equalsIgnoreCase(method)) {
			builder.POST(body == null ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofString(body));
		} else {
			builder.GET();
		}

		HttpResponse<String> response = httpClient.send(builder.build(), HttpResponse.BodyHandlers.ofString());
		if (response.statusCode() >= 300) {
			throw new IOException("Purview API call failed: HTTP " + response.statusCode() + " body=" + response.body());
		}

		if (response.body() == null || response.body().isBlank()) {
			return new JSONObject();
		}
		return new JSONObject(response.body());
	}

	private static String urlEncode(String value) {
		return URLEncoder.encode(value, StandardCharsets.UTF_8);
	}

	private static String firstNonBlank(String... values) {
		for (String value : values) {
			if (value != null && !value.isBlank()) {
				return value;
			}
		}
		return null;
	}

	private static String emptyToNull(String value) {
		if (value == null || value.isBlank()) {
			return null;
		}
		return value;
	}
}

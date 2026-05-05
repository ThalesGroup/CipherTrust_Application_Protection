package com.thales.bigid.transformation;

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

import org.json.JSONArray;
import org.json.JSONObject;

public class BigIdClient {

	private final RuntimeConfig config;
	private final HttpClient httpClient;

	public BigIdClient(RuntimeConfig config) {
		this.config = config;
		this.httpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(30)).build();
	}

	public List<BigIdAsset> querySensitiveAssets() throws IOException, InterruptedException {
		String token = getAccessToken();
		List<BigIdAsset> assets = new ArrayList<>();
		int offset = 0;

		while (true) {
			StringBuilder path = new StringBuilder("/api/v1/data-catalog?limit=")
					.append(config.bigIdPageSize)
					.append("&offset=")
					.append(offset);
			if (config.bigIdCatalogFilter != null) {
				path.append("&filter=").append(urlEncode(config.bigIdCatalogFilter));
			}

			JSONObject response = send("GET", path.toString(), null, token);
			JSONArray results = firstArray(response, "results", "data.results", "data.objects");
			if (results == null || results.length() == 0) {
				break;
			}

			for (int i = 0; i < results.length(); i++) {
				assets.add(parseAsset(results.getJSONObject(i)));
			}

			if (results.length() < config.bigIdPageSize) {
				break;
			}
			offset += config.bigIdPageSize;
		}

		return assets;
	}

	private String getAccessToken() throws IOException, InterruptedException {
		if (config.bigIdSystemToken != null) {
			return config.bigIdSystemToken;
		}

		HttpRequest request = HttpRequest.newBuilder()
				.uri(URI.create(trimTrailingSlash(config.bigIdBaseUrl) + "/api/v1/refresh-access-token"))
				.timeout(Duration.ofMinutes(1))
				.header("Authorization", "Bearer " + config.bigIdUserToken)
				.header("Content-Type", "application/json")
				.POST(HttpRequest.BodyPublishers.noBody())
				.build();
		HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
		if (response.statusCode() >= 300) {
			throw new IOException("BigID token exchange failed: HTTP " + response.statusCode() + " body="
					+ response.body());
		}
		JSONObject json = new JSONObject(response.body());
		String token = json.optString("systemToken", null);
		if (token == null || token.isBlank()) {
			throw new IOException("BigID token exchange did not return systemToken.");
		}
		return token;
	}

	private BigIdAsset parseAsset(JSONObject object) {
		String id = firstString(object, "id", "objectId", "catalog_id");
		String name = firstString(object, "name", "file_name", "object_name");
		String path = firstString(object, "path", "full_path", "location", "qualified_name", "fullyQualifiedName");
		String type = firstString(object, "type", "object_type", "asset_type");
		Set<String> classifications = new LinkedHashSet<>();

		JSONArray directClassifications = firstArray(object, "classifications", "classification");
		if (directClassifications != null) {
			for (int i = 0; i < directClassifications.length(); i++) {
				Object value = directClassifications.get(i);
				if (value instanceof JSONObject) {
					String parsed = firstString((JSONObject) value, "name", "typeName", "classification");
					if (parsed != null) {
						classifications.add(parsed);
					}
				} else if (value != null) {
					classifications.add(String.valueOf(value));
				}
			}
		}

		return new BigIdAsset(id, name, path, type, classifications);
	}

	private JSONObject send(String method, String path, String body, String token) throws IOException, InterruptedException {
		HttpRequest.Builder builder = HttpRequest.newBuilder()
				.uri(URI.create(trimTrailingSlash(config.bigIdBaseUrl) + path))
				.timeout(Duration.ofMinutes(2))
				.header("Authorization", "Bearer " + token)
				.header("Content-Type", "application/json");

		if ("POST".equalsIgnoreCase(method)) {
			builder.POST(body == null ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofString(body));
		} else {
			builder.GET();
		}

		HttpResponse<String> response = httpClient.send(builder.build(), HttpResponse.BodyHandlers.ofString());
		if (response.statusCode() >= 300) {
			throw new IOException("BigID API call failed: HTTP " + response.statusCode() + " body=" + response.body());
		}
		return response.body() == null || response.body().isBlank() ? new JSONObject() : new JSONObject(response.body());
	}

	private static JSONArray firstArray(JSONObject object, String... keys) {
		for (String key : keys) {
			Object value = dottedGet(object, key);
			if (value instanceof JSONArray) {
				return (JSONArray) value;
			}
		}
		return null;
	}

	private static String firstString(JSONObject object, String... keys) {
		for (String key : keys) {
			Object value = dottedGet(object, key);
			if (value instanceof String) {
				String stringValue = ((String) value).trim();
				if (!stringValue.isEmpty()) {
					return stringValue;
				}
			}
		}
		return null;
	}

	private static Object dottedGet(JSONObject object, String key) {
		String[] parts = key.split("\\.");
		Object current = object;
		for (String part : parts) {
			if (!(current instanceof JSONObject)) {
				return null;
			}
			JSONObject jsonObject = (JSONObject) current;
			if (!jsonObject.has(part) || jsonObject.isNull(part)) {
				return null;
			}
			current = jsonObject.get(part);
		}
		return current;
	}

	private static String trimTrailingSlash(String value) {
		return value.endsWith("/") ? value.substring(0, value.length() - 1) : value;
	}

	private static String urlEncode(String value) {
		return URLEncoder.encode(value, StandardCharsets.UTF_8);
	}
}

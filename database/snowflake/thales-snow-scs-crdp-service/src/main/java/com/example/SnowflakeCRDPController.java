package com.example;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.annotation.RequestBody;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.Collectors;
import java.util.Base64;

@RestController
public class SnowflakeCRDPController {

	private static final Logger log = LoggerFactory.getLogger(SnowflakeCRDPController.class);

	private final OkHttpClient client = new OkHttpClient();
	
	private final MediaType jsonMediaType = MediaType.get("application/json; charset=utf-8");
	private final ObjectMapper mapper = new ObjectMapper();

	// Environment variables (as before)
	private final int BATCH_SIZE = Integer.parseInt(System.getenv().getOrDefault("BATCHSIZE", "1000"));
	private final String CRDPIP = System.getenv().getOrDefault("CRDPIP",
			"http://thales-crdp-service.stuff.svc.spcs.internal");

	private final String CRDPIPPORT = System.getenv().getOrDefault("CRDPIPPORT", "8090");
	private final String BADDATATAG = System.getenv().getOrDefault("BADDATATAG", "999999999");
	private final String DEFAULTREVEALUSER = System.getenv().getOrDefault("DEFAULTREVEALUSER", "admin");

	
	private final String DEFAULTMETADATA = System.getenv().getOrDefault("DEFAULTMETADATA", "1001000");
	
	private final String DEFAULTMODE = System.getenv().getOrDefault("DEFAULTMODE", "external");
	
	private final String DEFAULTCHARPOLICY = System.getenv().getOrDefault("DEFAULTCHARPOLICY", "char-internal");
	private final String DEFAULTNBRCHARPOLICY = System.getenv().getOrDefault("DEFAULTNBRCHARPOLICY",
			"nbr-char-internal");
	private final String DEFAULTNBRNBRPOLICY = System.getenv().getOrDefault("DEFAULTNBRNBRPOLICY", "nbr-nbr-internal");

	private final String DEFAULTINTERNALCHARPOLICY = System.getenv().getOrDefault("DEFAULTINTERNALCHARPOLICY",
			"char-internal");
	private final String DEFAULTINTERNALNBRCHARPOLICY = System.getenv().getOrDefault("DEFAULTINTERNALNBRCHARPOLICY",
			"nbr-char-internal");
	private final String DEFAULTINTERNALNBRNBRPOLICY = System.getenv().getOrDefault("DEFAULTINTERNALNBRNBRPOLICY",
			"nbr-nbr-internal");

	private final String DEFAULTEXTERNALCHARPOLICY = System.getenv().getOrDefault("DEFAULTEXTERNALCHARPOLICY",
			"char-external");
	private final String DEFAULTEXTERNALNBRCHARPOLICY = System.getenv().getOrDefault("DEFAULTEXTERNALNBRCHARPOLICY",
			"nbr-char-external");
	private final String DEFAULTEXTERNALNBRNBRPOLICY = System.getenv().getOrDefault("DEFAULTEXTERNALNBRNBRPOLICY",
			"nbr-nbr-external");

	// Only INPUT_FORMAT from properties file
	@Value("${app.INPUT_FORMAT:external}")
	private String INPUT_FORMAT;

	private final String baseUrl = CRDPIP + ":" + CRDPIPPORT + "/v1/";

	// === POJOs ===
	// Updated to use Object to handle the mixed types [Integer, String] from
	// Snowflake
	public static class SnowflakeRequest {
		public List<List<Object>> data;
	}

	public static class SnowflakeResponse {
		public List<List<Object>> data;
	}

	public static class ProtectRequest {
		public String protection_policy_name;
		public List<String> data_array;
	}

	public static class RevealRequest {
		public String protection_policy_name;
		public String username;
		public List<Map<String, String>> protected_data_array;
	}

	@JsonIgnoreProperties(ignoreUnknown = true)
	public static class ProtectResponse {
		public String status;
		public List<Map<String, String>> protected_data_array;
	}

	@JsonIgnoreProperties(ignoreUnknown = true)
	public static class RevealResponse {
		public String status;
		public List<Map<String, String>> data_array;
	}

	// Helper record to manage index-value pairs internally.
	private record IndexedValue(int index, String value) {
	}

	// === Endpoints ===
	@PostMapping("/protectbulkchar")
	public SnowflakeResponse protectBulkChar(@RequestBody SnowflakeRequest request,
			@RequestHeader Map<String, String> headers) throws Exception {
		// Debug: Print incoming data format (only when debug logging is enabled)
		if (log.isDebugEnabled()) {
			headers.forEach((k, v) -> log.info("Header {} = {}", k, v));
			log.debug("=== INCOMING DATA DEBUG ===");
			log.debug("INPUT_FORMAT setting: {}", INPUT_FORMAT);
			log.debug("Raw JSON data: {}", mapper.writeValueAsString(request.data));
			log.debug("Number of rows: {}", request.data.size());
			log.debug("BATCHSIZE: {}", BATCH_SIZE);

			log.debug("=== END DEBUG ===");
		}

		return runProtect(DEFAULTCHARPOLICY, request, "protectbulk", "char", headers);
	}

	@PostMapping("/protectbulknbrchar")
	public SnowflakeResponse protectBulkNbrChar(@RequestBody SnowflakeRequest request,
			@RequestHeader Map<String, String> headers) throws Exception {
		if (log.isDebugEnabled()) {
			headers.forEach((k, v) -> log.info("Header {} = {}", k, v));
			log.debug("=== INCOMING DATA DEBUG ===");
			log.debug("INPUT_FORMAT setting: {}", INPUT_FORMAT);
			log.debug("Raw JSON data: {}", mapper.writeValueAsString(request.data));
			log.debug("Number of rows: {}", request.data.size());
			log.debug("BATCHSIZE: {}", BATCH_SIZE);
		}
		return runProtect(DEFAULTNBRCHARPOLICY, request, "protectbulk", "nbrchar", headers);
	}

	@PostMapping("/protectbulknbrnbr")
	public SnowflakeResponse protectBulkNbrNbr(@RequestBody SnowflakeRequest request,
			@RequestHeader Map<String, String> headers) throws Exception {
		if (log.isDebugEnabled()) {
			log.debug("=== INCOMING DATA DEBUG ===");
			log.debug("INPUT_FORMAT setting: {}", INPUT_FORMAT);
			log.debug("Raw JSON data: {}", mapper.writeValueAsString(request.data));
			log.debug("Number of rows: {}", request.data.size());
			log.debug("BATCHSIZE: {}", BATCH_SIZE);
		}
		return runProtect(DEFAULTNBRNBRPOLICY, request, "protectbulk", "nbrnbr", headers);
	}

	@PostMapping("/revealbulkchar")
	public SnowflakeResponse revealBulkChar(@RequestBody SnowflakeRequest request,
			@RequestHeader Map<String, String> headers) throws Exception {
		// Debug: Print incoming data format (only when debug logging is enabled)
		if (log.isDebugEnabled()) {
			log.debug("=== INCOMING REVEAL DATA DEBUG ===");
			log.debug("INPUT_FORMAT setting: {}", INPUT_FORMAT);
			log.debug("Raw JSON data: {}", mapper.writeValueAsString(request.data));
			log.debug("Headers: {}", headers);
			log.debug("Number of rows: {}", request.data.size());
			log.debug("BATCHSIZE: {}", BATCH_SIZE);


		}

		return runReveal(DEFAULTCHARPOLICY, request, "revealbulk", headers, "char");
	}

	@PostMapping("/revealbulknbrchar")
	public SnowflakeResponse revealBulkNbrChar(@RequestBody SnowflakeRequest request,
			@RequestHeader Map<String, String> headers) throws Exception {

		if (log.isDebugEnabled()) {
			log.debug("=== INCOMING REVEAL DATA DEBUG ===");
			log.debug("INPUT_FORMAT setting: {}", INPUT_FORMAT);
			log.debug("Raw JSON data: {}", mapper.writeValueAsString(request.data));
			log.debug("Headers: {}", headers);
			log.debug("Number of rows: {}", request.data.size());
			log.debug("BATCHSIZE: {}", BATCH_SIZE);
		}
		return runReveal(DEFAULTNBRCHARPOLICY, request, "revealbulk", headers, "nbrchar");
	}

	@PostMapping("/revealbulknbrnbr")
	public SnowflakeResponse revealBulkNbrNbr(@RequestBody SnowflakeRequest request,
			@RequestHeader Map<String, String> headers) throws Exception {
		if (log.isDebugEnabled()) {
			log.debug("=== INCOMING REVEAL DATA DEBUG ===");
			log.debug("INPUT_FORMAT setting: {}", INPUT_FORMAT);
			log.debug("Raw JSON data: {}", mapper.writeValueAsString(request.data));
			log.debug("Headers: {}", headers);
			log.debug("Number of rows: {}", request.data.size());
			log.debug("BATCHSIZE: {}", BATCH_SIZE);
		}
		return runReveal(DEFAULTNBRNBRPOLICY, request, "revealbulk", headers, "nbrnbr");
	}

	// === Shared Batch Runners ===
	private SnowflakeResponse runProtect(String defaultPolicy, SnowflakeRequest request, String endpoint,
			String dataType, @RequestHeader Map<String, String> headers) throws Exception {
		String mode = extractMode(headers);
		String metadata = extractMetadata(headers);

		String policy = switch (dataType.toLowerCase() + "-" + mode) {
		case "char-external" -> DEFAULTEXTERNALCHARPOLICY;
		case "nbrchar-external" -> DEFAULTEXTERNALNBRCHARPOLICY;
		case "nbrnbr-external" -> DEFAULTEXTERNALNBRNBRPOLICY;
		case "char-internal" -> DEFAULTINTERNALCHARPOLICY;
		case "nbrchar-internal" -> DEFAULTINTERNALNBRCHARPOLICY;
		case "nbrnbr-internal" -> DEFAULTINTERNALNBRNBRPOLICY;
		default -> defaultPolicy;
		};

   
		
		List<List<Object>> inputRows = request.data;
		List<List<Object>> results = new ArrayList<>();
		int effectiveBatchSize = extractBatchSize(headers);
		int loopcntr = 0;

		for (int i = 0; i < inputRows.size(); i += effectiveBatchSize) {
			int end = Math.min(i + effectiveBatchSize, inputRows.size());
			List<List<Object>> batch = inputRows.subList(i, end);
			results.addAll(handleProtectBatch(batch, policy, endpoint, i, dataType, mode, metadata));
			loopcntr++;
		}

		log.debug("NumberofChunks: {}", loopcntr);
		log.debug("BATCHSIZE: {}", effectiveBatchSize);
		SnowflakeResponse response = new SnowflakeResponse();
		response.data = results;
		return response;
	}

	private SnowflakeResponse runReveal(String defaultPolicy, SnowflakeRequest request, String endpoint,
			Map<String, String> headers, String dataType) throws Exception {
		String mode = extractMode(headers);
		String metadata = extractMetadata(headers);
		String revealUser = extractRevealUser(headers);

		String policy = switch (dataType.toLowerCase() + "-" + mode) {
		case "char-external" -> DEFAULTEXTERNALCHARPOLICY;
		case "nbrchar-external" -> DEFAULTEXTERNALNBRCHARPOLICY;
		case "nbrnbr-external" -> DEFAULTEXTERNALNBRNBRPOLICY;
		case "char-internal" -> DEFAULTINTERNALCHARPOLICY;
		case "nbrchar-internal" -> DEFAULTINTERNALNBRCHARPOLICY;
		case "nbrnbr-internal" -> DEFAULTINTERNALNBRNBRPOLICY;
		default -> defaultPolicy;
		};

		List<List<Object>> inputRows = request.data;
		List<List<Object>> results = new ArrayList<>();
		int effectiveBatchSize = extractBatchSize(headers);
		int loopcntr = 0;

		for (int i = 0; i < inputRows.size(); i += effectiveBatchSize) {
			int end = Math.min(i + effectiveBatchSize, inputRows.size());
			List<List<Object>> batch = inputRows.subList(i, end);
			results.addAll(handleRevealBatch(batch, policy, endpoint, revealUser, i, dataType, mode, metadata));
			loopcntr++;
		}

		log.debug("NumberofChunks: {}", loopcntr);
		log.debug("BATCHSIZE: {}", effectiveBatchSize);
		SnowflakeResponse response = new SnowflakeResponse();
		response.data = results;
		return response;
	}

	// === Batch Handlers (Updated to support both formats) ===
	private List<List<Object>> handleProtectBatch(List<List<Object>> batch, String policy, String endpoint,
			int batchStartIndex, String dataType, String mode, String metadata) throws Exception {

		List<IndexedValue> indexedValues;

		if ("spcs".equalsIgnoreCase(INPUT_FORMAT)) {
			// SPCS format: data is [[value1], [value2], ...] - each row is an array of
			// arguments
			indexedValues = new ArrayList<>();
			for (int i = 0; i < batch.size(); i++) {
				List<Object> row = batch.get(i);
				int rowIndex = batchStartIndex + i; // Sequential index per row
				// For single-argument functions, take the first (and likely only) argument
				String value = sanitizeForProtect(row.get(0), dataType);
				indexedValues.add(new IndexedValue(rowIndex, value));
			}
		} else {
			// External function format: data is [index, value]
			indexedValues = batch.stream().map(row -> {
				int rowIndex = ((Number) row.get(0)).intValue();
				String value = sanitizeForProtect(row.get(1), dataType);
				return new IndexedValue(rowIndex, value);
			}).collect(Collectors.toList());
		}

		// 2. Extract *only* the string values to build the request for the external
		// service.
		List<String> valuesToSend = indexedValues.stream().map(IndexedValue::value).collect(Collectors.toList());

		ProtectRequest req = new ProtectRequest();
		req.protection_policy_name = policy;
		req.data_array = valuesToSend;


		String json = mapper.writeValueAsString(req);


		log.debug("=== ======================= DEBUG ===");
		log.debug("json: {}", json);
		log.debug("endpoint: {}", endpoint);
		log.debug("baseUrl: {}", baseUrl);
		 

		Request httpRequest = new Request.Builder().url(baseUrl + endpoint)
				.post(okhttp3.RequestBody.create(json, jsonMediaType)).build();
		
	
		try (Response response = client.newCall(httpRequest).execute()) {
			ProtectResponse extResp = mapper.readValue(response.body().string(), ProtectResponse.class);

			List<List<Object>> finalResult = new ArrayList<>();
			if (extResp.protected_data_array != null && extResp.protected_data_array.size() == indexedValues.size()) {
				// 3. Recombine based on output format

				for (int i = 0; i < indexedValues.size(); i++) {
					int originalIndex = indexedValues.get(i).index();
					String protectedData = extResp.protected_data_array.get(i).get("protected_data");
					if (i ==1 & "external".equalsIgnoreCase(mode))
					{
						String metadatafromCRDP = extResp.protected_data_array.get(i).get("external_version");
						log.debug("External Metadata store this value: {}", metadatafromCRDP);
									//mapper.readTree(response.body().string()).path("external_version").asText());
					}
					if ("spcs".equalsIgnoreCase(INPUT_FORMAT)) {
						// SPCS output: just the protected data
						finalResult.add(Arrays.asList(protectedData));
					} else {
						// External function output: [index, protected_data]
						finalResult.add(Arrays.asList(originalIndex, protectedData));
					}
				}
			} else {
				// Fallback: Return BADDATATAG with appropriate format
				for (IndexedValue indexedValue : indexedValues) {
					if ("spcs".equalsIgnoreCase(INPUT_FORMAT)) {
						finalResult.add(Arrays.asList(BADDATATAG));
					} else {
						finalResult.add(Arrays.asList(indexedValue.index(), BADDATATAG));
					}
				}
			}
			return finalResult;
		}
	}

	private List<List<Object>> handleRevealBatch(List<List<Object>> batch, String policy, String endpoint,
			String revealUser, int batchStartIndex, String dataType, String mode, String metadata) throws Exception {
		// 1. Parse the incoming batch based on the INPUT_FORMAT
		List<IndexedValue> indexedValues;

		if ("spcs".equalsIgnoreCase(INPUT_FORMAT)) {
			// SPCS format: data is [value1, value2, ...] without row index
			indexedValues = new ArrayList<>();
			for (int i = 0; i < batch.size(); i++) {
				List<Object> row = batch.get(i);
				// For SPCS, each row can contain multiple values - process each value
				// separately
				for (int j = 0; j < row.size(); j++) {
					int rowIndex = batchStartIndex + (i * row.size()) + j; // Generate unique sequential index
					String value = sanitize(row.get(j)); // Process each value in the row
					indexedValues.add(new IndexedValue(rowIndex, value));
				}
			}
		} else {
			// External function format: data is [index, value]
			indexedValues = batch.stream().map(row -> {
				int rowIndex = ((Number) row.get(0)).intValue();
				String value = sanitize(row.get(1));
				return new IndexedValue(rowIndex, value);
			}).collect(Collectors.toList());
		}

		// 2. Build the request for the external service using only the values.
		List<Map<String, String>> protectedArray = indexedValues.stream().map(iv -> {
			Map<String, String> m = new HashMap<>();
			m.put("protected_data", iv.value());
			if ("external".equalsIgnoreCase(mode)) {
				m.put("external_version",metadata);
			}
			return m;
		}).collect(Collectors.toList());

		
		RevealRequest req = new RevealRequest();
		req.protection_policy_name = policy;
		req.username = revealUser;
		req.protected_data_array = protectedArray;

		String json = mapper.writeValueAsString(req);

		log.debug("=== ======================= DEBUG ===");
		log.debug("json: {}", json);
		log.debug("endpoint: {}", endpoint);
		log.debug("baseUrl: {}", baseUrl);
	 
		log.debug("User: {}", revealUser);
		
		Request httpRequest = new Request.Builder().url(baseUrl + endpoint)
				.post(okhttp3.RequestBody.create(json, jsonMediaType)).build();

	try (Response response = client.newCall(httpRequest).execute()) {
			RevealResponse extResp = mapper.readValue(response.body().string(), RevealResponse.class);

			List<List<Object>> finalResult = new ArrayList<>();
			if (extResp.data_array != null && extResp.data_array.size() == indexedValues.size()) {
				// 3. Recombine based on output format
				for (int i = 0; i < indexedValues.size(); i++) {
					int originalIndex = indexedValues.get(i).index();
					String revealedData = extResp.data_array.get(i).get("data");

					if ("spcs".equalsIgnoreCase(INPUT_FORMAT)) {
						// SPCS output: just the revealed data
						finalResult.add(Arrays.asList(revealedData));
					} else {
						// External function output: [index, revealed_data]
						finalResult.add(Arrays.asList(originalIndex, revealedData));
					}
				}
			} else {
				// Fallback: Return BADDATATAG with appropriate format
				for (IndexedValue indexedValue : indexedValues) {
					if ("spcs".equalsIgnoreCase(INPUT_FORMAT)) {
						finalResult.add(Arrays.asList(BADDATATAG));
					} else {
						finalResult.add(Arrays.asList(indexedValue.index(), BADDATATAG));
					}
				}
			}
			return finalResult;
		}
	}

	// === Helpers ===


	private String extractMode(Map<String, String> headers) {
		String value = headers.get("mode");
		log.debug("header value: '{}'", value);
		if (value != null) {
			try {
				return value.trim();
			} catch (NumberFormatException e) {
				log.warn("Invalid defaultmode header value: '{}', falling back to default {}", value, DEFAULTMODE);
			}
		}
		return DEFAULTMODE; // your existing default
	}
	

	private String extractMetadata(Map<String, String> headers) {
		String value = headers.get("metadata");
		log.debug("metadata value: '{}'", value);
		if (value != null) {
			try {
				return value.trim();
			} catch (NumberFormatException e) {
				log.warn("Invalid defaultmetadata header value: '{}', falling back to default {}", value, DEFAULTMETADATA);
			}
		}
		return DEFAULTMETADATA; // your existing default
	}
	
	private String extractRevealUser(Map<String, String> headers) {
		String b64 = headers.get("sf-context-current_user");
		if (b64 != null) {
			try {
				return new String(Base64.getDecoder().decode(b64), StandardCharsets.UTF_8);
			} catch (Exception ignored) {
			}
		}
		return DEFAULTREVEALUSER;
	}

	// === Helpers ===
	private int extractBatchSize(Map<String, String> headers) {
		String value = headers.get("batchsize"); // Spring makes header keys lowercase
		if (value != null) {
			try {
				return Integer.parseInt(value.trim());
			} catch (NumberFormatException e) {
				log.warn("Invalid BATCHSIZE header value: '{}', falling back to default {}", value, BATCH_SIZE);
			}
		}
		return BATCH_SIZE; // your existing default
	}

	/**
	 * Sanitize data for protect operations based on endpoint type
	 */
	private String sanitizeForProtect(Object val, String dataType) {
		if (val == null) {
			return getProtectValueForBadData("null", dataType);
		}

		String str = val.toString().trim();

		switch (dataType.toLowerCase()) {
		case "char":
		case "nbrchar":
			// For char and nbrchar: if bad data, append BADDATATAG to original input
			if (str.isEmpty() || str.length() < 2) {
				return str + BADDATATAG; // original input + BADDATATAG
			}
			return str;

		case "nbrnbr":
			// For nbrnbr: check if it's a valid number and has at least 2 bytes
			try {
				// Try to parse as number to validate
				Double.parseDouble(str);

				// Check byte length (assuming UTF-8 encoding)
				if (str.getBytes(StandardCharsets.UTF_8).length < 2) {
					return BADDATATAG; // return just BADDATATAG for small numbers
				}
				return str;
			} catch (NumberFormatException e) {
				// Not a valid number, return BADDATATAG
				return BADDATATAG;
			}

		default:
			// Default behavior
			return str.isEmpty() ? BADDATATAG : str;
		}
	}

	/**
	 * Sanitize data for reveal operations
	 */
	private String sanitizeForReveal(Object val, String dataType) {
		if (val == null)
			return BADDATATAG;
		String str = val.toString().trim();
		return str.isEmpty() ? BADDATATAG : str;
	}

	/**
	 * Helper method to get the appropriate value for bad data in protect operations
	 */
	private String getProtectValueForBadData(String originalInput, String dataType) {
		switch (dataType.toLowerCase()) {
		case "char":
		case "nbrchar":
			return originalInput + BADDATATAG;
		case "nbrnbr":
			return BADDATATAG;
		default:
			return BADDATATAG;
		}
	}

	/**
	 * Legacy sanitize method - kept for compatibility if needed
	 */
	private String sanitize(Object val) {
		if (val == null)
			return BADDATATAG;
		String s = val.toString().trim();
		return s.isEmpty() ? BADDATATAG : s;
	}
}
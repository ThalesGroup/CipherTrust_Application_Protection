package com.example;
import java.io.IOException; // Import IOException for handling I/O errors

import com.google.gson.Gson; // Import Gson for JSON serialization/deserialization
import com.google.gson.JsonElement; // Import JsonElement for generic JSON parsing
import com.google.gson.JsonObject; // Import JsonObject for JSON object representation
import com.google.gson.JsonParser; // Import JsonParser for parsing JSON strings
import com.google.gson.JsonPrimitive; // Import JsonPrimitive for JSON primitive types

import okhttp3.MediaType; // Import MediaType for specifying content type in HTTP requests
import okhttp3.OkHttpClient; // Import OkHttpClient for making HTTP requests
import okhttp3.Request; // Import Request for building HTTP requests
import okhttp3.RequestBody; // Import RequestBody for defining HTTP request bodies
import okhttp3.Response; // Import Response for handling HTTP responses


/**
 * ThalesRestProtectRevealHelper extends ThalesProtectRevealHelper to provide
 * data protection and revelation functionalities using the Thales CipherTrust
 * Data Protection (CDP) REST APIs. It communicates with a CDP server via HTTP
 * requests to perform cryptographic operations.
 */
public class ThalesRestProtectRevealHelper extends ThalesProtectRevealHelper {

	// The IP address of the CipherTrust Data Protection (CDP) REST endpoint.
	String crdpip = "yourip"; // Placeholder, should be configured.

	// A debug flag (static) to control debug output.
	static boolean debug = true;

	/**
	 * Constructor for ThalesRestProtectRevealHelper.
	 * Initializes the helper with the CDP IP, metadata, policy type, and show metadata flag.
	 *
	 * @param crdpip The IP address of the CDP REST endpoint.
	 * @param metadata Optional metadata string.
	 * @param policyType The type of policy ("internal" or "external").
	 * @param showmetadata A boolean indicating whether metadata should be shown.
	 */
	public ThalesRestProtectRevealHelper(String crdpip, String metadata, String policyType, boolean showmetadata) {
		this.crdpip = crdpip;
		this.metadata = metadata;
		this.policyType = policyType;
		this.showmetadata = showmetadata;
	}

	/**
	 * Main method for demonstrating the functionality of ThalesRestProtectRevealHelper.
	 * It performs a protect operation followed by a reveal operation using the REST APIs.
	 *
	 * @param args Command-line arguments:
	 * args[0]: crdpip (CDP REST endpoint IP)
	 * args[1]: metadata (optional metadata string)
	 * args[2]: policyType ("internal" or "external")
	 * args[3]: showmetadata ("true" or "false")
	 * args[4]: crdpuser (username for reveal operations)
	 * @throws Exception If any error occurs during the process.
	 */
	public static void main(String[] args) throws Exception {
		// Parse command-line arguments
		String crdpip = args[0];
		String metadata = args[1];
		String policyType = args[2];
		String showmetadata = args[3];
		String crdpuser = args[4];

		// Convert showmetadata argument to boolean
		boolean showmetadataparm = true;
		if (!showmetadata.equalsIgnoreCase("true"))
			showmetadataparm = false;

		// Create an instance of ThalesRestProtectRevealHelper
		ThalesRestProtectRevealHelper cmresthelper = new ThalesRestProtectRevealHelper(crdpip, metadata, policyType,
				showmetadataparm);

		// Perform a protect operation with sample data
		String results = cmresthelper.protectData("Thisisnewdata", "plain-alpha-internal", policyType);
		cmresthelper.revealUser = crdpuser; // Set the reveal user

		// Perform a reveal operation based on the policy type
		if (policyType.equalsIgnoreCase("external"))
			cmresthelper.revealData(results, "alpha-external", policyType);
		else
			cmresthelper.revealData( results, "plain-alpha-internal", policyType);
		
		System.out.println("metadata " + cmresthelper.metadata); // Print the metadata
	}

	/**
	 * Reveals (decrypts) encrypted data by making a REST API call to the CDP server.
	 *
	 * @param encryptedData The encrypted data string to be revealed.
	 * @param protectionPolicyName The name of the policy under which the data was protected.
	 * @param policyType The type of policy ("internal" or "external").
	 * @return The decrypted plain text string.
	 */
	@Override
	public String revealData(String encryptedData, String protectionPolicyName, String policyType) {
		String return_value = null;
		String protectedData = null;

		// Initialize OkHttpClient for making HTTP requests
		OkHttpClient client = new OkHttpClient().newBuilder().build();
		// Define the media type for the request body as JSON
		MediaType mediaType = MediaType.parse("application/json");

		String crdpjsonBody = null; // String to hold the JSON request body

		// Create a JSON object for the reveal request payload
		JsonObject crdp_payload = new JsonObject();
		crdp_payload.addProperty("protection_policy_name", protectionPolicyName);
		crdp_payload.addProperty("protected_data", encryptedData);
		// If policy type is external, include the external version (metadata)
		if (policyType.equalsIgnoreCase("external"))
			crdp_payload.addProperty("external_version", this.metadata);
		
		crdp_payload.addProperty("username", this.revealUser); // Include the reveal user
		crdpjsonBody = crdp_payload.toString(); // Convert JSON object to string
		System.out.println(crdpjsonBody); // Print the request JSON body
		
		// Create the request body with the JSON payload
		RequestBody body = RequestBody.create(mediaType, crdpjsonBody);

		// Build the HTTP POST request to the CDP reveal endpoint
		Request request = new Request.Builder().url("http://" + this.crdpip + ":8090/v1/reveal").method("POST", body)
				.addHeader("Content-Type", "application/json").build();
		Response response;
		try {
			// Execute the HTTP request
			response = client.newCall(request).execute();
			
			// Check if the response was successful
			if (response.isSuccessful()) {
				// Parse JSON response body
				String responseBody = response.body().string();
				System.out.println(responseBody); // Print the raw response body
				Gson gson = new Gson();
				JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);
				// Extract the revealed data from the JSON response
				protectedData = jsonObject.get("data").getAsString();

				// Print the revealed data
				System.out.println("Revealed Data: " + protectedData);
			} else {
				System.err.println("Request failed with status code: " + response.code());
			}
			response.close(); // Close the response body
		} catch (IOException e) {
			// Print stack trace if an I/O error occurs
			e.printStackTrace();
		}
		return_value = protectedData; // Set the return value
		return return_value;
	}

	/**
	 * Protects (encrypts) plain text data by making a REST API call to the CDP server.
	 *
	 * @param plainText The plain text data string to be protected.
	 * @param protectionPolicyName The name of the policy to apply for protection.
	 * @param policyType The type of policy ("internal" or "external").
	 * @return The protected (encrypted) string.
	 */
	@Override
	public String protectData(String plainText, String protectionPolicyName, String policyType) {
		String return_value = plainText; // Initialize return value with plain text
		String protectedData = return_value;
		this.policyType = policyType; // Set the policy type

		String crdpjsonBody = null; // String to hold the JSON request body
		
		// Validate the input plain text
		if (isValid(plainText)) {
			// Create a JSON object for the protect request payload
			JsonObject crdp_payload = new JsonObject();
			crdp_payload.addProperty("protection_policy_name", protectionPolicyName);
			crdp_payload.addProperty("data", plainText);

			// Initialize OkHttpClient
			OkHttpClient client = new OkHttpClient().newBuilder().build();
			// Define the media type for the request body as JSON
			MediaType mediaType = MediaType.parse("application/json");

			crdpjsonBody = crdp_payload.toString(); // Convert JSON object to string
			System.out.println(crdpjsonBody); // Print the request JSON body

			// Create the request body with the JSON payload
			RequestBody body = RequestBody.create(mediaType, crdpjsonBody);

			// Build the HTTP POST request to the CDP protect endpoint
			Request request = new Request.Builder().url("http://" + this.crdpip + ":8090/v1/protect")
					.method("POST", body).addHeader("Content-Type", "application/json").build();
			Response response;
			try {
				// Execute the HTTP request
				response = client.newCall(request).execute();
				String version = null; // Variable to hold external version (metadata)
				
				// Check if the response was successful
				if (response.isSuccessful()) {
					// Parse JSON response body
					String responseBody = response.body().string();
					Gson gson = new Gson();
					JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);
					// Extract the protected data from the JSON response
					protectedData = jsonObject.get("protected_data").getAsString();
					
					// Handle metadata based on policy type
					if (policyType.equalsIgnoreCase("external")) {
						// For external policy, extract and store the external version
						version = jsonObject.get("external_version").getAsString();
						System.out.println("external_version: " + version);
						this.metadata = version;
					} else { // Internal policy
						// For internal policy, metadata is part of the protected data (first 7 chars)
						this.metadata = protectedData.substring(0, 7);
						if (!this.showmetadata) {
							// If metadata is not to be shown, parse it out from the beginning
							protectedData = parseString(protectedData);
						}
					}
					// Print the protected data
					System.out.println("Protected Data: " + protectedData);
				} else {
					System.err.println("Request failed with status code: " + response.code());
				}
				response.close(); // Close the response body
			} catch (IOException e) {
				// Print stack trace if an I/O error occurs
				e.printStackTrace();
			}
		}
		return_value = protectedData; // Set the return value
		return return_value;
	}
}
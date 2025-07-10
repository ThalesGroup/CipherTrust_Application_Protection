package com.example;
import okhttp3.*; // Import OkHttp for making HTTP requests

import org.json.JSONArray; // Import JSONArray for handling JSON arrays
import org.json.JSONObject; // Import JSONObject for handling JSON objects

import java.io.IOException; // Import IOException for handling I/O errors
import java.io.InputStream; // Import InputStream for reading from files
import java.util.Iterator; // Import Iterator for iterating over JSON keys
import java.util.Properties; // Import Properties for loading configuration from a file

/**
 * ThalesAzureOpenAIClientPromptExample demonstrates how to interact with Azure OpenAI
 * services, specifically for sending prompts and processing responses, while
 * integrating with Thales CipherTrust Data Protection (CADP) for protecting
 * or revealing sensitive information (PII) within the prompt and response.
 * It loads configuration from a properties file and uses OkHttp for API calls.
 */
public class ThalesAzureOpenAIClientPromptExample {
	// A static Properties object to hold configuration loaded from thales-config.properties
	private static Properties properties;

	/**
	 * Static initializer block to load properties from "thales-config.properties"
	 * when the class is loaded. This ensures that configuration is available
	 * before any other methods are called.
	 * It throws a RuntimeException if the properties file cannot be found or loaded.
	 */
	static {
		try (InputStream input = ThalesAzureOpenAIClientPromptExample.class.getClassLoader()
				.getResourceAsStream("thales-config.properties")) {
			properties = new Properties();
			if (input == null) {
				// If the input stream is null, the properties file was not found
				throw new RuntimeException("Unable to find udfConfig.properties");
			}
			// Load properties from the input stream
			properties.load(input);

		} catch (Exception ex) {
			// Catch any exceptions during file loading and wrap them in a RuntimeException
			throw new RuntimeException("Error loading properties file", ex);
		}
	}

	/**
	 * The main method is the entry point of the application.
	 * It sets up the Thales CADP helper, prepares the prompt by processing
	 * sensitive data, sends the prompt to Azure OpenAI, and then processes
	 * the AI's response, including checking for PII in the output.
	 *
	 * @param args Command-line arguments:
	 * args[0]: Azure Cognitive Services Endpoint
	 * args[1]: Azure Cognitive Services API Key
	 * args[2]: OpenAI API Key
	 * args[3]: OpenAI Endpoint URL
	 * @throws IOException If an I/O error occurs during HTTP communication.
	 */
	public static void main(String[] args) throws IOException {

		// Retrieve various configuration properties from the loaded properties object
		String keymanagerhost = properties.getProperty("KEYMGRHOST");
		String crdptkn = properties.getProperty("CRDPTKN");
		String policyType = properties.getProperty("POLICYTYPE");
		String showmetadata = properties.getProperty("SHOWMETADATA");
		String revealuser = properties.getProperty("REVEALUSER");
		System.out.println(" user  " + revealuser); // Print the reveal user

		// Convert showmetadata property to a boolean
		boolean showmeta = showmetadata.equalsIgnoreCase("true");

		// Initialize AzureContentProcessor. This class is assumed to handle
		// the detection and processing (protection/revelation) of PII within text.
		AzureContentProcessor cp = new AzureContentProcessor(properties);
		// Set Azure Cognitive Services endpoint and API key from command-line arguments
		cp.cognitiveservices_endpoint = args[0];
		cp.cognitiveservices_apiKey = args[1];
		// Set OpenAI API key and endpoint from command-line arguments
		String OPENAI_API_KEY = args[2];
		String OPENAI_ENDPOINT = args[3];

		// Initialize ThalesProtectRevealHelper (specifically ThalesCADPProtectRevealHelper).
		// This helper interacts with the Thales CipherTrust Manager for cryptographic operations.
		ThalesProtectRevealHelper tprh = new ThalesCADPProtectRevealHelper(keymanagerhost, crdptkn, null, policyType,
				showmeta);
		// Set additional properties for the Thales CADP helper
		tprh.revealUser = revealuser;
		tprh.policyType = policyType;
		tprh.policyName = properties.getProperty("POLICYNAME");

		// Initialize OkHttpClient for making HTTP requests to the OpenAI API
		OkHttpClient client = new OkHttpClient();

		// Define the input content string that contains a prompt and potentially PII
		String inputcontent = "	String inputText = Explain 'rubber duck debugging' in one line to Kathi Wolf	Burney Circle	Mertzmouth	OH	24114	328.639.0623x3743	becker.drury@hotmail.com	7/7/1992	5.32755E+15	15	203-04-0501";
        		
		// Process the input content to protect/reveal PII before sending it to OpenAI.
		// The result `newPrompt` will have the sensitive data handled according to the policy.
		String newPrompt = cp.processTextChunk(inputcontent, tprh);
		System.out.println(newPrompt); // Print the processed prompt

        // Construct the JSON request body for the OpenAI API call
        JSONObject json = new JSONObject();
        
        // Add "messages" array to the JSON, containing a single system message with the processed prompt
        json.put("messages", new org.json.JSONArray().put(new JSONObject()
            .put("role", "system") // Role of the message sender (system, user, assistant)
            .put("content", newPrompt))); // The actual message content
        json.put("max_tokens", 200); // Set the maximum number of tokens for the AI's response
        
        // Create the request body with the JSON payload and specify content type as application/json
        RequestBody body = RequestBody.create(json.toString(), MediaType.get("application/json"));
        
        // Build the HTTP POST request to the OpenAI endpoint
        Request request = new Request.Builder()
            .url(OPENAI_ENDPOINT) // Set the URL for the request
            .addHeader("api-key", OPENAI_API_KEY) // Add the API key as a header
            .post(body) // Set the request method to POST and attach the body
            .build(); // Build the request

        // Execute the HTTP request and handle the response
        try (Response response = client.newCall(request).execute()) {
            // Check if the HTTP response was successful (2xx status code)
            if (!response.isSuccessful()) {
                System.out.println("Request failed: " + response); // Print failure details
                return; // Exit if the request failed
            }
            // Read the response body as a string
            String responseBody = response.body().string();
            System.out.println("Full Response: " + responseBody); // Print the full raw response

            // Parse the JSON response received from OpenAI
            JSONObject jsonResponse = new JSONObject(responseBody);
            System.out.println(jsonResponse); // Print the parsed JSON object
            // Get the "choices" array from the response, which contains the AI's generated text
            JSONArray choices = jsonResponse.getJSONArray("choices");

            // Check if there are any choices (generated responses)
            if (choices.length() > 0) {
                // Get the first choice (assuming only one is needed for this example)
                JSONObject choice = choices.getJSONObject(0);

                // Extract and print the content (the AI's generated text)
                JSONObject message = choice.getJSONObject("message");
                String content = message.getString("content");
                System.out.println("\nExtracted Content:\n" + content);
                System.out.println("\nNow checking for PII in output :\n" + content);
                
                // Process the AI's output content to reveal/protect any PII that might have been generated.
                // An example email "sam@aol.com" is appended to demonstrate PII detection in output.
            	String cleanoutput = cp.processTextChunk(content + " sam@aol.com", tprh);
            	
            	System.out.println("clean output = " + cleanoutput); // Print the cleaned output
        		
                // Extract and print content_filter_results, which indicate if the content was flagged
                // for harmfulness, sexual content, self-harm, or violence.
                JSONObject contentFilterResults = choice.getJSONObject("content_filter_results");
                System.out.println("\nContent Filter Results:");

                // Iterate over the keys (filter categories) in content_filter_results
                Iterator<String> keys = contentFilterResults.keys();
                while (keys.hasNext()) {
                    String key = keys.next(); // Get the filter category name
                    JSONObject filterDetails = contentFilterResults.getJSONObject(key); // Get details for this category
                    boolean filtered = filterDetails.getBoolean("filtered"); // Check if content was filtered
                    // Get severity if available, otherwise "N/A"
                    String severity = filterDetails.has("severity") ? filterDetails.getString("severity") : "N/A";
                    // Print the filter results for each category
                    System.out.println("- " + key + ": filtered=" + filtered + ", severity=" + severity);
                }
            } else {
                System.out.println("No choices found in response."); // Message if no AI response was generated
            }
        }
    }
}
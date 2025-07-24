package com.example;
import com.google.cloud.vertexai.VertexAI;
import com.google.cloud.vertexai.api.GenerateContentResponse;
import com.google.cloud.vertexai.generativeai.GenerativeModel;
import com.google.cloud.vertexai.generativeai.ResponseHandler;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * This class demonstrates an example of using Thales ProtectReveal with Google Cloud Vertex AI for prompt processing.
 * It loads configuration from a properties file, processes a text prompt through a Thales content processor,
 * and then sends the processed prompt to a Vertex AI Gemini model to get a text-only response.
 */
public class ThalesGCPVertexaiPromptExample {

	// Properties object to hold configurations loaded from 'thales-config.properties'.
	private static Properties properties;

	// Static initializer block to load properties file when the class is loaded.
	static {
		try (InputStream input = ThalesGCPProtectRevealBatchProcessor.class.getClassLoader()
				.getResourceAsStream("thales-config.properties")) {
			properties = new Properties();
			if (input == null) {
				// Throws a RuntimeException if the properties file is not found.
				throw new RuntimeException("Unable to find udfConfig.properties");
			}
			// Loads properties from the input stream.
			properties.load(input);

		} catch (Exception ex) {
			// Throws a RuntimeException if there's an error loading the properties file.
			throw new RuntimeException("Error loading properties file", ex);
		}
	}

	/**
	 * Main method to run the Vertex AI prompt example with Thales ProtectReveal.
	 *
	 * @param args Command-line arguments: projectId, location, and modelName for Vertex AI.
	 * @throws IOException if an I/O error occurs.
	 */
	public static void main(String[] args) throws IOException {
		// TODO(developer): Replace these variables before running the sample.
		// projectId: Google Cloud Project ID.
		String projectId = args[0];		
		// location: Google Cloud region where the Vertex AI model is deployed (e.g., "us-central1").
		String location = args[1];
		// modelName: Name of the Vertex AI generative model to use (e.g., "gemini-pro").
		String modelName = args[2];

		// Retrieve various configuration properties from the loaded 'thales-config.properties' file.
		String metadata = properties.getProperty("METADATA");
		String crdpip = properties.getProperty("CRDPIP"); // Thales CipherTrust Data Protection (CDP) IP/hostname.
		String keymanagerhost = properties.getProperty("KEYMGRHOST"); // Key Manager Host for Thales.
		String crdptkn = properties.getProperty("CRDPTKN"); // CDP Token.
		String policyType = properties.getProperty("POLICYTYPE"); // Thales policy type.
		String showmetadata = properties.getProperty("SHOWMETADATA"); // Flag to indicate whether to show metadata.
		String revealuser = properties.getProperty("REVEALUSER"); // User for reveal operations.
		System.out.println(" user  " + revealuser);

		// Convert showmetadata string to a boolean.
		boolean showmeta = showmetadata.equalsIgnoreCase("true");

		// Initialize GCPContentProcessor with loaded properties. This processor is likely responsible
		// for preparing the content before sending it to Thales ProtectReveal.
		GCPContentProcessor cp = new GCPContentProcessor(properties);
	
		// Initialize ThalesProtectRevealHelper. Two options are commented out, showing different
		// implementations (CADP vs. REST). The REST implementation is currently active.
		 ThalesProtectRevealHelper tprh = new ThalesCADPProtectRevealHelper(keymanagerhost, crdptkn, null, policyType,
		 				showmeta);
		
		// Using ThalesRestProtectRevealHelper for content protection and revelation.
		//ThalesProtectRevealHelper tprh = new ThalesRestProtectRevealHelper(crdpip, metadata, policyType,
		//			showmeta);
			
		// Set reveal user, policy type, and policy name on the ThalesProtectRevealHelper instance.
		tprh.revealUser = revealuser;
		tprh.policyType = policyType;
		tprh.policyName = properties.getProperty("POLICYNAME");

		// Define the initial text prompt. A commented-out example is also present.
		String textPrompt = "Jason who lives at 1211 Dickinson View,Rolfsonside,AZ wanted to know  what's a good name for a flower shop that specializes in selling bouquets of"
				+ " dried flowers in Arizona her email is v.racer@example.org?";

		// Process the original text prompt using the GCPContentProcessor, which likely
		// applies Thales ProtectReveal operations (e.g., tokenization or encryption).
		String newPrompt = cp.processText(projectId,textPrompt, tprh);
		System.out.println("Processed prompt: " + newPrompt); // Print the processed prompt.
		
		// Send the processed prompt to the Vertex AI Gemini model and get the response.
		String output = textInput(projectId, location, modelName, newPrompt);
		System.out.println("Model output: " + output); // Print the model's response.
	}

	/**
	 * Passes the provided text input to the Gemini model and returns the text-only response.
	 *
	 * @param projectId The Google Cloud project ID.
	 * @param location The Google Cloud region.
	 * @param modelName The name of the generative model (e.g., "gemini-pro").
	 * @param textPrompt The text prompt to send to the model.
	 * @return The text-only response from the Gemini model.
	 * @throws IOException if an I/O error occurs during API calls.
	 */
	public static String textInput(String projectId, String location, String modelName, String textPrompt)
			throws IOException {
		// Initialize client that will be used to send requests. This client only needs
		// to be created once, and can be reused for multiple requests.
		try (VertexAI vertexAI = new VertexAI(projectId, location)) {
			// Create a GenerativeModel instance with the specified model name and Vertex AI client.
			GenerativeModel model = new GenerativeModel(modelName, vertexAI);

			// Generate content using the provided text prompt.
			GenerateContentResponse response = model.generateContent(textPrompt);
			// Extract the text content from the model's response.
			String output = ResponseHandler.getText(response);
			return output;
		}
	}
}
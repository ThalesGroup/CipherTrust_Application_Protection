package com.example;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.apache.logging.log4j.core.Filter.Result;

import com.azure.ai.textanalytics.TextAnalyticsClient;
import com.azure.ai.textanalytics.TextAnalyticsClientBuilder;
import com.azure.ai.textanalytics.models.PiiEntity;
import com.azure.ai.textanalytics.models.RecognizePiiEntitiesOptions;
import com.azure.ai.textanalytics.models.PiiEntityCategory;
import com.azure.ai.textanalytics.models.RecognizeEntitiesResult;
import com.azure.ai.textanalytics.models.RecognizePiiEntitiesResult;
import com.azure.ai.textanalytics.util.RecognizeEntitiesResultCollection;
import com.azure.ai.textanalytics.util.RecognizePiiEntitiesResultCollection;
import com.azure.core.credential.AzureKeyCredential;

/**
 * Extends ContentProcessor to provide Azure-specific functionalities for
 * PII (Personally Identifiable Information) detection and protection/revelation.
 * It uses Azure Text Analytics service for PII recognition.
 */
public class AzureContentProcessor extends ContentProcessor {

	// Maximum characters allowed per request to the Azure Text Analytics API.
	private static final int CHUNK_SIZE = 5100;
	// Confidence threshold for PII entity recognition. Entities with confidence below this will be ignored.
	private static final double CONFIDENCE_THRESHOLD = 0.8;
	// Array of tags used for encryption (e.g., for email, numbers, characters).
	String[] tags = { "ENCEMAIL", "ENCNBR", "ENCCHAR" };

	// Static variables to hold Azure Cognitive Services endpoint and API key.
	static String  cognitiveservices_endpoint = null;
	static String cognitiveservices_apiKey = null;

	/**
	 * Constructor for AzureContentProcessor.
	 * Calls the superclass constructor to initialize common properties.
	 * @param p The Properties object containing configuration settings for the processor.
	 */
	public AzureContentProcessor(Properties p) {
		super(p);
		// TODO Auto-generated constructor stub - This comment indicates that
		// further initialization specific to AzureContentProcessor might be needed here.
	}

	/**
	 * Processes a given PDF file for PII detection and either protects (encrypts) or reveals (decrypts)
	 * the identified PII entities based on the specified mode.
	 *
	 * @param inputFile The input  file to process.
	 * @param outputDir The output file where the processed content will be written.
	 * @param projectId The project ID (currently unused in this method, but part of the contract).
	 * @param tprh An instance of ThalesProtectRevealHelper for cryptographic operations.
	 * @param mode The processing mode: "protect" to encrypt PII, or anything else to decrypt.
	 * @param skiphdr A boolean indicating whether to skip the first line (header) of the input file.
	 * @return The number of lines processed in the file.
	 */
	@Override
	public int processFile(File inputFile, File outputDir, String projectId, ThalesProtectRevealHelper tprh,
			String mode, boolean skiphdr) {

		int nbroflines = 0; // Counter for the number of lines processed.
		// Use try-with-resources to ensure BufferedReader and BufferedWriter are closed automatically.
		try (BufferedReader reader = Files.newBufferedReader(inputFile.toPath());
				BufferedWriter writer = Files.newBufferedWriter(outputDir.toPath())) {

			// If skiphdr is true, read and discard the first line (assuming it's a header).
			if (skiphdr) {
				String headerLine = reader.readLine();
			}
			String line;
			String content = null;
			// Read the file line by line until the end.
			while ((line = reader.readLine()) != null) {
				nbroflines++; // Increment line counter.

				// Process the line based on its length and the specified mode.
				if (line.length() < 2) {
					// If the line is very short, treat it as content directly (might be an empty or nearly empty line).
					content = line;
				} else {
					// If the mode is "protect", encrypt PII in the line. Otherwise, decrypt.
					if (mode.equalsIgnoreCase("protect")) {
						content = processTextChunk(line, tprh); // Encrypt PII in the line.
					} else {
						content = decryptLine(line, tprh); // Decrypt PII in the line.
					}
				}

				writer.write(content); // Write the processed content to the output file.
				writer.newLine(); // Add a new line character after each processed line.
			}

			System.out.println("Processing complete! Check the output file: " + outputDir.getAbsolutePath());

		} catch (IOException e) {
			// Print stack trace if an I/O error occurs during file operations.
			e.printStackTrace();
		}

		return nbroflines; // Return the total number of lines processed.
	}

	/**
	 * Splits a given text into smaller chunks of a specified size. This is useful for
	 * complying with API request limits (e.g., Azure Text Analytics has a character limit per request).
	 *
	 * @param text The input text to be split.
	 * @param chunkSize The maximum size of each chunk.
	 * @return A List of strings, where each string is a chunk of the original text.
	 */
	private static List<String> splitTextIntoChunks(String text, int chunkSize) {
		List<String> chunks = new ArrayList<>();
		int length = text.length();
		// Iterate through the text, creating substrings of 'chunkSize'.
		for (int i = 0; i < length; i += chunkSize) {
			chunks.add(text.substring(i, Math.min(length, i + chunkSize)));
		}
		return chunks;
	}

	/**
	 * Processes a chunk of text (typically a single line from a file) to identify and
	 * encrypt PII entities using Azure Text Analytics.
	 *
	 * @param line The text line to process.
	 * @param tprh An instance of ThalesProtectRevealHelper for encryption operations.
	 * @return The modified line with identified PII entities encrypted.
	 */
	public String processTextChunk(String line, ThalesProtectRevealHelper tprh) {

		String resultString = line; // Initialize result with the original line.

		// Create a Text Analytics Client using the configured endpoint and API key.
		TextAnalyticsClient textAnalyticsClient = new TextAnalyticsClientBuilder().endpoint(cognitiveservices_endpoint)
				.credential(new AzureKeyCredential(cognitiveservices_apiKey)).buildClient();

		// Split the input line into smaller chunks to accommodate API limits.
		List<String> textChunks = splitTextIntoChunks(line, CHUNK_SIZE);

		// Map to store original PII values and their encrypted versions.
		Map<String, String> nameEncryptionMap = new HashMap<>();

		// Configure options for PII entity recognition, specifying categories to filter.
		RecognizePiiEntitiesOptions options = new RecognizePiiEntitiesOptions()
				.setCategoriesFilter(
						PiiEntityCategory.PERSON,
						PiiEntityCategory.ADDRESS,
						PiiEntityCategory.EMAIL,
						PiiEntityCategory.PHONE_NUMBER,
						PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER,
						PiiEntityCategory.DATE,
						PiiEntityCategory.URL
				);

		// Process each chunk of text separately for PII detection.
		for (String chunk : textChunks) {

			String updatedValue = null;

			// Call Azure Text Analytics to recognize PII entities in the current chunk.
			// The second argument "en" specifies English language.
			RecognizePiiEntitiesResultCollection response = textAnalyticsClient.recognizePiiEntitiesBatch(List.of(chunk), "en",
					options);

			// Iterate through the results from the batch recognition.
			for (RecognizePiiEntitiesResult result : response) {

				// Iterate through each PII entity detected in the result.
				for (PiiEntity entity : result.getEntities()) {
					total_entities_found++; // Increment the total count of found entities.
					System.out.printf(" - PII Entity: %s, Category: %s, Confidence: %.2f%n", entity.getText(),
							entity.getCategory(), entity.getConfidenceScore());

					String originalValue = entity.getText();
					updatedValue = originalValue; // Initialize updatedValue with original.
					String piitype = entity.getCategory().toString(); // Get the PII category as a string.
					// Get the protection type (policy) from the piiMap based on the PII category.
					String protection_type = piiMap.get(piitype);

					// If no specific protection type is found, use the default policy.
					if (protection_type == null) {
						protection_type = tprh.defaultPolicy;
					}

					// Check the category and confidence score before encrypting.
					// If the confidence is below the threshold, the entity is skipped.
					if ("Person".equals(entity.getCategory().toString())
							&& entity.getConfidenceScore() >= CONFIDENCE_THRESHOLD) {
						originalValue = entity.getText();
						updatedValue = encryptData(originalValue, tprh, protection_type); // Encrypt the data.
						nameEncryptionMap.put(originalValue, updatedValue); // Store mapping for replacement.
					} else if ("Address".equals(entity.getCategory().toString())
							&& entity.getConfidenceScore() >= CONFIDENCE_THRESHOLD) {
						originalValue = entity.getText();
						updatedValue = encryptData(originalValue, tprh, protection_type);
						nameEncryptionMap.put(originalValue, updatedValue);
					} else if ("PhoneNumber".equals(entity.getCategory().toString())
							&& entity.getConfidenceScore() >= CONFIDENCE_THRESHOLD) {
						originalValue = entity.getText();
						updatedValue = encryptData(originalValue, tprh, protection_type);
						nameEncryptionMap.put(originalValue, updatedValue);
					} else if ("Email".equals(entity.getCategory().toString())
							&& entity.getConfidenceScore() >= CONFIDENCE_THRESHOLD) {
						originalValue = entity.getText();
						updatedValue = encryptData(originalValue, tprh, protection_type);
						nameEncryptionMap.put(originalValue, updatedValue);
					} else if ("URL".equals(entity.getCategory().toString())
							&& entity.getConfidenceScore() >= CONFIDENCE_THRESHOLD) {
						originalValue = entity.getText();
						updatedValue = encryptData(originalValue, tprh, protection_type);
						nameEncryptionMap.put(originalValue, updatedValue);
					}
					else // If the entity category is not explicitly handled or confidence is too low.
					{
						total_skipped_entities++; // Increment skipped entities counter.
					}
				}
			}
		}

		// After processing all chunks and identifying PIIs, replace the original
		// PII values in the 'line' with their encrypted versions.
		for (Map.Entry<String, String> entry : nameEncryptionMap.entrySet()) {
			line = line.replace(entry.getKey(), entry.getValue());
		}
		resultString = line; // Update the resultString with the modified line.

		return resultString; // Return the line with encrypted PII.
	}

	/**
	 * Processes a line of text, assuming it might contain comma-separated values (like CSV),
	 * and identifies/encrypts PII entities within these segments. It handles quoted fields
	 * to correctly split the line.
	 *
	 * @param line The text line to process, potentially containing CSV-like data.
	 * @param tprh An instance of ThalesProtectRevealHelper for encryption operations.
	 * @return The modified line with identified PII entities encrypted.
	 */
	public String processTextSplit(String line, ThalesProtectRevealHelper tprh) {

		String resultString = line; // Initialize result with the original line.

		// Create a Text Analytics Client using the configured endpoint and API key.
		TextAnalyticsClient textAnalyticsClient = new TextAnalyticsClientBuilder().endpoint(cognitiveservices_endpoint)
				.credential(new AzureKeyCredential(cognitiveservices_apiKey)).buildClient();

		// Configure options for PII entity recognition, specifying categories to filter.
		RecognizePiiEntitiesOptions options = new RecognizePiiEntitiesOptions()
				.setCategoriesFilter(
						PiiEntityCategory.PERSON,
						PiiEntityCategory.ADDRESS,
						PiiEntityCategory.EMAIL,
						PiiEntityCategory.PHONE_NUMBER,
						PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER,
						PiiEntityCategory.DATE,
						PiiEntityCategory.URL
				);

		// Split the line into fields, handling commas within quoted strings.
		// The regex `,(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)` splits by comma only if it's not inside quotes.
		// `-1` ensures that trailing empty strings are not discarded.
		String[] fields = line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1);

		// Map to store original PII values and their encrypted versions.
		Map<String, String> nameEncryptionMap = new HashMap<>();

		// Convert split fields into a list for easier processing.
		List<String> textSegments = new ArrayList<>();
		for (String segment : fields) {
			textSegments.add(segment.trim()); // Trim whitespace from each segment.
		}

		// Process segments in batches (e.g., of 5) to comply with API limits for batch processing.
		for (int i = 0; i < textSegments.size(); i += 5) {
			int end = Math.min(i + 5, textSegments.size());
			List<String> batch = textSegments.subList(i, end); // Create a sublist for the current batch.

			// Perform PII detection on the current batch.
			RecognizePiiEntitiesResultCollection response = textAnalyticsClient.recognizePiiEntitiesBatch(batch, "en",
					options);

			String updatedValue = null;
			System.out.println("\n🔹 Detected PII Entities:");
			// Iterate through the results from the batch recognition.
			for (RecognizePiiEntitiesResult result : response) {

				// Iterate through each PII entity detected in the result.
				for (PiiEntity entity : result.getEntities()) {
					total_entities_found++; // Increment the total count of found entities.

					System.out.printf(" - PII Entity: %s, Category: %s, Confidence: %.2f%n", entity.getText(),
							entity.getCategory(), entity.getConfidenceScore());

					String originalValue = entity.getText();
					String piitype = entity.getCategory().toString();
					String protection_type = piiMap.get(piitype); // Get protection profile from piiMap.

					// If no specific protection type is found, use the default policy.
					if (protection_type == null) {
						protection_type = tprh.defaultPolicy;
					}

					// Check the category and confidence score before encrypting.
					if ("Person".equals(entity.getCategory().toString())
							&& entity.getConfidenceScore() >= CONFIDENCE_THRESHOLD) {
						originalValue = entity.getText();
						updatedValue = encryptData(originalValue, tprh, protection_type);
						nameEncryptionMap.put(originalValue, updatedValue);
					} else if ("Address".equals(entity.getCategory().toString())
							&& entity.getConfidenceScore() >= CONFIDENCE_THRESHOLD) {
						originalValue = entity.getText();
						updatedValue = encryptData(originalValue, tprh, protection_type);
						nameEncryptionMap.put(originalValue, updatedValue);
					} else if ("PhoneNumber".equals(entity.getCategory().toString())
							&& entity.getConfidenceScore() >= CONFIDENCE_THRESHOLD) {
						originalValue = entity.getText();
						updatedValue = encryptData(originalValue, tprh, protection_type);
						nameEncryptionMap.put(originalValue, updatedValue);
					} else if ("Email".equals(entity.getCategory().toString())
							&& entity.getConfidenceScore() >= CONFIDENCE_THRESHOLD) {
						originalValue = entity.getText();
						updatedValue = encryptData(originalValue, tprh, protection_type);
						nameEncryptionMap.put(originalValue, updatedValue);
					} else if ("URL".equals(entity.getCategory().toString())
							&& entity.getConfidenceScore() >= CONFIDENCE_THRESHOLD) {
						originalValue = entity.getText();
						updatedValue = encryptData(originalValue, tprh, protection_type);
						nameEncryptionMap.put(originalValue, updatedValue);
					}
					else // If the entity category is not explicitly handled or confidence is too low.
					{
						total_skipped_entities++; // Increment skipped entities counter.
					}
				}
			}
		}

		// Replace original PII values with their encrypted versions in the 'line'.
		for (Map.Entry<String, String> entry : nameEncryptionMap.entrySet()) {
			line = line.replace(entry.getKey(), entry.getValue());
		}
		resultString = line; // Update the resultString with the modified line.

		// System.out.println("resultSTirng " + resultString); // Debugging print.
		return resultString; // Return the line with encrypted PII.
	}
}
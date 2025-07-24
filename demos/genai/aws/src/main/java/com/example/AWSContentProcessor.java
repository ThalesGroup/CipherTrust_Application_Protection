package com.example;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

// AWS SDK imports for Comprehend service
import software.amazon.awssdk.services.comprehend.ComprehendClient;
import software.amazon.awssdk.services.comprehend.model.DetectPiiEntitiesRequest;
import software.amazon.awssdk.services.comprehend.model.DetectPiiEntitiesResponse;
import software.amazon.awssdk.services.comprehend.model.LanguageCode;
import software.amazon.awssdk.services.comprehend.model.PiiEntity;
import software.amazon.awssdk.services.comprehend.model.PiiEntityType;
import software.amazon.awssdk.regions.Region;

/**
 * AWSContentProcessor extends ContentProcessor to provide functionalities for
 * processing text content, specifically detecting and handling PII (Personally
 * Identifiable Information) using AWS Comprehend, and then encrypting/decrypting
 * it using ThalesProtectRevealHelper.
 */
public class AWSContentProcessor extends ContentProcessor {

	// Static variable to hold the AWS region for Comprehend client
	public static Region awsregion = null;

	/**
	 * Constructor for AWSContentProcessor.
	 * Calls the superclass constructor with the provided properties.
	 * @param p Properties object containing configuration for the content processor.
	 */
	public AWSContentProcessor(Properties p) {
		super(p);
		// TODO Auto-generated constructor stub
	}

	/**
	 * Processes a single line of text to detect PII entities using AWS Comprehend
	 * and then encrypts the detected PII based on a confidence threshold and
	 * predefined PII types.
	 *
	 * @param line The input text line to be processed.
	 * @param tprh An instance of ThalesProtectRevealHelper for encryption operations.
	 * @return The modified line with detected PII encrypted, or the original line if no PII is found or processed.
	 */
	public String processText(String line, ThalesProtectRevealHelper tprh) {

		// Build Comprehend client with the specified AWS region
		ComprehendClient comprehendClient = ComprehendClient.builder().region(awsregion).build();

		// Initialize counter for entities found in the current line
		line_entities_found = 0;

		// Build a request to detect PII entities in the given text line,
		// specifying English as the language.
		DetectPiiEntitiesRequest request = DetectPiiEntitiesRequest.builder().text(line).languageCode(LanguageCode.EN)
				.build();

		// Send the request to AWS Comprehend and get the response
		DetectPiiEntitiesResponse response = comprehendClient.detectPiiEntities(request);
		// Get all detected PII entities from the response
		List<PiiEntity> allPiiEntities = response.entities();
		// Create a new list to store filtered PII entities
		List<PiiEntity> filteredEntities = new ArrayList<>();

		// Define the specific PII entity types that are of interest for filtering
		List<PiiEntityType> desiredEntityTypes = List.of(PiiEntityType.NAME, PiiEntityType.ADDRESS, PiiEntityType.EMAIL,
				PiiEntityType.PHONE, PiiEntityType.IP_ADDRESS, PiiEntityType.INTERNATIONAL_BANK_ACCOUNT_NUMBER,
				PiiEntityType.SSN, PiiEntityType.PIN, PiiEntityType.CREDIT_DEBIT_NUMBER);

		// Filter the detected entities: only add entities whose type is in the desiredEntityTypes list
		for (PiiEntity entity : allPiiEntities) {
			if (desiredEntityTypes.contains(entity.type())) {
				filteredEntities.add(entity);
			}
		}

		// Update the count of entities found in the current line after filtering
		line_entities_found = filteredEntities.size();
		// Set a confidence threshold for PII detection. Entities with scores below this will be skipped.
		double confidenceThreshold = 0.9;

		// Initialize the return value with the original line
		String return_value = line;

		// If filtered PII entities are found in the line
		if (!filteredEntities.isEmpty()) { // Use filteredEntities here
			// Use StringBuilder for efficient modification of the string
			StringBuilder modifiedLine = new StringBuilder(line);
			// This offset adjustment is needed because the length of the line changes
			// when PII is replaced with encrypted text.
			int offsetAdjustment = 0;

			// Iterate over the filtered PII entities
			for (PiiEntity entity : filteredEntities) { // Iterate over filteredEntities
				// If the confidence score of the entity is below the threshold, skip encryption
				if (entity.score() < confidenceThreshold) {
					// Increment the counter for skipped entities
					total_skipped_entities++;
					continue; // Move to the next entity
				}

				// Calculate the start and end offsets for the PII entity in the modified line,
				// adjusting for previous replacements
				int beginOffset = entity.beginOffset() + offsetAdjustment;
				int endOffset = entity.endOffset() + offsetAdjustment;

				// Basic validation for offsets to prevent IndexOutOfBoundsException
				if (beginOffset < 0 || endOffset > modifiedLine.length() || beginOffset > endOffset) {
					System.err.println("Invalid offsets: begin=" + beginOffset + ", end=" + endOffset + ", line length="
							+ modifiedLine.length());
					continue; // Skip this entity if offsets are invalid
				}
				// Get the PII type as a string
				String piitype = entity.typeAsString();
				System.out.println("pii type:" + piitype);
				// Get the protection profile associated with the PII type from piiMap (presumably inherited)
				String protection_profile = piiMap.get(piitype);

				// Extract the actual PII text from the modified line
				String piiText = modifiedLine.substring(beginOffset, endOffset);
				// Encrypt the PII text using the ThalesProtectRevealHelper and the determined protection profile
				String encryptedText = encryptData(piiText, tprh, protection_profile);

				// Replace the original PII text with the encrypted text in the StringBuilder
				modifiedLine.replace(beginOffset, endOffset, encryptedText);
				// Update the offset adjustment based on the difference in length between
				// the original PII text and its encrypted form
				offsetAdjustment += encryptedText.length() - piiText.length();
			}

			// Convert the StringBuilder content back to a String
			return_value = modifiedLine.toString();
		}

		// Print the total number of entities found in the current line
		System.out.println("total number of entities in line " + line_entities_found);

		// Add the line's entities to the overall total entities found
		total_entities_found = total_entities_found + line_entities_found;
		return return_value;
	}

	/**
	 * An older version of the text processing method. This method also detects PII
	 * using AWS Comprehend and encrypts it, but it does not include the filtering
	 * of PII entity types that `processText` does.
	 *
	 * @param awsregion The AWS region to use for the Comprehend client.
	 * @param line The input text line to be processed.
	 * @param tprh An instance of ThalesProtectRevealHelper for encryption operations.
	 * @return The modified line with detected PII encrypted, or the original line if no PII is found or processed.
	 */
	public String processTextOld(Region awsregion, String line, ThalesProtectRevealHelper tprh) {

		// Build Comprehend client with the specified AWS region
		ComprehendClient comprehendClient = ComprehendClient.builder().region(awsregion).build();

		// Initialize counter for entities found in the current line
		line_entities_found = 0;

		// Build a request to detect PII entities in the given text line,
		// specifying English as the language.
		DetectPiiEntitiesRequest request = DetectPiiEntitiesRequest.builder().text(line).languageCode(LanguageCode.EN)
				.build();

		// Send the request to AWS Comprehend and get the response
		DetectPiiEntitiesResponse response = comprehendClient.detectPiiEntities(request);
		// Get all detected PII entities from the response
		List<PiiEntity> piiEntities = response.entities();

		// Update the count of entities found in the current line
		line_entities_found = piiEntities.size();
		// Set a confidence threshold for PII detection. Entities with scores below this will be skipped.
		double confidenceThreshold = 0.9;

		// Initialize the return value with the original line
		String return_value = line;

		// If PII entities are found in the line
		if (piiEntities != null && !piiEntities.isEmpty()) {
			// Use StringBuilder for efficient modification of the string
			StringBuilder modifiedLine = new StringBuilder(line);
			// This offset adjustment is needed because the length of the line changes
			// when PII is replaced with encrypted text.
			int offsetAdjustment = 0;

			// Iterate over the detected PII entities
			for (PiiEntity entity : piiEntities) {
				// If the confidence score of the entity is below the threshold, skip encryption
				if (entity.score() < confidenceThreshold) {
					// Increment the counter for skipped entities
					total_skipped_entities++;
					continue; // Move to the next entity
				}

				// Calculate the start and end offsets for the PII entity in the modified line,
				// adjusting for previous replacements
				int beginOffset = entity.beginOffset() + offsetAdjustment;
				int endOffset = entity.endOffset() + offsetAdjustment;

				// Basic validation for offsets to prevent IndexOutOfBoundsException
				if (beginOffset < 0 || endOffset > modifiedLine.length() || beginOffset > endOffset) {
					System.err.println("Invalid offsets: begin=" + beginOffset + ", end=" + endOffset + ", line length="
							+ modifiedLine.length());
					continue; // Skip this entity if offsets are invalid
				}

				// Get the PII type as a string
				String piitype = entity.typeAsString();
				System.out.println("pii type:" + piitype);
				// Get the protection profile associated with the PII type from piiMap (presumably inherited)
				String protection_profile = piiMap.get(piitype);

				// Extract the actual PII text from the modified line
				String piiText = modifiedLine.substring(beginOffset, endOffset);

				// Encrypt the PII text using the ThalesProtectRevealHelper and the determined protection profile
				String encryptedText = encryptData(piiText, tprh, protection_profile);

				// Replace the original PII text with the encrypted text in the StringBuilder
				modifiedLine.replace(beginOffset, endOffset, encryptedText);
				// Update the offset adjustment based on the difference in length between
				// the original PII text and its encrypted form
				offsetAdjustment += encryptedText.length() - piiText.length();
			}

			// Add the line's entities to the overall total entities found
			total_entities_found = total_entities_found + line_entities_found;

			// Convert the StringBuilder content back to a String
			return_value = modifiedLine.toString();
		}

		// Print the total number of entities found in the current line
		System.out.println("total number of entities in line " + line_entities_found);
		return return_value;
	}

	/**
	 * Processes a file line by line, either protecting (encrypting PII) or
	 * revealing (decrypting previously protected data) its content.
	 *
	 * @param pdfFile The input file to be processed.
	 * @param outputDir The output directory or file where the processed content will be written.
	 * @param projectId (Currently unused in this method, likely for broader project context).
	 * @param tprh An instance of ThalesProtectRevealHelper for encryption/decryption operations.
	 * @param mode The processing mode: "protect" to encrypt PII, or anything else (e.g., "reveal") to decrypt.
	 * @param skiphdr A boolean indicating whether to skip the first line (header) of the input file.
	 * @return The number of lines processed in the file.
	 */
	public int processFile(File pdfFile, File outputDir, String projectId, ThalesProtectRevealHelper tprh,
			String mode, boolean skiphdr) {

		int nbroflines = 0; // Counter for the number of lines processed
		// Build Comprehend client with the specified AWS region
		ComprehendClient comprehendClient = ComprehendClient.builder().region(awsregion).build();

		// Use try-with-resources to ensure BufferedReader and BufferedWriter are closed automatically
		try (BufferedReader reader = Files.newBufferedReader(pdfFile.toPath());
				BufferedWriter writer = Files.newBufferedWriter(outputDir.toPath())) {

			// If skiphdr is true, read and discard the first line (header)
			if (skiphdr) {
				String headerLine = reader.readLine(); // Read header (skip this line)
			}
			String line;
			String content = null; // Variable to hold the processed content of each line
			// Read the file line by line until the end
			while ((line = reader.readLine()) != null) {
				nbroflines++; // Increment line counter
				// Based on the mode, either protect (encrypt) the line or decrypt it
				if (mode.equalsIgnoreCase("protect"))
					content = processText(line, tprh); // Encrypt PII in the line
				else
					content = decryptLine(line, tprh); // Decrypt the line (assuming decryptLine is in ContentProcessor)
				writer.write(content); // Write the processed content to the output file
				writer.newLine(); // Ensure each processed line is on a new line in the output file
			}

			System.out.println("Processing complete! Check the output file: " + outputDir.getAbsolutePath());

		} catch (IOException e) {
			// Print stack trace if an I/O error occurs
			e.printStackTrace();
		}

		return nbroflines; // Return the total number of lines processed
	}

}
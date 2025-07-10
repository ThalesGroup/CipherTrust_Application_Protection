package com.example;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets; // Not explicitly used but good for clarity in I/O operations
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Base64; // Not explicitly used for encoding in this class, but might be in helper classes
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.stream.Collectors;
import java.util.stream.Stream;

// Google Cloud DLP API imports
import com.google.cloud.dlp.v2.DlpServiceClient;
import com.google.privacy.dlp.v2.ByteContentItem;
import com.google.privacy.dlp.v2.ContentItem;
import com.google.privacy.dlp.v2.Finding;
import com.google.privacy.dlp.v2.InfoType;
import com.google.privacy.dlp.v2.InspectConfig;
import com.google.privacy.dlp.v2.InspectContentRequest;
import com.google.privacy.dlp.v2.InspectContentResponse;
import com.google.privacy.dlp.v2.InspectResult;
import com.google.privacy.dlp.v2.Likelihood;
import com.google.privacy.dlp.v2.LocationName;
import com.google.protobuf.ByteString;

/**
 * This class extends ContentProcessor and provides functionality to process content
 * using Google Cloud Data Loss Prevention (DLP) API. It can be used to either
 * protect (detect and encrypt) or reveal (decrypt) sensitive information within text files.
 */
public class GCPContentProcessor extends ContentProcessor {

	/**
	 * Constructor for GCPContentProcessor.
	 * @param p Properties object containing configuration for the processor.
	 */
	public GCPContentProcessor(Properties p) {
		super(p);
		// TODO Auto-generated constructor stub - This comment suggests potential for more constructor logic.
	}

	/**
	 * Processes a single file, either protecting or revealing its sensitive content.
	 * It reads the file line by line, applies the specified mode (protect or reveal),
	 * and writes the processed content to an output file.
	 *
	 * @param inputFile The input file to be processed.
	 * @param outputDir The output file where the processed content will be written.
	 * @param projectId The Google Cloud project ID for DLP API calls.
	 * @param tprh An instance of ThalesProtectRevealHelper for encryption/decryption operations.
	 * @param mode The processing mode: "protect" to detect and encrypt, or "reveal" to decrypt.
	 * @param skiphdr A boolean flag indicating whether to skip the header line of the input file.
	 * @return The number of lines processed in the file.
	 */
	public int processFile(File inputFile, File outputDir, String projectId, ThalesProtectRevealHelper tprh, String mode,
			boolean skiphdr) {

		int nbroflines = 0; // Counter for the number of lines processed.
		try (BufferedReader reader = Files.newBufferedReader(inputFile.toPath()); // Reader for the input file.
				BufferedWriter writer = Files.newBufferedWriter(outputDir.toPath())) { // Writer for the output file.

			if (skiphdr) {
				String headerLine = reader.readLine(); // Read and discard the header line if skiphdr is true.
			}
			String line;
			String content = null;
			// Read the file line by line until the end.
			while ((line = reader.readLine()) != null) {
				nbroflines++;
				//System.out.println("lenth of line " + line.length()); // Debugging line length.
				
				// Handle very short lines or empty lines.
				if (line.length() < 2) {
					content = line; // If the line is too short, keep it as is.
				} else {
					// Based on the mode, either protect or decrypt the content.
					if (mode.equalsIgnoreCase("protect"))
						content = processText(projectId, line, tprh); // Protect the line using DLP.
					else
						content = decryptLine(line, tprh); // Decrypt the line using Thales helper.
				}

				writer.write(content); // Write the processed content to the output file.
				writer.newLine(); // Ensure each processed line is on a new line in the output.
			}

			System.out.println("Processing complete! Check the output file: " + outputDir.getAbsolutePath());

		} catch (IOException e) {
			e.printStackTrace(); // Print stack trace if an I/O error occurs.
		}

		return nbroflines; // Return the total number of lines processed.

	}

	/**
	 * This method is intended for processing text by splitting it (e.g., by commas)
	 * and then applying DLP inspection and protection to each segment.
	 * It is currently not used in the `processFile` method, suggesting it might be an alternative
	 * or experimental approach.
	 *
	 * @param projectId The Google Cloud project ID.
	 * @param line The input text line to be processed.
	 * @param tprh An instance of ThalesProtectRevealHelper for encryption.
	 * @return The processed line with sensitive data replaced by encrypted tokens.
	 * @throws IOException If an I/O error occurs during DLP API communication.
	 */
	public String processTextSplit(String projectId, String line, ThalesProtectRevealHelper tprh) throws IOException {

		String resultString = line; // Initialize result with the original line.

		try (DlpServiceClient dlpServiceClient = DlpServiceClient.create()) { // Create a DLP service client.

			String[] values = line.split(","); // Split the line by comma, assuming CSV-like format.

			// Define a list of InfoTypes (types of sensitive data) to detect.
			List<InfoType> infoTypes = Stream
					.of("PERSON_NAME", "CREDIT_CARD_NUMBER", "DATE_OF_BIRTH", "EMAIL_ADDRESS", "PHONE_NUMBER",
							"STREET_ADDRESS", "US_SOCIAL_SECURITY_NUMBER")
					.map(it -> InfoType.newBuilder().setName(it).build()).collect(Collectors.toList());

			// Set the minimum likelihood for a finding to be considered.
			Likelihood minLikelihood = Likelihood.POSSIBLE;

			// Configure finding limits (e.g., maximum findings per item). Here, 0 means no limit.
			InspectConfig.FindingLimits findingLimits = InspectConfig.FindingLimits.newBuilder()
					.setMaxFindingsPerItem(0).build();

			// Build the InspectConfig with defined InfoTypes, likelihood, limits, and to include quotes.
			InspectConfig inspectConfig = InspectConfig.newBuilder().addAllInfoTypes(infoTypes)
					.setMinLikelihood(minLikelihood).setLimits(findingLimits).setIncludeQuote(true).build();

			System.out.println("Inspecting and replacing sensitive values:");
			int totalFindings = 0;

			// Build a list to hold the possibly updated values after inspection and protection.
			List<String> updatedValues = new ArrayList<>();

			// Iterate over each split value in the line.
			for (String value : values) {
				String trimmedValue = value.trim(); // Trim whitespace from the value.

				// Create a ByteContentItem from the trimmed value for DLP API.
				ByteContentItem byteContentItem = ByteContentItem.newBuilder()
						.setType(ByteContentItem.BytesType.TEXT_UTF8)
						.setData(com.google.protobuf.ByteString.copyFromUtf8(trimmedValue)).build();
				ContentItem contentItem = ContentItem.newBuilder().setByteItem(byteContentItem).build();

				// Build the InspectContentRequest.
				InspectContentRequest request = InspectContentRequest.newBuilder()
						.setParent(LocationName.of(projectId, "global").toString()).setInspectConfig(inspectConfig)
						.setItem(contentItem).build();

				// Send the request to DLP API and get the response.
				InspectContentResponse response = dlpServiceClient.inspectContent(request);
				InspectResult result = response.getResult();
				int findingsCount = result.getFindingsCount(); // Get the number of findings for the current value.
				totalFindings += findingsCount; // Accumulate total findings.

				String updatedValue = trimmedValue; // Initialize updatedValue with the original trimmed value.

				if (findingsCount > 0) {
					System.out.println("\nFindings for value: \"" + trimmedValue + "\"");
					// Iterate through each finding.
					for (Finding finding : result.getFindingsList()) {
						String quote = finding.getQuote(); // The actual sensitive data found.
						String piitype = finding.getInfoType().getName(); // The type of PII found.
						String protection_type = piiMap.get(piitype); // Get the protection type from a map.

						// Print finding details.
						System.out.println("\tQuote: " + quote);
						System.out.println("\tInfo type: " + finding.getInfoType().getName());
						System.out.println("\tLikelihood: " + finding.getLikelihood());
						System.out.println("\tLikelihood value : " + finding.getLikelihoodValue());
						
						// If the likelihood of the finding is above a certain threshold (3), encrypt it.
						if (finding.getLikelihoodValue() > 3) {
							String encoded = encryptData(quote, tprh, protection_type); // Encrypt the sensitive data.
							updatedValue = updatedValue.replace(quote, encoded); // Replace the original quote with the encrypted one.
						} else {
							total_skipped_entities++; // Increment skipped entities if likelihood is too low.
						}
					}
				} else {
					System.out.println("No findings for value: \"" + trimmedValue + "\"");
				}

				updatedValues.add(updatedValue); // Add the modified (or original) value to the list.
			}

			total_entities_found = total_entities_found + totalFindings; // Update global count of entities found.

			// Join the updated values back into a single comma-separated string.
			resultString = String.join(",", updatedValues);
		//	System.out.println("\nUpdated string with Base64 replacements:\n" + resultString); // Debugging output.
		}

		return resultString; // Return the processed string.
	}

	/**
	 * Processes a single line of text by sending it to Google Cloud DLP for inspection,
	 * and then encrypts any identified sensitive information.
	 *
	 * @param projectId The Google Cloud project ID for DLP API calls.
	 * @param line The input text line to be inspected and protected.
	 * @param tprh An instance of ThalesProtectRevealHelper for encryption operations.
	 * @return The modified text line with sensitive data replaced by encrypted tokens.
	 * @throws IOException If an I/O error occurs during DLP API communication.
	 */
	public String processText(String projectId, String line, ThalesProtectRevealHelper tprh) throws IOException {

		String modifiedText = null;
		try (DlpServiceClient dlpServiceClient = DlpServiceClient.create()) { // Create a DLP service client.

			// Create a ByteContentItem from the input line (UTF-8 encoded).
			ByteContentItem byteContentItem = ByteContentItem.newBuilder().setType(ByteContentItem.BytesType.TEXT_UTF8)
					.setData(ByteString.copyFromUtf8(line)).build();

			// Wrap the ByteContentItem in a ContentItem.
			ContentItem contentItem = ContentItem.newBuilder().setByteItem(byteContentItem).build();

			/*
			 * List<InfoType> infoTypes = Stream.of( "PERSON_NAME", "US_STATE",
			 * "CREDIT_CARD_NUMBER", "DATE_OF_BIRTH", "EMAIL_ADDRESS", "PHONE_NUMBER",
			 * "STREET_ADDRESS", "LOCATION", "DATE", "US_SOCIAL_SECURITY_NUMBER")
			 */
			// Define the InfoTypes (types of sensitive data) to detect.
			List<InfoType> infoTypes = Stream
					.of("PERSON_NAME", "CREDIT_CARD_NUMBER", "DATE_OF_BIRTH", "EMAIL_ADDRESS", "PHONE_NUMBER",
							"STREET_ADDRESS", "US_SOCIAL_SECURITY_NUMBER")
					.map(it -> InfoType.newBuilder().setName(it).build()).collect(Collectors.toList());

			// Configure finding limits (e.g., maximum findings per item). Here, 0 means no limit.
			InspectConfig.FindingLimits findingLimits = InspectConfig.FindingLimits.newBuilder()
					.setMaxFindingsPerItem(0).build();

			// Build the InspectConfig with defined InfoTypes, minimum likelihood, limits, and to include quotes.
			InspectConfig inspectConfig = InspectConfig.newBuilder().addAllInfoTypes(infoTypes)
					.setMinLikelihood(Likelihood.POSSIBLE).setLimits(findingLimits).setIncludeQuote(true).build();

			// Build the InspectContentRequest.
			InspectContentRequest request = InspectContentRequest.newBuilder()
					.setParent(LocationName.of(projectId, "global").toString()).setInspectConfig(inspectConfig)
					.setItem(contentItem).build();

			// Send the request to DLP API and get the response.
			InspectContentResponse response = dlpServiceClient.inspectContent(request);
			InspectResult result = response.getResult();

	//		System.out.println("Total findings: " + result.getFindingsCount()); // Debugging total findings.

			// Update the global count of entities found.
			total_entities_found = total_entities_found + result.getFindingsCount();
		//	System.out.println("new code total_entities_found " + total_entities_found); // Debugging updated total.

			// If no findings are present, return the original line as is.
			if (result.getFindingsCount() <= 0) {
				//System.out.println("No findings."); // Debugging no findings.
				return line;
			}

			// Store replacements in a map: original quote -> encrypted quote.
			Map<String, String> replacements = new HashMap<>();

			// Iterate through each finding.
			for (Finding finding : result.getFindingsList()) {
				String quote = finding.getQuote(); // The actual sensitive data found.
				// String encoded = base64Encode(quote); // Commented out - suggests an alternative encoding method.
				String piitype = finding.getInfoType().getName(); // The type of PII found.
				String protection_type = piiMap.get(piitype); // Get the protection type from a map.

				// Print finding details.
				System.out.println("\tQuote: " + quote);
				System.out.println("\tInfo type: " + finding.getInfoType().getName());
				System.out.println("\tLikelihood: " + finding.getLikelihood());
				System.out.println("\tLikelihood value : " + finding.getLikelihoodValue());
				
				// If the likelihood of the finding is above a certain threshold (3), encrypt it.
				if (finding.getLikelihoodValue() > 3) {
					String encoded = encryptData(quote, tprh, protection_type); // Encrypt the sensitive data.
					replacements.put(quote, encoded); // Add the original quote and its encrypted version to the map.
				} else {
					total_skipped_entities++; // Increment skipped entities if likelihood is too low.
				}
			}

			// Sort quotes by descending length to avoid partial replacement conflicts.
			// This ensures that longer matches are replaced first (e.g., "John Doe" before "John").
			List<Map.Entry<String, String>> sortedReplacements = new ArrayList<>(replacements.entrySet());
			sortedReplacements.sort((a, b) -> Integer.compare(b.getKey().length(), a.getKey().length()));

			modifiedText = line; // Start with the original line.
			// Iterate through the sorted replacements and apply them to the text.
			for (Map.Entry<String, String> entry : sortedReplacements) {
				modifiedText = modifiedText.replace(entry.getKey(), entry.getValue());
			}

			// System.out.println("\nModified Text with base64-encoded findings:\n" + modifiedText); // Debugging output.
		}

		return modifiedText; // Return the modified text with sensitive data protected.
	}

}

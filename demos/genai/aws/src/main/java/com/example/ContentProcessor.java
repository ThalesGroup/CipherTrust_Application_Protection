package com.example;
import java.io.File;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;


/**
 * Abstract class providing common functionalities for content processing,
 * especially for handling PII (Personally Identifiable Information)
 * protection and revelation using ThalesProtectRevealHelper.
 */
public abstract class ContentProcessor  {

	// Delimiter used in encoded/encrypted strings.
	private static final String delimeter = ":";
	// Properties object to hold configuration settings.
	private static Properties properties;

	// Map to store tag names and their corresponding values (e.g., protection profiles).
	protected static Map<String, String> tagMap = null;
	// Map to store PII types and their associated protection profiles.
	protected static Map<String, String> piiMap = null;
	// Total count of entities (e.g., PIIs) found across all processed files.
	public  int total_entities_found = 0;
	// Count of entities found in the current line being processed.
	protected static int line_entities_found = 0;
	// Total count of entities that were skipped during processing.
	protected static int total_skipped_entities = 0;


	/**
	 * Abstract method to be implemented by concrete subclasses for processing a file.
	 *
	 * @param inputFile The  file to be processed.
	 * @param outputDir The directory where output files should be saved.
	 * @param projectId The project ID associated with the processing.
	 * @param tprh An instance of ThalesProtectRevealHelper for protection/revelation operations.
	 * @param mode The processing mode (e.g., protect, reveal).
	 * @param skiphdr A boolean indicating whether to skip header processing.
	 * @return An integer representing the result of the file processing.
	 */
	public abstract int processFile(File inputFile, File outputDir, String projectId, ThalesProtectRevealHelper tprh,
			String mode, boolean skiphdr);


	/**
	 * Constructor for ContentProcessor. Initializes properties and loads tag and PII mappings.
	 *
	 * @param p The Properties object containing configuration.
	 */
	public  ContentProcessor(Properties p)
	{
		properties = p;
		// Populate the tagMap from properties.
		 tagMap = getTagValues();
		if (tagMap != null) {
			for (Map.Entry<String, String> entry : tagMap.entrySet()) {
				// This loop is currently empty, but could be used for debugging or further processing of tagMap.
			}
		}

		// Populate the piiMap using the tagMap.
		 piiMap = getPiiValues(tagMap);

		if (piiMap != null) {
			for (Map.Entry<String, String> entry : piiMap.entrySet()) {
				// This loop is currently empty, but could be used for debugging or further processing of piiMap.
				// System.out.println("Key: " + entry.getKey() + ", Value: " + entry.getValue());
			}
		}

	}

	/**
	 * Sets the properties for the content processor.
	 * @param p The Properties object to set.
	 */
	public void setProperties(Properties p)
	{
		properties = p;

	}

	/**
	 * Decrypts a given data string using the ThalesProtectRevealHelper.
	 * The data string is expected to be in a specific format (e.g., "prefix:encryptedData").
	 *
	 * @param data The encrypted data string.
	 * @param protection_profile The protection profile to use for decryption.
	 * @param tprh An instance of ThalesProtectRevealHelper.
	 * @return The decrypted string.
	 */
	private static String decryptData(String data, String protection_profile, ThalesProtectRevealHelper tprh) {

		String policyType = "external";

		// Determine if the policy type is internal based on the protection profile.
		boolean policyTypeInternal = protection_profile.toLowerCase().contains("internal");
		if (policyTypeInternal)
			policyType = "internal";

		String parsedString = null;
		// Find the index of the delimiter to extract the actual encrypted data.
		int colonIndex = data.indexOf(':');
		// Ensure the colon exists and is not at the end of the string.
		if (colonIndex != -1 && colonIndex < data.length() - 1) {
			parsedString = data.substring(colonIndex + 1);
			System.out.println("Parsed using indexOf/substring: " + parsedString);
		} else {
			System.out.println("Colon not found or at the end of the string.");
		}

		// Reveal the data using the ThalesProtectRevealHelper.
		String decryptedData = tprh.revealData(parsedString, protection_profile, policyType);
		int nbrofchars = decryptedData.length(); // Get the number of characters in the decrypted data.

		return decryptedData;

	}

	/**
	 * Decrypts encrypted entities within a single line of text.
	 * It looks for specific prefixes to identify encrypted data and then decrypts them.
	 *
	 * @param line The line of text to decrypt.
	 * @param tprh An instance of ThalesProtectRevealHelper.
	 * @return The line with encrypted data replaced by decrypted data.
	 */
	public  String decryptLine(String line, ThalesProtectRevealHelper tprh) {
		// Prefixes indicating encrypted data in the line.
		String[] prefixes = { "RU5DY2hhcg==", "RU5DbmJy" }; // These are Base64 encoded prefixes, likely "ENCchar" and "ENCnbr"
		Map<String, String> foundValues = new HashMap<>(); // Stores original encrypted strings and their extracted data.
		Map<String, String> protection_profileMap = new HashMap<>(); // Stores original encrypted strings and their determined protection profiles.
		StringBuilder modifiedLine = new StringBuilder(line); // Use StringBuilder for efficient string modification.
		String protection_profile = null;

		// Iterate through each defined prefix.
		for (String prefix : prefixes) {
			int prefixLength = prefix.length();
			int index = 0;

			// Find all occurrences of the current prefix followed by a hyphen.
			while ((index = modifiedLine.indexOf(prefix + "-", index)) != -1) {

				int hyphenIndex = index + prefixLength;
				int colonIndex = modifiedLine.indexOf(":", hyphenIndex); // Find the delimiter after the byte count.

				if (colonIndex != -1) {
					try {
						// Parse the byte count between the hyphen and the colon.
						int byteCount = Integer.parseInt(modifiedLine.substring(hyphenIndex + 1, colonIndex));
						int dataStartIndex = colonIndex + 1; // Start index of the actual encrypted data.

						// Check if the reported byte count is within the bounds of the line.
						if (dataStartIndex + byteCount <= modifiedLine.length()) {
							String encryptedData = modifiedLine.substring(dataStartIndex, dataStartIndex + byteCount); // Extract encrypted data.
							String originalValue = modifiedLine.substring(index, dataStartIndex + byteCount); // Get the entire original encrypted string (prefix-bytecount:data).
							foundValues.put(originalValue, encryptedData); // Store for later decryption.

							// Decode the prefix to get the original tag name.
							String protection_profile_tag = base64Decode(prefix);

							// If the decoded tag starts with the configured TAGPREFIX, remove it.
							if (protection_profile_tag.startsWith(properties.getProperty("TAGPREFIX"))) {
								protection_profile_tag = protection_profile_tag.substring(3); // Remove the first 3 characters (e.g., "TAG").
							}

							// Get the actual protection profile from the tagMap using the cleaned tag.
							protection_profile = tagMap.get(protection_profile_tag);

							protection_profileMap.put(originalValue, protection_profile); // Store the protection profile for the original value.
							index = dataStartIndex + byteCount; // Move past the processed section to find the next occurrence.
						} else {
							System.err.println(
									"Warning: Not enough bytes after colon for " + modifiedLine.substring(index));
							index = colonIndex + 1; // Move past the invalid section.
						}

					} catch (NumberFormatException e) {
						System.err.println("Error parsing byte count: " + e.getMessage());
						index = colonIndex + 1; // Move past the invalid section.
					}
				} else {
					index += prefixLength + 1; // Move past the prefix if no colon found to avoid infinite loop.
				}
			}
		}

		// This loop iterates through protection_profileMap, but doesn't perform any action.
		// It might be a leftover from debugging or a placeholder for future functionality.
		for (Map.Entry<String, String> entry : protection_profileMap.entrySet()) {
			String originalValue = entry.getKey();
			String profiletouse = entry.getValue();
		}

		// Now, iterate through the found encrypted values and decrypt them.
		for (Map.Entry<String, String> entry : foundValues.entrySet()) {
			String originalValue = entry.getKey();
			String encryptedData = entry.getValue(); // This variable is not used directly, as originalValue is passed to decryptData.

			protection_profile = protection_profileMap.get(originalValue); // Retrieve the correct profile for this original value.

			// Decrypt the data using the determined protection profile.
			String decryptedData = decryptData(originalValue, protection_profile, tprh);

			// Find the original encrypted string in the modifiedLine and replace it with the decrypted data.
			int startIndex = modifiedLine.indexOf(originalValue);
			if (startIndex != -1) {
				modifiedLine.replace(startIndex, startIndex + originalValue.length(), decryptedData);
			}

		}

		// Update the total count of entities found.
		total_entities_found = total_entities_found + foundValues.size();

		return modifiedLine.toString(); // Return the modified line with decrypted values.
	}

	/**
	 * Encrypts a given data string using ThalesProtectRevealHelper and formats it with a prefix,
	 * byte count, and delimiter.
	 *
	 * @param data The data string to encrypt.
	 * @param tprh An instance of ThalesProtectRevealHelper.
	 * @param protection_profile The protection profile to use for encryption. If null, a default policy is used.
	 * @return The formatted encrypted string (e.g., "Base64EncodedTag-ByteCount:EncryptedData").
	 */
	protected static String encryptData(String data, ThalesProtectRevealHelper tprh, String protection_profile) {

		String policyType = "external";

		// If no protection profile is provided, use the default from properties.
		if (protection_profile == null) {
			protection_profile = properties.getProperty("POLICYNAME");
		}

		// Get the tag name associated with the protection profile from the tagMap.
		String tagname = getKeyByValue(tagMap, protection_profile);
		//System.out.println("tag name " + tagname);

		// Determine if the policy type is internal.
		boolean policyTypeInternal = protection_profile.toLowerCase().contains("internal");
		if (policyTypeInternal)
			policyType = "internal";

		// Get the tag prefix from properties and prepend it to the tag name.
		String tagprefix = properties.getProperty("TAGPREFIX");
		tagname = tagprefix + tagname;

		// Protect the data using ThalesProtectRevealHelper.
		String encryptedData = tprh.protectData(data, protection_profile, policyType);
		int nbrofchars = encryptedData.length(); // Get the number of characters in the encrypted data.
		String prefix = base64Encode(tagname); // Base64 encode the full tag name for the prefix.

		// Return the formatted encrypted string.
		return prefix + "-" + nbrofchars + delimeter + encryptedData;

	}

	/**
	 * Retrieves tag values from the properties. Properties with keys starting with "TAG."
	 * are considered tag definitions. The "TAG." prefix is removed from the key to get the actual tag name.
	 *
	 * @return A Map where keys are tag names and values are their corresponding string values (e.g., protection profile names).
	 */
	private static Map<String, String> getTagValues() {
		Map<String, String> tagValues = new HashMap<>();
		if (properties != null) {
			// Iterate through all property names.
			for (String key : properties.stringPropertyNames()) {
				// Check if the property key starts with "TAG.".
				if (key.startsWith("TAG.")) {
					String newKey = key.substring(4); // Remove "TAG." to get the actual tag key.
					String value = properties.getProperty(key); // Get the value associated with the tag key.
					tagValues.put(newKey, value); // Add to the tagValues map.
				}
			}
		}
		return tagValues;
	}

	/**
	 * Finds the key in a map given its value. If the value is not found, or is null,
	 * it returns a default value from the properties.
	 *
	 * @param map The map to search within.
	 * @param value The value to search for.
	 * @param <K> The type of the keys in the map.
	 * @param <V> The type of the values in the map.
	 * @return The key associated with the value, or a default value if not found or value is null.
	 */
	private static <K, V> K getKeyByValue(Map<K, V> map, V value) {

		// Get a default policy name from properties to return if the value is not found or null.
		K defaultValue = (K) properties.getProperty("POLICYNAME");

		if (value == null) {
			return defaultValue; // Return default if value is null.
		}
		// Iterate through the map entries to find a matching value.
		for (Map.Entry<K, V> entry : map.entrySet()) {
			if (value.equals(entry.getValue())) {
				return entry.getKey(); // Return the key if the value matches.
			}
		}
		return defaultValue; // Value not found, return default.
	}

	/**
	 * Retrieves PII (Personally Identifiable Information) mappings from properties.
	 * Properties with keys starting with "PII." are considered PII definitions.
	 * The value of a "PII." property is expected to be a reference to a "TAG." property,
	 * which then provides the actual protection profile.
	 *
	 * @param tagMap A map of tag names to their values (protection profiles).
	 * @return A Map where keys are PII types and values are their corresponding protection profiles.
	 */
	private static Map<String, String> getPiiValues(Map<String, String> tagMap) {
		Map<String, String> piiValues = new HashMap<>();
		if (properties != null) {
			// Iterate through all property names.
			for (String key : properties.stringPropertyNames()) {
				// Check if the property key starts with "PII.".
				if (key.startsWith("PII.")) {
					String newKey = key.substring(4); // Remove "PII." to get the actual PII type.
					String tagReference = properties.getProperty(key); // Get the value, which is expected to be a tag reference (e.g., "TAG.char").
					// Check if the tag reference is valid and starts with "TAG.".
					if (tagReference != null && tagReference.startsWith("TAG.")) {
						String tagKey = tagReference.substring(4); // Remove "TAG." to get the tag key.
						String tagValue = tagMap.get(tagKey); // Look up the actual protection profile in the tagMap.
						if (tagValue != null) {
							piiValues.put(newKey, tagValue); // Add the PII type and its protection profile to piiValues.
						}
					}
				}
			}
		}
		return piiValues;
	}

	/**
	 * Encodes a given string into its Base64 representation using UTF-8 charset.
	 * @param input The string to encode.
	 * @return The Base64 encoded string.
	 */
	private static String base64Encode(String input) {
		byte[] encodedBytes = Base64.getEncoder().encode(input.getBytes(StandardCharsets.UTF_8));
		return new String(encodedBytes, StandardCharsets.UTF_8);
	}

	/**
	 * Decodes a Base64 encoded string back to its original string representation using UTF-8 charset.
	 * @param encodedInput The Base64 encoded string.
	 * @return The decoded string.
	 */
	private static String base64Decode(String encodedInput) {
		byte[] decodedBytes = Base64.getDecoder().decode(encodedInput.getBytes(StandardCharsets.UTF_8));
		return new String(decodedBytes, StandardCharsets.UTF_8);
	}


}
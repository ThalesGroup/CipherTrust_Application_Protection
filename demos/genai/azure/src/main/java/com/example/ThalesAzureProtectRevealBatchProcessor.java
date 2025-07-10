package com.example;
import java.io.*;
import java.util.Properties;

/**
 * ThalesAzureProtectRevealBatchProcessor is a batch processing application
 * designed to protect (encrypt) or reveal (decrypt) data within files,
 * specifically targeting Azure-related content, using Thales CipherTrust
 * Data Protection (CADP) solutions.
 * It reads configuration from a properties file, processes input files,
 * and writes the protected/revealed output to a specified directory.
 */
public class ThalesAzureProtectRevealBatchProcessor {

	// A static Properties object to hold configuration loaded from thales-config.properties
	private static Properties properties;

	/**
	 * Static initializer block to load properties from "thales-config.properties"
	 * when the class is loaded. This ensures that configuration is available
	 * before any other methods are called.
	 * It throws a RuntimeException if the properties file cannot be found or loaded.
	 */
	static {
		try (InputStream input = ThalesAzureProtectRevealBatchProcessor.class.getClassLoader()
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
	 * It orchestrates the entire process of reading configuration,
	 * initializing helpers, processing files, and reporting statistics.
	 *
	 * @param args Command-line arguments:
	 * args[0]: mode (e.g., "protect" or "reveal")
	 * args[1]: Azure Cognitive Services Endpoint
	 * args[2]: Azure Cognitive Services API Key
	 * args[3]: Input directory path
	 * args[4]: Output directory path
	 * args[5]: File extension to process (e.g., "pdf", "txt")
	 * @throws IOException If an I/O error occurs during file operations.
	 */
	public static void main(String[] args) throws IOException {

		// Record the start time in nanoseconds for performance measurement
		long startTime = System.nanoTime();

		// Flag to skip header (not explicitly used in the provided code, but often useful in batch processing)
		boolean skiphdr = false;
		// Cloud Service Provider, currently hardcoded to "azure"
		String csp = "azure";
		// Counter for number of records processed in the current file
		int nbrofrecords = 0;
		// Total number of records processed across all files
		int totalnbrofrecords = 0;

		// Retrieve various configuration properties from the loaded properties object
		String metadata = properties.getProperty("METADATA");
		String crdpip = properties.getProperty("CRDPIP");
		String keymanagerhost = properties.getProperty("KEYMGRHOST");
		String crdptkn = properties.getProperty("CRDPTKN");
		String policyType = properties.getProperty("POLICYTYPE");
		String defaultpolicy = properties.getProperty("DEFAULTPOLICY");
		String showmetadata = properties.getProperty("SHOWMETADATA");
		String revealuser = properties.getProperty("REVEALUSER");
		System.out.println(" user  " + revealuser); // Print the reveal user

		// Convert showmetadata property to a boolean
		boolean showmeta = showmetadata.equalsIgnoreCase("true");

		// Initialize ThalesCADPProtectRevealHelper. This helper class is responsible
		// for interacting with the Thales CipherTrust Manager for cryptographic operations.
		ThalesCADPProtectRevealHelper tprh = new ThalesCADPProtectRevealHelper(keymanagerhost, crdptkn, null,
				policyType, showmeta);

		// The commented-out line below shows an alternative helper for REST-based protection/reveal.
		// ThalesProtectRevealHelper tprh = new ThalesRestProtectRevealHelper(crdpip, metadata, policyType, showmeta);

		// Set additional properties for the Thales CADP helper
		tprh.revealUser = revealuser;
		tprh.policyType = policyType;
		tprh.policyName = properties.getProperty("POLICYNAME");
		tprh.defaultPolicy = defaultpolicy;

		// Initialize a ContentProcessor based on the Cloud Service Provider.
		// This processor handles the specific content type (e.g., Azure documents).
		ContentProcessor cp = null;
		if (csp.equalsIgnoreCase("azure"))
			cp = new AzureContentProcessor(properties);

		// Declare File objects for input and output directories
		File inputDir = null;
		File outputDir = null;
		
		// Parse command-line arguments
		String mode = args[0]; // "protect" or "reveal"
		AzureContentProcessor.cognitiveservices_endpoint = args[1]; // Azure Cognitive Services Endpoint
		AzureContentProcessor.cognitiveservices_apiKey = args[2];   // Azure Cognitive Services API Key
		inputDir = new File(args[3]); // Input directory path
		outputDir = new File(args[4]); // Output directory path
		String fileextension = args[5]; // File extension to process

		int nbroffiles = 0; // Counter for the number of files processed
		
		// Get a list of files from the input directory that match the specified file extension
		File[] inputFiles = inputDir.listFiles((dir, name) -> name.toLowerCase().endsWith(fileextension));

		File outputFile = null; // Declare outputFile here to be accessible within the loop

		// Check if any input files were found
		if (inputFiles != null) {
			// Iterate through each input file
			for (File inputFile : inputFiles) {

				// Determine the output file name based on the mode ("protected" or "revealed" prefix)
				if (mode.equalsIgnoreCase("protect"))
					outputFile = new File(outputDir, "protected" + inputFile.getName());
				else
					outputFile = new File(outputDir, "revealed" + inputFile.getName());

				// Process the file using the appropriate ContentProcessor (AzureContentProcessor in this case)
				if (csp.equalsIgnoreCase("azure"))
					nbrofrecords = cp.processFile(inputFile, outputFile, null, tprh, mode, skiphdr);

				nbroffiles++; // Increment the count of processed files
			}
			// Accumulate the total number of records processed
			totalnbrofrecords = totalnbrofrecords + nbrofrecords;
		} else {
			// If no files were found, print a message
			System.out.println("No " + fileextension + " files found in the directory: " + inputDir.getAbsolutePath());
		}

		// Record the end time in nanoseconds
		long endTime = System.nanoTime();

		// Calculate the elapsed time in nanoseconds
		long elapsedTimeNano = endTime - startTime;

		// Convert nanoseconds to seconds for readability
		double elapsedTimeSeconds = (double) elapsedTimeNano / 1_000_000_000.0;

		// Print the application execution time
		System.out.printf("Application execution time: %.6f seconds%n", elapsedTimeSeconds);

		// Print final statistics
		System.out.println("Number of files = " + nbroffiles);
		System.out.println("Total nbr of records = " + totalnbrofrecords);
		// Assuming cp (ContentProcessor) has these public fields for statistics
		System.out.println("Total skipped entities = " + cp.total_skipped_entities);
		System.out.println("Total entities found = " + cp.total_entities_found);
	}
}

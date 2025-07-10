package com.example;
import java.io.*;
import java.util.Properties;

/**
 * This class serves as a batch processor for protecting and revealing data
 * using Thales CipherTrust Data Security Platform (CADP) in conjunction with
 * Google Cloud Platform (GCP) DLP for sensitive data detection.
 * It reads configuration from a properties file, processes files in a specified
 * directory, and performs either protection or revelation based on the provided mode.
 */
public class ThalesGCPProtectRevealBatchProcessor {

	// Properties object to hold configurations loaded from the properties file.
	private static Properties properties;

	/**
	 * Static initializer block to load properties from "thales-config.properties" file.
	 * This block is executed once when the class is loaded.
	 * It throws a RuntimeException if the file is not found or an error occurs during loading.
	 */
	static {
		try (InputStream input = ThalesGCPProtectRevealBatchProcessor.class.getClassLoader()
				.getResourceAsStream("thales-config.properties")) {
			properties = new Properties();
			if (input == null) {
				// Throws an exception if the properties file is not found.
				throw new RuntimeException("Unable to find udfConfig.properties");
			}
			// Loads properties from the input stream.
			properties.load(input);

		} catch (Exception ex) {
			// Catches any exception during properties loading and re-throws as a RuntimeException.
			throw new RuntimeException("Error loading properties file", ex);
		}
	}

	/**
	 * The main method, serving as the entry point of the application.
	 * It processes command-line arguments, initializes necessary objects,
	 * and orchestrates the protection or revelation of files using GCP DLP and Thales CADP.
	 *
	 * @param args Command-line arguments:
	 * args[0]: mode ("protect" or "reveal")
	 * args[1]: inputDirectory (path to the directory containing files to process)
	 * args[2]: outputDirectory (path to the directory where processed files will be saved)
	 * args[3]: fileExtension (e.g., ".txt", ".csv")
	 * args[4]: projectId (Google Cloud Project ID for DLP operations)
	 * @throws IOException If an I/O error occurs during file processing.
	 */
	public static void main(String[] args) throws IOException {
		
		// Flag to indicate whether to skip header rows in files.
		boolean skiphdr = false;
		// Cloud Service Provider, currently set to GCP.
		String csp = "GCP";
		// Counter for the number of records processed in the current file.
		int nbrofrecords = 0;
		// Counter for the total number of records processed across all files.
		int totalnbrofrecords = 0;
		// Retrieves various configuration properties from the loaded properties object.
		String metadata = properties.getProperty("METADATA"); // Metadata for Thales operations (might be null if not used by CADP)
		String crdpip = properties.getProperty("CRDPIP");     // IP for Thales REST service (used if ThalesRestProtectRevealHelper is chosen)

		String keymanagerhost = properties.getProperty("KEYMGRHOST"); // Host for Thales Key Manager (for CADP)
		String crdptkn = properties.getProperty("CRDPTKN");           // Token for Thales CADP
		String policyType = properties.getProperty("POLICYTYPE");     // Type of Thales policy to apply
		String showmetadata = properties.getProperty("SHOWMETADATA"); // Flag to control showing metadata
		String defaultpolicy = properties.getProperty("DEFAULTPOLICY"); // Default Thales policy name
		String revealuser = properties.getProperty("REVEALUSER");       // User for reveal operations
		System.out.println(" user  " + revealuser); // Print the reveal user for logging/debugging

		// Converts the "SHOWMETADATA" property to a boolean.
		boolean showmeta = showmetadata.equalsIgnoreCase("true");

		// Initializes ThalesProtectRevealHelper, responsible for interacting with the Thales Protect Reveal service.
		// This example uses ThalesCADPProtectRevealHelper, implying direct integration with CADP.
		ThalesProtectRevealHelper tprh = new ThalesCADPProtectRevealHelper(keymanagerhost, crdptkn, null, policyType,
				showmeta);
		
		// The commented-out line below shows an alternative for using Thales REST service:
		// ThalesProtectRevealHelper tprh = new ThalesRestProtectRevealHelper(crdpip, metadata, policyType, showmeta);
		
		// Sets additional properties for the ThalesProtectRevealHelper instance.
		tprh.revealUser = revealuser;
		tprh.policyType = policyType;
		tprh.policyName = properties.getProperty("POLICYNAME");
		tprh.defaultPolicy = defaultpolicy;
		
		// Initializes a ContentProcessor. Based on the CSP, it will be a GCPContentProcessor.
		ContentProcessor cp = null;
		if (csp.equalsIgnoreCase("gcp"))
			cp = new GCPContentProcessor(properties);

		// Declare File objects for input and output directories.
		File inputDir = null;
		File outputDir = null;
		
		// Parse command-line arguments.
		String mode = args[0];       // Processing mode: "protect" or "reveal".
		inputDir = new File(args[1]); // Path to the input directory.
		outputDir = new File(args[2]); // Path to the output directory.
		String fileextension = args[3]; // File extension to process (e.g., ".txt", ".csv").
		String projectId = args[4];     // Google Cloud Project ID for DLP operations.
		
		// Counter for the number of files processed.
		int nbroffiles = 0;
		
		// Get a list of files in the input directory that match the specified file extension.
		File[] inputFiles = inputDir.listFiles((dir, name) -> name.toLowerCase().endsWith(fileextension));

		File outputFile = null;
		// Checks if any input files were found.
		if (inputFiles != null) {

			// Iterates through each input file.
			for (File inputFile : inputFiles) {

				// Determines the output file name based on the mode (protect or reveal).
				if (mode.equalsIgnoreCase("protect"))
					outputFile = new File(outputDir, "protected" + inputFile.getName());
				else
					outputFile = new File(outputDir, "revealed" + inputFile.getName());

				// Processes the file using the appropriate content processor (GCP in this case).
				// The processFile method performs either protection or revelation.
				if (csp.equalsIgnoreCase("gcp"))
					nbrofrecords = cp.processFile(inputFile, outputFile, projectId, tprh, mode, skiphdr);

				// Increments the count of processed files.
				nbroffiles++;
			}
			
			// Updates the total number of records processed.
			totalnbrofrecords = totalnbrofrecords + nbrofrecords;
			
		} else {
			// Prints a message if no files with the specified extension are found.
			System.out.println("No " + fileextension + " files found in the directory: " + inputDir.getAbsolutePath());
		}

		// Prints summary statistics.
		System.out.println("Number of files = " + nbroffiles);
		System.out.println("Total nbr of records = " + totalnbrofrecords);
		System.out.println("Total skipped entities = " + cp.total_skipped_entities);
		System.out.println("Total entities found = " + cp.total_entities_found);
	}
}

package com.example;
import java.io.*;
import java.util.Properties;

import software.amazon.awssdk.regions.Region;

/**
 * This class serves as a batch processor for protecting and revealing data using Thales Protect Reveal CADP.
 * It reads configuration from a properties file, processes files in a specified directory,
 * and performs either protection or revelation based on the provided mode.
 */
public class ThalesAWSProtectRevealCADPBatchProcessor {

	// Defines the AWS region to be used. This can be changed to your desired region.
	private static final Region REGION = Region.US_EAST_2; 

	// Properties object to hold configurations loaded from the properties file.
	private static Properties properties;

	/**
	 * Static initializer block to load properties from "thales-config.properties" file.
	 * This block is executed once when the class is loaded.
	 * It throws a RuntimeException if the file is not found or an error occurs during loading.
	 */
	static {
		try (InputStream input = ThalesAWSProtectRevealCADPBatchProcessor.class.getClassLoader()
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
	 * and orchestrates the protection or revelation of files.
	 * @param args Command-line arguments: [mode] [inputDirectory] [outputDirectory] [fileExtension]
	 * @throws IOException If an I/O error occurs during file processing.
	 */
	public static void main(String[] args) throws IOException {
		// Records the start time of the application for performance measurement.
		long startTime = System.nanoTime();

		// Flag to indicate whether to skip header rows in files.
		boolean skiphdr = false;
		// Cloud Service Provider, currently set to AWS.
		String csp = "AWS";
		// Counter for the number of records processed in the current file.
		int nbrofrecords = 0;
		// Counter for the total number of records processed across all files.
		int totalnbrofrecords = 0;

		// Retrieves various configuration properties from the loaded properties object.
		String metadata = properties.getProperty("METADATA");
		String crdpip = properties.getProperty("CRDPIP");

		String keymanagerhost = properties.getProperty("KEYMGRHOST"); // Unused in provided code.
		String crdptkn = properties.getProperty("CRDPTKN"); // Unused in provided code.
		String policyType = properties.getProperty("POLICYTYPE");
		String showmetadata = properties.getProperty("SHOWMETADATA");
		String revealuser = properties.getProperty("REVEALUSER");
		System.out.println(" user  " + revealuser);

		String defaultpolicy = properties.getProperty("DEFAULTPOLICY");
		// Converts the "SHOWMETADATA" property to a boolean.
		boolean showmeta = showmetadata.equalsIgnoreCase("true");

		// Initializes ThalesProtectRevealHelper, responsible for interacting with the Thales Protect Reveal service.
		ThalesProtectRevealHelper tprh = new ThalesRestProtectRevealHelper(crdpip, metadata, policyType, showmeta);

		// Sets properties for the ThalesProtectRevealHelper instance.
		tprh.revealUser = revealuser;
		tprh.policyType = policyType;
		tprh.policyName = properties.getProperty("POLICYNAME");
		tprh.defaultPolicy = defaultpolicy;

		// Initializes an AWSContentProcessor if the CSP is AWS.
		AWSContentProcessor cp = null;
		if (csp.equalsIgnoreCase("aws"))
			cp = new AWSContentProcessor(properties);

		// Sets the AWS region for the content processor.
		cp.awsregion = REGION;

		// Declare File objects for input and output directories
		File inputDir = null;
		File outputDir = null;

		// Parse command-line arguments
		String mode = args[0]; // "protect" or "reveal" mode
		inputDir = new File(args[1]); // Path to the input directory
		outputDir = new File(args[2]); // Path to the output directory
		String fileextension = args[3]; // File extension to process (e.g., ".pdf", ".txt")
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

				// Processes the file using the appropriate content processor (AWS in this case).
				// The processFile method performs either protection or revelation.
				if (csp.equalsIgnoreCase("aws"))
					nbrofrecords = cp.processFile(inputFile, outputFile, null, tprh, mode, skiphdr);

				// Increments the count of processed files.
				nbroffiles++;
			}
			// Updates the total number of records processed.
			totalnbrofrecords = totalnbrofrecords + nbrofrecords;
		} else {
			// Prints a message if no files with the specified extension are found.
			System.out.println("No " + fileextension + " files found in the directory: " + inputDir.getAbsolutePath());
		}

		// Records the end time in nanoseconds.
		long endTime = System.nanoTime();

		// Calculates the elapsed time in nanoseconds.
		long elapsedTimeNano = endTime - startTime;

		// Converts nanoseconds to seconds for better readability.
		double elapsedTimeSeconds = (double) elapsedTimeNano / 1_000_000_000.0;

		// Prints the application's execution time.
		System.out.printf("Application execution time: %.6f seconds%n", elapsedTimeSeconds);

		// Prints summary statistics.
		System.out.println("Number of files = " + nbroffiles);
		System.out.println("Total nbr of records = " + totalnbrofrecords);
		System.out.println("Total skipped entities = " + cp.total_skipped_entities);
		System.out.println("Total entities found = " + cp.total_entities_found);

	}

}
package com.example;
import java.io.InputStream;
import java.util.Properties;

// AWS SDK imports for Bedrock Runtime, Comprehend, credentials, and regions
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;
import software.amazon.awssdk.services.bedrockruntime.model.ContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.ConversationRole;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseResponse;
import software.amazon.awssdk.services.bedrockruntime.model.Message;
import software.amazon.awssdk.services.comprehend.ComprehendClient;

/**
 * ThalesAWSBedrockPromptExample demonstrates how to integrate AWS Bedrock
 * with a Thales data protection solution to process prompts containing PII.
 * It detects PII using AWS Comprehend, protects it using Thales's encryption,
 * and then simulates sending it to a Bedrock model (commented out in this example)
 * before revealing (decrypting) the data.
 */
public class ThalesAWSBedrockPromptExample {

	// Define the AWS region for Bedrock and Comprehend clients
	private static final Region REGION = Region.US_EAST_2; // Change to your desired region

	// Properties object to load configuration from a file
	private static Properties properties;

	// Static initializer block to load properties from 'thales-config.properties'
	static {
		try (InputStream input = ThalesAWSBedrockPromptExample.class.getClassLoader()
				.getResourceAsStream("thales-config.properties")) {
			properties = new Properties();
			if (input == null) {
				// Throw a runtime exception if the properties file is not found
				throw new RuntimeException("Unable to find udfConfig.properties");
			}
			// Load properties from the input stream
			properties.load(input);

		} catch (Exception ex) {
			// Catch any exceptions during properties loading and re-throw as a runtime exception
			throw new RuntimeException("Error loading properties file", ex);
		}
	}

	/**
	 * Main method to run the example.
	 *
	 * @param args Command line arguments (not used in this example).
	 */
	public static void main(String[] args) {

		// Build a BedrockRuntimeClient using default credential provider and the specified region
		BedrockRuntimeClient client = BedrockRuntimeClient.builder()
				.credentialsProvider(DefaultCredentialsProvider.create()).region(REGION).build();

		// Define the Bedrock model ID to be used (though Bedrock call is commented out)
		String modelId = "amazon.titan-embed-text-v2:0";
		// Retrieve various configuration properties from the loaded properties file
		String metadata = properties.getProperty("METADATA");
		String crdpip = properties.getProperty("CRDPIP");
		String keymanagerhost = properties.getProperty("KEYMGRHOST"); // Note: keymanagerhost seems is if using ThalesRestProtectRevealHelper
		String crdptkn = properties.getProperty("CRDPTKN"); // Note: crdptkn is unused if using ThalesRestProtectRevealHelper
		String policyType = properties.getProperty("POLICYTYPE");
		String showmetadata = properties.getProperty("SHOWMETADATA");
		String revealuser = properties.getProperty("REVEALUSER");
		System.out.println(" user  " + revealuser); // Print the reveal user

		// Convert showmetadata string to a boolean
		boolean showmeta = showmetadata.equalsIgnoreCase("true");

		// Initialize a ThalesProtectRevealHelper. This example uses ThalesRestProtectRevealHelper,
		// implying a REST-based integration with the Thales product.
		ThalesProtectRevealHelper tprh = new ThalesRestProtectRevealHelper(crdpip, metadata, policyType,
				showmeta);

		// Set reveal user, policy type, and policy name on the Thales helper object
		tprh.revealUser = revealuser;
		tprh.policyType = policyType;
		tprh.policyName = properties.getProperty("POLICYNAME");

		// Create an instance of AWSContentProcessor, passing in the loaded properties
		AWSContentProcessor cp = new AWSContentProcessor(properties);

		// Set the AWS region for the Content Processor (used by Comprehend within it)
		cp.awsregion = REGION;

		// Build a ComprehendClient using the specified region
		ComprehendClient comprehendClient = ComprehendClient.builder().region(REGION).build();

		// Define an example input text containing PII
		String inputText = "Explain 'rubber duck debugging' in one line to Kathi Wolf	Burney Circle	Mertzmouth	OH	24114	328.639.0623x3743	becker.drury@hotmail.com	7/7/1992	5.32755E+15	15	203-04-0501\r\n";
		System.out.println("Original prompt = " + inputText);

		// Process the input text to detect and protect PII using AWSContentProcessor
		inputText = cp.processText(inputText, tprh);
		System.out.println("Protected prompt = " + inputText);

		// The following Bedrock API call is commented out, indicating it's not
		// actively executed in this example, but shows the intended flow.
		/*
		 * Message message =
		 * Message.builder().content(ContentBlock.fromText(inputText)).role(
		 * ConversationRole.USER) .build(); ConverseResponse response =
		 * client.converse(request -> request.modelId(modelId).messages(message));
		 * String responseText = response.output().message().content().get(0).text();
		 * System.out.println(responseText); System.out.println("new string = " +
		 * inputText);
		 */

		// Close the Comprehend client to release resources
		comprehendClient.close();

		// Test decryption example: decrypt the previously protected data
		String decrypteddata = cp.decryptLine(inputText, tprh);
		System.out.println("decrypteddata = " + decrypteddata);
	}
}
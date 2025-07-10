Here's your content formatted with Markdown, a simple markup language:

# GenAI Demos

## Overview

Projects inside this folder are there to help developers who are building GenAI applications that commonly require policy-driven data protection to meet some compliance requirement, or for any other purpose. The idea is to showcase how to leverage various CipherTrust Application Data Protection products along with the Cloud Service Providers' sensitive data scanners. AWS, GCP, and Azure each have their own APIs and SDKs to find PII, PCI data. Once found, these examples will then protect it using CRDP.

This repository will hold code samples and/or integrations that you can use in your environment.

### AWS

* **ThalesAWSProtectRevealCADPBatchProcessor** - This class serves as a batch processor for protecting and revealing data using Thales Protect Reveal CADP. It reads configuration from a properties file, processes files in a specified directory, and performs either protection or revelation based on the provided mode.
* **ThalesAWSBedrockPromptExample** - Demonstrates how to integrate AWS Bedrock with a Thales data protection solution to process prompts containing PII. It detects PII using AWS Comprehend, protects it using Thales's encryption, and then simulates sending it to a Bedrock model (commented out in this example) before revealing (decrypting) the data.
* **AWSContentProcessor** - Extends `ContentProcessor` to provide functionalities for processing text content, specifically detecting and handling PII (Personally Identifiable Information) using AWS Comprehend, and then encrypting/decrypting it using `ThalesProtectRevealHelper`.
* **ContentProcessor** - Abstract class providing common functionalities for content processing, especially for handling PII (Personally Identifiable Information).
* **ThalesProtectRevealHelper** - Is an abstract base class that defines the common interface and shared utility methods for protecting (encrypting) and revealing (decrypting) data using Thales CipherTrust solutions. Subclasses will implement the specific mechanisms for protection and revelation, whether it's via CADP (CipherTrust Application Data Protection) or REST APIs.
* **ThalesCADPProtectRevealHelper** - Extends `ThalesProtectRevealHelper` to provide data protection and revelation functionalities specifically using the Thales CipherTrust Application Data Protection (CADP) Java SDK. It handles client registration with the CipherTrust Manager and performs cryptographic operations.
* **ThalesRestProtectRevealHelper** - Extends `ThalesProtectRevealHelper` to provide data protection and revelation functionalities using the Thales CipherTrust Data Protection (CDP) REST APIs. It communicates with a CDP server via HTTP requests to perform cryptographic operations.

### Azure

* **ThalesAzureOpenAIClientPromptExample** - An Azure prompt protection example using CADP Protect/Reveal SDK.
* **ThalesAzureOpenAIClientPromptExampleRest** - An Azure prompt protection example using CRDP container.
* **ThalesAzureProtectRevealBatchProcessor** - Will process all the files in the provided input directory and protect all the sensitive fields and create the same file in an output directory with the sensitive data replaced.
* **ContentProcessor** - Abstract class providing common functionalities for content processing, especially for handling PII (Personally Identifiable Information).
* **AzureContentProcessor** - Extends `ContentProcessor` to provide Azure-specific functionalities for PII (Personally Identifiable Information) detection and protection/revelation. It uses Azure Text Analytics service for PII recognition.
* **ThalesProtectRevealHelper** - Is an abstract base class that defines the common interface and shared utility methods for protecting (encrypting) and revealing (decrypting) data using Thales CipherTrust solutions. Subclasses will implement the specific mechanisms for protection and revelation, whether it's via CADP (CipherTrust Application Data Protection) or REST APIs.
* **ThalesCADPProtectRevealHelper** - Extends `ThalesProtectRevealHelper` to provide data protection and revelation functionalities specifically using the Thales CipherTrust Application Data Protection (CADP) Java SDK. It handles client registration with the CipherTrust Manager and performs cryptographic operations.
* **ThalesRestProtectRevealHelper** - Extends `ThalesProtectRevealHelper` to provide data protection and revelation functionalities using the Thales CipherTrust Data Protection (CDP) REST APIs. It communicates with a CDP server via HTTP requests to perform cryptographic operations.

### GCP

* **ThalesGCPProtectRevealBatchProcessor** - This class serves as a batch processor for protecting and revealing data using Thales CipherTrust Data Security Platform (CADP) in conjunction with Google Cloud Platform (GCP) DLP for sensitive data detection. It reads configuration from a properties file, processes files in a specified directory, and performs either protection or revelation based on the provided mode.
* **ThalesGCPVertexaiPromptExample** - This class demonstrates an example of using Thales ProtectReveal with Google Cloud Vertex AI for prompt processing. It loads configuration from a properties file, processes a text prompt through a Thales content processor, and then sends the processed prompt to a Vertex AI Gemini model to get a text-only response.
* **ContentProcessor** - Abstract class providing common functionalities for content processing, especially for handling PII (Personally Identifiable Information).
* **GCPContentProcessor** - This class extends `ContentProcessor` and provides functionality to process content using Google Cloud Data Loss Prevention (DLP) API. It can be used to either protect (detect and encrypt) or reveal (decrypt) sensitive information within text files.
* **ThalesProtectRevealHelper** - Is an abstract base class that defines the common interface and shared utility methods for protecting (encrypting) and revealing (decrypting) data using Thales CipherTrust solutions. Subclasses will implement the specific mechanisms for protection and revelation, whether it's via CADP (CipherTrust Application Data Protection) or REST APIs.
* **ThalesCADPProtectRevealHelper** - Extends `ThalesProtectRevealHelper` to provide data protection and revelation functionalities specifically using the Thales CipherTrust Application Data Protection (CADP) Java SDK. It handles client registration with the CipherTrust Manager and performs cryptographic operations.
* **ThalesRestProtectRevealHelper** - Extends `ThalesProtectRevealHelper` to provide data protection and revelation functionalities using the Thales CipherTrust Data Protection (CDP) REST APIs. It communicates with a CDP server via HTTP requests to perform cryptographic operations.
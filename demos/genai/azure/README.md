# Thales + Azure Sensitive Data Protection Samples

This project contains a set of Java samples that combine Microsoft Azure services and Thales CipherTrust to discover, detect, protect, and reveal sensitive data.

The repository now includes two related solution patterns:

- the **non-purview file-to-file and prompt-protection samples**
- the **Microsoft Purview-driven storage and Azure SQL protection flow**

## What Is In This Repo

At a high level, the samples show how to:

- identify sensitive data in unstructured or semi-structured content with Azure AI Language PII detection
- protect or reveal that sensitive data with Thales CipherTrust
- call Azure OpenAI with protected prompt content
- use Microsoft Purview to discover which assets or SQL columns should be processed before downstream AI, analytics, or vector-store use

## Main Sample Paths

### 1. File-to-file protection

This is the non-purview local file to local file batch-processing pattern.

- Read files from an input location
- Detect sensitive values in the content with Azure AI Language PII detection
- Protect those values with Thales CipherTrust
- Write a protected output file
- Optionally reverse the process with reveal mode

Primary class:

- [ThalesAzureProtectRevealBatchProcessor.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ThalesAzureProtectRevealBatchProcessor.java)

### 2. Prompt protection for Azure OpenAI

This sample shows how a prompt can be processed before it is sent to Azure OpenAI.

- Prepare input text that may contain sensitive values
- Protect those values before sending the prompt
- Call Azure OpenAI
- Inspect the response
- Optionally check the output again for sensitive values

Primary class:

- [ThalesAzureOpenAIClientPromptExample.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ThalesAzureOpenAIClientPromptExample.java)

### 3. Purview-driven storage protection

This is the newer governed workflow for Azure Storage and ADLS Gen2.

- Run or reuse a Microsoft Purview scan
- Search Purview for classified assets
- Read the same storage assets Purview identified
- Stream those assets directly from Azure Storage
- Use Azure AI Language PII detection to identify sensitive values in file content
- Protect those values with Thales CipherTrust
- Stream protected output back to a governed target location

Primary classes:

- [ThalesAzurePurviewBatchProcessor.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ThalesAzurePurviewBatchProcessor.java)
- [AzureStoragePurviewProcessor.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\AzureStoragePurviewProcessor.java)
- [PurviewClient.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\PurviewClient.java)

### 4. Purview-driven Azure SQL protection

This governed workflow uses Purview classifications to decide which SQL columns to protect.

- Run or reuse a Microsoft Purview scan of Azure SQL
- Search Purview for classified columns
- Read source rows from the configured table
- Protect only the classified columns
- Write the output to a target table

Primary class:

- [AzureSqlPurviewProcessor.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\AzureSqlPurviewProcessor.java)

## Core Classes

### Content and detection

- [AzureContentProcessor.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\AzureContentProcessor.java)
  Performs line-by-line processing for files and streams. Uses the Azure AI Language PII detection API to identify sensitive values in text before protection or after reveal.

- [ContentProcessor.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ContentProcessor.java)
  Shared base class for file/text content processing, tag mapping, PII policy mapping, and helper logic for protected-string formatting.

### Thales protection helpers

- [ThalesProtectRevealHelper.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ThalesProtectRevealHelper.java)
  Abstract base helper that defines the shared protection/reveal contract and common metadata parsing behavior.

- [ThalesCADPProtectRevealHelper.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ThalesCADPProtectRevealHelper.java)
  Uses the Thales CADP Java SDK and CipherTrust Manager registration flow for protect, reveal, and reprotect operations.

- [ThalesRestProtectRevealHelper.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ThalesRestProtectRevealHelper.java)
  Uses Thales CipherTrust Data Protection REST APIs over HTTP for protect and reveal operations. This is useful when you want a REST-based integration model instead of the CADP Java SDK.

## Sample Entry Points

### ThalesAzureProtectRevealBatchProcessor

[ThalesAzureProtectRevealBatchProcessor.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ThalesAzureProtectRevealBatchProcessor.java) is the original batch sample.

What it does:

- loads `thales-config.properties`
- initializes the Thales CADP helper
- uses `AzureContentProcessor`
- scans local input files with the requested extension
- writes protected or revealed output files

Command-line arguments:

1. `mode`
2. `textAnalyticsEndpoint`
3. `textAnalyticsApiKey`
4. `inputDir`
5. `outputDir`
6. `fileExtension`

Representative usage:

```powershell
java -cp target/genai.azure.example-0.0.1-SNAPSHOT.jar com.example.ThalesAzureProtectRevealBatchProcessor protect https://<language-endpoint> <language-key> C:\input C:\output .txt
```

### ThalesAzurePurviewBatchProcessor

[ThalesAzurePurviewBatchProcessor.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ThalesAzurePurviewBatchProcessor.java) is the governed batch sample.

What it does:

- runs or reuses a Purview scan
- searches Purview for classified assets
- processes storage assets, SQL assets, or both
- uses streaming for storage assets instead of local staging

Command-line arguments:

1. `mode`
2. `workload` = `storage`, `sql`, or `both`
3. `textAnalyticsEndpoint` or `-`
4. `textAnalyticsApiKey` or `-`
5. `fileExtension` or `-`

Representative usage:

```powershell
java -cp target/genai.azure.example-0.0.1-SNAPSHOT.jar com.example.ThalesAzurePurviewBatchProcessor protect storage https://<language-endpoint> <language-key> .txt
```

### ThalesAzureOpenAIClientPromptExample

[ThalesAzureOpenAIClientPromptExample.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ThalesAzureOpenAIClientPromptExample.java) demonstrates prompt protection for Azure OpenAI.

What it does:

- loads the Thales configuration
- protects prompt content before sending it
- sends a request to Azure OpenAI with OkHttp
- inspects the returned content
- runs a second PII detection/protection pass on the output for demonstration purposes

Command-line arguments:

1. `textAnalyticsEndpoint`
2. `textAnalyticsApiKey`
3. `azureOpenAiApiKey`
4. `azureOpenAiEndpoint`

Representative usage:

```powershell
java -cp target/genai.azure.example-0.0.1-SNAPSHOT.jar com.example.ThalesAzureOpenAIClientPromptExample https://<language-endpoint> <language-key> <openai-key> https://<openai-endpoint>
```

### ThalesRestProtectRevealHelper

[ThalesRestProtectRevealHelper.java](E:\codex\work\azure-purview\azure\src\main\java\com\example\ThalesRestProtectRevealHelper.java) is a lower-level helper and demo for REST-based Thales protection and reveal.

What it does:

- calls the Thales protect REST endpoint
- handles internal or external protection policy metadata
- calls the Thales reveal REST endpoint

Command-line arguments for its standalone demo:

1. `crdpip`
2. `metadata`
3. `policyType`
4. `showmetadata`
5. `crdpuser`

Representative usage:

```powershell
java -cp target/genai.azure.example-0.0.1-SNAPSHOT.jar com.example.ThalesRestProtectRevealHelper <crdp-ip> <metadata> internal true <user>
```

## Configuration

The main runtime configuration lives in [thales-config.properties](E:\codex\work\azure-purview\azure\src\main\resources\thales-config.properties).

Important property groups:

### Thales CipherTrust

- `KEYMGRHOST`
- `CRDPTKN`
- `POLICYNAME`
- `DEFAULTPOLICY`
- `POLICYTYPE`
- `SHOWMETADATA`
- `REVEALUSER`

### Tag and PII policy mappings

- `TAG.*`
- `PII.*`

These mappings decide which Thales protection policy is applied to each detected PII type.

### Azure AI Language PII detection

For the current samples, the endpoint and key are passed on the command line rather than stored in the properties file.

### Microsoft Purview

- `PURVIEW_ENDPOINT`
- `PURVIEW_ACCESS_TOKEN`
- `PURVIEW_DATASOURCE_NAME`
- `PURVIEW_SCAN_NAME`
- `PURVIEW_CLASSIFICATIONS`
- `PURVIEW_STORAGE_QUALIFIED_NAME_PREFIXES`

### Azure Storage

- `AZURE_STORAGE_CONNECTION_STRING`
- `PURVIEW_STORAGE_TARGET_CONTAINER`
- `PURVIEW_STORAGE_TARGET_PREFIX`

### Azure SQL

- `PURVIEW_SQL_JDBC_URL`
- `PURVIEW_SQL_USER`
- `PURVIEW_SQL_PASSWORD`
- `PURVIEW_SQL_SOURCE_TABLE`
- `PURVIEW_SQL_TARGET_TABLE`
- `PURVIEW_SQL_WHERE_CLAUSE`
- `PURVIEW_SQL_WRITE_MODE`

## Build

```powershell
mvn -DskipTests package
```

This now produces:

- `target/genai.azure.example-0.0.1-SNAPSHOT.jar`
  Thin project jar with only this project's classes and resources
- `target/genai.azure.example-0.0.1-SNAPSHOT-all.jar`
  Shaded jar that includes project dependencies

The shaded jar is the better choice when you want to run the samples directly from a single artifact.

## Launcher Scripts

Sample launcher scripts are included at the repo root:

- [run-samples.bat](E:\codex\work\azure-purview\azure\run-samples.bat)
- [run-samples.sh](E:\codex\work\azure-purview\azure\run-samples.sh)

They print sample commands for:

- non-Purview local file-to-file protect and reveal flows
- Purview storage flow
- Purview SQL flow
- combined Purview storage plus SQL flow
- Azure OpenAI prompt protection example
- REST-based Thales protect/reveal helper demo

## How The Pieces Fit Together

### Non-purview file-to-file batch path

- local file input
- Azure AI Language PII detection identifies sensitive values
- Thales protects or reveals values
- local file output

### Prompt path

- prompt content is protected before the Azure OpenAI request
- generated output can be checked again for sensitive content

### Governed Purview path

- Purview identifies sensitive assets or columns
- the application processes only the relevant storage assets or SQL columns
- file content still uses Azure AI Language PII detection for fine-grained in-content detection
- SQL uses Purview column classification as the field-level targeting signal

## Important Notes

- Purview is used here as the discovery and governance layer, not as the fine-grained in-record detection engine
- Azure AI Language PII detection is the in-content detection API used for file content
- SQL protection does not require Azure AI Language PII detection because Purview already identifies the sensitive columns
- Storage processing in the Purview flow now uses direct streaming from source blob to destination blob
- The file-to-file sample remains useful when you want a simple local processing demo without Purview

## Suggested Future Enhancements

- Add managed identity or Microsoft Entra token acquisition for Purview instead of using a configured bearer token
- Add direct support for Azure AI Search or vector-store load after protection
- Add more structured parsing for CSV, JSON, and document-specific flows
- Add tests around storage, SQL, and prompt scenarios
- Clean up duplicate dependency declarations in `pom.xml`

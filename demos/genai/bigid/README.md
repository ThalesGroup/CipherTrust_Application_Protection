# Thales + BigID Sensitive Data Protection Samples

This project contains Java samples that combine BigID discovery and classification with Azure Text Analytics and Thales CipherTrust protection.

The repository now includes two related BigID-driven solution patterns:

- the **BigID-driven unstructured document protection flow**
- the **BigID-driven structured SQL protection flow**

For provider-specific examples and a step-by-step explanation of Azure Blob, S3, GCS, and `auto` mode, see [cloud-sources.md](/E:/codex/work/bigid/cloud-sources.md).

## What Is In This Repo

At a high level, the samples show how to:

- use BigID as the discovery and classification layer
- identify exact sensitive spans inside document content with Azure AI Language PII detection
- protect those values with Thales CipherTrust
- add locator tag prefixes only for unstructured protected values
- process unstructured assets from local filesystem paths, Azure Blob and ADLS-style paths, Amazon S3, or Google Cloud Storage
- process structured SQL rows by protecting only the BigID-classified columns

## Main Sample Paths

### 1. BigID-driven document protection

This is the governed unstructured-content workflow.

- Query BigID catalog results for classified assets
- Resolve each asset to either a local file or a supported object store
- Convert PDF, Word, Excel, text, or CSV content into text
- Use Azure AI Language PII detection to identify the exact sensitive spans
- Protect those values with Thales CipherTrust
- Optionally emit extracted text, protected or revealed text, and a findings JSON report
- Write the selected review artifacts to a local directory or Azure Storage target

Primary classes:

- [BigidThalesTransformationApplication.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/BigidThalesTransformationApplication.java)
- [SensitiveAssetProcessor.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/SensitiveAssetProcessor.java)
- [BigIdClient.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/BigIdClient.java)
- [DocumentConversionService.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/DocumentConversionService.java)
- [AzureBlobDocumentStore.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/AzureBlobDocumentStore.java)
- [S3DocumentStore.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/S3DocumentStore.java)
- [GcsDocumentStore.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/GcsDocumentStore.java)

### 2. BigID-driven structured SQL protection

This governed workflow uses BigID classifications to decide which SQL columns to protect.

- Query BigID catalog results for classified structured fields
- Infer source tables and columns from the returned BigID asset metadata
- Read source rows through JDBC
- Protect only the BigID-classified columns
- Write the output to a target table

Primary class:

- [StructuredDataProcessor.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/StructuredDataProcessor.java)

### 3. BigID debug and metadata inspection

This is the recommended first-run workflow when connecting to a new BigID tenant.

- Query BigID catalog results without touching source content
- Dump normalized asset metadata to JSON
- Inspect how BigID represents paths, blob objects, tables, and columns
- Validate the inferred mappings before enabling protection

Primary classes:

- [SensitiveAssetProcessor.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/SensitiveAssetProcessor.java)
- [BigIdAsset.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/BigIdAsset.java)

## Core Classes

### Discovery and asset modeling

- [BigIdClient.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/BigIdClient.java)
  Small BigID REST client that authenticates with a system token or exchanged user token and queries the `data-catalog` endpoint.

- [BigIdAsset.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/BigIdAsset.java)
  Shared model for classified assets. It also contains helper logic to infer Azure Blob, S3, GCS, and structured table and column details from BigID metadata.

- [RuntimeConfig.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/RuntimeConfig.java)
  Loads the runtime properties file and validates which settings are required for local, Azure Blob, S3, GCS, SQL, and debug-only modes.

### Content conversion and detection

- [DocumentConversionService.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/DocumentConversionService.java)
  Converts `.pdf`, `.docx`, `.doc`, `.xlsx`, `.xls`, `.txt`, and `.csv` inputs into text so Azure AI Language can inspect them consistently.

- [AzureTextAnalyticsService.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/AzureTextAnalyticsService.java)
  Calls Azure AI Language PII detection and returns the sensitive spans that should be protected inside the extracted text.

### Thales protection helpers

- [ProtectionService.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/ProtectionService.java)
  Small abstraction for the protection operation.

- [CadpProtectionService.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/CadpProtectionService.java)
  Uses the Thales CADP helper to protect identified values.

- [ThalesProtectRevealHelper.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/ThalesProtectRevealHelper.java)
  Abstract base helper that defines the shared protection and reveal contract.

- [ThalesCADPProtectRevealHelper.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/ThalesCADPProtectRevealHelper.java)
  Uses the Thales CADP Java SDK and CipherTrust Manager registration flow for protect and reveal operations.

### Processing orchestration

- [SensitiveAssetProcessor.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/SensitiveAssetProcessor.java)
  Main orchestrator for unstructured content. Supports local filesystem mode, Azure Blob mode, S3 mode, GCS mode, auto mode, and debug-only mode.

- [StructuredDataProcessor.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/StructuredDataProcessor.java)
  JDBC-based processor for structured sources that protects only the BigID-classified columns.

- [BigidThalesTransformationApplication.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/BigidThalesTransformationApplication.java)
  Main entry point that wires together configuration, BigID discovery, document processing, and optional SQL processing.

## Sample Entry Point

### BigidThalesTransformationApplication

[BigidThalesTransformationApplication.java](/E:/codex/work/bigid/src/main/java/com/thales/bigid/transformation/BigidThalesTransformationApplication.java) is the main batch sample.

What it does:

- loads a properties file provided on the command line or through `BIGID_CONFIG_FILE`
- initializes the Thales CADP helper
- queries BigID for classified assets
- optionally writes a BigID asset debug dump
- processes unstructured document assets from local files, Azure Blob, or both
- optionally processes structured SQL tables

Command-line arguments:

1. `propertiesFile`

Representative usage:

```powershell
java -cp target/bigid.thales.transformation-0.0.1-SNAPSHOT-all.jar com.thales.bigid.transformation.BigidThalesTransformationApplication src/main/resources/application.properties
```

## Configuration

The main runtime configuration starts from [application.properties.example](/E:/codex/work/bigid/src/main/resources/application.properties.example).

In normal usage, copy it to `application.properties` and then update the runtime values.

Important property groups:

### Thales CipherTrust

- `CRDPIP`
- `METADATA`
- `CRDPTKN`
- `KEYMGRHOST`
- `POLICYNAME`
- `DEFAULTPOLICY`
- `POLICYTYPE`
- `SHOWMETADATA`
- `REVEALUSER`
- `thales.keyManagerHost`
- `thales.registrationToken`
- `thales.policyName`
- `thales.defaultPolicy`
- `thales.policyType`
- `thales.revealUser`
- `thales.showMetadata`

### Tag and PII policy mappings

- `TAG.*`
- `TAGCODE.*`
- `PII.*`

These mappings decide which Thales protection policy is applied to each detected PII type.

For this sample:

- unstructured document output uses the tag wrapper format
- structured SQL output does not use the tag wrapper format

### BigID discovery

- `bigid.baseUrl`
- `bigid.systemToken`
- `bigid.userToken`
- `bigid.catalogFilter`
- `bigid.pageSize`
- `bigid.classificationHints`

### BigID debug mode

- `bigid.debug.dumpAssets`
- `bigid.debug.dumpFile`
- `bigid.debug.only`

Use these when you want to inspect the BigID asset metadata before reading any content.

### Unstructured local filesystem mode

- `source.mode=local`
- `source.rootDirectory`
- `source.supportedExtensions`
- `output.directory`
- `unstructured.output.writeExtractedText`
- `unstructured.output.writeProtectedText`
- `unstructured.output.writeFindingsReport`

### Unstructured Azure Blob and ADLS-style mode

- `source.mode=azureblob`
- `azure.storage.connectionString`
- `azure.storage.targetContainer`
- `azure.storage.targetPrefix`
- `azure.storage.qualifiedNamePrefixes`

### Unstructured Amazon S3 mode

- `source.mode=s3`
- `s3.region`
- `s3.accessKey`
- `s3.secretKey`
- `s3.sessionToken`
- `s3.endpoint`
- `s3.pathStyleAccess`
- `s3.targetBucket`
- `s3.targetPrefix`
- `s3.qualifiedNamePrefixes`

### Unstructured Google Cloud Storage mode

- `source.mode=gcs`
- `gcs.projectId`
- `gcs.credentialsPath`
- `gcs.targetBucket`
- `gcs.targetPrefix`
- `gcs.qualifiedNamePrefixes`

### Mixed unstructured resolution mode

- `source.mode=auto`

This tries local filesystem resolution first and then any configured remote stores in order: Azure Blob, S3, and GCS.

### Azure AI Language PII detection

- `azure.textAnalytics.endpoint`
- `azure.textAnalytics.apiKey`
- `azure.textAnalytics.language`
- `azure.textAnalytics.confidenceThreshold`

### Structured SQL mode

- `sql.enabled`
- `sql.jdbcUrl`
- `sql.user`
- `sql.password`
- `sql.sourceTables`
- `sql.targetSchema`
- `sql.targetTableSuffix`
- `sql.whereClause`
- `sql.writeMode`

## Build

```powershell
mvn -DskipTests package
```

This produces:

- `target/bigid.thales.transformation-0.0.1-SNAPSHOT.jar`
  Thin project jar with only this project’s classes and resources
- `target/bigid.thales.transformation-0.0.1-SNAPSHOT-all.jar`
  Shaded jar that includes project dependencies

The shaded jar is the better choice when you want to run the sample directly from a single artifact.

## Launcher Scripts

Launcher scripts are included at the repo root:

- [run-bigid-transformation.bat](/E:/codex/work/bigid/run-bigid-transformation.bat)
- [run-bigid-transformation.sh](/E:/codex/work/bigid/run-bigid-transformation.sh)

They support:

- `BIGID_CONFIG_FILE`
- `BIGID_JAR`
- `JAVA_CMD`
- `JAVA_OPTS`

## Docker Assets

Container assets are included at the repo root:

- [Dockerfile](/E:/codex/work/bigid/Dockerfile)
- [.dockerignore](/E:/codex/work/bigid/.dockerignore)
- [deployment.md](/E:/codex/work/bigid/deployment.md)

The deployment guide covers:

- Windows and Linux local execution
- local and Azure Blob source modes
- structured SQL mode
- Docker build and run instructions
- debug-only startup guidance

For the runtime step-by-step behavior of the structured and unstructured paths, see [operations.md](/E:/codex/work/bigid/operations.md). For remote source examples and cloud-specific configuration, see [cloud-sources.md](/E:/codex/work/bigid/cloud-sources.md).

## How The Pieces Fit Together

### BigID-driven document path

- BigID identifies which document assets are sensitive
- the application resolves those assets from local files, Azure Blob or ADLS-style paths, S3 objects, or GCS objects
- document content is converted into text
- Azure AI Language PII detection identifies the exact sensitive spans
- Thales protects only those values
- the application can optionally write extracted text and a findings report alongside the primary output
- remote object sources are staged in a temp file only for conversion and that temp file is deleted immediately afterward
- output is written to the configured target

### BigID-driven structured SQL path

- BigID identifies which structured fields are sensitive
- the application infers table and column mappings
- JDBC reads the source rows
- only the classified columns are protected
- rows are written to the configured target table

### BigID debug-only path

- BigID is queried without reading any content
- asset metadata is normalized and written to a JSON dump
- the dump is reviewed to validate blob, filesystem, table, and column mapping assumptions

## Important Notes

- BigID is used here as the discovery and classification layer, not as the in-content detection engine
- Azure AI Language PII detection is the fine-grained in-document detection API used for unstructured content
- structured SQL protection does not require Azure AI Language PII detection because BigID already identifies the sensitive columns
- the current BigID sample assumes BigID has already scanned and cataloged the data before this application runs
- the BigID `data-catalog` response shape can differ between tenants, so the parser and inference rules are intentionally defensive
- Azure Blob, S3, and GCS support depend on how your BigID tenant represents those object paths in catalog results
- local source files are never overwritten; review artifacts are written separately under `output.directory`

## Suggested First Run

1. Copy `application.properties.example` to `application.properties`
2. Set a narrow `bigid.catalogFilter`
3. Enable:
   - `bigid.debug.dumpAssets=true`
   - `bigid.debug.only=true`
4. Run the utility once
5. Inspect the generated `bigid-asset-debug.json`
6. Confirm:
   - local paths look correct
   - Azure Blob paths parse into the right container and blob name
   - S3 paths parse into the right bucket and object key
   - GCS paths parse into the right bucket and object name
   - structured assets infer the correct table and column names
7. Disable `bigid.debug.only` and run the full protection flow

## BigID References

These current docs were used while shaping the sample:

- [Getting Started](https://developer.bigid.com/guides/get-started/)
- [Token Authentication](https://developer.bigid.com/wiki/BigID_API/Token_Authentication)
- [Find Duplicate Data Tutorial](https://developer.bigid.com/wiki/BigID_API/Duplicate_Data_Tutorial)
- [Scan Payload Tutorial](https://developer.bigid.com/api/bigid-api-scan-payload-tutorial/)

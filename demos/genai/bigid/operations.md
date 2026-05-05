# Operations Guide

This guide explains how the BigID-driven flows operate at runtime.

It focuses on:

- how the unstructured document path works
- how the structured SQL path works
- how BigID catalog filtering relates to each path
- which properties turn each path on or off

## High-Level Model

This sample separates the workflow into two layers:

1. BigID is the discovery and classification layer
2. The application is the execution and protection layer

That means BigID is expected to have already scanned and cataloged the data before this application runs.

The application then:

- queries BigID catalog results
- decides which returned assets belong to the unstructured path
- decides which returned assets belong to the structured path
- reads the corresponding source data
- protects only the targeted content

## Shared BigID Discovery Step

Both the unstructured and structured paths begin the same way:

1. The application authenticates to BigID using either `bigid.systemToken` or `bigid.userToken`.
2. The application queries BigID catalog using `bigid.catalogFilter`.
3. The application pages through the returned results.
4. The application normalizes those results into `BigIdAsset` objects.
5. The application applies `bigid.classificationHints` as an additional local filter.

Important point:

- `bigid.catalogFilter` is not SQL-specific and not document-specific.
- It is the shared BigID search filter used before either runtime path starts.
- If a returned asset path looks like Azure Blob, S3, or GCS, the application can route it automatically to the matching remote reader when the corresponding source settings are configured.

Examples:

```properties
bigid.catalogFilter=classification="PII"
bigid.classificationHints=PII,PHI,PCI
```

In practice, that means:

- BigID first determines which assets are returned
- then the application decides whether each returned asset belongs to the document path or the SQL path

## Unstructured Document Path

The unstructured path is used for:

- PDF
- Word
- Excel
- text
- CSV
- other file-like assets that BigID reports in a recognizable path form

### What Turns It On

The unstructured path is always available unless `bigid.debug.only=true`.

Which source reader is used depends on:

- `source.mode=local`
- `source.mode=azureblob`
- `source.mode=auto`

### Unstructured Flow

1. The application queries BigID catalog using `bigid.catalogFilter`.
2. The application keeps only assets that look like unstructured file or blob content.
3. The application checks `source.mode` to decide how the asset should be resolved.
4. In `local` mode, the application tries to resolve the asset under `source.rootDirectory`.
5. In `azureblob` mode, the application tries to parse the BigID asset path into Azure container and blob names.
6. In `auto` mode, the application tries local resolution first and Azure Blob resolution second.
7. The application converts the input document to text using the document conversion service.
8. The application sends the extracted text to Azure AI Language PII detection.
9. Azure returns the exact sensitive spans found inside the content.
10. The application protects only those spans with the Thales CADP protect method.
11. The unstructured output is wrapped with the configured locator tag prefix such as `TAGCODE.nbr` or `TAGCODE.char`.
12. If enabled, the application writes a review copy of the extracted text.
13. If enabled, the application writes a findings JSON report with category, offset, length, confidence, original text, and protected text for each detected span.
14. If enabled, the application writes the primary protected or revealed text output either:
   - to `output.directory` for local mode
   - to `azure.storage.targetContainer` for Azure Blob mode
15. For Azure Blob mode, the source file is downloaded only to a temp file for conversion and that temp file is deleted immediately after extraction.

### Unstructured Properties

Shared discovery:

- `bigid.baseUrl`
- `bigid.systemToken`
- `bigid.userToken`
- `bigid.catalogFilter`
- `bigid.classificationHints`

Local mode:

- `source.mode=local`
- `source.rootDirectory`
- `output.directory`
- `source.supportedExtensions`
- `unstructured.output.writeExtractedText`
- `unstructured.output.writeProtectedText`
- `unstructured.output.writeFindingsReport`

Azure Blob mode:

- `source.mode=azureblob`
- `azure.storage.connectionString`
- `azure.storage.targetContainer`
- `azure.storage.targetPrefix`
- `azure.storage.qualifiedNamePrefixes`

Amazon S3 mode:

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

Google Cloud Storage mode:

- `source.mode=gcs`
- `gcs.projectId`
- `gcs.credentialsPath`
- `gcs.targetBucket`
- `gcs.targetPrefix`
- `gcs.qualifiedNamePrefixes`

Auto mode:

- `source.mode=auto`

In auto mode, the application tries:

1. local filesystem resolution
2. Azure Blob resolution if Azure settings are configured
3. S3 resolution if S3 settings are configured
4. GCS resolution if GCS settings are configured

Detection and protection:

- `azure.textAnalytics.endpoint`
- `azure.textAnalytics.apiKey`
- `azure.textAnalytics.language`
- `azure.textAnalytics.confidenceThreshold`
- `thales.*`
- `PII.*`
- `TAG.*`

### How BigID Filtering Relates To Unstructured Processing

`bigid.catalogFilter` does not directly say “use local mode” or “use Azure Blob mode”.

Instead:

1. BigID returns candidate classified assets
2. the application checks whether each asset looks like a file or blob object
3. the configured source mode determines how to fetch the content

So the BigID filter decides what candidate assets enter the pipeline, and `source.mode` decides how those assets are read.

The remote-provider execution model is:

1. BigID returns a classified asset.
2. The application recognizes the path as Azure Blob, S3, or GCS.
3. The application downloads the source object to a temp file.
4. The temp file is converted to text.
5. Azure AI Language identifies exact sensitive spans.
6. Thales protects only those spans.
7. The application writes new output artifacts to the configured target location.

### Example Unstructured Scenarios

Local filesystem scenario:

- BigID returns a classified asset whose path matches a file under `source.rootDirectory`
- the application converts the file to text
- Azure detects exact sensitive spans
- Thales protects only those spans
- output is written to `output.directory`

Azure Blob scenario:

- BigID returns a classified asset with a Blob or ADLS-style path
- the application parses container and blob name from that path
- the blob is downloaded temporarily for text extraction
- the temp file is deleted immediately after conversion
- Azure detects exact sensitive spans
- Thales protects only those spans
- output is written to the configured target container and prefix

Amazon S3 scenario:

- BigID returns a classified asset with an S3-style path
- the application parses bucket and object key from that path
- the object is downloaded temporarily for text extraction
- the temp file is deleted immediately after conversion
- Azure detects exact sensitive spans
- Thales protects only those spans
- output is written to the configured target bucket and prefix

Google Cloud Storage scenario:

- BigID returns a classified asset with a GCS-style path
- the application parses bucket and object name from that path
- the object is downloaded temporarily for text extraction
- the temp file is deleted immediately after conversion
- Azure detects exact sensitive spans
- Thales protects only those spans
- output is written to the configured target bucket and prefix

## Structured SQL Path

The structured path is used for database tables and columns that BigID has already classified.

### What Turns It On

The structured path runs only when:

```properties
sql.enabled=true
```

It is skipped when:

- `sql.enabled=false`
- or `bigid.debug.only=true`

Simply having `sql.*` properties present does not turn it on.

The actual switch is `sql.enabled`.

### Structured Flow

1. The application queries BigID catalog using `bigid.catalogFilter`.
2. The structured processor keeps only assets that look like fields or columns.
3. The processor infers table and column names from the BigID asset metadata.
4. If `sql.sourceTables` is populated, the processor keeps only assets whose inferred table matches that list.
5. The processor connects to SQL Server using `sql.jdbcUrl`, `sql.user`, and `sql.password`.
6. The processor reads the source table metadata and matches actual source columns against the inferred BigID-sensitive columns.
7. The processor creates or re-creates a target table using `sql.targetSchema` and `sql.targetTableSuffix`.
8. The processor reads source rows from the table, optionally using `sql.whereClause`.
9. The processor protects only the values in the BigID-classified columns using the Thales CADP protect method.
10. The structured output is stored as plain protected values without the unstructured locator tag wrapper.
11. The processor writes the transformed rows to the target table.

### Structured Properties

Shared discovery:

- `bigid.baseUrl`
- `bigid.systemToken`
- `bigid.userToken`
- `bigid.catalogFilter`
- `bigid.classificationHints`

Structured execution:

- `sql.enabled`
- `sql.jdbcUrl`
- `sql.user`
- `sql.password`
- `sql.sourceTables`
- `sql.targetSchema`
- `sql.targetTableSuffix`
- `sql.whereClause`
- `sql.writeMode`

Protection:

- `thales.*`

### How `sql.sourceTables` Works

Yes, `sql.sourceTables` is comma-separated.

Example:

```properties
sql.sourceTables=customers,employees,claims
```

This property is an allowlist for execution time.

It does not tell BigID what to scan.

It means:

- after BigID returns classified structured assets
- and after the application infers table names from those assets
- only those tables named in `sql.sourceTables` are allowed to continue

If `sql.sourceTables` is blank:

- the application will attempt to process any structured BigID assets it can map successfully

If `sql.sourceTables` is populated:

- the application narrows processing to only those tables

### How BigID Filtering Relates To Structured Processing

`bigid.catalogFilter` is still the first gate for structured data.

That means the structured path is:

1. BigID catalog query through `bigid.catalogFilter`
2. local application filtering to only structured assets
3. optional table restriction through `sql.sourceTables`
4. JDBC read and Thales protect on only the classified columns

So the relationship is:

- `bigid.catalogFilter` controls which BigID catalog results are available
- `sql.enabled` turns the structured execution path on
- `sql.sourceTables` optionally narrows which inferred tables are processed

### Example Structured Scenario

Suppose:

```properties
bigid.catalogFilter=classification="PII"
sql.enabled=true
sql.sourceTables=customers
```

Then the runtime behavior is:

1. query BigID for assets classified as PII
2. keep only returned assets that look like structured fields or columns
3. infer table and column names
4. discard any inferred table other than `customers`
5. read rows from `customers`
6. protect only the columns BigID identified as sensitive
7. write the results to `dbo.customers_protected`

## Debug-Only Path

Debug-only mode is the safest way to validate a new BigID tenant before turning on protection.

### What Turns It On

```properties
bigid.debug.dumpAssets=true
bigid.debug.only=true
```

### Debug Flow

1. The application queries BigID catalog using `bigid.catalogFilter`.
2. The application normalizes the returned assets.
3. The application writes the asset dump JSON to `bigid.debug.dumpFile` or a default debug file.
4. The application stops before reading local files, Azure blobs, or SQL rows.

### What To Inspect

Look at:

- `path`
- `looksLikeBlobObject`
- `storageContainerName`
- `storageBlobName`
- `looksLikeS3Object`
- `s3BucketName`
- `s3ObjectKey`
- `looksLikeGcsObject`
- `gcsBucketName`
- `gcsObjectName`
- `looksLikeStructuredColumn`
- `inferredTableName`
- `inferredColumnName`

This tells you whether:

- Azure object paths are being parsed correctly
- S3 object paths are being parsed correctly
- GCS object paths are being parsed correctly
- filesystem paths line up with local files
- structured table and column inference is correct

## Recommended Operational Sequence

For a new environment:

1. Configure BigID access and set a narrow `bigid.catalogFilter`
2. Enable:
   - `bigid.debug.dumpAssets=true`
   - `bigid.debug.only=true`
3. Run the application once
4. Review the asset dump JSON
5. Confirm unstructured path mapping
6. Confirm structured table and column mapping
7. Set `bigid.debug.only=false`
8. Enable either:
   - `source.mode` for unstructured protection
   - `sql.enabled=true` for structured protection
   - or both
9. Run the full protection flow

## Important Operational Notes

- BigID is not being asked to scan data by this application today; it is assumed BigID has already scanned and cataloged the sources.
- The application is a consumer of BigID catalog results, not a BigID scan orchestrator.
- The structured and unstructured paths both begin with the same BigID catalog query.
- The distinction between the two paths happens after the catalog results are returned.

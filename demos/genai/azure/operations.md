# Operations Guide

This guide explains how the Azure Purview sample operates at runtime.

It focuses on:

- how the shared Purview discovery step works
- how the unstructured storage path works
- how the structured Azure SQL path works
- how the hybrid streaming and document-conversion model behaves
- which properties turn each path on or off

## High-Level Model

This sample separates the workflow into two layers:

1. Microsoft Purview is the discovery and governance layer
2. The application is the execution and protection layer

That means the sample can:

- start or reuse a Purview scan
- search Purview for classified assets
- decide whether those assets belong to the storage path or the SQL path
- read the corresponding source data
- protect only the targeted content

For unstructured content, Azure AI Language PII detection is still used to locate the exact values inside the extracted text.

For structured SQL content, Purview column classification is the targeting signal, so no second text-analytics pass is required.

## Shared Purview Discovery Step

Both the storage and SQL paths begin the same way:

1. The application loads `thales-config.properties`.
2. The application builds `PurviewConfig` from the configured properties.
3. The application authenticates to Purview with `PURVIEW_ACCESS_TOKEN`.
4. If `PURVIEW_RUN_SCAN=true`, the application starts the configured Purview scan.
5. If `PURVIEW_WAIT_FOR_SCAN=true`, the application polls until the scan succeeds or fails.
6. The application searches Purview using `PURVIEW_CLASSIFICATIONS`.
7. The application normalizes the returned search results into `PurviewAsset` objects.
8. The selected workload determines whether the returned assets are sent to the storage path, the SQL path, or both.

Important point:

- `PURVIEW_CLASSIFICATIONS` is the shared Purview search filter.
- It is not SQL-specific and not storage-specific.
- The distinction between storage and SQL happens after Purview returns results.

## Unstructured Storage Path

The storage path is used for blob and ADLS-style assets that Purview already classified.

### What Turns It On

The storage path runs when the workload argument is:

- `storage`
- `files`
- `both`

It also requires:

- `AZURE_STORAGE_CONNECTION_STRING`
- `PURVIEW_STORAGE_TARGET_CONTAINER`
- command-line `textAnalyticsEndpoint`
- command-line `textAnalyticsApiKey`

### Storage Flow

1. The application searches Purview using `PURVIEW_CLASSIFICATIONS`.
2. The storage processor keeps only assets that look like blob or ADLS objects.
3. The processor applies `PURVIEW_FILE_ENTITY_HINTS` as an additional filter.
4. The processor optionally narrows candidates using `PURVIEW_STORAGE_QUALIFIED_NAME_PREFIXES`.
5. The processor optionally narrows candidates again using the command-line `fileExtension` filter.
6. The processor opens the matching source blob from Azure Storage.
7. If the source file is text-like such as `.txt`, `.csv`, or `.json`, the processor stays on the streaming path.
8. If the source file is a document such as `.pdf`, `.doc`, `.docx`, `.xls`, or `.xlsx`, the processor downloads it to a temp file, converts it to text, and deletes the temp file immediately after conversion.
9. The processor sends the extracted text to Azure AI Language PII detection when running in protect mode.
10. Azure returns the sensitive entities found in the content.
11. The processor protects only those values with Thales CipherTrust using the unstructured tag-wrapper format.
12. In reveal mode, the processor scans the tagged protected content and reveals it inline.
13. The processor writes the primary output blob to `PURVIEW_STORAGE_TARGET_CONTAINER` under `PURVIEW_STORAGE_TARGET_PREFIX`.
14. If enabled, the processor also writes:
   - extracted text output
   - PII findings JSON report

### Hybrid Storage Behavior

The storage path now uses two execution models:

Text-like streaming path:

- source formats: `.txt`, `.csv`, `.json`
- reads directly from blob stream
- processes line by line
- writes text output to target blob storage

Document conversion path:

- source formats: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`
- downloads source blob to a temp file
- converts the document to text first
- processes the extracted text
- deletes the temp file immediately after conversion
- writes text-based artifacts to target blob storage

This design works well when the downstream goal is vector loading, text indexing, or JSON-oriented pipelines rather than preserving the original document format.

### Storage Properties

Shared Purview discovery:

- `PURVIEW_ENDPOINT`
- `PURVIEW_ACCESS_TOKEN`
- `PURVIEW_RUN_SCAN`
- `PURVIEW_WAIT_FOR_SCAN`
- `PURVIEW_SCAN_POLL_SECONDS`
- `PURVIEW_DATASOURCE_NAME`
- `PURVIEW_SCAN_NAME`
- `PURVIEW_CLASSIFICATIONS`

Storage selection:

- `PURVIEW_FILE_ENTITY_HINTS`
- `PURVIEW_STORAGE_QUALIFIED_NAME_PREFIXES`

Azure Storage:

- `AZURE_STORAGE_CONNECTION_STRING`
- `PURVIEW_STORAGE_TARGET_CONTAINER`
- `PURVIEW_STORAGE_TARGET_PREFIX`

Text detection and protection:

- command-line `textAnalyticsEndpoint`
- command-line `textAnalyticsApiKey`
- `TAG.*`
- `PII.*`
- `UNSTRUCTURED_OUTPUT_WRITE_EXTRACTED_TEXT`
- `UNSTRUCTURED_OUTPUT_WRITE_PROTECTED_TEXT`
- `UNSTRUCTURED_OUTPUT_WRITE_FINDINGS_REPORT`

### How Purview Filtering Relates To Storage Processing

`PURVIEW_CLASSIFICATIONS` does not directly say “this is a blob to process.”

Instead:

1. Purview returns classified assets
2. the application checks whether each returned asset looks like storage content
3. the file hints and qualified-name prefixes optionally narrow those results
4. the application decides whether the file stays on the streaming path or goes through document conversion

So the Purview search determines which candidate assets enter the pipeline, and the file type determines how the content is read.

## Structured Azure SQL Path

The SQL path is used for Azure SQL tables and columns that Purview already classified.

### What Turns It On

The SQL path runs when the workload argument is:

- `sql`
- `both`

It also requires:

- `PURVIEW_SQL_JDBC_URL`
- `PURVIEW_SQL_USER`
- `PURVIEW_SQL_PASSWORD`
- `PURVIEW_SQL_SOURCE_TABLE`
- `PURVIEW_SQL_TARGET_TABLE`

### SQL Flow

1. The application searches Purview using `PURVIEW_CLASSIFICATIONS`.
2. The SQL processor keeps only assets that look like SQL columns using `PURVIEW_SQL_COLUMN_ENTITY_HINTS`.
3. If `PURVIEW_SQL_SOURCE_TABLE` is set, the processor keeps only assets whose qualified name references that table.
4. The processor extracts the matching sensitive column names from the Purview assets.
5. The processor connects to Azure SQL using JDBC.
6. The processor reads the source table metadata and confirms which sensitive columns actually exist in the table.
7. The processor creates or re-creates the target table depending on `PURVIEW_SQL_WRITE_MODE`.
8. The processor reads source rows, optionally constrained by `PURVIEW_SQL_WHERE_CLAUSE`.
9. The processor protects only the values in the Purview-classified columns.
10. The processor writes the transformed rows to `PURVIEW_SQL_TARGET_TABLE`.
11. Structured SQL values are stored as plain protected values and do not use the unstructured locator tag wrapper.

### SQL Properties

Shared Purview discovery:

- `PURVIEW_ENDPOINT`
- `PURVIEW_ACCESS_TOKEN`
- `PURVIEW_CLASSIFICATIONS`

SQL selection and execution:

- `PURVIEW_SQL_COLUMN_ENTITY_HINTS`
- `PURVIEW_SQL_JDBC_URL`
- `PURVIEW_SQL_USER`
- `PURVIEW_SQL_PASSWORD`
- `PURVIEW_SQL_SOURCE_TABLE`
- `PURVIEW_SQL_TARGET_TABLE`
- `PURVIEW_SQL_WHERE_CLAUSE`
- `PURVIEW_SQL_WRITE_MODE`

Protection:

- `KEYMGRHOST`
- `CRDPTKN`
- `POLICYNAME`
- `DEFAULTPOLICY`
- `POLICYTYPE`

### How Purview Filtering Relates To SQL Processing

The SQL path is:

1. Purview search through `PURVIEW_CLASSIFICATIONS`
2. local filtering to only SQL-column-like assets
3. optional restriction to `PURVIEW_SQL_SOURCE_TABLE`
4. JDBC read and Thales protect on only the classified columns

So the relationship is:

- `PURVIEW_CLASSIFICATIONS` controls which Purview search results are available
- the workload argument turns the SQL execution path on
- `PURVIEW_SQL_SOURCE_TABLE` narrows which matching table is processed

## Local File-To-File Path

The non-Purview local file-to-file sample is still useful for simpler offline testing.

### What Turns It On

This path runs when you use:

- `ThalesAzureProtectRevealBatchProcessor`

It does not use Purview discovery.

### Local File Flow

1. The application reads local files from the input directory.
2. The application converts each file to text first.
3. The application supports `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.txt`, `.csv`, and `.json`.
4. Azure AI Language detects sensitive values inside the extracted text in protect mode.
5. The application protects only those values with Thales.
6. The application writes the primary output file to the output directory.
7. If enabled, the application also writes:
   - extracted text
   - findings JSON report

This local path now uses the same document-conversion-first model as the Purview storage document path.

## Recommended Operational Sequence

For a new Purview-backed environment:

1. Configure `PURVIEW_ENDPOINT`, `PURVIEW_ACCESS_TOKEN`, and `PURVIEW_CLASSIFICATIONS`
2. Decide whether you want Purview to start the scan or reuse existing scan results
3. If you want the sample to trigger scans, set:
   - `PURVIEW_RUN_SCAN=true`
   - `PURVIEW_DATASOURCE_NAME`
   - `PURVIEW_SCAN_NAME`
4. Run the storage path with a narrow `fileExtension` or qualified-name prefix first
5. Enable:
   - `UNSTRUCTURED_OUTPUT_WRITE_EXTRACTED_TEXT=true`
   - `UNSTRUCTURED_OUTPUT_WRITE_FINDINGS_REPORT=true`
6. Review the extracted text and findings report
7. Confirm that the sensitive matches are correct for your vector-load workflow
8. Expand the storage scope or enable the SQL path
9. For SQL, confirm the target table naming and write mode before processing larger datasets

## Important Operational Notes

- Purview is used here as the discovery and governance layer, not the fine-grained in-content detection engine.
- Azure AI Language is still the exact-value detector for unstructured content.
- SQL does not run Azure AI Language because Purview column classification already identifies the target fields.
- Text-like storage assets benefit from streaming because they do not require binary parsing.
- Binary document formats benefit from conversion-first processing because the downstream output is text-oriented anyway.
- The hybrid model is a good fit when the target system is a vector database, search index, or JSON/text enrichment pipeline.

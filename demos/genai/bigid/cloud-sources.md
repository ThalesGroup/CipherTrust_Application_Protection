# Cloud Sources Guide

This guide explains how the BigID sample works with remote object stores:

- Azure Blob and ADLS-style paths
- Amazon S3
- Google Cloud Storage
- mixed `auto` mode

It also includes example property blocks you can copy into `application.properties`.

## How It Works

The model is the same for all remote object stores:

1. BigID catalog returns a classified asset.
2. The application inspects the asset path.
3. If the path looks like Azure Blob, S3, or GCS, the application routes it to the matching document store.
4. The application downloads the source object to a temp file.
5. The temp file is converted to text.
6. Azure AI Language identifies the exact sensitive spans in that text.
7. Thales protects only those spans.
8. The application writes the output artifacts to the configured target container or bucket and prefix.

Important operational points:

- The application does not overwrite the original source object.
- The application writes new output artifacts to the configured target location.
- The source object is staged only temporarily for text extraction.
- The temp file is deleted immediately after conversion.

So in practice, if BigID determines that a sensitive asset is on S3 or GCS, the main remaining requirement is to provide the correct source-mode settings and credentials in the properties file.

## What Must Be True

Automatic processing works when all of these are true:

1. BigID returns a path format the parser recognizes.
2. `source.mode` allows that provider.
3. The matching credentials and target settings are present.
4. The file extension is included in `source.supportedExtensions`.

If those conditions are met, the application can process the remote content automatically after BigID discovery.

## Source Modes

### Azure Blob

Use this when BigID returns Azure Blob or ADLS-style paths.

```properties
source.mode=azureblob
azure.storage.connectionString=DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net
azure.storage.targetContainer=protected
azure.storage.targetPrefix=thales-output
azure.storage.qualifiedNamePrefixes=
```

What happens:

- BigID returns an Azure object path
- the app parses container and blob name
- downloads the object
- converts it to text
- protects detected spans
- uploads artifacts to the configured target container and prefix

### Amazon S3

Use this when BigID returns S3-style paths such as `s3://bucket/key`.

```properties
source.mode=s3
s3.region=us-east-1
s3.accessKey=
s3.secretKey=
s3.sessionToken=
s3.endpoint=
s3.pathStyleAccess=false
s3.targetBucket=protected-output
s3.targetPrefix=thales-output
s3.qualifiedNamePrefixes=
```

What happens:

- BigID returns an S3 path
- the app parses bucket and object key
- downloads the object from S3
- converts it to text
- protects detected spans
- uploads artifacts to `s3.targetBucket` under `s3.targetPrefix`

Notes:

- If `s3.accessKey` and `s3.secretKey` are blank, the AWS SDK default credential chain is used
- `s3.endpoint` is useful for S3-compatible storage
- `s3.pathStyleAccess=true` can help with some compatible object stores

### Google Cloud Storage

Use this when BigID returns GCS-style paths such as `gs://bucket/object`.

```properties
source.mode=gcs
gcs.projectId=
gcs.credentialsPath=
gcs.targetBucket=protected-output
gcs.targetPrefix=thales-output
gcs.qualifiedNamePrefixes=
```

What happens:

- BigID returns a GCS path
- the app parses bucket and object name
- downloads the object from GCS
- converts it to text
- protects detected spans
- uploads artifacts to `gcs.targetBucket` under `gcs.targetPrefix`

Notes:

- `gcs.credentialsPath` is optional if the runtime already has Google credentials available
- `gcs.projectId` is helpful when the environment does not supply one automatically

### Auto Mode

Use this when you want one runtime to handle multiple source types.

```properties
source.mode=auto
source.rootDirectory=E:/data/inbound
output.directory=E:/data/protected

azure.storage.connectionString=...
azure.storage.targetContainer=protected
azure.storage.targetPrefix=thales-output

s3.region=us-east-1
s3.targetBucket=protected-output
s3.targetPrefix=thales-output

gcs.targetBucket=protected-output
gcs.targetPrefix=thales-output
```

In `auto` mode, the application tries:

1. local filesystem resolution
2. Azure Blob resolution if Azure settings are configured
3. S3 resolution if S3 settings are configured
4. GCS resolution if GCS settings are configured

This is useful when BigID catalog results may point to multiple storage systems in the same environment.

## Recommended First Test

Before enabling full protection for a new provider, run debug-only mode first.

### S3 debug test

```properties
bigid.debug.dumpAssets=true
bigid.debug.only=true
source.mode=s3
```

Inspect:

- `looksLikeS3Object`
- `s3BucketName`
- `s3ObjectKey`

### GCS debug test

```properties
bigid.debug.dumpAssets=true
bigid.debug.only=true
source.mode=gcs
```

Inspect:

- `looksLikeGcsObject`
- `gcsBucketName`
- `gcsObjectName`

If those inferred fields look correct, turn off `bigid.debug.only` and run the full protection flow.

## Output Behavior

For remote object stores, the application can write these artifacts:

- extracted text
- protected text or revealed text
- findings JSON report

That behavior is controlled by:

```properties
unstructured.output.writeExtractedText=true
unstructured.output.writeProtectedText=true
unstructured.output.writeFindingsReport=true
```

The output is written to the configured target location for that provider, not back to the original source object.

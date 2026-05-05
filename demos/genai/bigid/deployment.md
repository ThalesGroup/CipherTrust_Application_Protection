# Deployment Guide

This project can be run in three common ways:

1. Directly on Windows with `run-bigid-transformation.bat`
2. Directly on Linux with `run-bigid-transformation.sh`
3. In a container with the included `Dockerfile`

## Prerequisites

- Java 11 or later
- Maven 3.9+ for local builds
- Network access from the runtime to:
  - your BigID endpoint
  - your Azure Text Analytics endpoint
  - your Thales CipherTrust Manager
  - your SQL Server, if `sql.enabled=true`

## 1. Prepare Configuration

Create a runtime config file from the example:

```powershell
Copy-Item E:\codex\work\bigid\src\main\resources\application.properties.example E:\codex\work\bigid\src\main\resources\application.properties
```

```bash
cp /path/to/bigid/src/main/resources/application.properties.example /path/to/bigid/src/main/resources/application.properties
```

Update the copied file with your environment values:

- BigID base URL and token
- source mode and related source settings
- Azure Text Analytics endpoint and key
- Thales registration details
- optional SQL settings

## 2. Build the Utility

From [pom.xml](/E:/codex/work/bigid/pom.xml):

```powershell
mvn -DskipTests package
```

```bash
mvn -DskipTests package
```

This creates:

- `target/bigid.thales.transformation-0.0.1-SNAPSHOT.jar`
- `target/bigid.thales.transformation-0.0.1-SNAPSHOT-all.jar`

Use the `-all.jar` file for runtime because it contains dependencies.

## 3. Run on Windows

The Windows launcher is [run-bigid-transformation.bat](/E:/codex/work/bigid/run-bigid-transformation.bat).

Default behavior:

- looks for the shaded jar in `target\bigid.thales.transformation-0.0.1-SNAPSHOT-all.jar`
- looks for config in `src\main\resources\application.properties`

Example:

```powershell
set BIGID_CONFIG_FILE=E:\codex\work\bigid\src\main\resources\application.properties
set JAVA_OPTS=-Xms512m -Xmx2g
E:\codex\work\bigid\run-bigid-transformation.bat
```

Useful environment variables:

- `BIGID_CONFIG_FILE`
- `BIGID_JAR`
- `JAVA_CMD`
- `JAVA_OPTS`

## 4. Run on Linux

The Linux launcher is [run-bigid-transformation.sh](/E:/codex/work/bigid/run-bigid-transformation.sh).

Make it executable once:

```bash
chmod +x /path/to/bigid/run-bigid-transformation.sh
```

Example:

```bash
export BIGID_CONFIG_FILE=/opt/bigid/application.properties
export JAVA_OPTS="-Xms512m -Xmx2g"
/path/to/bigid/run-bigid-transformation.sh
```

Useful environment variables:

- `BIGID_CONFIG_FILE`
- `BIGID_JAR`
- `JAVA_CMD`
- `JAVA_OPTS`

## 5. Structured SQL Flow

To enable structured data processing, set these in your properties file:

```properties
sql.enabled=true
sql.jdbcUrl=jdbc:sqlserver://host:1433;databaseName=sample
sql.user=your-user
sql.password=your-password
sql.sourceTables=customers,employees
sql.targetSchema=dbo
sql.targetTableSuffix=_protected
sql.whereClause=
sql.writeMode=replace
```

Behavior:

- BigID identifies sensitive structured fields
- the utility maps those results to source tables and columns
- rows are copied into target tables
- only the BigID-classified columns are protected

## 6. Unstructured Source Modes

The utility supports three unstructured source modes:

```properties
source.mode=local
```

Use this when the Java process can read files directly from a filesystem path.

Required settings:

- `source.rootDirectory`
- `output.directory`

```properties
source.mode=azureblob
azure.storage.connectionString=DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net
azure.storage.targetContainer=protected
azure.storage.targetPrefix=thales-output
azure.storage.qualifiedNamePrefixes=
```

Use this when BigID has classified Azure Blob or ADLS-style objects and the runtime should read those objects directly from Azure Storage.

Required settings:

- `azure.storage.connectionString`
- `azure.storage.targetContainer`

Optional setting:

- `azure.storage.qualifiedNamePrefixes`
  Use this if you want to limit processing to BigID asset paths with specific qualified-name prefixes.

```properties
source.mode=auto
```

Use this when you want local resolution first and Azure Blob resolution as a fallback.

## 7. Docker Build

Build the image from [Dockerfile](/E:/codex/work/bigid/Dockerfile):

```bash
docker build -t bigid-thales-transformation:latest .
```

The image:

- builds the project in a Maven stage
- copies the shaded jar into a Java 11 runtime image
- uses `BIGID_CONFIG_FILE=/config/application.properties` by default

## 8. Docker Run

Mount a config directory and any local source/output directories the job should use.

Example:

```bash
docker run --rm \
  -e BIGID_CONFIG_FILE=/config/application.properties \
  -e JAVA_OPTS="-Xms512m -Xmx2g" \
  -v /opt/bigid-config:/config \
  -v /data/inbound:/data/inbound \
  -v /data/protected:/data/protected \
  bigid-thales-transformation:latest
```

If your properties file uses local paths, those paths must exist inside the container. For example:

- `source.rootDirectory=/data/inbound`
- `output.directory=/data/protected`

For Azure Blob mode inside Docker, the properties file can instead use:

- `source.mode=azureblob`
- `azure.storage.connectionString=...`
- `azure.storage.targetContainer=protected`

## 9. Secrets Guidance

For production use, avoid baking secrets into the image.

Recommended approaches:

- mount the properties file at runtime
- inject `BIGID_CONFIG_FILE` as an environment variable
- manage the properties file with your platform secret store or deployment tool

## 10. Operational Notes

- The utility needs a valid BigID token and catalog filter.
- The BigID catalog payload can differ between tenants, so the table and column inference logic may need small tuning against your live results.
- Document flows use Azure Text Analytics to find exact spans.
- Document assets can now be read from either local filesystem paths or Azure Blob/ADLS-style paths.
- Structured SQL flows use BigID classifications to choose which columns to protect.

## 11. BigID Debugging Tips

When you are first connecting to a new BigID tenant, turn on the asset dump:

```properties
bigid.debug.dumpAssets=true
bigid.debug.dumpFile=E:/data/protected/bigid-asset-debug.json
bigid.debug.only=true
```

What to check in the dump:

- `path`
  Confirms how BigID represents Azure objects, filesystem paths, tables, and columns
- `looksLikeBlobObject`
  Confirms whether the sample recognized the asset as Azure Blob or ADLS-style content
- `storageContainerName` and `storageBlobName`
  Confirms whether the Azure path parser is extracting the right values
- `inferredTableName` and `inferredColumnName`
  Confirms whether the structured SQL inference matches your schema

Recommended first-run approach:

1. Start with a narrow `bigid.catalogFilter`
2. Enable `bigid.debug.dumpAssets=true`
3. Enable `bigid.debug.only=true`
4. Review the JSON dump
5. Adjust `azure.storage.qualifiedNamePrefixes` or `sql.sourceTables` if needed
6. Run the full protection flow after the asset mapping looks right

# Synthetic Member Data Generator Guide

This repo now includes two versions of the synthetic member data generator.

They create the same member-style sample schema used by the benchmark notebooks:

- `custid`
- `name`
- `address`
- `city`
- `state`
- `zip`
- `phone`
- `email`
- `dob`
- `creditcard`
- `creditcardcode`
- `ssn`

## Which Version To Use

### 1. Databricks notebook version

Use this when:

- you want Spark to generate large test files
- you want to write directly to Databricks-accessible storage
- you want to write to `abfss://`, `dbfs:/`, `/Volumes/...`, or `/mnt/...`
- you want generation behavior that is close to the benchmark notebooks

File:

- [synthetic_member_data_generator.py](/E:/codex/work/thales.databricks.integration/notebooks/utils/synthetic_member_data_generator.py:1)

This version is intended to run inside Databricks notebooks.

### 2. Standalone Python version

Use this when:

- you want to generate files outside Databricks
- you want to create local Windows or Linux files
- you do not want to depend on Spark
- you just need test input files for later loading

File:

- [synthetic_member_data_generator.py](/E:/codex/work/thales.databricks.integration/tools/synthetic_member_data_generator.py:1)

This version runs as normal Python and writes:

- CSV
- JSON Lines

## Standalone Generator Examples

### Windows example

```powershell
python E:\codex\work\thales.databricks.integration\tools\synthetic_member_data_generator.py `
  --row-count 1000000 `
  --output-files 8 `
  --output-dir C:\data\member_output `
  --format csv
```

### Linux example

```bash
python /path/to/thales.databricks.integration/tools/synthetic_member_data_generator.py \
  --row-count 1000000 \
  --output-files 8 \
  --output-dir /data/output/member_output \
  --format csv
```

## Databricks Notebook Example Settings

Inside the notebook version, set values like:

```python
ROW_COUNT = 1_000_000
OUTPUT_FILE_COUNT = 16
OUTPUT_DIRECTORY = "abfss://raw@mystorage.dfs.core.windows.net/databricks/input/member_data_1m"
OUTPUT_FORMAT = "csv"
```

Or for a Databricks-managed path:

```python
ROW_COUNT = 500_000
OUTPUT_FILE_COUNT = 8
OUTPUT_DIRECTORY = "dbfs:/tmp/thales/synthetic_member_data"
OUTPUT_FORMAT = "csv"
```

## Practical Recommendation

Use the standalone version when you simply need to create files.

Use the Databricks notebook version when you want:

- direct ADLS output
- direct DBFS or Volume output
- large-scale Spark-based file generation
- behavior that stays close to the benchmark generation pattern

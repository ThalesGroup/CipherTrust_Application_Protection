# Databricks TLS Runtime Guide

This guide explains which TLS configuration model applies to which Databricks
runtime in this project.

Use this document when you need to answer:

- which SSL/TLS settings belong to Java compute clusters
- which settings belong to Python on compute clusters
- which settings belong to SQL Warehouse
- where certs/keys should live for each runtime
- what tools to use when troubleshooting

## Why this guide exists

There are now three valid TLS deployment patterns in this repo:

1. Java on Databricks compute clusters
2. Python on Databricks compute clusters
3. Python in Databricks SQL Warehouse / Unity Catalog functions

They do not use the same certificate-loading model.

If you mix them together, the most common outcomes are:

- file not found errors
- TLS handshake failures
- server verification failures
- client certificate not presented
- SQL Warehouse runtime path issues

## Quick matrix

| Runtime | Main code path | TLS material format | How files are supplied | Recommended |
|---|---|---|---|---|
| Compute cluster Java | Java UDF jar | PKCS12 client cert + CA file | init script copies files to `/tmp/thales_config` | Yes |
| Compute cluster Python | Python wheel in notebook/cluster runtime | PEM client cert + PEM key + CA file | init script copies files to `/tmp/thales_config` | Yes |
| SQL Warehouse | Unity Catalog Python functions | base64-embedded CA/cert/key in generated SQL | generator embeds cert bytes into `PROPERTIES` | Yes |

## 1. Compute cluster Java TLS

### Use this when

- you are using the Java UDF path
- the workload runs on an all-purpose or job compute cluster
- the cluster init script is available

### Main config model

Typical properties:

```properties
CRDPIP=your-crdp-ip
CRDPPORT=8091
CRDP_SSL_ENABLED=true
CRDP_SSL_VERIFY_SERVER=true
CRDP_CA_CERT_PATH=/tmp/thales_config/crdp-ca.pem
CRDP_CLIENT_PKCS12_PATH=/tmp/thales_config/crdp-client.p12
CRDP_CLIENT_PKCS12_PASSWORD=changeit
CRDP_CONNECT_TIMEOUT_MS=10000
CRDP_READ_TIMEOUT_MS=30000
CRDP_WRITE_TIMEOUT_MS=30000
CRDP_HTTP_MAX_IDLE_CONNECTIONS=20
CRDP_HTTP_KEEPALIVE_MINUTES=5
```

### How it works

- the init script copies TLS files from the Unity Catalog volume to
  `/tmp/thales_config`
- Java builds an HTTPS client with a shared pooled `OkHttpClient`
- keep-alive and connection reuse are preserved

### Files typically used

- `crdp-client.p12`
- `crdp-ca.pem`
- `udfConfig.properties`

### Good fit

- high-throughput Spark jobs
- bulk protect/reveal
- local cluster-side file staging

## 2. Compute cluster Python TLS

### Use this when

- you are using the Python wheel from a notebook or cluster-attached Python runtime
- the cluster init script is available
- you want Python-based protect/reveal helpers on compute clusters

### Main config model

Typical properties:

```properties
CRDPIP=your-crdp-ip
CRDPPORT=8091
CRDP_SSL_ENABLED=true
CRDP_SSL_VERIFY_SERVER=true
CRDP_CA_CERT_PATH=/tmp/thales_config/crdp-ca.pem
CRDP_CLIENT_CERT_PATH=/tmp/thales_config/databricks-crdp-client-cert.pem
CRDP_CLIENT_KEY_PATH=/tmp/thales_config/databricks-crdp-client-key.pem
CRDP_CONNECT_TIMEOUT_MS=10000
CRDP_READ_TIMEOUT_MS=30000
```

### How it works

- the init script copies PEM files into `/tmp/thales_config`
- Python uses a shared pooled `requests.Session()`
- TLS files are referenced as local file paths

### Files typically used

- `databricks-crdp-client-cert.pem`
- `databricks-crdp-client-key.pem`
- `crdp-ca.pem`
- `udfConfig.properties`

### Good fit

- cluster-side notebook testing
- Python wheel smoke tests
- Python-based cluster runtime workflows

## 3. SQL Warehouse TLS

### Use this when

- you are deploying Unity Catalog Python functions in SQL Warehouse
- you need TLS and client certificate authentication from SQL Warehouse

### Important rule

Do **not** rely on these for SQL Warehouse TLS:

- `/tmp/thales_config/...`
- `/Volumes/...` passed directly to `requests` as cert/key/CA file paths

Those path-based models are valid for compute clusters, but they are not the
recommended SQL Warehouse TLS pattern in this project.

### Recommended SQL Warehouse TLS model

Use the embedded-config generator to emit:

- `CRDP_CA_CERT_PEM_B64`
- `CRDP_CLIENT_CERT_PEM_B64`
- `CRDP_CLIENT_KEY_PEM_B64`

The Python helper decodes those values, writes them to local temporary files at
runtime, and then points `requests` at those temp files.

### How it works

1. source PEM files are stored in a trusted working location
2. `generate_embedded_config_sql_from_properties.py` reads those files
3. the generator embeds base64-encoded bytes into the SQL Warehouse
   `PROPERTIES = {...}` block
4. the SQL Warehouse Python UDF decodes them at runtime
5. the wheel writes local temp files and configures `requests`

### Good fit

- persistent Unity Catalog Python functions
- SQL Warehouse reveal/protect patterns
- SQL-native governed access

## Which properties belong to which runtime

### Shared/general

These are broadly valid across runtimes:

- `CRDPIP`
- `CRDPPORT`
- `CRDP_SSL_ENABLED`
- `CRDP_SSL_VERIFY_SERVER`
- `CRDP_CONNECT_TIMEOUT_MS`
- `CRDP_READ_TIMEOUT_MS`

### Java compute cluster

- `CRDP_CA_CERT_PATH`
- `CRDP_CLIENT_PKCS12_PATH`
- `CRDP_CLIENT_PKCS12_PASSWORD`
- `CRDP_WRITE_TIMEOUT_MS`
- `CRDP_HTTP_MAX_IDLE_CONNECTIONS`
- `CRDP_HTTP_KEEPALIVE_MINUTES`

### Python compute cluster

- `CRDP_CA_CERT_PATH`
- `CRDP_CLIENT_CERT_PATH`
- `CRDP_CLIENT_KEY_PATH`

### SQL Warehouse

- `CRDP_CA_CERT_PEM_B64`
- `CRDP_CLIENT_CERT_PEM_B64`
- `CRDP_CLIENT_KEY_PEM_B64`

## Can both Java and Python settings exist at the same time

Yes.

It is valid for one property file or generated configuration source to include
both:

- Java PKCS12 settings
- Python PEM settings

Example:

```properties
CRDPIP=your-crdp-ip
CRDPPORT=8091
CRDP_SSL_ENABLED=true
CRDP_SSL_VERIFY_SERVER=true
CRDP_CA_CERT_PATH=/tmp/thales_config/crdp-ca.pem

CRDP_CLIENT_PKCS12_PATH=/tmp/thales_config/crdp-client.p12
CRDP_CLIENT_PKCS12_PASSWORD=changeit

CRDP_CLIENT_CERT_PATH=/tmp/thales_config/databricks-crdp-client-cert.pem
CRDP_CLIENT_KEY_PATH=/tmp/thales_config/databricks-crdp-client-key.pem
```

That is fine because:

- Java ignores the PEM client-cert settings
- Python ignores the PKCS12 client-auth settings

For SQL Warehouse, prefer the base64-embedded properties instead of path-based
TLS file settings.

## Tools and places to look when troubleshooting

### 1. CRDP logs

Use CRDP logs when you need to answer:

- did the request reach CRDP
- which endpoint was called
- which policy was used
- which user identity CRDP associated with the request
- whether CRDP reported success or per-record errors

Useful fields:

- `endpoint`
- `protection_policy_name`
- `status`
- `records_details[].error`
- `user`

Important note:

- CRDP audit logs often show `user` as the audit field name even though the
  client request field is `username`

### 2. curl

Use curl when you want the simplest direct test outside Databricks.

Typical mTLS example:

```bash
curl --cacert ca-chain.pem \
  --cert databricks-crdp-client-cert.pem \
  --key databricks-crdp-client-key.pem \
  --location 'https://your-crdp-ip:8091/v1/protect' \
  --header 'Content-Type: application/json' \
  --data '{"protection_policy_name": "static-char-internal","data": "104-85-6564-3453455"}' -v
```

Use curl to answer:

- does HTTPS reach the CRDP endpoint
- does the client cert/key pair work
- does the CA file validate the server

### 3. OpenSSL

Use OpenSSL when you need to inspect:

- the CA certificate
- server certificate issuer/subject
- whether the server chain validates

Useful commands:

```bash
openssl x509 -in crdp-ca.pem -noout -subject -issuer -text
```

```bash
openssl s_client -connect your-crdp-ip:8091 -showcerts -cert databricks-crdp-client-cert.pem -key databricks-crdp-client-key.pem -CAfile crdp-ca.pem
```

Use OpenSSL to answer:

- is the CA file actually a CA cert
- what server certificate is CRDP presenting
- does verification succeed outside Databricks

### 4. Compute cluster Python TLS smoke test

Use:

- [sample_tls_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_tls_smoke_test.py)

Use it when you want to confirm:

- wheel import path
- local TLS files exist in `/tmp/thales_config`
- protect/reveal work from cluster-side Python
- repeated-call behavior works

### 5. SQL Warehouse TLS debug function

Use:

- [sample_tls_debug_uc_function.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_tls_debug_uc_function.sql)

Use it when you want to confirm:

- base64 TLS properties are present
- temp files are being materialized
- Python `ssl` can load the CA bundle
- Python `ssl` can load the client cert/key pair

This is the best first stop for SQL Warehouse TLS issues.

### 6. SQL Warehouse embedded-config generator

Use:

- [generate_embedded_config_sql_from_properties.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\utils\generate_embedded_config_sql_from_properties.py)

Use it when you want to:

- stamp an environment-specific SQL deployment file
- embed SQL Warehouse TLS material
- avoid hand-editing long `PROPERTIES = {...}` blocks

### 7. SQL Warehouse deployment docs

Use:

- [SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md)
- [SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md)

Use these when you need:

- deployment order
- correct wheel version/path
- embedded SQL guidance
- validation steps

## Common failure patterns

### File not found for `/tmp/thales_config/...`

Meaning:

- you are likely using a compute-cluster path model in the wrong runtime

Most common causes:

- SQL Warehouse trying to use compute-cluster TLS file paths
- init script did not copy files

### SQL Warehouse cannot use `/Volumes/...` cert path

Meaning:

- the warehouse runtime can see the wheel dependency path, but not necessarily
  use the same path as a TLS file path for `requests`

Fix:

- use the base64-embedded SQL Warehouse model

### `unterminated string literal`

Meaning:

- raw PEM text was embedded incorrectly in the SQL function body

Fix:

- use the generator’s base64-embedding model

### `unable to get local issuer certificate`

Meaning:

- CA verification failed

Check:

- whether the right CA file or chain is being used
- whether OpenSSL validates the server with the same CA material

### `tlsv13 alert certificate required`

Meaning:

- CRDP requires a client certificate, but the runtime did not present one

Check:

- embedded client cert/key presence
- SQL Warehouse TLS debug function output
- whether Python `ssl` can load the cert chain locally

### Ciphertext returned instead of plaintext

Meaning:

- fallback may still be enabled
- or reveal failed and was masked

Check:

- `RETURNCIPHERTEXTFORUSERWITHNOKEYACCESS`
- `returnciphertextforuserwithnokeyaccess`
- CRDP audit log status

## Related docs

- [CRDP_TLS_SETUP_CHECKLIST.md](E:\eclipse-workspace\thales.databricks.udf\docs\CRDP_TLS_SETUP_CHECKLIST.md)
- [CONFIG_HARDENING_PHASES.md](E:\eclipse-workspace\thales.databricks.udf\docs\CONFIG_HARDENING_PHASES.md)
- [SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md)
- [SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md)
- [COMPUTE_CLUSTER_DEPLOYMENT_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\COMPUTE_CLUSTER_DEPLOYMENT_GUIDE.md)

# CRDP TLS Setup Checklist

This checklist explains how to set up TLS for Databricks calling Thales CRDP,
including the difference between the CRDP server certificate, the Databricks
client certificate, the CA files, and the PKCS12 file used by the Java UDF
path.

For the runtime-specific deployment split, see
[DATABRICKS_TLS_RUNTIME_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\docs\DATABRICKS_TLS_RUNTIME_GUIDE.md).
This checklist explains certificate roles; the runtime guide explains which TLS
loading model belongs to Java compute clusters, Python compute clusters, and
SQL Warehouse.

## 1. Understand the certificate roles

### CRDP server certificate

This certificate represents the **CRDP HTTPS service**.

Used for:
- CRDP proving its identity to Databricks or any other HTTPS client
- enabling encrypted HTTPS traffic to the CRDP endpoint
- hostname verification when `CRDP_SSL_VERIFY_SERVER=true`

Recommended server certificate identity:
- `CN=mycrdp.something.com`
- DNS SAN includes `mycrdp.something.com`

If clients may also connect by IP:
- include the IP in the certificate SAN as an IP address

### Databricks client certificate

This certificate represents the **Databricks caller**.

Used for:
- Databricks proving its identity to CRDP in mutual TLS mode

Recommended client certificate identity:
- `CN=databricks-crdp-client`

Notes:
- the client certificate CN does **not** need to match `CRDPIP`
- the client certificate usually does not need DNS or IP SAN entries unless
  your PKI policy requires them

### Trusted CA on the CRDP container

This is the CA CRDP uses to trust **client certificates** presented by
Databricks.

CRDP startup example:

```bash
-e TRUSTED_CA="<trusted ca>"
```

### CA file on the Databricks side

This is the CA Databricks uses to trust the **CRDP server certificate**.

Databricks config:

```properties
CRDP_CA_CERT_PATH=/tmp/thales_config/crdp-ca.pem
```

## 2. Understand `tls-cert` vs `tls-cert-opt`

Based on the CRDP startup naming:

### `SERVER_MODE=tls-cert`

Most likely means:
- HTTPS enabled
- CRDP presents a server certificate
- client certificate authentication is required

This is the strict mutual TLS mode.

### `SERVER_MODE=tls-cert-opt`

Most likely means:
- HTTPS enabled
- CRDP presents a server certificate
- client certificate authentication is optional

This is a compatibility or migration mode where some clients may connect
without a client certificate.

## 3. Create the CRDP server certificate

If Databricks will connect using:

```properties
CRDPIP=mycrdp.something.com
CRDP_SSL_ENABLED=true
CRDP_SSL_VERIFY_SERVER=true
```

then create the CRDP server certificate like this:

- Common Name:
  - `mycrdp.something.com`
- DNS Names:
  - `mycrdp.something.com`
- IP Addresses:
  - add the CRDP IP only if you also want IP-based validation support

Important:
- in the Thales certificate UI, do **not** type `DNS:` or `IP:`
- enter the raw hostname in the DNS field
- enter the raw IP in the IP field

Example in the Thales UI:
- Common Name: `mycrdp.something.com`
- DNS Names: `mycrdp.something.com`
- IP Addresses: `129.134.111.1`

## 4. Create the Databricks client certificate

Create a client certificate for Databricks with a meaningful identity, such as:

- Common Name: `databricks-crdp-client`

Recommended notes:
- RSA is the safer compatibility-first choice if that matches your CRDP
  certificate guidance
- the client CN can be any meaningful caller identity
- it does not need to match a host name or IP

## 5. Export the Databricks client certificate and key

You will typically need:

- `crdpuserCertificate.pem`
- `crdpuserkey.pem`

If your PKI has intermediate CAs, also gather:

- `ca-chain.pem`

## 6. Build the PKCS12 file for Databricks

### Simplest command

```bash
openssl pkcs12 -export \
  -out crdp-client.p12 \
  -inkey crdpuserkey.pem \
  -in crdpuserCertificate.pem
```

### With a friendly alias

```bash
openssl pkcs12 -export \
  -out crdp-client.p12 \
  -inkey crdpuserkey.pem \
  -in crdpuserCertificate.pem \
  -name "databricks-crdp-client"
```

### Recommended form with CA chain

```bash
openssl pkcs12 -export \
  -out crdp-client.p12 \
  -inkey crdpuserkey.pem \
  -in crdpuserCertificate.pem \
  -certfile ca-chain.pem \
  -name "databricks-crdp-client"
```

### With an explicit password

```bash
openssl pkcs12 -export \
  -out crdp-client.p12 \
  -inkey crdpuserkey.pem \
  -in crdpuserCertificate.pem \
  -certfile ca-chain.pem \
  -name "databricks-crdp-client" \
  -passout pass:changeit
```

Recommendation:
- include the CA chain if the client certificate is issued by an intermediate CA
- this is not always strictly required, but it is usually the safer and more
  portable choice

## 7. Verify the PKCS12 file

### Verify with OpenSSL

```bash
openssl pkcs12 -info -in crdp-client.p12
```

Show only the client certificate and not the keys:

```bash
openssl pkcs12 -in crdp-client.p12 -clcerts -nokeys
```

### Verify with keytool

This is also a useful way to inspect the PKCS12 contents:

```bash
keytool -list -storetype PKCS12 -keystore crdp-client.p12
```

For a more detailed view, including certificate-chain information when present:

```bash
keytool -list -v -storetype PKCS12 -keystore crdp-client.p12
```

## 8. Prepare the CA files

### `crdp-ca.pem`

This file is used by Databricks to trust the **CRDP server certificate**.

It can be either:
- a single self-signed or trusted CA certificate
- or a PEM CA bundle / chain file when CRDP presents a certificate chain
  rooted in a private root or intermediate CA

Use it here:

```properties
CRDP_CA_CERT_PATH=/tmp/thales_config/crdp-ca.pem
```

### `TRUSTED_CA`

This is provided to the CRDP container and is used by CRDP to trust the
**Databricks client certificate**.

Use the CA or CA chain that issued the Databricks client cert.

## 9. Configure the CRDP container

Example strict mTLS startup:

```bash
docker run \
  -e KEY_MANAGER_HOST=<IP address or host name> \
  -e REGISTRATION_TOKEN=<registration token> \
  -p <host port>:8090 \
  -p <probes port>:8080 \
  -e SERVER_MODE=tls-cert \
  -e CERT_VALUE="<certificate value>" \
  -e KEY_VALUE="<key value>" \
  -e TRUSTED_CA="<trusted ca>" \
  <crdp image name>
```

Meaning:
- `CERT_VALUE` = CRDP server certificate
- `KEY_VALUE` = CRDP server private key
- `TRUSTED_CA` = CA CRDP uses to trust Databricks client certificates

## 10. Put the Databricks runtime files in the Unity Catalog volume

Place these files in:

- `/Volumes/my_catalog/my_schema/volume_forjars`

Files:
- `udfConfig.properties`
- `crdp-client.p12`
- `crdp-ca.pem`
- `databricks-crdp-client-cert.pem`
- `databricks-crdp-client-key.pem`

The cluster init script copies them to:

- `/tmp/thales_config`

## 11. Configure Databricks runtime properties

Example:

```properties
CRDPIP=mycrdp.something.com
CRDPPORT=444
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

For the Python wheel path, use PEM certificate and key files instead:

```properties
CRDPIP=mycrdp.something.com
CRDPPORT=444
CRDP_SSL_ENABLED=true
CRDP_SSL_VERIFY_SERVER=true
CRDP_CA_CERT_PATH=/tmp/thales_config/crdp-ca.pem
CRDP_CLIENT_CERT_PATH=/tmp/thales_config/databricks-crdp-client-cert.pem
CRDP_CLIENT_KEY_PATH=/tmp/thales_config/databricks-crdp-client-key.pem
CRDP_CONNECT_TIMEOUT_MS=10000
CRDP_READ_TIMEOUT_MS=30000
```

Important:
- if `CRDPIP` does not include `https://`, the Java client will use HTTPS when
  `CRDP_SSL_ENABLED=true`
- if `CRDP_SSL_VERIFY_SERVER=true`, the CRDP server certificate must match the
  host value used in `CRDPIP`

## 12. First connection test

Start with:
- one simple protect or reveal request
- low concurrency
- strict verification first if possible

If needed for temporary bring-up only:

```properties
CRDP_SSL_VERIFY_SERVER=false
```

This disables server certificate and hostname verification in the Java client
and should be used only for non-production testing.

## 13. Performance note

The Java Databricks CRDP client uses a shared pooled `OkHttpClient`.

That means:
- HTTPS connections can be reused with keep-alive
- the full TLS handshake should not happen on every request
- after the initial connection, ongoing request overhead should be much lower

This is especially important for bulk API throughput.

The Python Databricks wheel now uses a shared pooled `requests.Session()`.

That means:
- HTTPS connections can be reused with keep-alive
- the full TLS handshake should not happen on every request
- the Python path now behaves more like the Java path from a connection-reuse perspective

## 14. Troubleshooting certificate contents

If `keytool -list -storetype PKCS12 -keystore crdp-client.p12` only shows a
single `PrivateKeyEntry`, that does not necessarily mean the CA chain is
missing. It just means the short listing is terse.

Use these commands to inspect the contents more deeply.

### Show detailed PKCS12 entry information with keytool

```bash
keytool -list -v -storetype PKCS12 -keystore crdp-client.p12
```

Look for:
- certificate chain length
- subject and issuer values
- validity dates
- fingerprints

### Show all certificates and keys in the PKCS12 with OpenSSL

```bash
openssl pkcs12 -in crdp-client.p12 -nodes
```

Use this only in a secure environment because it prints the private key too.

### Show all certificates without exposing the private key

```bash
openssl pkcs12 -in crdp-client.p12 -nokeys
```

### Show only the client certificate

```bash
openssl pkcs12 -in crdp-client.p12 -clcerts -nokeys
```

### Show only CA certificates included in the PKCS12

```bash
openssl pkcs12 -in crdp-client.p12 -cacerts -nokeys
```

These commands are useful for verifying whether:
- the client certificate is present
- the intermediate CA chain is present
- the root CA is present

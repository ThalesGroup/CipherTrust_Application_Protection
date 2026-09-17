# Thales CRDP Server Modes on Snowpark Container Services

This is the consolidated deployment guide for the Spring Boot UDF service and
CipherTrust RESTful Data Protection (CRDP) on Snowpark Container Services.

| CRDP `SERVER_MODE` | UDF-to-CRDP transport | Client certificate |
| --- | --- | --- |
| `no-tls` | HTTP | Not required |
| `tls-cert-opt` | HTTPS, server-authenticated TLS | Not required |
| `tls-cert` | HTTPS, mutual TLS | Required |

The examples use Snowflake `GENERIC_STRING` secrets. Keep registration tokens,
private keys, PEM content, PKCS#12 data, and passwords out of Dockerfiles,
images, and service-spec `env:` values.

## Common architecture and configuration

- `thales_udf_service` runs this Spring Boot application. Its service-function
  endpoint remains port `8083`; `EXPOSE 8083` in its Dockerfile is correct in
  all modes.
- `thales_backend_service` runs CRDP on private port `8090`.
- `CRDP_PORT=8090` is an outbound UDF-client setting. It does not expose port
  `8090` in the UDF image.
- Use the backend's internal DNS name as the bare `CRDP_HOST` value. Retrieve
  it with `DESC SERVICE thales_backend_service` or
  `SELECT SYSTEM$GET_SERVICE_DNS_DOMAIN('SF_TUTS.PUBLIC')`.
- Do not use legacy `CRDPIP` in the Dockerfile or service spec. The application
  derives the scheme from `CRDP_SSL_ENABLED` when `CRDP_HOST` is a bare name.

```text
CRDP_SSL_ENABLED=false -> http://<CRDP_HOST>:8090/v1/
CRDP_SSL_ENABLED=true  -> https://<CRDP_HOST>:8090/v1/
```

Do not combine `CRDP_SSL_ENABLED=true` with `CRDPIP=http://...`. That sends
plaintext HTTP to a TLS listener and causes the CRDP error response beginning
with `Client`, rather than JSON.

Keep `APP_INPUT_FORMAT=external`. This application uses Snowflake's compatible
external-function request and response envelope for SPCS service functions.

## Environment variable reference

The application has two configuration paths. This distinction explains why
some variables appear in `application.properties` and others appear directly
in `SnowflakeCRDPController`.

### Spring-bound CRDP connection settings

`application.properties` maps environment variables to `crdp.*` properties;
Spring Boot then binds them to `CrdpProperties` because that class is annotated
with `@ConfigurationProperties(prefix = "crdp")`.

| Environment variable | Spring property | Purpose | Default |
| --- | --- | --- | --- |
| `CRDP_HOST` | `crdp.host` | CRDP hostname; use a bare internal DNS name | legacy `CRDPIP`, then built-in hostname |
| `CRDP_PORT` | `crdp.port` | CRDP listener port | legacy `CRDPIPPORT`/`CRDPPORT`, then `8090` |
| `CRDP_SSL_ENABLED` | `crdp.ssl.enabled` | Chooses HTTP or HTTPS for a bare host | `false` |
| `CRDP_SSL_VERIFY_SERVER` | `crdp.ssl.verify-server` | Validates CRDP certificate chain and hostname | `true` |
| `CRDP_CA_CERT_PATH` | `crdp.ssl.ca-cert-path` | PEM CA bundle file for server validation | empty |
| `CRDP_SSL_TRUST_STORE_PATH` | `crdp.ssl.trust-store-path` | Optional JKS/PKCS12 truststore alternative | empty |
| `CRDP_CLIENT_PKCS12_PATH` | `crdp.ssl.client-pkcs12-path` | Client PKCS#12 file for mTLS | empty |
| `CRDP_CLIENT_PKCS12_B64_FILE` | `crdp.ssl.client-pkcs12-b64-file` | File containing base64 PKCS#12 for mTLS | empty |
| `CRDP_CLIENT_PKCS12_PASSWORD_FILE` | `crdp.ssl.client-pkcs12-password-file` | File containing P12 password | empty |

`CRDP_HOST` and `CRDP_PORT` are therefore supported even though they are not
read using `System.getenv()` in the controller. The `${CRDP_HOST:...}` and
`${CRDP_PORT:...}` placeholders in `application.properties` perform that
environment lookup before Spring binds `CrdpProperties`.

### Direct controller defaults

The following are read directly through `System.getenv()` in
`SnowflakeCRDPController`. They control request routing and policy selection,
not the network/TLS connection.

| Environment variable | Purpose | Default |
| --- | --- | --- |
| `BATCHSIZE` | Maximum values processed in a CRDP request batch | `1000` |
| `BADDATATAG` | Fallback value returned for invalid CRDP result shape | `999999999` |
| `DEFAULTREVEALUSER` | Reveal-user fallback if Snowflake user context is unavailable | `admin` |
| `DEFAULTMETADATA` | External-policy `external_version` fallback | `1001000` |
| `DEFAULTMODE` | Default `internal` or `external` policy mode | `external` |
| `DEFAULTCHARPOLICY` | Default character policy | `char-internal` |
| `DEFAULTNBRCHARPOLICY` | Default numeric-character policy | `nbr-char-internal` |
| `DEFAULTNBRNBRPOLICY` | Default numeric policy | `nbr-nbr-internal` |
| `DEFAULTINTERNALCHARPOLICY`, `DEFAULTINTERNALNBRCHARPOLICY`, `DEFAULTINTERNALNBRNBRPOLICY` | Explicit internal policy names | respective `*-internal` values |
| `DEFAULTEXTERNALCHARPOLICY`, `DEFAULTEXTERNALNBRCHARPOLICY`, `DEFAULTEXTERNALNBRNBRPOLICY` | Explicit external policy names | respective `*-external` values |
| `PORT` | Spring Boot UDF listener port through `server.port` | `8083` |
| `APP_INPUT_FORMAT` | Spring property override for the service-function envelope | `external` |

Use `CRDP_HOST`, `CRDP_PORT`, and the TLS variables for every new deployment.
`CRDPIP`, `CRDPIPPORT`, and `CRDPPORT` are legacy fallback names only.

## Create shared Snowflake secrets

Preserve `BEGIN`/`END` lines and line breaks in PEM values. Do not base64-encode
the PEM supplied to CRDP as `CERT_VALUE`, `KEY_VALUE`, or `TRUSTED_CA`.

```sql
CREATE OR REPLACE SECRET SF_TUTS.PUBLIC.CRDP_REGISTRATION_TOKEN_SECRET
  TYPE = GENERIC_STRING
  SECRET_STRING = '<CRDP registration token>';

CREATE OR REPLACE SECRET SF_TUTS.PUBLIC.CRDP_SERVER_CERT_SECRET
  TYPE = GENERIC_STRING
  SECRET_STRING = '<server certificate PEM>';

CREATE OR REPLACE SECRET SF_TUTS.PUBLIC.CRDP_SERVER_KEY_SECRET
  TYPE = GENERIC_STRING
  SECRET_STRING = '<server private key PEM>';

CREATE OR REPLACE SECRET SF_TUTS.PUBLIC.CRDP_TRUST_MATERIAL
  TYPE = GENERIC_STRING
  SECRET_STRING = '<CA PEM or CA-chain PEM>';
```

`CRDP_TRUST_MATERIAL` is a CA trust bundle, containing its issuing root and
any intermediate CA certificates. It is not the CRDP server leaf certificate.
When mounted using `directoryPath`, Snowflake exposes its content at a file
named `secret_string` beneath that directory.

```yaml
secrets:
  - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_TRUST_MATERIAL
    directoryPath: "/etc/ssl/certs/crdp-trust"
```

The Java property for that secret is:

```yaml
CRDP_CA_CERT_PATH: "/etc/ssl/certs/crdp-trust/secret_string"
```

## 1. `SERVER_MODE: "no-tls"`

Use only for isolated proof-of-concept work or when plaintext internal traffic
is explicitly approved. This is not the preferred production mode.

### CRDP backend

```sql
CREATE OR REPLACE SERVICE thales_backend_service
  IN COMPUTE POOL my_compute_pool
  FROM SPECIFICATION $$
spec:
  containers:
    - name: ciphertrust-service
      image: /sf_tuts/public/my_backend_repo/ciphertrust-restful-data-protection:1.2.1
      env:
        KEY_MANAGER_HOST: "ciphertrust.manager.com"
        SERVER_MODE: "no-tls"
      secrets:
        - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_REGISTRATION_TOKEN_SECRET
          envVarName: REGISTRATION_TOKEN
          secretKeyRef: secret_string
  endpoints:
    - name: backendendpoint
      port: 8090
      protocol: HTTP
      public: false
$$
  EXTERNAL_ACCESS_INTEGRATIONS = (thales_access_integration)
  MIN_INSTANCES = 1
  MAX_INSTANCES = 1;
```

### UDF service

```yaml
env:
  PORT: "8083"
  APP_INPUT_FORMAT: "external"
  CRDP_HOST: "thales-backend-service.yourhashcode.svc.spcs.internal"
  CRDP_PORT: "8090"
  CRDP_SSL_ENABLED: "false"
  CRDP_SSL_VERIFY_SERVER: "false"
  DEFAULTMODE: "internal"
  DEFAULTMETADATA: "1001000"
```

Use the normal private UDF endpoint on port `8083`. The UDF service does not
need an external access integration to call internal CRDP; CRDP may need one
to reach an external CipherTrust Manager.

## 2. `SERVER_MODE: "tls-cert-opt"`

This is server-authenticated TLS. CRDP presents a server certificate and the
UDF validates its CA chain and hostname. A client PKCS#12 is not used.

### CRDP backend

```sql
CREATE OR REPLACE SERVICE thales_backend_service
  IN COMPUTE POOL my_compute_pool
  FROM SPECIFICATION $$
spec:
  containers:
    - name: ciphertrust-service
      image: /sf_tuts/public/my_backend_repo/ciphertrust-restful-data-protection:1.2.1
      env:
        KEY_MANAGER_HOST: "ciphertrust.manager.com"
        SERVER_MODE: "tls-cert-opt"
      secrets:
        - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_REGISTRATION_TOKEN_SECRET
          envVarName: REGISTRATION_TOKEN
          secretKeyRef: secret_string
        - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_SERVER_CERT_SECRET
          envVarName: CERT_VALUE
          secretKeyRef: secret_string
        - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_SERVER_KEY_SECRET
          envVarName: KEY_VALUE
          secretKeyRef: secret_string
  endpoints:
    - name: backendendpoint
      port: 8090
      protocol: TCP
      public: false
$$
  EXTERNAL_ACCESS_INTEGRATIONS = (thales_access_integration)
  MIN_INSTANCES = 1
  MAX_INSTANCES = 1;
```

SPCS declares `TCP`; CRDP itself terminates TLS. The server certificate SAN
must include the exact `CRDP_HOST`, such as
`DNS:thales-backend-service.yourhashcode.svc.spcs.internal`.

### UDF service

```yaml
env:
  PORT: "8083"
  APP_INPUT_FORMAT: "external"
  CRDP_HOST: "thales-backend-service.yourhashcode.svc.spcs.internal"
  CRDP_PORT: "8090"
  CRDP_SSL_ENABLED: "true"
  CRDP_SSL_VERIFY_SERVER: "true"
  CRDP_CA_CERT_PATH: "/etc/ssl/certs/crdp-trust/secret_string"
  BATCHSIZE: "1000"
  DEFAULTMETADATA: "1001000"
  DEFAULTMODE: "internal"
secrets:
  - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_TRUST_MATERIAL
    directoryPath: "/etc/ssl/certs/crdp-trust"
```

For initial diagnosis, `CRDP_SSL_VERIFY_SERVER=false` still uses TLS but skips
certificate and hostname verification. Do not leave it disabled in production.

## 3. `SERVER_MODE: "tls-cert"` (mutual TLS)

This adds client authentication. CRDP validates the certificate presented by
the UDF, and the UDF validates the CRDP server. `TRUSTED_CA` must trust the
client-certificate issuer. If the same CA issued server and client certificates,
reuse `CRDP_TRUST_MATERIAL` for both roles.

### Create and validate the client PKCS#12

Use a nonblank password. The alias is a label and does not need to match the
certificate CN.

```bash
openssl pkcs12 -export \
  -out crdp-client.p12 \
  -inkey client.key \
  -in client.crt \
  -certfile ca.crt \
  -name crdp-client

openssl pkcs12 -info -in crdp-client.p12 -noout
```

Base64 encode the whole binary P12 file, not a PEM body:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("crdp-client.p12")) |
  Set-Content -NoNewline "crdp-client.p12.b64"
```

```sql
CREATE OR REPLACE SECRET SF_TUTS.PUBLIC.CRDP_CLIENT_P12_B64_SECRET
  TYPE = GENERIC_STRING
  SECRET_STRING = '<single-line base64 of crdp-client.p12>';

CREATE OR REPLACE SECRET SF_TUTS.PUBLIC.CRDP_CLIENT_P12_PASSWORD_SECRET
  TYPE = GENERIC_STRING
  SECRET_STRING = '<PKCS#12 password>';
```

The client certificate should have `CA:FALSE`, `digitalSignature`, and
`clientAuth` extended key usage. RSA 2048 with SHA-256 is a conservative
compatibility choice. The client certificate does not need the CRDP DNS name;
the server certificate does.

### CRDP backend differences from `tls-cert-opt`

Add `TRUSTED_CA` and change the server mode:

```yaml
env:
  KEY_MANAGER_HOST: "ciphertrust.manager.com"
  SERVER_MODE: "tls-cert"
secrets:
  - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_REGISTRATION_TOKEN_SECRET
    envVarName: REGISTRATION_TOKEN
    secretKeyRef: secret_string
  - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_SERVER_CERT_SECRET
    envVarName: CERT_VALUE
    secretKeyRef: secret_string
  - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_SERVER_KEY_SECRET
    envVarName: KEY_VALUE
    secretKeyRef: secret_string
  - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_TRUST_MATERIAL
    envVarName: TRUSTED_CA
    secretKeyRef: secret_string
```

Keep its private endpoint as `protocol: TCP`, port `8090`.

### UDF service differences from `tls-cert-opt`

Keep the CA trust mount and add the P12 and password secret mounts:

```yaml
env:
  CRDP_SSL_ENABLED: "true"
  CRDP_SSL_VERIFY_SERVER: "true"
  CRDP_CA_CERT_PATH: "/etc/ssl/certs/crdp-trust/secret_string"
  CRDP_CLIENT_PKCS12_B64_FILE: "/etc/ssl/certs/crdp-client-p12/secret_string"
  CRDP_CLIENT_PKCS12_PASSWORD_FILE: "/etc/ssl/certs/crdp-client-p12-password/secret_string"
secrets:
  - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_TRUST_MATERIAL
    directoryPath: "/etc/ssl/certs/crdp-trust"
  - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_CLIENT_P12_B64_SECRET
    directoryPath: "/etc/ssl/certs/crdp-client-p12"
  - snowflakeSecret: SF_TUTS.PUBLIC.CRDP_CLIENT_P12_PASSWORD_SECRET
    directoryPath: "/etc/ssl/certs/crdp-client-p12-password"
```

## Validate and troubleshoot

```sql
DESC SERVICE thales_backend_service;
DESC SERVICE thales_udf_service;
SHOW ENDPOINTS IN SERVICE thales_backend_service;
```

Check UDF service logs for the resolved base URL:

```text
baseUrl: https://thales-backend-service.<domain>:8090/v1/
```

`http://` is expected only in `no-tls`. If `tls-cert-opt` works with
verification disabled but fails with it enabled, validate the CA bundle,
certificate chain and expiration, and the server SAN. If mTLS then fails,
validate the P12 password, client chain, `clientAuth` EKU, and `TRUSTED_CA`.

For external policies, the one-argument service functions cannot inspect
sibling table header columns. If no metadata request header is supplied, the
application sends `DEFAULTMETADATA`, for example `1001000`, as CRDP
`external_version` and logs that choice.

## Operational guidance

- Use `CRDP_SSL_VERIFY_SERVER=true` for production TLS.
- Rotate secrets through the approved secret process and redeploy or restart
  the UDF service; its shared TLS client loads trust and identity material at
  JVM startup.
- Use immutable image tags for releases instead of relying on `latest`.
- Do not log private keys, PEM values, P12 data, passwords, tokens, or
  plaintext protected/revealed values.

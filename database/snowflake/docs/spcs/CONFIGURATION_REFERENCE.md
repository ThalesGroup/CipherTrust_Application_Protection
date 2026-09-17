# Configuration Reference

This document lists the environment variables supported by the UDF service.
Use `CRDP_HOST` and `CRDP_PORT` for new deployments; older names are fallback
compatibility options only.

## Connection and TLS Settings

These values are read by Spring Boot from `application.properties`, bound to
`CrdpProperties`, and used by the shared OkHttp client.

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `8083` | Spring Boot UDF listener port. |
| `CRDP_HOST` | legacy `CRDPIP`, then built-in hostname | Bare CRDP DNS name recommended. |
| `CRDP_PORT` | legacy `CRDPIPPORT`/`CRDPPORT`, then `8090` | CRDP listener port. |
| `CRDP_SSL_ENABLED` | `false` | Uses HTTPS for a bare host when `true`; HTTP when `false`. |
| `CRDP_SSL_VERIFY_SERVER` | `true` | Validates CRDP chain and hostname. Set `false` only for diagnosis. |
| `CRDP_CA_CERT_PATH` | empty | PEM CA bundle file path. |
| `CRDP_SSL_TRUST_STORE_PATH` | empty | Optional truststore alternative to CA PEM. |
| `CRDP_SSL_TRUST_STORE_TYPE` | `JKS` | Truststore type. |
| `CRDP_SSL_TRUST_STORE_PASSWORD` | empty | Truststore password; prefer its file alternative. |
| `CRDP_SSL_TRUST_STORE_PASSWORD_FILE` | empty | File containing truststore password. |
| `CRDP_CLIENT_PKCS12_PATH` | empty | Client PKCS#12 file for mTLS. |
| `CRDP_CLIENT_PKCS12_B64` | empty | Base64 PKCS#12 string; avoid using plaintext environment values. |
| `CRDP_CLIENT_PKCS12_B64_FILE` | empty | File containing base64 PKCS#12 data. |
| `CRDP_CLIENT_PKCS12_PASSWORD` | empty | P12 password; prefer its file alternative. |
| `CRDP_CLIENT_PKCS12_PASSWORD_FILE` | empty | File containing P12 password. |
| `CRDP_CONNECT_TIMEOUT_MS` | `10000` | CRDP connection timeout in milliseconds. |
| `CRDP_READ_TIMEOUT_MS` | `30000` | CRDP read timeout in milliseconds. |
| `CRDP_WRITE_TIMEOUT_MS` | `30000` | CRDP write timeout in milliseconds. |
| `CRDP_HTTP_MAX_IDLE_CONNECTIONS` | `20` | Maximum pooled idle CRDP connections. |
| `CRDP_HTTP_KEEPALIVE_MINUTES` | `5` | Idle connection keepalive duration. |
| `APP_INPUT_FORMAT` | `external` | Service-function request/response envelope. Keep `external`. |

### Legacy connection-variable compatibility

| Variable | Recommendation | Behavior |
| --- | --- | --- |
| `CRDPIP` | Do not use for new deployments. | Legacy fallback for `CRDP_HOST`. It is a hostname or complete URL, not an IP address. If it is a URL, it must include `:8090` and use the same HTTP/HTTPS scheme as `CRDP_SSL_ENABLED`. |
| `CRDPIPPORT` | Do not use for new deployments. | Legacy fallback for `CRDP_PORT`. |
| `CRDPPORT` | Do not use for new deployments. | Older legacy fallback for `CRDP_PORT`. |

An explicitly supplied `http://` or `https://` URL must agree with
`CRDP_SSL_ENABLED`. New deployments should use a bare hostname to avoid this
ambiguity. Do not configure both `CRDP_CA_CERT_PATH` and
`CRDP_SSL_TRUST_STORE_PATH`.

## Policy and Request Routing Settings

These values are read directly through `System.getenv()` in
`SnowflakeCRDPController`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `BATCHSIZE` | `1000` | Maximum input values grouped into one CRDP bulk API request. This is separate from Snowflake function `MAX_BATCH_ROWS`. |
| `BADDATATAG` | `999999999` | Fallback returned when CRDP returns a missing or unexpected result-array shape. It is not a general CRDP error code. |
| `DEFAULTREVEALUSER` | `admin` | Fallback reveal user only when Snowflake does not provide `sf-context-current-user`. |
| `DEFAULTMETADATA` | `1001000` | `external_version` sent for current one-argument external-policy reveal calls. |
| `DEFAULTMODE` | `external` | Default policy mode when no mode is supplied. Set `internal` or `external` explicitly in each service spec. |
| `DEFAULTCHARPOLICY` | `char-internal` | Fallback character policy when the mode is not recognized. |
| `DEFAULTNBRCHARPOLICY` | `nbr-char-internal` | Fallback number-character policy when the mode is not recognized. |
| `DEFAULTNBRNBRPOLICY` | `nbr-nbr-internal` | Fallback number-number policy when the mode is not recognized. |
| `DEFAULTINTERNALCHARPOLICY` | `char-internal` | Character policy selected for internal mode. |
| `DEFAULTINTERNALNBRCHARPOLICY` | `nbr-char-internal` | Number-character policy selected for internal mode. |
| `DEFAULTINTERNALNBRNBRPOLICY` | `nbr-nbr-internal` | Number-number policy selected for internal mode. |
| `DEFAULTEXTERNALCHARPOLICY` | `char-external` | Character policy selected for external mode. |
| `DEFAULTEXTERNALNBRCHARPOLICY` | `nbr-char-external` | Number-character policy selected for external mode. |
| `DEFAULTEXTERNALNBRNBRPOLICY` | `nbr-nbr-external` | Number-number policy selected for external mode. |

## Current External-Policy Behavior

When `DEFAULTMODE=external`, the controller selects the configured external
policy for the endpoint data type and supplies CRDP with an `external_version`.
For example, `THALES_CRDP_SCS_REVEALBULK_CHAR(EMAIL)` uses the configured
external character policy.

For the current one-argument SPCS service functions, set `DEFAULTMETADATA` on
the UDF service to the external-policy `external_version` required by CRDP.
For example, `THALES_CRDP_SCS_REVEALBULK_CHAR(EMAIL)` uses the configured
external character policy and sends the service's `DEFAULTMETADATA` value as
the CRDP `external_version`.

SPCS service-function DDL supports Snowflake `CONTEXT_HEADERS` such as
`CURRENT_USER`, but it does not support arbitrary static `HEADERS`. Therefore,
the current SQL integration does not use a custom `metadata` HTTP header.

## CRDP Backend Container Settings

These variables belong to `thales_backend_service`, not the Java UDF service.
Secret values should use Snowflake `secrets:` mappings rather than plaintext
values in `env:`.

| Variable | Required for | Purpose |
| --- | --- | --- |
| `KEY_MANAGER_HOST` | All CRDP modes | CipherTrust Manager hostname or address. |
| `REGISTRATION_TOKEN` | All CRDP modes | CRDP registration token; inject from a Snowflake secret. |
| `SERVER_MODE` | All CRDP modes | CRDP listener mode: `no-tls`, `tls-cert-opt`, or `tls-cert`. |
| `CERT_VALUE` | `tls-cert-opt`, `tls-cert` | CRDP server certificate PEM; inject from a secret. |
| `KEY_VALUE` | `tls-cert-opt`, `tls-cert` | CRDP server private-key PEM; inject from a secret. |
| `TRUSTED_CA` | `tls-cert` | CA PEM/chain trusted by CRDP for client certificate validation; inject from a secret. |


## Secret Handling

Use Snowflake secrets with `directoryPath` for CA PEM, P12 base64, and password
files; reference the mounted `secret_string` file in the corresponding path
variable. Use `envVarName` plus `secretKeyRef: secret_string` only when the
CRDP container needs its secret as an environment variable, such as
`REGISTRATION_TOKEN`, `CERT_VALUE`, `KEY_VALUE`, or `TRUSTED_CA`.

See [SPCS_CRDP_SERVER_MODES_DEPLOYMENT.md](SPCS_CRDP_SERVER_MODES_DEPLOYMENT.md)
for complete secret and certificate examples.

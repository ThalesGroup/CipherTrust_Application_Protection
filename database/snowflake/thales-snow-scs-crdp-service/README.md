# Snowflake CRDP Service: Thales CipherTrust Integration

This project provides a Java 17 Spring Boot application that protects and
reveals sensitive Snowflake data through Thales CipherTrust RESTful Data
Protection (CRDP). It runs within Snowpark Container Services (SPCS) and
exposes CRDP protect and reveal operations as a private web service for
Snowflake service functions.

The service supports bulk operations for three CRDP data types: `character`,
`number-character`, and `number-number`. It is designed to keep the Snowflake
SQL integration, CRDP policy routing, and optional TLS configuration in one
containerized service pattern.

## Prerequisites

- Java 17 or later.
- Maven.
- Docker for image creation.
- CipherTrust Manager with CRDP enabled and appropriate protection policies.
- A Snowflake account and role authorized to create image repositories, compute
  pools, services, service functions, secrets, and required grants.

## What It Does

```text
Snowflake SQL service function
  -> Spring Boot UDF service (port 8083)
  -> Thales CRDP service (port 8090)
  -> CipherTrust Manager for policy and key management
```

## Capabilities

- Bulk protect and reveal for character, number-character, and number-number data.
- Internal/external policy routing and configurable policy names.
- External-policy metadata fallback through `DEFAULTMETADATA`.
- Snowflake current-user context forwarded to CRDP during reveals.
- HTTP, server-authenticated TLS, and mutual TLS to CRDP.
- CA PEM, optional truststore, and PKCS#12 client identity support.
- Configurable batching, timeouts, and pooled HTTP connections.
- Safe route diagnostics that identify policy and metadata source without
  logging protected or revealed values.
- Snowflake current-user context forwarded from the
  `sf-context-current-user` request header for reveal operations.

## REST Endpoints

| Data type | Protect | Reveal |
| --- | --- | --- |
| Character | `POST /protectbulkchar` | `POST /revealbulkchar` |
| Number-character | `POST /protectbulknbrchar` | `POST /revealbulknbrchar` |
| Number-number | `POST /protectbulknbrnbr` | `POST /revealbulknbrnbr` |

## Build

```powershell
mvn -DskipTests package
Copy-Item target\thales-snow-scs-crdp-service-0.0.1-SNAPSHOT.jar .
docker build -t thales-snow-scs-crdp-service:local .
```

The Dockerfile exposes port `8083` for the UDF service. CRDP port `8090` is a
separate private endpoint, configured by `CRDP_PORT` in the service spec.

## Recommended Connection Configuration

```yaml
PORT: "8083"
CRDP_HOST: "thales-backend-service.yourhashcode.svc.spcs.internal"
CRDP_PORT: "8090"
CRDP_SSL_ENABLED: "true"
CRDP_SSL_VERIFY_SERVER: "true"
CRDP_CA_CERT_PATH: "/etc/ssl/certs/crdp-trust/secret_string"
DEFAULTMODE: "internal"
DEFAULTMETADATA: "1001000"
```

Use a bare `CRDP_HOST` for new deployments. `CRDPIP`, `CRDPIPPORT`, and
`CRDPPORT` are legacy fallbacks. Keep tokens, PEM values, PKCS#12 content, and
passwords in Snowflake secrets, never in image layers or plaintext `env:`.

## Documentation

- [Quick Start](docs/QUICKSTART.md): build, deploy, and test one value.
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md): production deployment,
  service functions, validation, upgrades, and rollback.
- [Configuration Reference](docs/CONFIGURATION_REFERENCE.md): supported
  environment variables, defaults, and secret handling.
- [CRDP Server Modes](docs/SPCS_CRDP_SERVER_MODES_DEPLOYMENT.md): `no-tls`,
  `tls-cert-opt`, and `tls-cert` deployment and certificate guidance.

## Security Boundaries

Snowflake roles control services and service functions. Thales CRDP and
CipherTrust Manager control data-protection policies and cryptographic keys.
Define reveal authorization in both systems, and never log plaintext values,
registration tokens, private keys, certificate bodies, or passwords.

## External Policy Metadata

For a one-argument function such as
`THALES_CRDP_SCS_REVEALBULK_CHAR(EMAIL)`, Snowflake sends only the `EMAIL`
value to this service. The current implementation does not discover or read a
sibling `EMAIL_HEADER` column, and `SELECT *` does not automatically invoke a
protect or reveal function.

When `DEFAULTMODE=external`, the service selects the configured external
policy and sends CRDP an `external_version` using `DEFAULTMETADATA` from the
UDF service environment, such as `1001000`.

SPCS service-function DDL cannot declare arbitrary static HTTP headers. For
the current SQL integration, configure `DEFAULTMETADATA` on the UDF service.

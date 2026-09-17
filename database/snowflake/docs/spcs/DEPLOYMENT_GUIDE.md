# Deployment Guide: Thales CRDP Service on SPCS

This guide describes a production-oriented rollout of the Spring Boot UDF
service and CRDP service. Certificate and TLS mode configuration is maintained
in [SPCS_CRDP_SERVER_MODES_DEPLOYMENT.md](SPCS_CRDP_SERVER_MODES_DEPLOYMENT.md).

## Deployment Sequence

1. Create or select an image repository and compute pool sized for the expected
   UDF and CRDP concurrency.
2. Create Snowflake secrets for the CRDP registration token and, for TLS,
   certificate, key, CA, and optional client PKCS#12 materials.
3. Build, tag, and push an immutable UDF image. Do not promote `latest`.
4. Deploy `thales_backend_service`, confirm CRDP registration and listener
   readiness, then retrieve its internal DNS name using `DESC SERVICE`.
5. Deploy `thales_udf_service` with the backend DNS name in `CRDP_HOST`.
6. Create Snowflake service functions using the private `udfendpoint`.
7. Execute protect and reveal smoke tests with non-sensitive test values.
8. Review UDF and CRDP logs, enforce TLS verification, then promote the same
   image and declarative configuration through each environment.

## Responsibilities

| Area | Primary responsibility |
| --- | --- |
| Snowflake roles, image repository, compute pool, services, functions | Snowflake platform team |
| CRDP policy, tokenization/encryption definitions, key lifecycle | Thales security/key-management team |
| Certificate issuance, CA trust, secret rotation, egress allowlist | Shared platform and security ownership |
| Application image, endpoint compatibility, logging, capacity tuning | Application/service owner |

## Service Function DDL

Create functions that match the endpoint data type. Preserve the existing
function signatures if they are already used by queries and views.

```sql
CREATE OR REPLACE FUNCTION SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_CHAR(input VARCHAR)
RETURNS VARCHAR
RETURNS NULL ON NULL INPUT
SERVICE = thales_udf_service
ENDPOINT = udfendpoint
CONTEXT_HEADERS = (CURRENT_USER)
MAX_BATCH_ROWS = 5000
AS '/protectbulkchar';

CREATE OR REPLACE FUNCTION SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR(input VARCHAR)
RETURNS VARCHAR
RETURNS NULL ON NULL INPUT
SERVICE = thales_udf_service
ENDPOINT = udfendpoint
CONTEXT_HEADERS = (CURRENT_USER)
MAX_BATCH_ROWS = 5000
AS '/revealbulkchar';
```

Use `/protectbulknbrchar`, `/revealbulknbrchar`, `/protectbulknbrnbr`, and
`/revealbulknbrnbr` for the other supported types.

## Validation Checklist

```sql
DESC SERVICE thales_backend_service;
DESC SERVICE thales_udf_service;
SHOW ENDPOINTS IN SERVICE thales_backend_service;
SHOW ENDPOINTS IN SERVICE thales_udf_service;
```

- Backend endpoint is private and uses port `8090`.
- TLS backend endpoints use `protocol: TCP`; CRDP terminates TLS.
- UDF endpoint is private and uses port `8083`.
- UDF logs show `https://...:8090/v1/` for TLS or `http://...:8090/v1/` only
  for `no-tls`.
- The server certificate DNS SAN exactly matches `CRDP_HOST` when verification
  is enabled.
- Protect and reveal tests produce the expected CRDP policy behavior.
- Logs do not contain plaintext values, certificates, private keys, or tokens.

## Capacity and Operations

Set `BATCHSIZE`, Snowflake `MAX_BATCH_ROWS`, service instance counts, and
compute-pool capacity from measured throughput and latency. Monitor UDF HTTP
errors, CRDP errors, request latency, service restarts, and compute-pool
utilization. Size the UDF and CRDP services independently.

## Upgrade and Rollback

Publish each build with a new immutable image tag. Deploy the new tag to a
non-production service first, run the validation checklist, then update the
production service. Roll back by redeploying the prior known-good tag and
configuration. Rotate mounted secrets through the approved process and restart
the UDF service because its shared TLS client loads trust and identity material
at JVM startup.

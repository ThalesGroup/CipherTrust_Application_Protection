# Quick Start: Thales CRDP on Snowpark Container Services

Use this guide to validate one UDF-to-CRDP protect call. It assumes CRDP
policies such as `char-external` `char-internal`are already configured in CipherTrust Manager.
For complete TLS instructions, see [CRDP Server Modes](SPCS_CRDP_SERVER_MODES_DEPLOYMENT.md).

## 1. Build the UDF image

```powershell
mvn -DskipTests package
Copy-Item target\thales-snow-scs-crdp-service-0.0.1-SNAPSHOT.jar .
docker build -t thales-snow-scs-crdp-service:quickstart .
```

Tag and push the image to your Snowflake image repository using your approved
repository authentication process.

## 2. Create the registration-token secret

```sql
CREATE OR REPLACE SECRET SF_TUTS.PUBLIC.CRDP_REGISTRATION_TOKEN_SECRET
  TYPE = GENERIC_STRING
  SECRET_STRING = '<CRDP registration token>';
```

## 3. Deploy CRDP in `no-tls` mode

This is the shortest connectivity test. Move to `tls-cert-opt` before
production.

```sql
CREATE OR REPLACE SERVICE thales_backend_service
  IN COMPUTE POOL my_compute_pool
  FROM SPECIFICATION $$
spec:
  containers:
    - name: ciphertrust-service
      image: /sf_tuts/public/my_backend_repo/ciphertrust-restful-data-protection:1.2.1
      env:
        KEY_MANAGER_HOST: "ciphertrust.manager.example"
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

Run `DESC SERVICE thales_backend_service` and copy its internal DNS name.

## 4. Deploy the UDF service

```sql
CREATE OR REPLACE SERVICE thales_udf_service
  IN COMPUTE POOL my_compute_pool
  FROM SPECIFICATION $$
spec:
  containers:
    - name: udf
      image: /sf_tuts/public/my_repo/thales-snow-scs-crdp-service:quickstart
      env:
        PORT: "8083"
        APP_INPUT_FORMAT: "internal"
        CRDP_HOST: "thales-backend-service.yourhashcode.svc.spcs.internal"
        CRDP_PORT: "8090"
        CRDP_SSL_ENABLED: "false"
        CRDP_SSL_VERIFY_SERVER: "false"
        DEFAULTMODE: "internal"
        DEFAULTMETADATA: "1001000"
  endpoints:
    - name: udfendpoint
      port: 8083
      public: false
$$
  MIN_INSTANCES = 1
  MAX_INSTANCES = 1;
```

## 5. Create and call a service function

```sql
CREATE OR REPLACE FUNCTION SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_CHAR(input VARCHAR)
RETURNS VARCHAR
RETURNS NULL ON NULL INPUT
SERVICE = thales_udf_service
ENDPOINT = udfendpoint
CONTEXT_HEADERS = (CURRENT_USER)
MAX_BATCH_ROWS = 5000
AS '/protectbulkchar';

SELECT SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_CHAR('quickstart-test');
```

Create a corresponding reveal function with `AS '/revealbulkchar'` and test the
returned protected value. Confirm the UDF logs show the expected HTTP base URL
and policy routing.

## Next Step

Deploy `tls-cert-opt` with a CA secret and `CRDP_SSL_VERIFY_SERVER=true`, then
use the [Deployment Guide](DEPLOYMENT_GUIDE.md) for production rollout.

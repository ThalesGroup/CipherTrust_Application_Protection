# Logging Guide

This guide describes the current logging behavior in the active
`thales.databricks.integration` project.

It focuses on:

- what the current Java and Python runtimes emit
- which logging-related settings are active today
- where to look in Databricks when troubleshooting
- how to use the current logging safely during support and operations

## Current Logging Model

The current runtime uses two main logging paths:

- the Java runtime writes operational messages directly to console streams
- the Python helper path uses the standard Python `logging` module

Databricks captures those driver and executor logs through its normal cluster
logging behavior.

Current implementation references:

- Java CRDP runtime:
  [JavaCrdpService.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/service/JavaCrdpService.java:1)
- Java config loader:
  [IntegrationConfig.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/config/IntegrationConfig.java:1)
- Python helper executor logging:
  [executor.py](/E:/codex/work/thales.databricks.integration/src/thales_databricks_integration/executor.py:1)
- runtime diagnostics helper:
  [runtime_diagnostics.py](/E:/codex/work/thales.databricks.integration/notebooks/utils/runtime_diagnostics.py:1)

## What Is Logged Today

### Java runtime

The Java runtime currently emits:

- startup summary information to `stdout`
- reveal fail-open events to `stderr`
- exception text as part of thrown failures
- optional request payload suffixes on some failure paths when payload debug
  logging is enabled

Examples in the code:

- startup summary:
  [JavaCrdpService.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/service/JavaCrdpService.java:478)
- reveal fail-open logging:
  [JavaCrdpService.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/service/JavaCrdpService.java:659)
- payload suffix on failed HTTP or invalid-response paths:
  [JavaCrdpService.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/service/JavaCrdpService.java:443)
  and
  [JavaCrdpService.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/service/JavaCrdpService.java:652)

### Python helper runtime

The Python helper path currently emits:

- reveal fail-open log events through Python `logging`
- request traces and execution summaries returned as structured results rather
  than ordinary log lines
- notebook-visible diagnostics through helper notebooks such as
  `runtime_diagnostics.py`

Example:

- reveal fail-open logger call:
  [executor.py](/E:/codex/work/thales.databricks.integration/src/thales_databricks_integration/executor.py:628)

## Active Logging-Related Settings

### `CRDP_DEBUG_LOG_PAYLOAD`

Purpose:

- controls whether certain Java failure messages append the outbound request
  payload

Current behavior:

- `false`
  request payload is not appended
- `true`
  request payload may be appended to some failure messages

Code path:

- property read:
  [IntegrationConfig.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/config/IntegrationConfig.java:197)
- payload suffix behavior:
  [JavaCrdpService.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/service/JavaCrdpService.java:652)

Important warning:

- when enabled, this may expose request content in logs
- use only for tightly controlled troubleshooting
- do not leave enabled for routine production runs

### `REVEAL_FAIL_OPEN_TO_CIPHERTEXT`

Purpose:

- allows reveal operations to return ciphertext instead of failing hard when a
  reveal exception occurs

Code path:

- property read:
  [IntegrationConfig.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/config/IntegrationConfig.java:228)
- Java fail-open handling:
  [JavaCrdpService.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/service/JavaCrdpService.java:168)
- Python fail-open handling:
  [executor.py](/E:/codex/work/thales.databricks.integration/src/thales_databricks_integration/executor.py:589)

### `REVEAL_FAIL_OPEN_LOG_LEVEL`

Purpose:

- controls the severity label used when fail-open events are logged

Code path:

- property read:
  [IntegrationConfig.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/config/IntegrationConfig.java:231)
- Java fail-open log output:
  [JavaCrdpService.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/service/JavaCrdpService.java:665)
- Python fail-open log output:
  [executor.py](/E:/codex/work/thales.databricks.integration/src/thales_databricks_integration/executor.py:624)

### `CONFIG_VERSION`, `CONFIG_RELEASE_DATE`, `CONFIG_CHANGE_REF`

Purpose:

- add environment/version fingerprints that appear in diagnostics and fail-open
  logs

These are useful for operational traceability and release correlation.


## Where Logs Go

Current behavior is straightforward:

- Java startup and informational console output goes to `stdout`
- Java fail-open messages go to `stderr`
- thrown exceptions surface through Databricks notebook errors, driver logs,
  or executor logs depending on where execution occurred
- Python logger output follows normal Databricks Python logging capture

In practice:

- driver-side actions usually appear in driver logs
- executor-side Java UDF activity appears in executor logs
- Python helper work may surface in notebook output, driver logs, or executor
  logs depending on execution shape

## What Is Safe To Log

Generally safe operational fields include:

- event name
- object name
- logical column name
- policy type
- API version
- transport mode
- batch size
- grouped request sizes
- config version metadata
- coarse success or failure outcome
- exception class and summary

## What Must Be Treated Carefully

Do not casually log:

- plaintext values
- protected tokens
- external header values
- credentials
- full request payloads
- full CRDP response payloads

Important nuance for the current code:

- full or partial response bodies can appear in thrown exception text on some
  error paths
- request payloads can be appended when `CRDP_DEBUG_LOG_PAYLOAD=true`

The current runtime should therefore be treated as:

- operationally useful for troubleshooting
- requiring care when enabling deeper debug behavior

## Databricks Troubleshooting Guidance

For compute-cluster troubleshooting, check:

- driver logs for config-path, startup, and notebook-orchestration issues
- executor logs for distributed Java UDF failures
- notebook stack traces for surfaced exceptions
- runtime diagnostics notebook output when verifying loaded configuration

Good starting points:

- [compute_cluster_java_udf_smoke_test_bulk_reveal.py](/E:/codex/work/thales.databricks.integration/notebooks/smoke_tests/compute_cluster_java_udf_smoke_test_bulk_reveal.py:1)
- [compute_cluster_python_helper_smoke_test.py](/E:/codex/work/thales.databricks.integration/notebooks/smoke_tests/compute_cluster_python_helper_smoke_test.py:1)
- [runtime_diagnostics.py](/E:/codex/work/thales.databricks.integration/notebooks/utils/runtime_diagnostics.py:1)

## Recommended Operational Practice

### Normal runs

Use:

```properties
CRDP_DEBUG_LOG_PAYLOAD=false
REVEAL_FAIL_OPEN_TO_CIPHERTEXT=false
```

Why:

- minimizes exposure of sensitive request details
- keeps failures explicit
- avoids troubleshooting-only verbosity

### Controlled troubleshooting

Use temporarily:

```properties
CRDP_DEBUG_LOG_PAYLOAD=true
```

Why:

- helps inspect the exact request payload for hard-to-diagnose CRDP failures

But:

- use only in a controlled environment
- remove it immediately after troubleshooting
- assume the payload may contain sensitive material

### Fail-open troubleshooting or rollout validation

Use when intentionally testing fail-open behavior:

```properties
REVEAL_FAIL_OPEN_TO_CIPHERTEXT=true
REVEAL_FAIL_OPEN_LOG_LEVEL=ERROR
```

Why:

- lets you validate that reveal requests degrade to ciphertext instead of
  hard-failing
- preserves a clear operational signal in logs

## Splunk And External Routing

The preferred model is:

1. let the runtime emit console or Python logging output
2. let Databricks capture driver and executor logs
3. forward those logs through the customer's normal Databricks log-export path

This keeps logging responsibility aligned with the Databricks platform model.

## Bottom Line

The current project provides operational logging that is useful for support,
troubleshooting, and runtime verification.

The most important active controls today are:

- `CRDP_DEBUG_LOG_PAYLOAD`
- `REVEAL_FAIL_OPEN_TO_CIPHERTEXT`
- `REVEAL_FAIL_OPEN_LOG_LEVEL`
- config version metadata fields used for diagnostics and traceability

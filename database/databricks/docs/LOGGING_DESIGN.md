# Logging Guide

This guide explains how logging works in the Databricks UDF project today, how
to configure it, where to find the logs, and how customers can forward those
logs to external platforms such as Splunk.

## What is implemented

The project uses an internal Java logger:

- [ThalesLogger.java](E:\eclipse-workspace\thales.databricks.udf\src\main\java\ThalesLogger.java)

The logger is already used by key runtime classes such as:

- [ThalesDataBricksCRDPBulkService.java](E:\eclipse-workspace\thales.databricks.udf\src\main\java\ThalesDataBricksCRDPBulkService.java)
- [ThalesDataBricksCRDPFPE.java](E:\eclipse-workspace\thales.databricks.udf\src\main\java\ThalesDataBricksCRDPFPE.java)
- [ThalesDataBricksCADPFPE.java](E:\eclipse-workspace\thales.databricks.udf\src\main\java\ThalesDataBricksCADPFPE.java)

The logger reads its runtime settings from:

- [udfConfig.properties](E:\eclipse-workspace\thales.databricks.udf\src\main\resources\udfConfig.properties)

via:

- [ThalesDataBricksUdfConfig.java](E:\eclipse-workspace\thales.databricks.udf\src\main\java\ThalesDataBricksUdfConfig.java)

## Where logs go

The current logger writes to standard console streams:

- `INFO`, `WARN`, and `DEBUG` go to `stdout`
- `ERROR` goes to `stderr`

This means:

- driver-side execution writes to driver logs
- executor-side execution writes to executor logs
- Databricks is responsible for capturing those logs from the cluster runtime

## Logging settings

These settings are supported in `udfConfig.properties`:

```properties
APP_LOG_LEVEL=INFO
APP_LOG_FORMAT=kv
APP_LOG_INCLUDE_STACKTRACE=false
APP_LOG_COMPONENT=thales-databricks-udf
```

### `APP_LOG_LEVEL`

Supported values:

- `ERROR`
- `WARN`
- `INFO`
- `DEBUG`

Default:

- `INFO`

Behavior:

- `ERROR` shows only error events
- `WARN` shows warnings and errors
- `INFO` shows informational events, warnings, and errors
- `DEBUG` shows the most detail, including normal request start/success events

### `APP_LOG_FORMAT`

Supported values:

- `kv`
- `json`

Default:

- `kv`

Behavior:

- `kv` produces one-line key/value logs
- `json` produces one-line JSON logs

### `APP_LOG_INCLUDE_STACKTRACE`

Supported values:

- `true`
- `false`

Default:

- `false`

Behavior:

- when `true`, stack traces are printed after the log line for warning/error events with exceptions
- when `false`, the log line still includes exception class and message summary, but not the full stack trace

### `APP_LOG_COMPONENT`

Default:

- `thales-databricks-udf`

Behavior:

- sets a stable component identifier in each log line
- useful for log filtering and external routing rules

## How log levels work

The logger uses a minimum-level model.

If `APP_LOG_LEVEL=INFO`, then:

- `INFO` logs are shown
- `WARN` logs are shown
- `ERROR` logs are shown
- `DEBUG` logs are hidden

If `APP_LOG_LEVEL=DEBUG`, then everything is shown.

If `APP_LOG_LEVEL=ERROR`, then only errors are shown.

## Log format examples

### Key/value format

Example:

```text
[THALES-UDF] level=INFO component=thales-databricks-udf logger=ThalesDataBricksCRDPBulkService event=crdp_http_request_success endpoint=v1/protectbulk rows=5469 status_code=200 elapsed_ms=187
```

### JSON format

Example:

```json
{"level":"INFO","component":"thales-databricks-udf","logger":"ThalesDataBricksCRDPBulkService","event":"crdp_http_request_success","endpoint":"v1/protectbulk","rows":"5469","status_code":"200","elapsed_ms":"187","ts":"2026-05-21T15:01:00Z"}
```

## Common events

The CRDP bulk service already emits structured events such as:

- `crdp_http_request_start`
- `crdp_http_request_success`
- `crdp_http_request_failed`
- `crdp_http_request_timeout`
- `crdp_http_request_io_error`
- `crdp_authorize_request_failed`

These events are designed to focus on operational context such as:

- endpoint
- grouped row count or request row count
- HTTP status code
- elapsed milliseconds
- exception class
- message summary

## What is safe to log

Good logging fields include:

- event name
- mode such as `protect`, `reveal`, `protectbulk`, `revealbulk`
- endpoint such as `v1/protectbulk`
- object name
- logical column name
- resolved policy type
- batch size
- row count
- elapsed milliseconds
- coarse outcome such as success, fallback, skipped, timeout, or failed

## What must not be logged

Do not log:

- plaintext values
- protected tokens
- external header values
- passwords
- API credentials
- full HTTP payloads
- full response payloads

For this project, the log lines should stay focused on metadata and timing, not
customer data.

## Where to look in Databricks

For Databricks compute-cluster runs, start by checking:

- driver logs for notebook-scoped or driver-side issues
- executor logs for distributed UDF execution behavior
- stdout for `INFO`, `WARN`, and `DEBUG`
- stderr for `ERROR`

In practice, the most useful places are usually:

- cluster driver logs when debugging setup/config issues
- executor logs when debugging per-task UDF execution
- exported or centralized cluster logs when doing operational monitoring

## Suggested operating levels

### Normal production or large-volume testing

Use:

```properties
APP_LOG_LEVEL=INFO
APP_LOG_FORMAT=kv
APP_LOG_INCLUDE_STACKTRACE=false
```

Why:

- keeps log volume reasonable
- preserves error and timing visibility
- avoids flooding logs with routine request-start and request-success noise

### Active troubleshooting

Use:

```properties
APP_LOG_LEVEL=DEBUG
APP_LOG_FORMAT=kv
APP_LOG_INCLUDE_STACKTRACE=true
```

Why:

- exposes detailed request flow
- helps correlate grouped-call behavior with executor activity
- surfaces stack traces for troubleshooting

After troubleshooting, reduce the verbosity again.

### Structured external parsing

Use:

```properties
APP_LOG_LEVEL=INFO
APP_LOG_FORMAT=json
APP_LOG_INCLUDE_STACKTRACE=false
```

Why:

- JSON is often easier for downstream parsing rules
- useful when an external platform expects structured logs

## Splunk and external log routing

The recommended model is:

1. emit clean stdout/stderr logs from the UDF runtime
2. let Databricks capture driver and executor logs
3. forward those logs to Splunk using the customer’s normal Databricks log collection path

This is preferred over embedding a direct Splunk client in the shaded jar.

Benefits:

- fewer dependency collisions
- less code in the UDF runtime
- simpler rollback
- clearer separation between application logging and platform log shipping

## What customers should configure for Splunk

At a minimum, customers should decide:

- whether they want `kv` or `json` log format
- which clusters/jobs should emit `DEBUG` vs `INFO`
- how Databricks driver and executor logs are exported from their environment
- which log filters in Splunk should match:
  - `component=thales-databricks-udf`
  - `logger=<class name>`
  - event names such as `crdp_http_request_failed`

Recommended starting point:

- `APP_LOG_FORMAT=kv` if the log pipeline is simple and grep-like
- `APP_LOG_FORMAT=json` if Splunk parsing is built around structured JSON

## Practical troubleshooting workflow

1. set `APP_LOG_LEVEL=INFO`
2. confirm the cluster picks up the desired `udfConfig.properties`
3. run the notebook or job
4. inspect driver and executor logs for:
   - request failures
   - timeouts
   - authorization errors
   - unexpected request sizes
5. if needed, temporarily raise to `DEBUG`
6. if needed, enable `APP_LOG_INCLUDE_STACKTRACE=true`
7. reduce verbosity after the issue is understood

## Related files

- logger implementation:
  [ThalesLogger.java](E:\eclipse-workspace\thales.databricks.udf\src\main\java\ThalesLogger.java)
- logging config reader:
  [ThalesDataBricksUdfConfig.java](E:\eclipse-workspace\thales.databricks.udf\src\main\java\ThalesDataBricksUdfConfig.java)
- default config example:
  [udfConfig.properties](E:\eclipse-workspace\thales.databricks.udf\src\main\resources\udfConfig.properties)

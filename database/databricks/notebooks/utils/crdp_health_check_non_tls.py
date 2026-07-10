"""
Compute-cluster CRDP non-TLS health check helpers.

Use this from a Databricks Python notebook attached to a compute cluster when
you want to validate basic HTTP connectivity to a CRDP health endpoint such as:

    GET http://mycrdp:8080/healthz

This script supports two scopes:

- driver-side notebook check
- executor-side distributed Spark check
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request


def _fetch_health_url(url: str, timeout_seconds: int) -> dict[str, Any]:
    request = urllib_request.Request(url, method="GET")
    try:
        with urllib_request.urlopen(request, timeout=timeout_seconds) as response:
            body_bytes = response.read()
            body_text = body_bytes.decode("utf-8", errors="replace")
            return {
                "ok": True,
                "url": url,
                "status_code": response.getcode(),
                "body": body_text,
                "error": None,
            }
    except urllib_error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "url": url,
            "status_code": exc.code,
            "body": error_body,
            "error": repr(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "url": url,
            "status_code": None,
            "body": None,
            "error": repr(exc),
        }


def run_driver_health_check(
    url: str = "http://mycrdp:8080/healthz",
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    """
    Run the health check from the notebook driver only.
    """

    result = _fetch_health_url(url, timeout_seconds)
    print("CRDP non-TLS driver health check")
    print(json.dumps(result, indent=2))
    return result


def run_executor_health_check(
    spark_session,
    url: str = "http://mycrdp:8080/healthz",
    timeout_seconds: int = 10,
    partitions: int = 4,
) -> list[dict[str, Any]]:
    """
    Run the health check from Spark executors using mapPartitions.

    This is usually the more important cluster validation because protect/reveal
    work executes on executors too.
    """

    sc = spark_session.sparkContext

    def check_partition(_):
        import json as _json
        import os as _os
        from urllib import error as _urllib_error
        from urllib import request as _urllib_request

        request = _urllib_request.Request(url, method="GET")
        host_name = _os.environ.get("SPARK_LOCAL_HOSTNAME") or _os.environ.get("HOSTNAME")
        try:
            with _urllib_request.urlopen(request, timeout=timeout_seconds) as response:
                body_text = response.read().decode("utf-8", errors="replace")
                payload = {
                    "ok": True,
                    "url": url,
                    "status_code": response.getcode(),
                    "body": body_text,
                    "error": None,
                    "executor_host": host_name,
                }
        except _urllib_error.HTTPError as exc:
            payload = {
                "ok": False,
                "url": url,
                "status_code": exc.code,
                "body": exc.read().decode("utf-8", errors="replace"),
                "error": repr(exc),
                "executor_host": host_name,
            }
        except Exception as exc:
            payload = {
                "ok": False,
                "url": url,
                "status_code": None,
                "body": None,
                "error": repr(exc),
                "executor_host": host_name,
            }
        return [_json.dumps(payload)]

    raw_results = sc.parallelize(range(partitions), partitions).mapPartitions(check_partition).collect()
    parsed_results = [json.loads(item) for item in raw_results]

    print("CRDP non-TLS executor health check")
    for item in parsed_results:
        print(json.dumps(item, indent=2))
    return parsed_results


print(
    "crdp_health_check_non_tls.py loaded. "
    "Run run_driver_health_check(...) or run_executor_health_check(spark, ...)."
)

# COMMAND ----------

try:
    spark_session = spark  # type: ignore[name-defined]
except NameError:
    print(
        "No active Spark session variable named 'spark' was found. "
        "Run this from a Databricks Python notebook or call the functions manually."
    )
else:
    run_driver_health_check("http://mycrdp:8080/healthz")

# COMMAND ----------

try:
    spark_session = spark  # type: ignore[name-defined]
except NameError:
    print(
        "No active Spark session variable named 'spark' was found. "
        "Run this from a Databricks Python notebook or call the functions manually."
    )
else:
    run_executor_health_check(
        spark_session,
        "http://mycrdp:8080/healthz",
        partitions=4,
    )

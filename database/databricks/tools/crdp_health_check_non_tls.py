"""
Standalone CRDP non-TLS health check helper.

Use this outside Databricks when you want to validate basic HTTP connectivity
to a CRDP health endpoint such as:

    GET http://mycrdp:8080/healthz

This tool is intentionally driver/local only. It does not include Spark
executor-distributed checks.
"""

from __future__ import annotations

import argparse
import json
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request


def fetch_health_url(url: str, timeout_seconds: int) -> dict[str, Any]:
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
    result = fetch_health_url(url, timeout_seconds)
    print("CRDP non-TLS driver health check")
    print(json.dumps(result, indent=2))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Standalone CRDP non-TLS health check.")
    parser.add_argument(
        "--url",
        default="http://mycrdp:8080/healthz",
        help="CRDP health endpoint URL.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=10,
        help="Request timeout in seconds.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_driver_health_check(
        url=args.url,
        timeout_seconds=args.timeout_seconds,
    )

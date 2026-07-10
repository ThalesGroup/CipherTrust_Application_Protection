#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="${1:-$(cd "$(dirname "$0")" && pwd)/identity-userset-sync.properties}"

JAVA_SSL_OPTS=()
if [[ -n "${JAVA_TRUSTSTORE_PATH:-}" ]]; then
  JAVA_SSL_OPTS+=("-Djavax.net.ssl.trustStore=${JAVA_TRUSTSTORE_PATH}")
fi
if [[ -n "${JAVA_TRUSTSTORE_PASSWORD:-}" ]]; then
  JAVA_SSL_OPTS+=("-Djavax.net.ssl.trustStorePassword=${JAVA_TRUSTSTORE_PASSWORD}")
fi
if [[ -n "${JAVA_TRUSTSTORE_TYPE:-}" ]]; then
  JAVA_SSL_OPTS+=("-Djavax.net.ssl.trustStoreType=${JAVA_TRUSTSTORE_TYPE}")
fi

java "${JAVA_SSL_OPTS[@]}" ${JAVA_OPTS:-} -cp target/thales-userset-sync-tool-0.0.1-SNAPSHOT-all.jar com.thales.usersets.tool.IdentityUserSetSyncTool "$CONFIG_FILE"

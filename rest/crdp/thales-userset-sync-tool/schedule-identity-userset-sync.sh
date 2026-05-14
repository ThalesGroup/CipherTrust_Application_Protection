#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${1:-$BASE_DIR/identity-userset-sync.properties}"
JAVA_EXE="${JAVA_EXE:-java}"
JAR_PATH="${JAR_PATH:-$BASE_DIR/target/thales-userset-sync-tool-0.0.1-SNAPSHOT-all.jar}"
LOG_DIR="${LOG_DIR:-$BASE_DIR/logs/identity-userset-sync}"
LOCK_DIR="${LOCK_DIR:-$BASE_DIR/locks/identity-userset-sync}"
JAVA_TRUSTSTORE_PATH="${JAVA_TRUSTSTORE_PATH:-}"
JAVA_TRUSTSTORE_PASSWORD="${JAVA_TRUSTSTORE_PASSWORD:-}"
JAVA_TRUSTSTORE_TYPE="${JAVA_TRUSTSTORE_TYPE:-}"

mkdir -p "$LOG_DIR" "$(dirname "$LOCK_DIR")"

if mkdir "$LOCK_DIR" 2>/dev/null; then
  trap 'rm -rf "$LOCK_DIR"' EXIT
else
  echo "Another identity userset sync appears to be running. Lock exists at $LOCK_DIR" >&2
  exit 2
fi

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOG_DIR/identity-userset-sync-$TIMESTAMP.log"

echo "Starting identity userset sync"
echo "Config: $CONFIG_FILE"
echo "Log: $LOG_FILE"
if [[ -n "$JAVA_TRUSTSTORE_PATH" ]]; then
  echo "TrustStore: $JAVA_TRUSTSTORE_PATH"
fi

JAVA_SSL_OPTS=()
if [[ -n "$JAVA_TRUSTSTORE_PATH" ]]; then
  JAVA_SSL_OPTS+=("-Djavax.net.ssl.trustStore=$JAVA_TRUSTSTORE_PATH")
fi
if [[ -n "$JAVA_TRUSTSTORE_PASSWORD" ]]; then
  JAVA_SSL_OPTS+=("-Djavax.net.ssl.trustStorePassword=$JAVA_TRUSTSTORE_PASSWORD")
fi
if [[ -n "$JAVA_TRUSTSTORE_TYPE" ]]; then
  JAVA_SSL_OPTS+=("-Djavax.net.ssl.trustStoreType=$JAVA_TRUSTSTORE_TYPE")
fi

"$JAVA_EXE" "${JAVA_SSL_OPTS[@]}" -cp "$JAR_PATH" com.thales.usersets.tool.IdentityUserSetSyncTool "$CONFIG_FILE" 2>&1 | tee "$LOG_FILE"

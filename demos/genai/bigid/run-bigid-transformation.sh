#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
APP_HOME="$SCRIPT_DIR"

BIGID_CONFIG_FILE="${BIGID_CONFIG_FILE:-$APP_HOME/src/main/resources/application.properties}"
BIGID_JAR="${BIGID_JAR:-$APP_HOME/target/bigid.thales.transformation-0.0.1-SNAPSHOT-all.jar}"
JAVA_CMD="${JAVA_CMD:-java}"
BIGID_MAIN_CLASS="com.thales.bigid.transformation.BigidThalesTransformationApplication"

if [ ! -f "$BIGID_JAR" ]; then
  echo "Shaded jar not found at '$BIGID_JAR'."
  echo "Build the project first with: mvn -DskipTests package"
  exit 1
fi

if [ ! -f "$BIGID_CONFIG_FILE" ]; then
  echo "Config file not found at '$BIGID_CONFIG_FILE'."
  echo "Copy src/main/resources/application.properties.example to application.properties and update it."
  exit 1
fi

echo "Using config: $BIGID_CONFIG_FILE"
echo "Using jar: $BIGID_JAR"

exec "$JAVA_CMD" ${JAVA_OPTS:-} -cp "$BIGID_JAR" "$BIGID_MAIN_CLASS" "$BIGID_CONFIG_FILE"

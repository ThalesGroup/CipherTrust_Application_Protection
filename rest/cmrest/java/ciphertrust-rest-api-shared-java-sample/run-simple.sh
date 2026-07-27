#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")"; pwd)
JAR_PATH="$SCRIPT_DIR/target/ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar"

if [ ! -f "$JAR_PATH" ]; then
  echo "Jar not found: $JAR_PATH" >&2
  echo "Build it first with: mvn clean package" >&2
  exit 1
fi

exec java -jar "$JAR_PATH" "$@"
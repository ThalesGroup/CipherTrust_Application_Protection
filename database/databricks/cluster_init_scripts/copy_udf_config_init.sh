#!/bin/bash

# Thales CRDP UDF init script
#
# Copies udfConfig.properties from the Unity Catalog volume to a local path
# before the Spark JVM starts. This avoids the FUSE "Operation not permitted"
# issue when Java UDF code reads the config from Spark task threads.

LOCAL_DIR="/tmp/thales_config"
VOLUME_PATH="/Volumes/my_catalog/my_schema/volume_forjars"
CONFIG_FILE="udfConfig.properties"

mkdir -p "$LOCAL_DIR"
cp "${VOLUME_PATH}/${CONFIG_FILE}" "${LOCAL_DIR}/${CONFIG_FILE}"

if [ -f "${LOCAL_DIR}/${CONFIG_FILE}" ]; then
  echo "Init script: copied ${CONFIG_FILE} to ${LOCAL_DIR}/"
else
  echo "Init script: ERROR - failed to copy ${CONFIG_FILE}" >&2
  exit 1
fi

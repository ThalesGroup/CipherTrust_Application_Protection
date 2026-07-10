#!/bin/bash

# Thales CRDP UDF init script
#
# Copies udfConfig.properties from the Unity Catalog volume to a local path
# before the Spark JVM starts. This avoids the FUSE "Operation not permitted"
# issue when Java UDF code reads the config from Spark task threads.

LOCAL_DIR="/tmp/thales_config"
VOLUME_PATH="/Volumes/my_catalog/my_schema/volume_forjars"
CONFIG_FILE="udfConfig.properties"
CLIENT_PKCS12_FILE="crdp-client.p12"
CA_CERT_FILE="crdp-ca.pem"
CLIENT_CERT_PEM_FILE="databricks-crdp-client-cert.pem"
CLIENT_KEY_PEM_FILE="databricks-crdp-client-key.pem"

mkdir -p "$LOCAL_DIR"
cp "${VOLUME_PATH}/${CONFIG_FILE}" "${LOCAL_DIR}/${CONFIG_FILE}"

if [ -f "${LOCAL_DIR}/${CONFIG_FILE}" ]; then
  echo "Init script: copied ${CONFIG_FILE} to ${LOCAL_DIR}/"
else
  echo "Init script: ERROR - failed to copy ${CONFIG_FILE}" >&2
  exit 1
fi

if [ -f "${VOLUME_PATH}/${CLIENT_PKCS12_FILE}" ]; then
  cp "${VOLUME_PATH}/${CLIENT_PKCS12_FILE}" "${LOCAL_DIR}/${CLIENT_PKCS12_FILE}"
  chmod 600 "${LOCAL_DIR}/${CLIENT_PKCS12_FILE}"
  echo "Init script: copied ${CLIENT_PKCS12_FILE} to ${LOCAL_DIR}/"
else
  echo "Init script: ${CLIENT_PKCS12_FILE} not present in ${VOLUME_PATH}, skipping."
fi

if [ -f "${VOLUME_PATH}/${CA_CERT_FILE}" ]; then
  cp "${VOLUME_PATH}/${CA_CERT_FILE}" "${LOCAL_DIR}/${CA_CERT_FILE}"
  echo "Init script: copied ${CA_CERT_FILE} to ${LOCAL_DIR}/"
else
  echo "Init script: ${CA_CERT_FILE} not present in ${VOLUME_PATH}, skipping."
fi

if [ -f "${VOLUME_PATH}/${CLIENT_CERT_PEM_FILE}" ]; then
  cp "${VOLUME_PATH}/${CLIENT_CERT_PEM_FILE}" "${LOCAL_DIR}/${CLIENT_CERT_PEM_FILE}"
  echo "Init script: copied ${CLIENT_CERT_PEM_FILE} to ${LOCAL_DIR}/"
else
  echo "Init script: ${CLIENT_CERT_PEM_FILE} not present in ${VOLUME_PATH}, skipping."
fi

if [ -f "${VOLUME_PATH}/${CLIENT_KEY_PEM_FILE}" ]; then
  cp "${VOLUME_PATH}/${CLIENT_KEY_PEM_FILE}" "${LOCAL_DIR}/${CLIENT_KEY_PEM_FILE}"
  chmod 600 "${LOCAL_DIR}/${CLIENT_KEY_PEM_FILE}"
  echo "Init script: copied ${CLIENT_KEY_PEM_FILE} to ${LOCAL_DIR}/"
else
  echo "Init script: ${CLIENT_KEY_PEM_FILE} not present in ${VOLUME_PATH}, skipping."
fi

@echo off
setlocal

set "CONFIG_FILE=%~1"
if "%CONFIG_FILE%"=="" set "CONFIG_FILE=%~dp0identity-userset-sync.properties"

set "JAVA_SSL_OPTS="
if not "%JAVA_TRUSTSTORE_PATH%"=="" set "JAVA_SSL_OPTS=%JAVA_SSL_OPTS% -Djavax.net.ssl.trustStore=%JAVA_TRUSTSTORE_PATH%"
if not "%JAVA_TRUSTSTORE_PASSWORD%"=="" set "JAVA_SSL_OPTS=%JAVA_SSL_OPTS% -Djavax.net.ssl.trustStorePassword=%JAVA_TRUSTSTORE_PASSWORD%"
if not "%JAVA_TRUSTSTORE_TYPE%"=="" set "JAVA_SSL_OPTS=%JAVA_SSL_OPTS% -Djavax.net.ssl.trustStoreType=%JAVA_TRUSTSTORE_TYPE%"

java %JAVA_SSL_OPTS% %JAVA_OPTS% -cp target\thales-userset-sync-tool-0.0.1-SNAPSHOT-all.jar com.thales.usersets.tool.IdentityUserSetSyncTool "%CONFIG_FILE%"

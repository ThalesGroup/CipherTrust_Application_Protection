@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "APP_HOME=%SCRIPT_DIR%"

if "%BIGID_CONFIG_FILE%"=="" set "BIGID_CONFIG_FILE=%APP_HOME%src\main\resources\application.properties"
if "%BIGID_JAR%"=="" set "BIGID_JAR=%APP_HOME%target\bigid.thales.transformation-0.0.1-SNAPSHOT-all.jar"
if "%JAVA_CMD%"=="" set "JAVA_CMD=java"

if not exist "%BIGID_JAR%" (
  echo Shaded jar not found at "%BIGID_JAR%".
  echo Build the project first with: mvn -DskipTests package
  exit /b 1
)

if not exist "%BIGID_CONFIG_FILE%" (
  echo Config file not found at "%BIGID_CONFIG_FILE%".
  echo Copy src\main\resources\application.properties.example to application.properties and update it.
  exit /b 1
)

set "BIGID_MAIN_CLASS=com.thales.bigid.transformation.BigidThalesTransformationApplication"

echo Using config: %BIGID_CONFIG_FILE%
echo Using jar: %BIGID_JAR%

"%JAVA_CMD%" %JAVA_OPTS% -cp "%BIGID_JAR%" %BIGID_MAIN_CLASS% "%BIGID_CONFIG_FILE%"
exit /b %ERRORLEVEL%

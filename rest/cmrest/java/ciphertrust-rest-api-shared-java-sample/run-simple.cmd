@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "JAR_PATH=%SCRIPT_DIR%target\ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar"

if not exist "%JAR_PATH%" (
    echo Jar not found: %JAR_PATH%
    echo Build it first with: mvn clean package
    exit /b 1
)

java -jar "%JAR_PATH%" %*
exit /b %ERRORLEVEL%
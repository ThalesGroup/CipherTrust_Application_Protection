@echo off
setlocal

set JAR=target\genai.azure.example-0.0.1-SNAPSHOT-all.jar

if not exist "%JAR%" (
  echo Shaded jar not found: %JAR%
  echo Build it first with: mvn clean package
  exit /b 1
)

echo.
echo Sample commands for this project:
echo.
echo 1. Non-Purview local file-to-file protect flow
echo    java -cp "%JAR%" com.example.ThalesAzureProtectRevealBatchProcessor protect https://your-language-endpoint your-language-key C:\input C:\output .txt
echo.
echo 2. Non-Purview local file-to-file reveal flow
echo    java -cp "%JAR%" com.example.ThalesAzureProtectRevealBatchProcessor reveal https://your-language-endpoint your-language-key C:\input C:\output .txt
echo.
echo 3. Purview storage flow
echo    java -cp "%JAR%" com.example.ThalesAzurePurviewBatchProcessor protect storage https://your-language-endpoint your-language-key .txt
echo.
echo 4. Purview SQL flow
echo    java -cp "%JAR%" com.example.ThalesAzurePurviewBatchProcessor protect sql - - -
echo.
echo 5. Purview storage plus SQL flow
echo    java -cp "%JAR%" com.example.ThalesAzurePurviewBatchProcessor protect both https://your-language-endpoint your-language-key .txt
echo.
echo 6. Azure OpenAI prompt protection example
echo    java -cp "%JAR%" com.example.ThalesAzureOpenAIClientPromptExample https://your-language-endpoint your-language-key your-openai-key https://your-openai-endpoint
echo.
echo 7. REST-based Thales protect/reveal helper demo
echo    java -cp "%JAR%" com.example.ThalesRestProtectRevealHelper your-crdp-ip metadata internal true your-user
echo.
echo Replace placeholder values and ensure thales-config.properties is set for your environment.

endlocal

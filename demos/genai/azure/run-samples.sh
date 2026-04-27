#!/usr/bin/env sh

JAR="target/genai.azure.example-0.0.1-SNAPSHOT-all.jar"

if [ ! -f "$JAR" ]; then
  echo "Shaded jar not found: $JAR"
  echo "Build it first with: mvn clean package"
  exit 1
fi

cat <<EOF

Sample commands for this project:

1. Non-Purview local file-to-file protect flow
   java -cp "$JAR" com.example.ThalesAzureProtectRevealBatchProcessor protect https://your-language-endpoint your-language-key /path/input /path/output .txt

2. Non-Purview local file-to-file reveal flow
   java -cp "$JAR" com.example.ThalesAzureProtectRevealBatchProcessor reveal https://your-language-endpoint your-language-key /path/input /path/output .txt

3. Purview storage flow
   java -cp "$JAR" com.example.ThalesAzurePurviewBatchProcessor protect storage https://your-language-endpoint your-language-key .txt

4. Purview SQL flow
   java -cp "$JAR" com.example.ThalesAzurePurviewBatchProcessor protect sql - - -

5. Purview storage plus SQL flow
   java -cp "$JAR" com.example.ThalesAzurePurviewBatchProcessor protect both https://your-language-endpoint your-language-key .txt

6. Azure OpenAI prompt protection example
   java -cp "$JAR" com.example.ThalesAzureOpenAIClientPromptExample https://your-language-endpoint your-language-key your-openai-key https://your-openai-endpoint

7. REST-based Thales protect/reveal helper demo
   java -cp "$JAR" com.example.ThalesRestProtectRevealHelper your-crdp-ip metadata internal true your-user

Replace placeholder values and ensure thales-config.properties is set for your environment.
EOF

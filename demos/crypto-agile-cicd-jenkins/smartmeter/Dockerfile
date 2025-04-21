# Use official OpenJDK 21 image
FROM eclipse-temurin:21-jdk-jammy

# Set working directory
WORKDIR /app

# Copy the JAR file into the container
COPY ./keys /app/keys
COPY target/smartmeter-*.jar app.jar

# Define environment variable names
ENV SM_API_URL=http://192.168.2.216:9090/api/v1/smart-meter-data
ENV SM_USER_ID=1
ENV SM_SMART_METER_ID=1

# Set environment variables for Java runtime (optional)
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"

# Expose port if needed (though this is a scheduler, not a web app)
EXPOSE 8080

# Run the application
ENTRYPOINT ["sh", "-c", "java ${JAVA_OPTS} -jar app.jar"]
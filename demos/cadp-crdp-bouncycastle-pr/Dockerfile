# Stage 1: Build the application using Maven
FROM maven:3.9.5-eclipse-temurin-21 as build
WORKDIR /app

# Copy the pom.xml and source code
COPY pom.xml .
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Stage 2: Create a lightweight runtime image
FROM eclipse-temurin:21-jre-jammy
WORKDIR /app

# Copy the JAR file from the build stage
COPY --from=build /app/target/crdp_demo-0.0.1-SNAPSHOT.jar ./app.jar

# Expose the port your application runs on
EXPOSE 9001

# Command to run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
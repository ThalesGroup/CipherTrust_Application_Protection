FROM maven:3.9.9-eclipse-temurin-11 AS build
WORKDIR /workspace

COPY pom.xml .
COPY src ./src

RUN mvn -DskipTests package

FROM eclipse-temurin:11-jre
WORKDIR /app

COPY --from=build /workspace/target/bigid.thales.transformation-0.0.1-SNAPSHOT-all.jar /app/bigid-thales-transformation.jar
COPY run-bigid-transformation.sh /app/run-bigid-transformation.sh
COPY src/main/resources/application.properties.example /app/application.properties.example

RUN chmod +x /app/run-bigid-transformation.sh

ENV BIGID_CONFIG_FILE=/config/application.properties

ENTRYPOINT ["/app/run-bigid-transformation.sh"]

FROM maven:3.8.3-openjdk-17 AS build
COPY src /home/app/src
COPY pom.xml /home/app
RUN mvn -f /home/app/pom.xml clean package

FROM openjdk:17
COPY --from=build /home/app/target/api-0.0.1-SNAPSHOT.jar /usr/local/lib/api.jar
ENTRYPOINT ["java","-jar","/usr/local/lib/api.jar"]
EXPOSE 8080
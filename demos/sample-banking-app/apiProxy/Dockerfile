FROM maven:3.8.3-openjdk-17 AS build
COPY src /home/app/src
COPY pom.xml /home/app
RUN mvn -f /home/app/pom.xml clean package

FROM openjdk:17
COPY --from=build /home/app/target/apiProxy-0.0.1.jar /usr/local/lib/apiProxy.jar
ENTRYPOINT ["java","-jar","/usr/local/lib/apiProxy.jar"]
EXPOSE 8081
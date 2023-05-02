# Introduction

This project leverages following libraries primarily (you can find the complete list in pom.xml of this project)

* Maven - to build, publish, and deploy this application
* SpringBoot - base Java framwork leveraged by this application
* springdoc-openapi-ui - Swagger OpenAPI documentation
* spring-boot-starter-web - create REST API controllers

As with other applications in this project, this project is also designed to run inside a container, but can be run directly as well - check the section below for steps.

## Building and Running application from source

This project hosts the APIs that ui application mostly works with.
For most of the actual work, this application relies heavily on the APIs exposed by dpgBankDemo

### 1) Update application.properties file
| Parameter | Usage | Value |
| --- | --- | --- |
| server.port | this is the port that will be used to run this project. ui interacts with this application on this port | default value is 8081. If you change this, you would need to update other projects and docker-compose.yml to reflect the same |
| springdoc.swagger-ui.path | swagger endpoint | default: /swagger-ui.html | 


### 2) Build the project
Maven is used for the process

`mvn clean package`

This will build the required jar and will place that as ./target/apiProxy-0.0.1-SNAPSHOT.jar

### 3) Running the project
Java is needed to run the project

`java -jar ./target/apiProxy-0.0.1-SNAPSHOT.jar`

Once executed, you should be able to launch the swagger interface at

localhot:8081/swagger-ui.html
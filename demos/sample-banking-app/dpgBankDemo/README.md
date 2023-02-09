# Introduction

This project leverages following libraries primarily (you can find the complete list in pom.xml of this project)

* Maven - to build, publish, and deploy this application
* SpringBoot - base Java framwork leveraged by this application
* spring-boot-starter-data-mongodb - to work with the MongoDb database
* springdoc-openapi-ui - Swagger OpenAPI documentation
* spring-boot-starter-web - create REST API controllers
* aws-java-sdk-dynamodb - optional, if you want to use DynamoDb instead of MongoDb

As with other applications in this project, this project is also designed to run inside a container, but can be run directly as well - check the section below for steps.

## Building and Running application from source

This project hosts the APIs that are protected by the DPG data protection tool, from Thales.
This is also the only project in this repo which interacts with the Database (MongoDb)

### 1) Update application.properties file
| Parameter | Usage | Value |
| --- | --- | --- |
| server.port | this is the port that will be used to run this project. apiProxy and ui interacts with this application on this port | default value is 8080. If you change this, you would need to update other projects and docker-compose.yml to reflect the same |
| spring.data.mongodb.authentication-database | this is the database that holds the username and password needed to work with MongoDb | Values are derived from the mongo-init.js file at the root of this repo. Default is dpg |
| spring.data.mongodb.username | this is the username application will use to authenticate with MongoDb | Values are derived from the mongo-init.js file at the root of this repo. Default is root |
| spring.data.mongodb.password | this is the password application will use to authenticate with MongoDb | Values are derived from the mongo-init.js file at the root of this repo. Default is root |
| spring.data.mongodb.database | this is the database where all the data is stored by the app, like account details | Values are derived from the mongo-init.js file at the root of this repo. Default is dpg |
| spring.data.mongodb.port | port where MongoDb is listening | default is 27017 |
| spring.data.mongodb.host | host where MongoDb is running | default is mongodb as defined in the docker-compose-template.yml |
| springdoc.swagger-ui.path | swagger endpoint | default: /swagger-ui.html | 


### 2) Build the project
Maven is used for the process

`mvn clean package`

This will build the required jar and will place that as ./target/dpgBankDemo-0.0.1-SNAPSHOT.jar

### 3) Running the project
Java is needed to run the project

`java -jar ./target/dpgBankDemo-0.0.1-SNAPSHOT.jar`

Once executed, you should be able to launch the swagger interface at

localhot:8080/swagger-ui.html
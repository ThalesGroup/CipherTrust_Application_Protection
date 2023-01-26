# Turnkey demo bank app with Data Protection Gateway
This sample is a turnkey docker based multi-tier application that demonstrates data protection with Thales Ciphertrust Manager (CM)Community Edition. Securing credit card information as well as user's personal information like SSN is not only a value add, but a compliance mandated requirement.
This project will let you
* Deploy a fully functional app including ReactJs based frontend, SpringBoot based REST API backend, and MongoDB based data persistence all within a single docker deployment
* Using a PowerShell script to automate all the configurations needed on Thales CipherTrust Manager to rub this demo

## Architecture
<kbd><img src="https://user-images.githubusercontent.com/111074839/189827400-3377df49-b028-4f32-bca3-087ce61fb0c4.png"></kbd>

## Prerequisites
* On Windows
  * PowerShell > 3.x (recommended PowerShel 7.3.0)
  * Docker Desktop
  * yq (YAML formatter)
    * Follow instructions at https://github.com/mikefarah/yq/#install
* On Linux (Ubuntu 20.04 LTS)
  * PowerShell
    * Follow instructions at https://learn.microsoft.com/en-us/powershell/scripting/install/install-ubuntu?view=powershell-7.3  
  * Git
    * If not already installed
      ```
      sudo apt install git
      ```
  * Docker
    * Follow instructions at https://docs.docker.com/engine/install/ubuntu/ 
  * yq (YAML formatter)
    * Follow instructions at https://github.com/mikefarah/yq/#install

## Network Requirements
Below ports need to be opened if firewall is there
<kbd><img src="https://user-images.githubusercontent.com/111074839/211354811-4f671792-c0ee-4515-8040-e56177c77618.png"></kbd>

## Quickstart
#### 1) Deploy Ciphertrust Manager (CM) community edition (Always Free)
To deploy Ciphertrust Manager, follow the link https://ciphertrust.io/ 
You can deploy Ciphertrust Manager in you favorite cloud environment or on local server/virtual machine
Detailed steps are available on CM web page above.
#### 2) Clone the repo 
Clone this repo on your Windows workstation
```
git clone https://github.com/thalescpl-io/CipherTrust_Application_Protection
cd ./CipherTrust_Application_Protection/demos/sample-banking-app
```
#### 3) Configure PowerShell script
Once you have the CM installed and repo cloned, the only thing you need to change are some of the variables in the bundled ps1 file i.e. 'deploy-demo-win-ps-71.ps1'
Updated below variables at the top of the file -

| Variable | Description |
| --- | --- |
| username | Username of CM instance which we want to configure to work with this demo  | 
| password | Password of the above CM user |
| kms | IP address of FQDN of the CM instance e.g. 10.10.10.10 or example.com |
| protocol | Depending on CM instance can be http or https... URL generated will be protocol://kms |
| counter | This is a unique identifier which you may want to suffix with, all the CM assets created by the PS script |
| sampleUserPassword | PowerShell script bundled with this repo creates some sample users on CM for you to test with. This variable holds the password value for those users |
| host_machine | The IP address or FQDN of the host machine where all teh docker containers of this sample app are to be executed, can be localhost as well |

#### 4) Understanding docker compose file
All the three sample applications and the Mongo DB are run inside docker containers for this sample app.
Below is some explanation for the same

| Service | Use | Service Configuration |
| --- | --- | --- |
| proxy | SpringBoot application that acts as a API proxy layer. UI interacts with this layer directly. | <ul><li>Port Listening at: 8081 (UI talks to this layer on this port)</li><li>image: this is either docker hub based or can be built from source</li></ul> |
| mongodb | Password of the above CM user | <ul><li>Port Listening at: 27017 (Backend SpringBoot App talks to MongoDb on this port)</li><li>image: mongo:latest (from Docker Hub)</li><li>environment: environment vars including initial database and authentication credentials.</li><li>volumes: mongo-init.js contains auth database and credentials. Changing this would need change to the backend app.</li></ul> |
| frontend | React JS based frontend app that leverages Tailwind CSS for styling | <ul><li>Port Listening at: 3000 (allows opening app at localhost:3000)</li><li>environment: environment vars including host machine IP or FQDN</li><li>image: this is either docker hub based or can be built from source</li></ul>
| api | SpringBoot application that acts as the backend API layer that also talks to CM and MongoDb | <ul><li>Port Listening at: 8000</li><li>image: this is either docker hub based or can be built from source</li><li>environment: environment vars including CM URL, credentials and a CM user set ID auto populated by PowerShell script</li></ul> |
| ciphertrust | DPG container | <ul><li>Port Listening at: 9005 (NAE port)</li><li>image: thalesciphertrust/ciphertrust-data-protection-gateway:latest (from Docker Hub)</li><li>environment: environment vars for DPG containers</li></ul> |

#### 5) Understanding mongo-init.js file
mongo-init.js file is embedded within the MongoDb container while we create the container.
The purpose of this file is to define the username and password that the backend API SpringBoot application (dpgBankDemo) uses to authenticate and perform CRUD operations on the embedded MongoDb.

The file contains some default values which, if changed, need to be replicated in the file dpgBankDemo/src/main/resources/applicatio.properties.

| mongo-init.js parameter | Usage | application.properties counterpart |
| --- | --- | --- |
| user | username used by java app to talk to MongoDb running in container | spring.data.mongodb.username |
| pwd | password used by java app to talk to MongoDb running in container | spring.data.mongodb.password |
| roles.db | actual database where all the collections are to be created and data stored and retrieved | spring.data.mongodb.database |

If you change any of these properties, change should be in both the places.

### Running demo from pre-built images
#### 1) List of images
| Service | Image |
| --- | --- |
| proxy | ciphertrust/learn:banking-demo-backend-proxy |
| mongodb | mongo:latest |
| frontend | ciphertrust/learn:banking-demo-ui |
| api | ciphertrust/learn:banking-demo-backend-api |
| ciphertrust | thalesciphertrust/ciphertrust-data-protection-gateway:latest |

### Running demo from source
#### 1) Update UI .env file
update the .env file in ui folder with the IP address of the server where you want to deploy this docker based application
```
REACT_APP_BACKEND_IP_ADDRESS=localhost
```
#### 2) List of images
| Service | Image |
| --- | --- |
| proxy | build from ./apiProxy/Dockerfile |
| mongodb | mongo:latest |
| frontend | build from ./ui/Dockerfile |
| api | build from ./dpgBankDemo/Dockerfile |
| ciphertrust | thalesciphertrust/ciphertrust-data-protection-gateway:latest |

Sample docker-compose-template.yml in this case -
```
version: '3.7'

services:      
  mongodb:
    image: mongo:latest
    container_name: mongodb
    restart: always
    command: --quiet
    environment:
      MONGO_INITDB_ROOT_USERNAME: <admin_username>
      MONGO_INITDB_ROOT_PASSWORD: <admin_password>
      MONGO_INITDB_DATABASE: dpg
    ports:
      - 27017:27017
    volumes:
      - ./mongo/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
      
  frontend:
    stdin_open: true
    container_name: frontend
    build:
      dockerfile: Dockerfile
      context: ./ui
    volumes:
      - /app/node_modules
      - ./ui:/app
    ports:
      - 3000:3000
      
  api:
    environment:
      - CMIP: GENERATED_BY_POWERSHELL
      - CM_USERNAME: GENERATED_BY_POWERSHELL
      - CM_PASSWORD: GENERATED_BY_POWERSHELL
      - CM_USER_SET_ID: GENERATED_BY_POWERSHELL
    container_name: api
    build:
      dockerfile: Dockerfile
      context: ./dpgBankDemo
    ports:
      - 8080:8080
      
  proxy:
    container_name: proxy
    build:
      dockerfile: Dockerfile
      context: ./apiProxy
    ports:
      - 8081:8081

  ciphertrust:
    image: thalesciphertrust/ciphertrust-data-protection-gateway:latest
    container_name: ciphertrust
    environment:
      - REG_TOKEN=GENERATED_BY_POWERSHELL
      - DESTINATION_URL=http://api:8080
      - DPG_PORT=9005
      - TLS_ENABLED=false
      - KMS=GENERATED_BY_POWERSHELL
    ports:
      - 9005:9005
      
networks:
  db_net:
    driver: bridge
```

### Deploying and running demo
We are all set now, run the below command to deploy the docker containers that holds the demo application
```
# On Windows
.\deploy-demo-win-ps-71.ps1

# On Ubuntu
pwsh deploy-demo-win-ps-71.ps1
```
Once the script execution completes, open the demo using the URL -
```
localhost:3000
```
Register new account 
```
localhost:3000/userCreate
```
<kbd><img src="https://user-images.githubusercontent.com/111074839/204612767-7527e353-a5e3-47e0-afce-5444b177c5d1.png"></kbd>

Login with new account
```
localhost:3000/login
```
<kbd><img src="https://user-images.githubusercontent.com/111074839/204613093-7350d3b4-1450-426e-944f-b47626c63497.png"></kbd>

Sensitive information is securely stored in the database
<kbd><img src="https://user-images.githubusercontent.com/111074839/204615720-9311a6ad-aee9-485b-83a0-6585a5cde405.png"></kbd>

Personal information can be viewed by account owner...based on reveal policy created on CipherTrust Manager
<kbd><img src="https://user-images.githubusercontent.com/111074839/204616468-f2998f48-6fd2-4772-a5cd-e348c6549538.png"></kbd>
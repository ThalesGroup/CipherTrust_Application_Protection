# Sample Bank Application :: Turnkey Data Protection and Access Control

## About this sample app
This is a sample app that has been created to mimic some of the very basic functionalities of a banking app and showcase how adding a Thales Data Protection Gateway (DPG) can solve a really complex problem of apply data protection, reveal, and masking based on policies defined at a higher level. The purpose of this application is to take a regular multi tier application and add the DPG sidecar and make sure that the DPG sidecar simply intercepts the API calls and apply data protection and data reveal based on certain polocies applied at the CipherTrust Manager platform.
This application consists of -
* Frontend application written in React JS
* Authentication APIs (SpringBoot application) that take user credentials from frontend and validate/authorize request via CipherTrust Manager API interface, also acquire token that will provide authorization to the logged in user to view a particular dataset as plain text, plain text with some charcaters masked, and finally a completly encrypted form of sensitive information
* Middleware APIs (SpringBoot application) that will cater to the sensitive requests like storing the PCI data encrypyted and revealing data as per policies
* MongoDB container to provide persistence layer
* Last, but not the least, DPG sidecar container

The demo application comes with the utility files such as -
* docker-compose.yml and Dockerfile that would suffice to get the demo environment up and running with just one command
* PowerShell utility script to configure the CipherTrust platform so that it can support the demo

Pre-requisites
* Java 14 to compile the springboot application code
* Docker itself

## Architecture
![image](https://user-images.githubusercontent.com/111074839/189827400-3377df49-b028-4f32-bca3-087ce61fb0c4.png)

### Understanding the Architecture in few bullets
* User authenticates with Ciphertrust Manager to acquire JWT token
* Admin applies protection and reveal policy suitable for the data that needs to be protected
* Ciphertrust Data Protection Gateway (DPG) running as a sidecar within your existing environment
* All APIs are routed to DPG so that correct policies are applied

## Quick Start Guide
### Ciphertrust Manager
Download your free copy of Ciphertrust Manager from https://ciphertrust.io and deploy the OVA file in your environment or deploy Ciphertrust in your favorite cloud. Follow the quick start guide at https://thalesdocs.com/ctp/cm/latest/get_started/deployment/index.html#deployment-environments to get the Ciphertrust up and running.

### Deployment Data Protection Gateway and run demo
The helper script provided along with the project would help you in setting up some boilerplate configuration that will allow you to run the demo out of the box.
The helper script can be modified to suit your needs very easily with very little to no knowledge of PowerShell need, simply replace the values of some of the variables and the script will yake care of rest. Some of the more relevant parameters and what they mean are below -

Parameter | Description
--- | ---
username | CM username with admin privileges
password | CM password corresponding to the above user
kms | CM IP for your ciphertrust manager instance
counter | suffix for the various assets that would be created to easily differentiate between those assets

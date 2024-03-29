# Introduction

This project leverages React and Tailwind CSS framework for creating all the UI components and pages.
There are other libraries used and can be found in the package.json file.

As with other applications in this project, the ui project is also designed to run inside a container, but can be run directly as well - check the section below for steps.

## Building and Running application from source

This application works directly with the apiProxy and dpgBankDemo applications.
apiProxy and dpgBankDemo provides the APIs, Data Access Layer (DAL), and business logic to store the data in MongoDb or retrieve it.

If you wish to run this "ui" application directly you can do so following below steps.

### 1) Update .env file
.env file in the root directory of "ui" application contains a variable "REACT_APP_BACKEND_IP_ADDRESS".
This variable points to the IP or FQDN of the server where apiProxy and dpgBankDemo are running.
If you are running all the three applications on same machine, you may choose the value "localhost", else put the IP or FQDN of that machine.

If you are using the docker-compose.yml file auto generated by the PowerShell script, you do not need to make any change as the docker-compose.yml will automatically pass the correct value to the "ui" container.

### 2) Build the project
If running for the first time, excecute the following command -

`npm install`

This will pull all the required modules from npm repo and add them to node_modules folder inside the "ui" directory.
You would need to install nodeJs and npm to make it work.

### 3) Running the project
Once the project is built successfully, you can run the project by executing the follow command -

`npm run start`

Once executed, you should be able to launch the UI application by opening below URL in your preffered browser (note: this has been tested with Chrome browser only)

localhot:3000

## Other dependencies
To ensure this UI application works as desired, you would need to start the apiProxy, dpgBankingDemo, MongoDb, and ciphertrust DPG applications as well. Please follow the README inside other project directories to understand how you can run them locally.
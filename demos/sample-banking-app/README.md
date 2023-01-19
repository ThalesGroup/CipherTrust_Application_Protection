# Turnkey demo bank app with Data Protection Gateway
This sample is a turnkey docker based multi-tier application that demonstrates data protection with Thales Ciphertrust Manager Community Edition. Securing credit card information as well as user's personal information like SSN is not only a value add, but a compliance mandated requirement.
This project will let you
* Deploy a fully functional app including ReactJs based frontend, SpringBoot based REST API backend, and MongoDB based data persistence all within a single docker deployment
* Using a PowerShell script to automate all the configurations needed on Thales CipherTrust Manager to rub this demo

## Architecture
<kbd><img src="https://user-images.githubusercontent.com/111074839/189827400-3377df49-b028-4f32-bca3-087ce61fb0c4.png"></kbd>

## Getting Started
### Prerequisites
* On Windows
  * PowerShell > 3.x (recommended PowerShel 7.3.0)
  * Docker Desktop
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
### Network Requirements
Below ports need to be opened if firewall is there
<kbd><img src="https://user-images.githubusercontent.com/111074839/211354811-4f671792-c0ee-4515-8040-e56177c77618.png"></kbd>
### Quickstart
#### 1) Deploy Ciphertrust Manager (CM) community edition (Always Free)
To deploy Ciphertrust Manager, follow the link https://ciphertrust.io/ 
You can deploy Ciphertrust Manager in you favorite cloud environment or on local server/virtual machine
Detailed steps are available on CM web page above.
#### 2) Clone the repo 
Clone this repo on your Windows workstation
```
git clone https://github.com/anugram/BankingApp-CM29_DPG11.git
```
#### 3) Install required PowerShell modules 
Install YQ "YAML Parser" utility based on host OS (example Ubuntu)
```
sudo snap install yq
```


The helper PowerShell script bundled with this demo requires YAML module which can be installed using the command -
```
Install-Module -Name powershell-yaml -RequiredVersion 0.4.2
```
***You might require to add -Scope {CurrentUser} if not running as an administrator***
The PowerShell script at the root of this repo is a helper script that can get you started without understanding Ciphertrust Manager or any other internal details that may be overwhelming initially.
#### 4) Update UI .env file
update the .env file in ui folder with the IP address of the server where you want to deploy this docker based application
```
REACT_APP_BACKEND_IP_ADDRESS=1.2.3.4
```
#### 5) Configure PowerShell script
Once you have the CM installed and repo cloned, the only thing you need to change are some of the variables in the bundled ps1 file i.e. 'deploy-demo-win-ps.ps1'
Updated below variables at the top of the file
```
$username = "<CM Username>"
$password = "<CM Password>"
$kms = "<CM Hostname/IP>"
$counter = "suffix"
```
#### 6) Deploying and running demo
We are all set now, run the below command to deploy the docker containers that holds the demo application
```
# On Windows
.\deploy-demo-win-ps.ps1

# On Ubuntu
pwsh pwsh deploy-demo-win-ps-71.ps1
```
Once the script execution completes, open the demo using the URL -
```
SERVER_ADDRESS:3000
```
Register new account 
```
SERVER_ADDRESS:3000/userCreate
```
<kbd><img src="https://user-images.githubusercontent.com/111074839/204612767-7527e353-a5e3-47e0-afce-5444b177c5d1.png"></kbd>

Login with new account
```
SERVER_ADDRESS:3000/login
```
<kbd><img src="https://user-images.githubusercontent.com/111074839/204613093-7350d3b4-1450-426e-944f-b47626c63497.png"></kbd>

Sensitive information is securely stored in the database
<kbd><img src="https://user-images.githubusercontent.com/111074839/204615720-9311a6ad-aee9-485b-83a0-6585a5cde405.png"></kbd>

Personal information can be viewed by account owner...based on reveal policy created on CipherTrust Manager
<kbd><img src="https://user-images.githubusercontent.com/111074839/204616468-f2998f48-6fd2-4772-a5cd-e348c6549538.png"></kbd>


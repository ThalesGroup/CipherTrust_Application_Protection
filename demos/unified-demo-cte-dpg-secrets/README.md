# Table of Content
* [Learn more about Ansible script](Ansible.md)
* [Learn more about Docker image](Docker.md)
* [Learn more about the Helm chart](Helm.md)
* Rest everything is on this page

# Sample application using DPG, CTE for K8s, and CSM
This is a sample application to showcase how you can acheive data protection in your full-stack application deployed in Kubernetes in a fully transparent manner and even without requiring any application level code changes. Everything related to running this demo is available in open-source or free space and does not mandate any kind of licensing. Licensing will be required to try enterprise capabilities of Thales CipherTrust Data Security Platform (CDSP). 
This project will provide you - 
* A full stack sample application showcasing processing sensitive data like user's personal information, or payment related info, etc. It contains -
  * SpringBoot based REST API backend and embedded Database
  * ReactJS based frontend
  * Helm charts to deploy the full application stack as well as CDSP connectors
  * Docker image to automate configuration of CipherTrust Manager
  * Utility file to stitch everything together

## Prerequisites
* Existing Kubernetes Environment - cloud or on-prem
* Docker to automate CipherTrust Manager configuration for DPG and CTE for Kubernetes as well as create Helm Chart's values file
* Helm to deploy the application and connectors on Kubernetes
* CipherTrust Manager - community edition or enterprise edition with CiherTrust Secrets Manager (via Akeyless) enabled and configured
* An NFS server that will be used as a file storage backend to test CTE for Kubernetes 

## Network Requirements
You might have to open a few ports to ensure that application and CipherTrust components are reachable either internally or externally. We will cover this in more detail in below sections.

## Quickstart
#### 1) Deploy Ciphertrust Manager (CM) community edition (Always Free)
To deploy Ciphertrust Manager, follow the link https://cpl.thalesgroup.com/encryption/ciphertrust-platform-community-edition 
You can deploy Ciphertrust Manager in a cloud environment or on local server/virtual machine
Detailed steps are available on the Community Edition URL above.
#### 2) Clone the repo 
Clone this repo on your Windows workstation
```
git clone https://github.com/thalescpl-io/CipherTrust_Application_Protection
cd ./CipherTrust_Application_Protection/demos/unified-demo-cte-dpg-secrets
```
#### 3) Deploy demo using run.sh
To install the demo without Data Protection Gateway
```
./run.sh ANSIBLE=true CM_IP=<CM_IP> CM_USERNAME=<CM_USERNAME> CM_PASSWORD=<CM_PASSWORD> CA_ID=<LOCAL_CA_ID> KUBE_PUBLIC_IP=<IP/FQDN of Kubernetes Public access or Ingress> INSTALL_CTE=true SETUP_KUBE=true HELM_OP=install
```

| Variable | Description |
| --- | --- |
| CM_USERNAME | Username of CM instance which we want to configure to work with this demo  | 
| CM_PASSWORD | Password of the above CM user |
| CM_IP | IP address of FQDN of the CM instance e.g. 10.10.10.10 or example.com |
| CA_ID | ID of one of the local Certificate Authority from CipherTrust Manager, check image below on where to find it |
| KUBE_PUBLIC_IP | IP Address where the cluster's services are reachable, can be the IP address/hostname of the host machine or the IP/FQDN of an Ingress Controller. This is where UI service of the demo will find the API service |
| INSTALL_CTE | This will deploy CipherTrust Transparent Encryption agent on your Kubernetes cluster |
| SETUP_KUBE | If true, this will create Namespace, Storage Class, Persistent Volume Claim on your Kubernetes cluster. These files are auto generated for you by the [Ansible](Ansible.md) Playbook in the /tmp directory of the machine where this run.sh is being executed |
| HELM_OP | Can be either "install" or "upgrade". Install option will deploy UI and API service without Data Protection Gateway, while upgrade will setup with Data Protection Gateway. You have to first install before running upgrade |

Once installed, you may run below command to upgrade the deployment and add DPG to the deployment

```
./run.sh HELM_OP=upgrade
```

## References
### How to get Local CA ID
<kbd>![image](https://github.com/ThalesGroup/CipherTrust_Application_Protection/assets/111074839/cccd43d7-9387-4433-ad0d-69b1cc5d2408)</kbd>

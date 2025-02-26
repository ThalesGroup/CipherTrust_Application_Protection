# Crypto Agility with Thales CipherTrust RESTful Data Protection

## Pre-requisites
- Docker installed
- Kubernetes installed
- CipherTrust Manager installed

## Clone repo and deploy application
### Clone this repo
```
git clone https://github.com/thalescpl-io/CipherTrust_Application_Protection.git
```
### Build docker image
```
cd demos/cadp-crdp-bouncycastle-pr
docker build -t crdp-java-app:latest .
```
### Deploy in Kubernetes
Update deploy/deployment.yaml
| Parameter | Description | Example |
| --------- | ----------- | ------- |
| KEY_MANAGER_HOST | IP address or FQDN of CipherTrust Manager | "10.10.10.10" |
| PROTECTION_POLICY | Protection Policy name on CipherTrust Manager for CRDP | demo |
| SERVER_MODE | Whether to support or not TLS for CRDP | no-tls |
| REGISTRATION_TOKEN | Registration token to setup CRDP container | QGzmEELoHdDGPEB2aZg3ukyP3S6i7WEhNIjNiSOqmlGDXmAqc57mq0HTHuPUaQ9A |

Now deploy the application stack on Kubernetes
```
kubectl apply -f deploy/deployment.yaml
```

## Test APIs using an API client such as Postman
### Encrypt using BouncyCastle endpoint
<kbd>![image](https://github.com/user-attachments/assets/13bc6a1c-4ef4-4db4-b584-72ff12d26f5c)</kbd>

### Decrypt using BouncyCastle endpoint
<kbd>![image](https://github.com/user-attachments/assets/6253999c-0472-41c6-9c21-2e8db0dc3f40)</kbd>

### PROTECT using CRDP
<kbd>![image](https://github.com/user-attachments/assets/525bad33-e557-4939-9018-c7636b2523e4)</kbd>

### REVEAL Using CRDP
Plaintext
<kbd>![image](https://github.com/user-attachments/assets/a6b68629-a646-47df-b78d-bdad62197908)</kbd>

Masked
<kbd>![image](https://github.com/user-attachments/assets/274d565b-bba1-45fe-9e2c-da1e1728e45c)</kbd>

CipherText
<kbd>![image](https://github.com/user-attachments/assets/f1474c30-b09a-4802-ab05-c1493537d16e)</kbd>

## Creating access and protection policy on CipherTrust Manager 

## Crypto Agility with Central Management



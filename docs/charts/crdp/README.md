# CipherTrust RESTful Data Protection (CRDP) Helm Chart
This is a Helm chart for deploying CRDP within a pod in your Kubernetes environment

# Installation Instructions
## Download Chart Repository
```
helm repo add --force-update cdsp https://thalesgroup.github.io/CipherTrust_Application_Protection/
```

## Create custom values file
Create values file for your environment -
```
configuration:
  servermode: <servermode>
  kms: <IP/FQDN of CipherTrust Manager>
  rtoken: <REG_TOKEN>
```

| Parameter  | Description  | Required |
|---|---|--|
| kms  | IP address/Hostname of the CipherTrust Manager (CM) | Required |
| servermode  | Specifies the mode in which Client will communicate with CRDP. Valid options are <ul><li>no-tls</li> <li>tls-cert-opt</li> <li>tls-cert</li></ul>. Choose <ul><li>no-tls to disable TLS</li><li>tls-cert-opt to keep TLS enabled without certificate validation</li><li>tls-cert to enforce TLS with validation</li></ul> | Required |
| rtoken  | Application Registration Token from CM | Required |
| servercrt  | Certificate in case of TLS enabled | Optional |
| serverkey  | Private Key in case of TLS enabled | Optional |
| trustedca  | CA Certificate in case of TLS enabled | Optional |

## Install CRDP Chart
```
helm install -f values_crdp.yaml crdp cdsp/crdp
```

# Test APIs
## Using Postman
### Protect Data
<kbd>![image](https://github.com/ThalesGroup/CipherTrust_Application_Protection/assets/111074839/f3c92454-040c-4e80-a2b5-72c28e6ee44b)</kbd>

### Reveal Data
<kbd>![image](https://github.com/ThalesGroup/CipherTrust_Application_Protection/assets/111074839/920ae4f7-72b0-4f06-8ed9-2aa6a3892e1d)</kbd>


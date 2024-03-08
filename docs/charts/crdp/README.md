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
| servermode  | Specifies the mode in which Client will communicate with CRDP. Valid options are no-tls, tls-cert-opt, tls-cert. Choose no-tls to disable TLS, tls-cert-opt to keep TLS enabled without certificate validation or tls-cert to enforce TLS with validation | Required |
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
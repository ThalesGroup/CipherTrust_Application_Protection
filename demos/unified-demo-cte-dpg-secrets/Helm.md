# Introduction
Helm Chart repository is hosted on this repository's GitHub Pages, URL is https://thalesgroup.github.io/CipherTrust_Application_Protection/
The chart repository is also open source and is part of this GitHub repo.

Installing the Chart repository
```
helm repo add --force-update cdsp https://thalesgroup.github.io/CipherTrust_Application_Protection/
```

## Deploy the UI project chart
### Chart Details
Chart Name for the UI Service - cdsp/demo-cte-dpg-secrets-ui

### Values.yaml file
```
runlabel: uideployment

deployment:
  replicas: 1
  appimage: ciphertrust/learn:demo-dpg-cte-secrets-ui
  pullPolicy: IfNotPresent

service:
  name: svc-ui
  type: NodePort
  uiappname: ui-port
  uiappnodePort: 32080
  uiappPort: 3000
  uiapptargetPort: 3000

configuration:
  api_server_ip: <Kubernetes_Cluster_IP>
  api_server_port: 9000
```

## Deploy the API project chart without DPG
### Chart Details
Chart Name for the UI Service - cdsp/demo-cte-dpg-secrets-api

### Values.yaml file
```
runlabel: appserver

deployment:
  replicas: 1
  appimage: ciphertrust/learn:demo-dpg-cte-secrets-api
  pullPolicy: IfNotPresent

service:
  type: NodePort
  apiappname: api-port
  apiappnodePort: 32081
  apiappPort: 8080
  apiapptargetPort: 8080

configuration:
  addSideContainer: false
```

## Deploy the API project chart with DPG
### Chart Details
Chart Name for the UI Service - cdsp/demo-cte-dpg-secrets-api

### Values.yaml file
```
runlabel: appserver

deployment:
  replicas: 1
  appimage: ciphertrust/learn:demo-dpg-cte-secrets-api
  dpgimage: thalesciphertrust/ciphertrust-data-protection-gateway:1.1.0
  pullPolicy: IfNotPresent

service:
  type: NodePort
  apiappname: api-port
  apiappnodePort: 32081
  apiappPort: 8990
  apiapptargetPort: 8990

configuration:
  addSideContainer: true
  secretname: dpg-secret
  configmapname: dpg-configmap
  kms: <CM_IP>
  appurl: http://localhost:8080
  tlsenabled: false
  reg_token: <REG_TOKEN>
```

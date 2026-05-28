# Thales Data Protection Gateway (DPG) Quick Start Sample App

## Overview
This repository contains the source code for the DPG quick start sample application designed to demonstrate Thales CipherTrust Data Protection Gateway or DPG.
The usage of this application along with DPG is documented at [ThalesDocs](https://thalesdocs.com/ctp/con/dpg/latest/admin/dpg-quick-start/index.html).

## Building and Testing locally
Running directly
```
git clone https://github.com/ThalesGroup/CipherTrust_Application_Protection.git
cd demos/DPG-sample-app-code
go run server.go
```
To run as a docker container
```
docker build --no-cache -t app_server:latest . 
docker run --rm app_server:latest
```

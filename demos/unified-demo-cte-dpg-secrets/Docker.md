# Introduction
You may configure CipherTrust Manager Manually for CTE and DPG, or follow the instructions for [Ansible](Ansible.md), or we have created a helper Docker Image that does the same for you.

With this you just need to have Docker setup and everything can be cofigured to run this particular demo with single command.

## Install Docker Image
Image is hosted on Docker Hub with name and tag as - ciphertrust/automation:demo-dpg-cte-secrets-ansible
```
docker run --detach --privileged --name ansible --volume=/sys/fs/cgroup:/sys/fs/cgroup:rw --volume=/home/aj/.kube:/root/.kube --volume=/tmp:/tmp:rw --cgroupns=host ciphertrust/automation:demo-dpg-cte-secrets-ansible
```

## Run the docker container
```
docker exec --tty ansible env TERM=xterm ansible-playbook /root/run_demo.yml -e "CM_IP=192.168.2.233" -e "CM_USERNAME=admin" -e "CM_PASSWORD=ChangeIt01!" -e "LOCAL_CA_ID=50e566a1-9cff-4787-9741-d4f545f7657f" -e "ADD_DPG_FLAG=false" -e "SERVER_IP"="192.168.2.221" -e "SERVER_PORT"="9000" -v
```
Parameters as below -
| Name | Description | Comment |
|--|--|--|
| CM_IP | IP or FQDN of the CipherTrust Manager | |
| CM_USERNAME | Username for teh above CM | |
| CM_PASSWORD | Password of the above CM | |
| LOCAL_CA_ID | Certificate Authority ID for one of the Local CAs | |
| SERVER_IP | IP or FQDN of the Kubernetes cluster or the Ingress controller. UI service will reach API service on this IP | |

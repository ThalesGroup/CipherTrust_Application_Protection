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
docker exec --tty ansible env TERM=xterm ansible-playbook /root/run_demo.yml -e "CM_IP=<CM_IP>" -e "CM_USERNAME=<CM_USERNAME>" -e "CM_PASSWORD=<CM_PASSWORD>" -e "LOCAL_CA_ID=<LOCAL_CA_ID>" -e "ADD_DPG_FLAG=false" -e "SERVER_IP=<CLUSTER_OR_INGRESS_IP>" -e "SERVER_PORT"="9000" -e "NFS_IP=<NFS_SERVER_IP>" -v
```
Parameters as below -
| Name | Description |
|--|--|
| CM_IP | IP or FQDN of the CipherTrust Manager |
| CM_USERNAME | Username for teh above CM |
| CM_PASSWORD | Password of the above CM |
| LOCAL_CA_ID | Certificate Authority ID for one of the Local CAs |
| SERVER_IP | IP or FQDN of the Kubernetes cluster or the Ingress controller. UI service will reach API service on this IP |
| NFS_IP | IP or FQDN of the NFS Server IP |

## Ouput
This Docker image will configure the CipherTrust Manager for CTE and DPG that we need to run this demo.
This will also generate a bunch of files in /tmp directory that we can use to configure our Kubernetes cluster so that Persistent Volume Claim and the Storage Class are configured correctly. It will also create files for installing our Helm Charts correctly as described in the documentation for [Helm](Helm.md)

List of files created -
| Name | Description |
|--|--|
| namespace.yaml | Creates namespace |
| cm-token-secret.yaml | Creates secret file using the registration token created o CM |
| storage-class.yaml | Creates Storage Class using the secret and CM details |
| nfs-pv.yaml | Creates NFS type persistent volume, you would need to adjust the NFS server IP according to your requirements |
| nfs-pvc.yaml | Creates a PVC for the above PV |
| cte-pvc.yaml | Using the NFS PVC, create a CTE PVC that will apply the keys and policies using the registration token as auth mechanism |
| values_ui.yaml | Values files for deploying UI service by Helm |
| values_api.yaml | Values files for deploying API service without DPG by Helm |
| values_api_with_dpg.yaml | Values files for deploying API service along with DPG by Helm |

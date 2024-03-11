#!/bin/bash

for ARGUMENT in "$@"
do
   KEY=$(echo $ARGUMENT | cut -f1 -d=)

   KEY_LENGTH=${#KEY}
   VALUE="${ARGUMENT:$KEY_LENGTH+1}"

   export "$KEY"="$VALUE"
done

# docker run -d --restart unless-stopped -v /home/aj/registry-vol:/var/lib/registry -p 5000:5000 --name registry registry:2.7
# Setup Minikube cluster
if [ "$MINIKUBE" = "true" ];
then
  minikube stop
  minikube delete
  minikube start --memory 8192 --cpus 3
fi

# Push images to Docker Registry
if [ "$DOCKER" = "true" ];
then
  docker tag kubecon-demo-ui localhost:5000/kubecon-demo-ui
  docker tag kubecon-demo-api localhost:5000/kubecon-demo-api
  docker push localhost:5000/kubecon-demo-ui
  docker push localhost:5000/kubecon-demo-api
fi

# Set the Akeyless Vault token
if [ "$TOKEN" = "true" ];
then
  T=`akeyless auth --access-id "$CSM_ACCESS_ID" --access-key "$CSM_ACCESS_KEY" --json true | awk '/token/ { gsub(/[",]/,"",$2); print $2}'`
  rm -rf /home/$USER/.vault-token
  echo $T >> /home/$USER/.vault-token
  vault login token=$TOKEN
fi

# Run the Ansible script
if [ "$ANSIBLE" = "true" ];
then
  docker run --detach --privileged --name ansible --volume=/sys/fs/cgroup:/sys/fs/cgroup:rw --volume=/home/aj/.kube:/root/.kube --volume=/tmp:/tmp:rw --cgroupns=host ciphertrust/automation:demo-dpg-cte-secrets-ansible
  docker exec --tty ansible env TERM=xterm ansible-playbook /root/run_demo.yml -e "CM_IP=$CM_IP" -e "CM_USERNAME=$CM_USERNAME" -e "CM_PASSWORD=$CM_PASSWORD" -e "LOCAL_CA_ID=$CA_ID" -e "ADD_DPG_FLAG=false" -e "SERVER_IP=$KUBE_PUBLIC_IP" -e "SERVER_PORT=9000" -e "NFS_IP=$NFS_SERVER_IP" -v
fi

# Install CTE for kubernetes
if [ "$INSTALL_CTE" = "true" ];
then
  cd /tmp
  git clone https://github.com/thalescpl-io/ciphertrust-transparent-encryption-kubernetes.git
  cd ciphertrust-transparent-encryption-kubernetes
  ./deploy.sh
fi

# Apply k8s scripts
if [ "$SETUP_KUBE" = "true" ];
then
  pkill -f "port-forward"
  kubectl apply -f /tmp/namespace.yaml
  kubectl apply -f /tmp/cm-token-secret.yaml
  kubectl apply -f /tmp/storage-class.yaml
  kubectl apply -f /tmp/nfs-pv.yaml
  kubectl apply -f /tmp/nfs-pvc.yaml
  kubectl apply -f /tmp/cte-pvc.yaml
fi

# Pull Helm Repo
if [ "$PULL_HELM" = "true" ];
then
  helm repo add --force-update cdsp https://thalesgroup.github.io/CipherTrust_Application_Protection/
fi

# Helm Install Chart with custom values file
if [ "$HELM_OP" = "install" ];
then
  pkill -f port-forward
  helm install -f /tmp/values_api.yaml kubecon-demo-api cdsp/demo-cte-dpg-secrets-api --insecure-skip-tls-verify -n kubecon
  helm install -f /tmp/values_ui.yaml kubecon-demo-ui cdsp/demo-cte-dpg-secrets-ui --insecure-skip-tls-verify -n kubecon  
fi

# Helm Upgrade Chart with custom values file
if [ "$HELM_OP" = "upgrade" ];
then
  pkill -f port-forward
  helm delete kubecon-demo-api -n kubecon
  helm install -f /tmp/values_api_with_dpg.yaml kubecon-demo-api cdsp/demo-cte-dpg-secrets-api --insecure-skip-tls-verify -n kubecon
fi

# Enable Port-Forward if true
if [ "$PORT_FWD" = "true" ];
then
  RETRIES=0
  CHK_ROLLOUT="kubectl rollout status deployment/demo-cte-dpg-secrets-api -n kubecon"
  until $CHK_ROLLOUT || [ $RETRIES -eq 30 ]; do
    $CHK_ROLLOUT
    RETRIES=$((RETRIES + 1))
    sleep 5
  done
    
  if [ "$HELM_OP" = "install" ];
  then
    kubectl port-forward -n kubecon deployment/demo-cte-dpg-secrets-api 9000:8080 --address 0.0.0.0 &
  fi
  if [ "$HELM_OP" = "upgrade" ];
  then
    kubectl port-forward -n kubecon deployment/demo-cte-dpg-secrets-api 9000:8990 --address 0.0.0.0 &
  fi
  
  RETRIES=0
  CHK_ROLLOUT="kubectl rollout status deployment/demo-cte-dpg-secrets-ui -n kubecon"
  until $CHK_ROLLOUT || [ $RETRIES -eq 30 ]; do
    $CHK_ROLLOUT
    RETRIES=$((RETRIES + 1))
    sleep 5
  done
  kubectl port-forward -n kubecon deployment/demo-cte-dpg-secrets-ui 9001:3000 --address 0.0.0.0 &
fi

echo "=========================================="
echo "You may now access the UI of the demo at -"
echo "http://$KUBE_PUBLIC_IP:9001"
echo "=========================================="

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
  minikube start --memory 8192 --cpus 3 --insecure-registry="192.168.2.221/24"
fi

# Push images to Docker Registry
if [ "$DOCKER" = "true" ];
then
  docker tag kubecon-demo-ui localhost:5000/kubecon-demo-ui
  docker tag kubecon-demo-api localhost:5000/kubecon-demo-api
  docker push localhost:5000/kubecon-demo-ui
  docker push localhost:5000/kubecon-demo-api
fi

# Set the Vault token
if [ "$TOKEN" = "true" ];
then
  TOKEN=`akeyless auth --access-id "p-t23bmtngine1am" --access-key "+rhGnyiHPVpK8RdfYLi3YELowOnwhNzQrfg5jluqGXU=" --json true | awk '/token/ { gsub(/[",]/,"",$2); print $2}'`
  rm -rf /home/aj/.vault-token
  echo $TOKEN >> /home/aj/.vault-token
  vault login token=$TOKEN
fi

# Run the Ansible script
if [ "$ANSIBLE" = "true" ];
then
  docker run --detach --privileged --name ansible --volume=/sys/fs/cgroup:/sys/fs/cgroup:rw --volume=/home/aj/.kube:/root/.kube --volume=/tmp:/tmp:rw --cgroupns=host kubecon-demo-ansible

  docker exec --tty ansible env TERM=xterm ansible-playbook /root/run_demo.yml -e "CM_IP=192.168.2.233" -e "CM_USERNAME=admin" -e "CM_PASSWORD=ChangeIt01!" -e "LOCAL_CA_ID=50e566a1-9cff-4787-9741-d4f545f7657f" -e "ADD_DPG_FLAG=false" -e "SERVER_IP"="192.168.2.221" -e "SERVER_PORT"="9000" -v
fi

# Install CTE for kubernetes
if [ "$INSTALL_CTE" = "true" ];
then
  cd /home/aj/Desktop/kubeConSetup/cte/
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
  helm repo add --force-update cdsp https://anugram.github.io/helm-charts/
fi

# Helm Install Chart with custom values file
if [ "$HELM_OP" = "install" ];
then
  pkill -f port-forward
  helm install -f /tmp/values_api.yaml kubecon-demo-api cdsp/demo-cte-dpg-secrets-api --insecure-skip-tls-verify -n kubecon
  helm install -f /tmp/values_ui.yaml kubecon-demo-ui cdsp/demo-cte-dpg-secrets-ui --insecure-skip-tls-verify -n kubecon
  
  RETRIES=0
  CHK_ROLLOUT="kubectl rollout status deployment/demo-cte-dpg-secrets-api -n kubecon"
  until $CHK_ROLLOUT || [ $RETRIES -eq 30 ]; do
    $CHK_ROLLOUT
    RETRIES=$((RETRIES + 1))
    sleep 5
  done
  kubectl port-forward -n kubecon deployment/demo-cte-dpg-secrets-api 9000:8080
  
  RETRIES=0
  CHK_ROLLOUT="kubectl rollout status deployment/demo-cte-dpg-secrets-ui -n kubecon"
  until $CHK_ROLLOUT || [ $RETRIES -eq 30 ]; do
    $CHK_ROLLOUT
    RETRIES=$((RETRIES + 1))
    sleep 5
  done
  kubectl port-forward -n kubecon deployment/demo-cte-dpg-secrets-ui 9001:3000
fi

# Helm Upgrade Chart with custom values file
if [ "$HELM_OP" = "upgrade" ];
then
  pkill -f port-forward
  kubectl port-forward -n kubecon deployment/demo-cte-dpg-secrets-ui 9001:3000
  
  helm upgrade -f /tmp/values_api_with_dpg.yaml kubecon-demo-api cdsp/demo-cte-dpg-secrets-api
  RETRIES=0
  CHK_ROLLOUT="kubectl rollout status deployment/demo-cte-dpg-secrets-api -n kubecon"
  until $CHK_ROLLOUT || [ $RETRIES -eq 30 ]; do
    $CHK_ROLLOUT
    RETRIES=$((RETRIES + 1))
    sleep 5
  done
  kubectl port-forward -n kubecon deployment/demo-cte-dpg-secrets-api 9000:8990
  
fi
  
if [ "$FAKE" = "true" ];
then
  echo "Fake Stuff"
fi
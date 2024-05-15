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

# Configure kubernetes and akelyess to work with each other
if [ "$SETUP_AKL" = "true" ];
then
  helm repo add external-secrets https://charts.external-secrets.io
  helm install external-secrets external-secrets/external-secrets -n kubecon --create-namespace

  #helm repo add akeyless https://akeylesslabs.github.io/helm-charts
  #helm repo update

  #kubectl create ns kubecon
  #kubectl label namespace kubecon name=kubecon

  #CM_IP_WITHOUT_PROTOCOL=$(echo ${CM_IP} | awk -F/ '{print $3}')

  #helm install aks akeyless/akeyless-secrets-injection --namespace kubecon --set AKEYLESS_ACCESS_ID=${access_id} --set AKEYLESS_API_KEY=${access_key} --set AKEYLESS_ACCESS_TYPE=${api_key} --set AKEYLESS_URL="https://${CM_IP}:8080"
fi

# if [ "$SETUP_AKL" = "true" ];
# then
#   akeyless create-role --name /CM/akl_role
#   akeyless assoc-role-am --role-name /CM/akl_role --am-name CM/akl_auth
#   akeyless set-role-rule --role-name /CM/akl_role --path /CM/'*' --capability read --capability list

#   helm repo add akeyless https://akeylesslabs.github.io/helm-charts
#   helm repo update
#   helm install aks akeyless/akeyless-secrets-injection --namespace kubecon -f /tmp/akeyless-helm-values.yaml
# fi

# Run the Ansible script
if [ "$ANSIBLE" = "true" ];
then
  akeyless delete-auth-method --name CMAPISecret
  akeyless delete-role --name "CMAPIRole" 
  output=$(akeyless create-auth-method --name CMAPISecret)
  access_id=$(echo "$output" | awk -F 'Access ID: ' '{print $2}' | awk -F ' - Access Key: ' '{print $1}' | tr -d '\n')
  access_key=$(echo "$output" | awk -F 'Access Key: ' '{print $2}' | tr -d '\n')
  akeyless create-role --name "CMAPIRole"
  akeyless set-role-rule --role-name "CMAPIRole" --path "/cm/*" --rule-type=item-rule --capability read --capability list --capability create
  akeyless assoc-role-am --role-name "CMAPIRole" --am-name "CMAPISecret"

  docker run --detach --privileged --name ansible --volume=/sys/fs/cgroup:/sys/fs/cgroup:rw --volume=/home/aj/.kube:/root/.kube --volume=/tmp:/tmp:rw --cgroupns=host ciphertrust/automation:star-demo-ansible
  docker exec --tty ansible env TERM=xterm ansible-playbook /root/run_demo.yml -e "CM_IP=$CM_IP" -e "CM_USERNAME=$CM_USERNAME" -e "CM_PASSWORD=$CM_PASSWORD" -e "LOCAL_CA_ID=$CA_ID" -e "ADD_DPG_FLAG=false" -e "SERVER_IP=$KUBE_PUBLIC_IP" -e "SERVER_PORT=9000" -e "NFS_IP=$NFS_SERVER_IP" -e "AKL_ACCESS_ID=$access_id" -e "AKL_ACCESS_KEY=$access_key" -e "AKEYLESS_API_ACCESS_ID=$access_id" -e "AKEYLESS_API_ACCESS_KEY=$access_key" -v
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
  akeyless delete-item --name /cm/cte_encoded_reg_token
  akeyless delete-item --name /cm/dpg_reg_token
  sh /tmp/akeyless-create-secrets.sh
  
  kubectl apply -f /tmp/akeyless-auth-secret.yaml -n kubecon
  kubectl apply -f /tmp/akl-external-secret-store.yaml -n kubecon
  sleep 5s
  kubectl apply -f /tmp/akl-external-secret.yaml -n kubecon
  sleep 5s

  pkill -f "port-forward"
  #kubectl apply -f /tmp/cm-token-secret.yaml
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
echo "$KUBE_PUBLIC_IP:9001"
echo "=========================================="
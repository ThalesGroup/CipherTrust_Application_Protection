# Configuring minikube and Jenkins to work together

```bash
kubectl create namespace jenkins
kubectl create serviceaccount jenkins-sa -n jenkins
```

```bash
kubectl create clusterrolebinding jenkins-sa-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=jenkins:jenkins-sa
```

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: jenkins-sa-token
  namespace: jenkins
  annotations:
    kubernetes.io/service-account.name: jenkins-sa
type: kubernetes.io/service-account-token
EOF
```

```bash
SECRET_NAME=$(kubectl get sa jenkins-sa -n jenkins -o jsonpath="{.secrets[0].name}")
SECRET_NAME=jenkins-sa-token
TOKEN=$(kubectl get secret $SECRET_NAME -n jenkins -o jsonpath="{.data.token}" | base64 -d)
CA_CRT=$(kubectl get secret $SECRET_NAME -n jenkins -o jsonpath="{.data['ca\.crt']}" | base64 -d)
```

```bash
CLUSTER_NAME=$(kubectl config view -o jsonpath='{.clusters[0].name}')
SERVER=$(kubectl config view -o jsonpath='{.clusters[0].cluster.server}')

cat <<EOF > jenkins-sa-kubeconfig.yaml
apiVersion: v1
kind: Config
clusters:
- name: $CLUSTER_NAME
  cluster:
    server: $SERVER
    certificate-authority-data: $(echo "$CA_CRT" | base64 | tr -d '\n')
contexts:
- name: jenkins
  context:
    cluster: $CLUSTER_NAME
    namespace: jenkins
    user: jenkins-sa
current-context: jenkins
users:
- name: jenkins-sa
  user:
    token: $TOKEN
EOF
```

```bash
kubectl port-forward -n kube-system \
  $(kubectl get pods -n kube-system -l component=kube-apiserver -o name) \
  8443:8443 --address 0.0.0.0 &
```
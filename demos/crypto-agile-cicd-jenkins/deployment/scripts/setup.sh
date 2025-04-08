#!/bin/bash

# Default parameter (equivalent to PowerShell's param)
CONFIG_GITLAB="${1:-no}"

# Variables
GITHUB_REPO="https://github.com/ThalesGroup/CipherTrust_Application_Protection"
GITLAB_URL="http://localhost"
GITLAB_ROOT_PASSWORD="ChangeIt01!"
REPO_NAME_UI="crestline-ui"
REPO_NAME_API="Crestline-api"
REPO_NAME_DEP="crestline-deployment"
JENKINS_ADMIN_PASSWORD="ChangeIt01!"
SCRIPTS_DIR=$(pwd)
GITLAB_API_URL="$GITLAB_URL/api/v4"
KUBE_CONFIG_TEST_PATH="kubeconfig"  # Replace with actual path on host
KUBE_CONFIG_PROD_PATH="kubeconfig"  # Replace with actual path on host
KUBE_CONFIG_SA_PATH="jenkins-sa-kubeconfig.yaml"
JENKINS_URL="http://localhost:8080"

export API_SERVER_IP="192.168.2.221"
export REGISTRY_ADDRESS_K8S="192.168.2.221:5000"

# Create directories
CERT_AND_KEY_DIR=$(dirname "$SCRIPTS_DIR")
CERTS_DIR="$CERT_AND_KEY_DIR/certs"
CONFIG_DIR="$CERT_AND_KEY_DIR/compose/config"

# Only generate certificates if they don't exist
CERT_FILE="$CERTS_DIR/domain.crt"
KEY_FILE="$CERTS_DIR/domain.key"

echo "Creating directories..."
mkdir -p "$CERTS_DIR"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "Generating self-signed certificate..."
    openssl req -x509 -newkey rsa:4096 -keyout "$KEY_FILE" -out "$CERT_FILE" -days 365 -nodes \
        -subj "/CN=localhost" -sha256
    if [ $? -ne 0 ]; then
        echo "Error: Failed to generate certificates."
        exit 1
    fi
    echo "PEM-format certificates generated successfully:"
    echo "Certificate: $CERT_FILE"
    echo "Private key: $KEY_FILE"
else
    echo "Certificates already exist, skipping generation:"
    echo "Certificate: $CERT_FILE"
    echo "Private key: $KEY_FILE"
fi

# Ensure Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install it first."
    exit 1
fi

# Create or retrieve GitLab personal access token for root (before starting services)
echo "Creating or retrieving GitLab personal access token for root..."
docker-compose up -d gitlab  # Start GitLab first
GITLAB_READY=false
TIMEOUT=600
ELAPSED=0
INTERVAL=10
while [ "$GITLAB_READY" != "true" ] && [ $ELAPSED -lt $TIMEOUT ]; do
    if curl -s --head "$GITLAB_URL/users/sign_in" | grep -q "200"; then
        GITLAB_READY=true
        echo "GitLab is ready for token creation!"
    else
        echo "Waiting for GitLab... ($ELAPSED of $TIMEOUT seconds elapsed)"
        sleep $INTERVAL
        ELAPSED=$((ELAPSED + INTERVAL))
    fi
done
if [ "$GITLAB_READY" != "true" ]; then
    echo "Error: GitLab failed to start within 10 minutes."
    exit 1
fi

TOKEN_SCRIPT="token = PersonalAccessToken.find_by_description('Jenkins Integration'); unless token; token = PersonalAccessToken.create!(user: User.find_by_username('root'), name: 'Jenkins Integration', scopes: ['api'], expires_at: Date.today + 365); end; puts token.token"
TOKEN=$(docker exec gitlab gitlab-rails runner "$TOKEN_SCRIPT" | tail -n 1)
if [ -z "$TOKEN" ]; then
    echo "Error: Failed to create or retrieve GitLab access token."
    exit 1
fi
echo "GitLab token: $TOKEN"
export GITLAB_PERSONAL_ACCESS_TOKEN="$TOKEN"  # Set env var before starting all services

if [ ! -f "$KUBE_CONFIG_TEST_PATH" ]; then
    echo "Error: kubeconfig file not found at path: $KUBE_CONFIG_TEST_PATH"
    exit 1
fi

KUBE_CONFIG_FILE="$SCRIPTS_DIR/$KUBE_CONFIG_TEST_PATH"
# Read and encode
BASE64=$(base64 -w 0 "$KUBE_CONFIG_FILE")
export KUBECONFIG_BASE64="$BASE64"
echo -e "\n✅ KUBECONFIG_BASE64 environment variable set successfully."

KUBE_CONFIG_SA_FILE="$SCRIPTS_DIR/$KUBE_CONFIG_SA_PATH"
# Read and encode
BASE64_SA=$(base64 -w 0 "$KUBE_CONFIG_SA_FILE")
export KUBECONFIG_SA_BASE64="$BASE64_SA"
echo -e "\n✅ KUBECONFIG_SA_BASE64 environment variable set successfully."

# Start all services
echo "Starting Jenkins, GitLab, and Registry..."
docker compose build
if [ $? -eq 0 ]; then
    docker compose up -d
fi

# Check GitLab readiness
echo "Checking if GitLab is ready at $GITLAB_URL/users/sign_in..."
GITLAB_READY=false
TIMEOUT=600
ELAPSED=0
while [ "$GITLAB_READY" != "true" ] && [ $ELAPSED -lt $TIMEOUT ]; do
    if curl -s --head "$GITLAB_URL/users/sign_in" | grep -q "200"; then
        GITLAB_READY=true
        echo "GitLab is ready!"
    else
        echo "GitLab not ready yet..."
        sleep 10
        ELAPSED=$((ELAPSED + 10))
    fi
done
if [ "$GITLAB_READY" != "true" ]; then
    echo "Error: GitLab failed to start within 5 minutes. Check logs with 'docker logs gitlab'."
    docker logs gitlab
    exit 1
fi

if [ "$CONFIG_GITLAB" = "yes" ]; then
    # Ensure GitLab root password is set correctly
    echo "Ensuring GitLab root password is set to $GITLAB_ROOT_PASSWORD..."
    docker exec gitlab gitlab-rails runner "user = User.find_by_username('root'); if user.password != '$GITLAB_ROOT_PASSWORD'; user.password = '$GITLAB_ROOT_PASSWORD'; user.password_confirmation = '$GITLAB_ROOT_PASSWORD'; user.save!; end"

    echo "Allowing local requests from web hooks and services..."
    ALLOW_LOCAL_SCRIPT="ApplicationSetting.current.update!(allow_local_requests_from_web_hooks_and_services: true)"
    docker exec gitlab gitlab-rails runner "$ALLOW_LOCAL_SCRIPT"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to perform GitLab local request configuration"
        exit 1
    fi

    # Create GitLab projects
    create_project() {
        local REPO_NAME=$1
        RUBY_SCRIPT=$(cat <<EOF
begin
  user = User.find_by_username('root')
  unless user
    puts "ERROR: Root user not found"
    exit 1
  end
  namespace = Namespace.find_by_path('root')
  unless namespace
    puts "ERROR: Root namespace not found"
    exit 1
  end
  project = Project.find_by_full_path("root/$REPO_NAME")
  if project
    puts "Project already exists"
  else
    project = Projects::CreateService.new(
      user,
      name: '$REPO_NAME',
      path: '$REPO_NAME',
      namespace_id: namespace.id,
      visibility_level: 20
    ).execute
    if project.persisted?
      puts "Project created successfully"
    else
      puts "ERROR: #{project.errors.full_messages.join(', ')}"
      exit 1
    end
  end
rescue => e
  puts "ERROR: #{e.message}"
  exit 1
end
EOF
)
        echo "Creating GitLab project '$REPO_NAME'..."
        echo "$RUBY_SCRIPT" | docker exec -i gitlab gitlab-rails runner -
        if [ $? -ne 0 ]; then
            echo "Error: Failed to create GitLab project '$REPO_NAME'"
            exit 1
        fi
    }

    create_project "$REPO_NAME_UI"
    create_project "$REPO_NAME_API"
    create_project "$REPO_NAME_DEP"

    # Clone GitHub repo locally
    echo "Cloning GitHub repository..."
    BRANCH_NAME="crypto-agility-jenkins"
    SOURCE_FOLDER_UI="demos/crypto-agile-cicd-jenkins/power-company-ui"
    SOURCE_FOLDER_API="demos/crypto-agile-cicd-jenkins/power-company-api"
    SOURCE_FOLDER_DEP="demos/crypto-agile-cicd-jenkins/deployment"
    rm -rf github-repo
    git config --global core.longpaths true
    git clone --branch "$BRANCH_NAME" --single-branch "$GITHUB_REPO" github-repo
    if [ $? -ne 0 ]; then
        echo "Error: Failed to clone GitHub repository. Check the URL, branch name, or your network."
        exit 1
    fi

    # Push UI app to GitLab
    push_to_gitlab() {
        local SOURCE_FOLDER=$1
        local REPO_NAME=$2
        echo "Preparing to push '$SOURCE_FOLDER' to GitLab..."
        cd "$SCRIPTS_DIR/github-repo"
        SOURCE_FULL_PATH="$PWD/$SOURCE_FOLDER"
        if [ ! -d "$SOURCE_FULL_PATH" ]; then
            echo "Error: Source folder not found at $SOURCE_FULL_PATH"
            exit 1
        fi
        cd "$SOURCE_FULL_PATH"
        git init --initial-branch=main
        git add .
        git commit -m "Initial commit of filtered content from $SOURCE_FULL_PATH"
        git remote add origin "http://root:$GITLAB_ROOT_PASSWORD@localhost/root/$REPO_NAME.git" -f
        git push --set-upstream origin main
        if [ $? -ne 0 ]; then
            echo "Error: Failed to push to GitLab. Check GitLab logs or credentials."
            exit 1
        fi
    }

    push_to_gitlab "$SOURCE_FOLDER_UI" "$REPO_NAME_UI"
    push_to_gitlab "$SOURCE_FOLDER_API" "$REPO_NAME_API"
    push_to_gitlab "$SOURCE_FOLDER_DEP" "$REPO_NAME_DEP"
else
    echo "Skipping Git projects setup"
fi

# Wait for Jenkins to be fully ready
echo "Waiting for Jenkins to start..."
JENKINS_READY=false
TIMEOUT=600
ELAPSED=0
INTERVAL=10
while [ "$JENKINS_READY" != "true" ] && [ $ELAPSED -lt $TIMEOUT ]; do
    if curl -s --head "$JENKINS_URL/login" | grep -q "200"; then
        JENKINS_READY=true
        echo "Jenkins is ready!"
    else
        echo "Checking Jenkins availability... ($ELAPSED of $TIMEOUT seconds elapsed)"
        sleep $INTERVAL
        ELAPSED=$((ELAPSED + INTERVAL))
    fi
done
if [ "$JENKINS_READY" != "true" ]; then
    echo "Error: Jenkins failed to start within 10 minutes."
    exit 1
fi

cd "$SCRIPTS_DIR"
# Copy kubeconfig files to Jenkins
echo "Copying kubeconfig files to Jenkins..."
docker cp "$KUBE_CONFIG_TEST_PATH" custom_jenkins:/var/jenkins_home/kubeconfig-test
docker cp "$KUBE_CONFIG_PROD_PATH" custom_jenkins:/var/jenkins_home/kubeconfig-prod
docker cp "$KUBE_CONFIG_SA_PATH" custom_jenkins:/var/jenkins_home/jenkins-sa-kubeconfig.yaml

# Configure Jenkins
echo "Configuring Jenkins..."
docker cp configure-jenkins.sh custom_jenkins:/tmp/configure-jenkins.sh
docker exec custom_jenkins bash /tmp/configure-jenkins.sh
if [ $? -ne 0 ]; then
    echo "Error: Failed to configure Jenkins. Check the configure-jenkins.sh script or Jenkins logs."
    # exit 1
fi

# Fetch the project ID for crestline-deployment
echo "Fetching project ID for root/crestline-deployment..."
PROJECT_ID=$(curl -s --header "PRIVATE-TOKEN: $TOKEN" "$GITLAB_API_URL/projects?search=crestline-deployment" | \
    jq -r '.[] | select(.path_with_namespace == "root/crestline-deployment") | .id')
if [ -z "$PROJECT_ID" ]; then
    echo "Error: Could not find project root/crestline-deployment."
    exit 1
fi
echo "Found project ID: $PROJECT_ID"

# Configure GitLab Jenkins integration
echo "Configuring GitLab Jenkins integration..."
JENKINS_URL_INTERNAL="http://host.docker.internal:8080"
curl -s -X PUT \
    --header "PRIVATE-TOKEN: $TOKEN" \
    --header "Content-Type: application/json" \
    -d "{\"active\": true, \"push_events\": true, \"merge_requests_events\": false, \"jenkins_url\": \"$JENKINS_URL_INTERNAL\", \"project_name\": \"Deploy_Sample_App_ADP\", \"username\": \"admin\", \"password\": \"$JENKINS_ADMIN_PASSWORD\", \"enable_ssl_verification\": false}" \
    "$GITLAB_API_URL/projects/$PROJECT_ID/integrations/jenkins"
if [ $? -ne 0 ]; then
    echo "Error: Failed to configure Jenkins integration."
    exit 1
fi
echo "Jenkins integration configured successfully!"

echo "Setup complete!"
echo "Jenkins: $JENKINS_URL (admin/$JENKINS_ADMIN_PASSWORD)"
echo "GitLab: $GITLAB_URL (root/$GITLAB_ROOT_PASSWORD)"
echo "GitLab project: $GITLAB_URL/root/$REPO_NAME_DEP"
echo "Docker Registry: http://localhost:5000"
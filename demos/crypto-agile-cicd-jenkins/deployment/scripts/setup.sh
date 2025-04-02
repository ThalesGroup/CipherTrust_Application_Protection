#!/bin/bash

# Variables
GITHUB_REPO="https://github.com/your-username/your-repo.git"  # Replace with your GitHub repo URL
GITLAB_URL="http://localhost"  # Change to "http://localhost:8081" if port 80 is changed
GITLAB_ROOT_PASSWORD="ChangeIt01!"
REPO_NAME="your-repo"
JENKINS_ADMIN_PASSWORD="ChangeIt01!"

# Ensure Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install it first."
    exit 1
fi

# Start Docker Compose
echo "Starting Jenkins and GitLab..."
docker-compose up -d --build

# Wait longer for GitLab to initialize
echo "Waiting for GitLab to start (initial delay)..."
sleep 120  # Increased from 60 to 120 seconds

# Check GitLab readiness with detailed error handling
echo "Checking if GitLab is ready at ${GITLAB_URL}/users/sign_in..."
gitlab_ready=false
timeout=300  # 5 minutes timeout
elapsed=0
while [ "$gitlab_ready" = false ] && [ $elapsed -lt $timeout ]; do
    if curl -s -f "${GITLAB_URL}/users/sign_in" > /dev/null; then
        gitlab_ready=true
        echo "GitLab is ready!"
    else
        echo "GitLab not ready yet."
        sleep 10
        elapsed=$((elapsed + 10))
    fi
done

if [ "$gitlab_ready" = false ]; then
    echo "Error: GitLab failed to start within 5 minutes. Check logs with 'docker logs gitlab'."
    docker logs gitlab
    exit 1
fi

# Ensure GitLab root password is set correctly
echo "Ensuring GitLab root password is set to ${GITLAB_ROOT_PASSWORD}..."
docker exec gitlab gitlab-rails runner "user = User.find_by_username('root'); if user.password != '${GITLAB_ROOT_PASSWORD}'; user.password = '${GITLAB_ROOT_PASSWORD}'; user.password_confirmation = '${GITLAB_ROOT_PASSWORD}'; user.save!; end"

# Create GitLab project
echo "Creating GitLab project '${REPO_NAME}'..."

# Create the Ruby script content
ruby_script=$(cat <<EOF
begin
  # Find root user and namespace
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

  # Check if project exists
  project = Project.find_by_full_path('root/${REPO_NAME}')
  if project
    puts "Project already exists"
  else
    # Create project using the service
    project = Projects::CreateService.new(
      user,
      name: '${REPO_NAME}',
      path: '${REPO_NAME}',
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

# Execute the script by piping it to docker exec
echo "$ruby_script" | docker exec -i gitlab gitlab-rails runner -

# Check exit code
if [ $? -ne 0 ]; then
    echo "Failed to create GitLab project"
    exit 1
fi

# Wait for Jenkins to be fully ready
echo "Waiting for Jenkins to start..."
jenkins_ready=false
timeout=600  # 10 minutes timeout
elapsed=0
while [ "$jenkins_ready" = false ] && [ $elapsed -lt $timeout ]; do
    if curl -s -f "http://localhost:8080/login" > /dev/null; then
        jenkins_ready=true
        echo "Jenkins is ready!"
    else
        echo "Jenkins not ready yet."
        sleep 10
        elapsed=$((elapsed + 10))
    fi
done

if [ "$jenkins_ready" = false ]; then
    echo "Error: Jenkins failed to start within 10 minutes. Check logs with 'docker logs jenkins'."
    docker logs jenkins
    exit 1
fi

# Configure Jenkins
echo "Configuring Jenkins..."
docker cp scripts/configure-jenkins.sh jenkins:/tmp/configure-jenkins.sh
docker exec jenkins bash /tmp/configure-jenkins.sh
if [ $? -ne 0 ]; then
    echo "Error: Failed to configure Jenkins. Check the configure-jenkins.sh script or Jenkins logs."
    exit 1
fi

echo "Setup complete!"
echo "Jenkins: http://localhost:8080 (admin/${JENKINS_ADMIN_PASSWORD})"
echo "GitLab: ${GITLAB_URL} (root/${GITLAB_ROOT_PASSWORD})"
echo "GitLab project: ${GITLAB_URL}/root/${REPO_NAME}"
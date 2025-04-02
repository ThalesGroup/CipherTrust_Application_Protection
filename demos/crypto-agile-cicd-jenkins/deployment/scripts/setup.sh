#!/bin/bash

# Variables
GITHUB_REPO="https://github.com/your-username/your-repo.git"
GITLAB_URL="http://localhost"
GITLAB_ROOT_PASSWORD="ChangeIt01!"
REPO_NAME="your-repo"

# Start Docker Compose
echo "Starting Jenkins and GitLab..."
docker-compose up -d --build

# Wait for GitLab to be ready
echo "Waiting for GitLab to start..."
sleep 60 # Adjust based on system
until curl -s -f "$GITLAB_URL/users/sign_in" > /dev/null; do
    echo "GitLab not ready yet, waiting..."
    sleep 10
done

# Configure GitLab: Create project
echo "Configuring GitLab..."
docker exec gitlab gitlab-rails runner "user = User.find_by_username('root'); user.password = '$GITLAB_ROOT_PASSWORD'; user.save!"
docker exec gitlab gitlab-rails runner "project = Project.create!(namespace_id: 1, name: '$REPO_NAME', path: '$REPO_NAME', visibility_level: 20); project.add_owner(User.find_by_username('root'))"

# Clone GitHub repo locally
# echo "Cloning GitHub repository..."
# if [ ! -d "github-repo" ]; then
#     git clone "$GITHUB_REPO" github-repo
# fi

# Push to GitLab
# echo "Pushing to GitLab..."
# cd github-repo
# git remote add gitlab http://root:$GITLAB_ROOT_PASSWORD@localhost/root/$REPO_NAME.git
# git push gitlab main

# Configure Jenkins
echo "Configuring Jenkins..."
docker cp scripts/configure-jenkins.sh jenkins:/tmp/configure-jenkins.sh
docker exec jenkins bash /tmp/configure-jenkins.sh

echo "Setup complete! Jenkins: http://localhost:8080, GitLab: http://localhost"
echo "Jenkins admin: admin/ChangeIt01!, GitLab root: root/$GITLAB_ROOT_PASSWORD"
# Variables
$GITHUB_REPO = "https://github.com/your-username/your-repo.git"  # Replace with your GitHub repo URL
$GITLAB_URL = "http://localhost"  # Change to "http://localhost:8081" if port 80 is changed
$GITLAB_ROOT_PASSWORD = "ChangeIt01!"
$REPO_NAME = "your-repo"
$JENKINS_ADMIN_PASSWORD = "ChangeIt01!"

# Ensure Docker Compose is installed
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "Docker Compose is not installed. Please install it first."
    exit 1
}

# Start Docker Compose
Write-Host "Starting Jenkins and GitLab..."
docker-compose up -d --build

# Wait longer for GitLab to initialize
Write-Host "Waiting for GitLab to start (initial delay)..."
Start-Sleep -Seconds 120  # Increased from 60 to 120 seconds

# Check GitLab readiness with detailed error handling
Write-Host "Checking if GitLab is ready at $GITLAB_URL/users/sign_in..."
$gitlabReady = $false
$timeout = 300  # 5 minutes timeout
$elapsed = 0
while (-not $gitlabReady -and $elapsed -lt $timeout) {
    try {
        $response = Invoke-WebRequest -Uri "$GITLAB_URL/users/sign_in" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $gitlabReady = $true
            Write-Host "GitLab is ready!"
        }
    } catch {
        Write-Host "GitLab not ready yet. Error: $($_.Exception.Message)"
        Start-Sleep -Seconds 10
        $elapsed += 10
    }
}
if (-not $gitlabReady) {
    Write-Host "Error: GitLab failed to start within 5 minutes. Check logs with 'docker logs gitlab'."
    docker logs gitlab
    exit 1
}

# Ensure GitLab root password is set correctly
Write-Host "Ensuring GitLab root password is set to $GITLAB_ROOT_PASSWORD..."
docker exec gitlab gitlab-rails runner "user = User.find_by_username('root'); if user.password != '$GITLAB_ROOT_PASSWORD'; user.password = '$GITLAB_ROOT_PASSWORD'; user.password_confirmation = '$GITLAB_ROOT_PASSWORD'; user.save!; end"

# Create GitLab project
Write-Host "Creating GitLab project '$REPO_NAME'..."
docker exec gitlab gitlab-rails runner "project = Project.find_by_full_path('root/$REPO_NAME'); unless project; project = Project.create!(namespace_id: 1, name: '$REPO_NAME', path: '$REPO_NAME', visibility_level: 20); project.add_owner(User.find_by_username('root')); end"

# Clone GitHub repo locally
# Write-Host "Cloning GitHub repository..."
# if (-not (Test-Path "github-repo")) {
#     git clone $GITHUB_REPO github-repo
#     if ($LASTEXITCODE -ne 0) {
#         Write-Host "Error: Failed to clone GitHub repository. Check the URL or your network."
#         exit 1
#     }
# }

# Push to GitLab
# Write-Host "Pushing to GitLab..."
# Set-Location github-repo
# git remote add gitlab http://root:$GITLAB_ROOT_PASSWORD@localhost/root/$REPO_NAME.git -f
# git push gitlab main
# if ($LASTEXITCODE -ne 0) {
#     Write-Host "Error: Failed to push to GitLab. Check GitLab logs or credentials."
#     exit 1
# }

# Wait for Jenkins to be fully ready
Write-Host "Waiting for Jenkins to start..."
$jenkinsReady = $false
$timeout = 600  # 10 minutes timeout
$elapsed = 0
while (-not $jenkinsReady -and $elapsed -lt $timeout) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/login" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $jenkinsReady = $true
            Write-Host "Jenkins is ready!"
        }
    } catch {
        Write-Host "Jenkins not ready yet. Error: $($_.Exception.Message)"
        Start-Sleep -Seconds 10
        $elapsed += 10
    }
}
if (-not $jenkinsReady) {
    Write-Host "Error: Jenkins failed to start within 10 minutes. Check logs with 'docker logs jenkins'."
    docker logs jenkins
    exit 1
}

# Configure Jenkins
Write-Host "Configuring Jenkins..."
docker cp scripts/configure-jenkins.sh jenkins:/tmp/configure-jenkins.sh
docker exec jenkins bash /tmp/configure-jenkins.sh
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to configure Jenkins. Check the configure-jenkins.sh script or Jenkins logs."
    exit 1
}

Write-Host "Setup complete!"
Write-Host "Jenkins: http://localhost:8080 (admin/$JENKINS_ADMIN_PASSWORD)"
Write-Host "GitLab: $GITLAB_URL (root/$GITLAB_ROOT_PASSWORD)"
Write-Host "GitLab project: $GITLAB_URL/root/$REPO_NAME"
# Variables
$GITHUB_REPO = "https://github.com/ThalesGroup/CipherTrust_Application_Protection"  # Replace with your GitHub repo URL
$GITLAB_URL = "http://localhost"  # Change to "http://localhost:8081" if port 80 is changed
$GITLAB_ROOT_PASSWORD = "ChangeIt01!"
$REPO_NAME_UI = "crestline-ui"
$REPO_NAME_API = "Crestline-api"
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
Write-Host "Creating GitLab project '$REPO_NAME_UI'..."
#docker exec gitlab gitlab-rails runner "project = Project.find_by_full_path('root/$REPO_NAME'); unless project; project = Project.create!(namespace_id: 1, name: '$REPO_NAME', path: '$REPO_NAME', visibility_level: 20); project.add_owner(User.find_by_username('root')); end"

$rubyScriptUI = @"
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
  project = Project.find_by_full_path('root/$REPO_NAME_UI')
  if project
    puts "Project already exists"
  else
    # Create project using the service
    project = Projects::CreateService.new(
      user,
      name: '$REPO_NAME_UI',
      path: '$REPO_NAME_UI',
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
"@

$rubyScriptAPI = @"
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
  project = Project.find_by_full_path('root/$REPO_NAME_API')
  if project
    puts "Project already exists"
  else
    # Create project using the service
    project = Projects::CreateService.new(
      user,
      name: '$REPO_NAME_API',
      path: '$REPO_NAME_API',
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
"@

# Execute the script by piping it to docker exec
$rubyScriptUI | docker exec -i gitlab gitlab-rails runner -

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create GitLab project '$REPO_NAME_UI'"
    exit 1
}

# Execute the script by piping it to docker exec
$rubyScriptAPI | docker exec -i gitlab gitlab-rails runner -

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create GitLab project '$REPO_NAME_API'"
    exit 1
}

# Clone GitHub repo locally
Write-Host "Cloning GitHub repository..."
$BRANCH_NAME = "crypto-agility-jenkins"
$SOURCE_FOLDER_UI = "demos/crypto-agile-cicd-jenkins/power-company-ui"
$SOURCE_FOLDER_API = "demos/crypto-agile-cicd-jenkins/power-company-api"
if (-not (Test-Path "github-repo")) {
    git clone --branch $BRANCH_NAME --single-branch $GITHUB_REPO github-repo
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to clone GitHub repository. Check the URL, branch name, or your network."
        exit 1
    }
}

# Push UI app to GitLab
Write-Host "Preparing to push '$SOURCE_FOLDER_UI' to GitLab..."
Set-Location github-repo
# Create a temporary directory for the filtered content
$TEMP_DIR_UI = "$env:TEMP\gitlab-push-ui"
New-Item -ItemType Directory -Path $TEMP_DIR_UI -Force | Out-Null

# Copy only the desired folder content
Copy-Item -Path $SOURCE_FOLDER_UI\* -Destination $TEMP_DIR_UI -Recurse -Force

# Initialize new git repo with just the filtered content
Set-Location $TEMP_DIR_UI
git init --initial-branch=main
git add .
git commit -m "Initial commit of filtered content from $SOURCE_FOLDER_UI"


git remote add origin http://root:$GITLAB_ROOT_PASSWORD@localhost/root/$REPO_NAME_UI.git -f
git push --set-upstream origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to push to GitLab. Check GitLab logs or credentials."
    exit 1
}

# Push API app to GitLab
Write-Host "Preparing to push '$SOURCE_FOLDER_API' to GitLab..."
Set-Location github-repo
# Create a temporary directory for the filtered content
$TEMP_DIR_API = "$env:TEMP\gitlab-push-api"
New-Item -ItemType Directory -Path $TEMP_DIR_API -Force | Out-Null

# Copy only the desired folder content
Copy-Item -Path $SOURCE_FOLDER_API\* -Destination $TEMP_DIR_API -Recurse -Force

# Initialize new git repo with just the filtered content
Set-Location $TEMP_DIR_API
git init --initial-branch=main
git add .
git commit -m "Initial commit of filtered content from $SOURCE_FOLDER_API"


git remote add origin http://root:$GITLAB_ROOT_PASSWORD@localhost/root/$REPO_NAME_API.git -f
git push --set-upstream origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to push to GitLab. Check GitLab logs or credentials."
    exit 1
}

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
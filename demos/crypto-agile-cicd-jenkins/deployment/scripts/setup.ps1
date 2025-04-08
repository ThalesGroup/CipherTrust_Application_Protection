param(
    [string]$configGitlab = "no"
)

# Variables
$GITHUB_REPO = "https://github.com/ThalesGroup/CipherTrust_Application_Protection"  # Replace with your GitHub repo URL
$GITLAB_URL = "http://localhost"
$GITLAB_ROOT_PASSWORD = "ChangeIt01!"
$REPO_NAME_UI = "crestline-ui"
$REPO_NAME_API = "Crestline-api"
$REPO_NAME_DEP = "crestline-deployment"
$JENKINS_ADMIN_PASSWORD = "ChangeIt01!"
$SCRIPTS_Dir = Get-Location
$GITLAB_API_URL = "$GITLAB_URL/api/v4"
$KUBE_CONFIG_TEST_PATH = "kubeconfig"  # Replace with actual path on host
$KUBE_CONFIG_PROD_PATH = "kubeconfig"  # Replace with actual path on host
$KUBE_CONFIG_SA_PATH = "jenkins-sa-kubeconfig.yaml"
$JENKINS_URL = "http://localhost:8080"

$env:API_SERVER_IP = "192.168.2.221"
$env:REGISTRY_ADDRESS_K8S = "192.168.2.216:5000"

# Create directories
$certAndKeyDir = Split-Path -Parent $SCRIPTS_Dir
$certsDir = "$certAndKeyDir/certs"
$configDir = "$certAndKeyDir/compose/config"

# Only generate certificates if they don't exist or are invalid
$certFile = "$certsDir\domain.crt"
$keyFile = "$certsDir\domain.key"

Write-Host "Creating directories..."
New-Item -ItemType Directory -Force -Path $certsDir
New-Item -ItemType Directory -Force -Path $configDir

if (-not (Test-Path $certFile) -or -not (Test-Path $keyFile)) {
    # Create certificate
    $cert = New-SelfSignedCertificate `
        -Subject "CN=localhost" `
        -KeyAlgorithm RSA `
        -KeyLength 4096 `
        -NotBefore (Get-Date) `
        -NotAfter (Get-Date).AddYears(1) `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -KeyExportPolicy Exportable `
        -KeySpec Signature `
        -HashAlgorithm SHA256

    # Export certificate in PEM format
    $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
    $certPem = "-----BEGIN CERTIFICATE-----`n"
    $certPem += [Convert]::ToBase64String($certBytes, [System.Base64FormattingOptions]::InsertLineBreaks)
    $certPem += "`n-----END CERTIFICATE-----"
    [System.IO.File]::WriteAllText("$certsDir\domain.crt", $certPem)

    # Export private key in PEM format
    $password = ConvertTo-SecureString -String "YourPassword123!" -Force -AsPlainText
    $pfxBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Pfx, $password)
    $pfx = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($pfxBytes, $password, [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::Exportable)

    if ($PSVersionTable.PSVersion.Major -ge 7) {
        # PowerShell 7+ method
        $keyBytes = $pfx.GetRSAPrivateKey().ExportPkcs8PrivateKey()
        $keyPem = "-----BEGIN PRIVATE KEY-----`n"
        $keyPem += [Convert]::ToBase64String($keyBytes, [System.Base64FormattingOptions]::InsertLineBreaks)
        $keyPem += "`n-----END PRIVATE KEY-----"
    } else {
        # Windows PowerShell fallback
        $rsa = $pfx.PrivateKey -as [System.Security.Cryptography.RSACryptoServiceProvider]
        $keyPem = "-----BEGIN RSA PRIVATE KEY-----`n"
        $keyPem += [Convert]::ToBase64String($rsa.ExportCspBlob($true), [System.Base64FormattingOptions]::InsertLineBreaks)
        $keyPem += "`n-----END RSA PRIVATE KEY-----"
    }

    [System.IO.File]::WriteAllText("$certsDir\domain.key", $keyPem)
    
    Write-Host "PEM-format certificates generated successfully:"
    Write-Host "Certificate: $certsDir\domain.crt"
    Write-Host "Private key: $certsDir\domain.key"
}
else 
{
    Write-Host "Certificates already exist, skipping generation:"
    Write-Host "Certificate: $certFile"
    Write-Host "Private key: $keyFile"
}

# Ensure Docker Compose is installed
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "Docker Compose is not installed. Please install it first."
    exit 1
}

# Create or retrieve GitLab personal access token for root (before starting services)
Write-Host "Creating or retrieving GitLab personal access token for root..."
docker-compose up -d gitlab  # Start GitLab first
$gitlabReady = $false
$timeout = 600
$elapsed = 0
$interval = 10
while (-not $gitlabReady -and $elapsed -lt $timeout) {
    try {
        $response = Invoke-WebRequest -Uri "$GITLAB_URL/users/sign_in" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $gitlabReady = $true
            Write-Progress -Activity "Waiting for GitLab" -Status "GitLab is ready!" -PercentComplete 100 -Completed
            Write-Host "GitLab is ready for token creation!"
        }
    } catch {
        $percentComplete = [math]::Min(($elapsed / $timeout) * 100, 99)  # Cap at 99% until success
        $secondsRemaining = $timeout - $elapsed        
        Write-Progress -Activity "Waiting for GitLab" -Status "Checking availability... ($elapsed of $timeout seconds elapsed)" -PercentComplete $percentComplete -SecondsRemaining $secondsRemaining
        Start-Sleep -Seconds $interval
        $elapsed += $interval
    }
}
if (-not $gitlabReady) {
    Write-Progress -Activity "Waiting for GitLab" -Status "Error: GitLab failed to start within 10 minutes." -PercentComplete 100 -Completed
    Write-Host "Error: GitLab failed to start within 10 minutes."
    exit 1
}
$tokenScript = "token = PersonalAccessToken.find_by_description('Jenkins Integration'); unless token; token = PersonalAccessToken.create!(user: User.find_by_username('root'), name: 'Jenkins Integration', scopes: ['api'], expires_at: Date.today + 365); end; puts token.token"
$token = docker exec gitlab gitlab-rails runner "$tokenScript" | Select-Object -Last 1
if (-not $token) {
    Write-Host "Error: Failed to create or retrieve GitLab access token."
    exit 1
}
Write-Host "GitLab token: $token"
$env:GITLAB_PERSONAL_ACCESS_TOKEN = $token  # Set env var before starting all services

if (-Not (Test-Path $KUBE_CONFIG_TEST_PATH)) {
    Write-Error "kubeconfig file not found at path: $KUBE_CONFIG_TEST_PATH"
    exit 1
}


$KUBE_CONFIG_FILE = Join-Path -Path ($SCRIPTS_Dir) -ChildPath $KUBE_CONFIG_TEST_PATH
# Read and encode
$base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($KUBE_CONFIG_FILE))

# Set environment variable
$env:KUBECONFIG_BASE64 = $base64
Write-Host "`n✅ KUBECONFIG_BASE64 environment variable set successfully."

$KUBE_CONFIG_SA_FILE = Join-Path -Path ($SCRIPTS_Dir) -ChildPath $KUBE_CONFIG_SA_PATH
# Read and encode
$base64_sa = [Convert]::ToBase64String([IO.File]::ReadAllBytes($KUBE_CONFIG_SA_FILE))

# Set environment variable
$env:KUBECONFIG_SA_BASE64 = $base64_sa
Write-Host "`n✅ KUBECONFIG_SA_BASE64 environment variable set successfully."

# Start all services
Write-Host "Starting Jenkins, GitLab, and Registry..."
docker compose build
if ($LASTEXITCODE -eq 0) {
    docker compose up -d
}

# Check GitLab readiness with detailed error handling
Write-Host "Checking if GitLab is ready at $GITLAB_URL/users/sign_in..."
$gitlabReady = $false
$timeout = 600  # 5 minutes timeout
$elapsed = 0
$interval = 10
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

if ($configGitlab -eq "yes") {
    # Ensure GitLab root password is set correctly
    Write-Host "Ensuring GitLab root password is set to $GITLAB_ROOT_PASSWORD..."
    docker exec gitlab gitlab-rails runner "user = User.find_by_username('root'); if user.password != '$GITLAB_ROOT_PASSWORD'; user.password = '$GITLAB_ROOT_PASSWORD'; user.password_confirmation = '$GITLAB_ROOT_PASSWORD'; user.save!; end"

    Write-Host "Allowing local requests from web hooks and services..."
    $allowLocalScript = "ApplicationSetting.current.update!(allow_local_requests_from_web_hooks_and_services: true)"

    docker exec gitlab gitlab-rails runner "$allowLocalScript"

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to perform GitLab local request configuration"
        exit 1
    }

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

    Write-Host "Creating GitLab project '$REPO_NAME_API'..."

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

    Write-Host "Creating GitLab project '$REPO_NAME_DEP'..."

    $rubyScriptDEP = @"
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
  project = Project.find_by_full_path('root/$REPO_NAME_DEP')
  if project
    puts "Project already exists"
  else
    # Create project using the service
    project = Projects::CreateService.new(
      user,
      name: '$REPO_NAME_DEP',
      path: '$REPO_NAME_DEP',
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

    # Execute the script by piping it to docker exec
    $rubyScriptDEP | docker exec -i gitlab gitlab-rails runner -

    # Check exit code
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create GitLab project '$rubyScriptDEP'"
        exit 1
    }

    # Clone GitHub repo locally
    #Get-ChildItem -Path github-repo -Recurse | Remove-Item -force -recurse
    #Remove-Item github-repo -Force 
    Write-Host "Cloning GitHub repository..."
    $BRANCH_NAME = "crypto-agility-jenkins"
    $SOURCE_FOLDER_UI = "demos/crypto-agile-cicd-jenkins/power-company-ui"
    $SOURCE_FOLDER_API = "demos/crypto-agile-cicd-jenkins/power-company-api"
    $SOURCE_FOLDER_DEP = "demos/crypto-agile-cicd-jenkins/deployment"
    #if (-not (Test-Path "github-repo")) {
    git config --global core.longpaths true
    git clone --branch $BRANCH_NAME --single-branch $GITHUB_REPO github-repo
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to clone GitHub repository. Check the URL, branch name, or your network."
        exit 1
    }
    #}

    # Push UI app to GitLab
    Write-Host "Preparing to push '$SOURCE_FOLDER_UI' to GitLab..."
    Set-Location github-repo
    # Create a temporary directory for the filtered content
    $SOURCE_FULL_PATH_UI = Join-Path -Path (Get-Location) -ChildPath $SOURCE_FOLDER_UI

    if (-not (Test-Path $SOURCE_FULL_PATH_UI)) {
        Write-Host "Error: Source folder not found at $SOURCE_FULL_PATH_UI"
        exit 1
    }

    # Initialize new git repo with just the filtered content
    Set-Location $SOURCE_FULL_PATH_UI
    git init --initial-branch=main
    git add .
    git commit -m "Initial commit of filtered content from $SOURCE_FULL_PATH_UI"


    git remote add origin http://root:$GITLAB_ROOT_PASSWORD@localhost/root/$REPO_NAME_UI.git -f
    git push --set-upstream origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to push to GitLab. Check GitLab logs or credentials."
        exit 1
    }

    # Push API app to GitLab
    Write-Host "Preparing to push '$SOURCE_FOLDER_API' to GitLab..."
    Set-Location (Join-Path -Path $SCRIPTS_DIR -ChildPath "github-repo")
    # Create a temporary directory for the filtered content
    $SOURCE_FULL_PATH_API = Join-Path -Path (Get-Location) -ChildPath $SOURCE_FOLDER_API

    if (-not (Test-Path $SOURCE_FULL_PATH_API)) {
        Write-Host "Error: Source folder not found at $SOURCE_FULL_PATH_API"
        exit 1
    }

    # Initialize new git repo with just the filtered content
    Set-Location $SOURCE_FULL_PATH_API
    git init --initial-branch=main
    git add .
    git commit -m "Initial commit of filtered content from $SOURCE_FULL_PATH_API"


    git remote add origin http://root:$GITLAB_ROOT_PASSWORD@localhost/root/$REPO_NAME_API.git -f
    git push --set-upstream origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to push to GitLab. Check GitLab logs or credentials."
        exit 1
    }

    # Push Deployment scripts (Jenkinsfile) to GitLab
    Write-Host "Preparing to push '$SOURCE_FOLDER_DEP' to GitLab..."
    Set-Location (Join-Path -Path $SCRIPTS_DIR -ChildPath "github-repo")
    # Create a temporary directory for the filtered content
    $SOURCE_FULL_PATH_DEP = Join-Path -Path (Get-Location) -ChildPath $SOURCE_FOLDER_DEP

    if (-not (Test-Path $SOURCE_FULL_PATH_DEP)) {
        Write-Host "Error: Source folder not found at $SOURCE_FULL_PATH_DEP"
        exit 1
    }

    # Initialize new git repo with just the filtered content
    Set-Location $SOURCE_FULL_PATH_DEP
    git init --initial-branch=main
    git add Jenkinsfile
    git add app-deployment.yaml
    git commit -m "Initial commit of filtered content from $SOURCE_FULL_PATH_DEP"

    git remote add origin http://root:$GITLAB_ROOT_PASSWORD@localhost/root/$REPO_NAME_DEP.git -f
    git push --set-upstream origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to push to GitLab. Check GitLab logs or credentials."
        exit 1
    }
}
else {
    Write-Host "Skipping Git projects setup"
}


# Wait for Jenkins to be fully ready
Write-Host "Waiting for Jenkins to start..."
$jenkinsReady = $false
$timeout = 600
$elapsed = 0
$interval = 10
while (-not $jenkinsReady -and $elapsed -lt $timeout) {
    try {
        $response = Invoke-WebRequest -Uri "$JENKINS_URL/login" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $jenkinsReady = $true
            Write-Progress -Activity "Waiting for Jenkins" -Status "Jenkins is ready!" -PercentComplete 100 -Completed
            Write-Host "Jenkins is ready!"
        }
    } catch {
        $percentComplete = [math]::Min(($elapsed / $timeout) * 100, 99)
        $secondsRemaining = $timeout - $elapsed
        Write-Progress -Activity "Waiting for Jenkins" -Status "Checking availability... ($elapsed of $timeout seconds elapsed)" -PercentComplete $percentComplete -SecondsRemaining $secondsRemaining
        Start-Sleep -Seconds $interval
        $elapsed += $interval
    }
}
if (-not $jenkinsReady) {
    Write-Progress -Activity "Waiting for Jenkins" -Status "Error: Jenkins failed to start within 10 minutes." -PercentComplete 100 -Completed
    Write-Host "Error: Jenkins failed to start within 10 minutes."
    #docker logs jenkins
    exit 1
}

Set-Location $SCRIPTS_DIR
# Copy kubeconfig files to Jenkins
Write-Host "Copying kubeconfig files to Jenkins..."
docker cp $KUBE_CONFIG_TEST_PATH custom_jenkins:/var/jenkins_home/kubeconfig-test
docker cp $KUBE_CONFIG_PROD_PATH custom_jenkins:/var/jenkins_home/kubeconfig-prod
docker cp $KUBE_CONFIG_SA_PATH custom_jenkins:/var/jenkins_home/jenkins-sa-kubeconfig.yaml

# Configure Jenkins
Write-Host "Configuring Jenkins..."
Set-Location $SCRIPTS_DIR
docker cp configure-jenkins.sh custom_jenkins:/tmp/configure-jenkins.sh
docker exec custom_jenkins bash /tmp/configure-jenkins.sh
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to configure Jenkins. Check the configure-jenkins.sh script or Jenkins logs."
    #exit 1
}

# Create or retrieve GitLab personal access token for root
# Write-Host "Creating or retrieving GitLab personal access token for root..."
# $tokenScript = "token = PersonalAccessToken.find_by_description('Jenkins Webhook'); unless token; token = PersonalAccessToken.create!(user: User.find_by_username('root'), name: 'Jenkins Webhook', scopes: ['api'], expires_at: Date.today + 365); end; puts token.token"
# $token = docker exec gitlab gitlab-rails runner "$tokenScript" | Select-Object -Last 1
# if (-not $token) {
#     Write-Host "Error: Failed to create or retrieve GitLab access token."
#     exit 1
# }
# Write-Host "GitLab token: $token"

# Set the token as an environment variable for Jenkins
# Write-Host "Setting GitLab token as environment variable for Jenkins..."
# $env:GITLAB_PERSONAL_ACCESS_TOKEN = $token
# docker-compose restart jenkins

# Wait for Jenkins to restart
# Start-Sleep -Seconds 30
# $jenkinsReady = $false
# $elapsed = 0
# while (-not $jenkinsReady -and $elapsed -lt $timeout) {
#     try {
#         $response = Invoke-WebRequest -Uri "$JENKINS_URL/login" -UseBasicParsing -ErrorAction Stop
#         if ($response.StatusCode -eq 200) {
#             $jenkinsReady = $true
#             Write-Host "Jenkins restarted successfully!"
#         }
#     } catch {
#         Write-Host "Jenkins not ready yet after restart. Error: $($_.Exception.Message)"
#         Start-Sleep -Seconds 10
#         $elapsed += 10
#     }
# }
# if (-not $jenkinsReady) {
#     Write-Host "Error: Jenkins failed to restart within 10 minutes."
#     exit 1
# }

# Fetch the project ID for crestline-deployment
Write-Host "Fetching project ID for root/crestline-deployment..."
$headers = @{
    "PRIVATE-TOKEN" = $token
    "Content-Type" = "application/json"
}
try {
    $projects = Invoke-RestMethod -Uri "$GITLAB_API_URL/projects?search=crestline-deployment" -Method Get -Headers $headers -ErrorAction Stop
    $projectId = ($projects | Where-Object { $_.path_with_namespace -eq "root/crestline-deployment" }).id
    if (-not $projectId) {
        Write-Host "Error: Could not find project root/crestline-deployment."
        exit 1
    }
    Write-Host "Found project ID: $projectId"
} catch {
    Write-Host "Error fetching project ID: $($_.Exception.Message)"
    exit 1
}

# Configure GitLab webhook for crestline-deployment
# Write-Host "Configuring GitLab webhook to trigger Jenkins..."
# $webhookUrl = "http://custom_jenkins:8080/gitlab-webhook/post"
# $headers = @{
#     "PRIVATE-TOKEN" = $token
#     "Content-Type" = "application/json"
# }
# $body = @{
#     url = $webhookUrl
#     push_events = $true
#     merge_requests_events = $false
# } | ConvertTo-Json
# try {
#     #$projectId = 3  # Adjust based on order of creation (crestline-deployment is third)
#     $response = Invoke-RestMethod -Uri "$GITLAB_API_URL/projects/$projectId/hooks" -Method Post -Headers $headers -Body $body -ErrorAction Stop
#     Write-Host "Webhook configured successfully!"
# } catch {
#     Write-Host "Error: Failed to configure webhook. Error: $($_.Exception.Message)"
#     exit 1
# }

# Configure GitLab Jenkins integration
Write-Host "Configuring GitLab Jenkins integration..."
$jenkinsUrl = "http://host.docker.internal:8080"
$body = @{
    active = $true
    push_events = $true
    merge_requests_events = $false
    jenkins_url = $jenkinsUrl
    project_name = "Deploy_Sample_App_ADP"
    username = "admin"
    password = $JENKINS_ADMIN_PASSWORD
    enable_ssl_verification = $false
} | ConvertTo-Json
try {
    $response = Invoke-RestMethod -Uri "$GITLAB_API_URL/projects/$projectId/integrations/jenkins" -Method Put -Headers $headers -Body $body -ErrorAction Stop
    Write-Host "Jenkins integration configured successfully!"
} catch {
    Write-Host "Error: Failed to configure Jenkins integration."
    Write-Host "Status Code: $($_.Exception.Response.StatusCode)"
    Write-Host "Status Description: $($_.Exception.Response.StatusDescription)"
    $responseStream = $_.Exception.Response.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($responseStream)
    $errorDetails = $reader.ReadToEnd()
    Write-Host "Error Details: $errorDetails"
    exit 1
}

Write-Host "Setup complete!"
Write-Host "Jenkins: $JENKINS_URL (admin/$JENKINS_ADMIN_PASSWORD)"
Write-Host "GitLab: $GITLAB_URL (root/$GITLAB_ROOT_PASSWORD)"
Write-Host "GitLab project: $GITLAB_URL/root/$REPO_NAME"
Write-Host "Docker Registry: http://localhost:5000"
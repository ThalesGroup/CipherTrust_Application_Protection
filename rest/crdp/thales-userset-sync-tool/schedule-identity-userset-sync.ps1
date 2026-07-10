param(
    [string]$ConfigFile = "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\identity-userset-sync.properties",
    [string]$JavaExe = "java",
    [string]$JarPath = "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\target\thales-userset-sync-tool-0.0.1-SNAPSHOT-all.jar",
    [string]$LogDir = "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\logs\identity-userset-sync",
    [string]$LockDir = "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\locks\identity-userset-sync",
    [string]$TrustStorePath = $env:JAVA_TRUSTSTORE_PATH,
    [string]$TrustStorePassword = $env:JAVA_TRUSTSTORE_PASSWORD,
    [string]$TrustStoreType = $env:JAVA_TRUSTSTORE_TYPE
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $LockDir) | Out-Null

if (Test-Path $LockDir) {
    Write-Host "Another identity userset sync appears to be running. Lock exists at $LockDir"
    exit 2
}

New-Item -ItemType Directory -Path $LockDir | Out-Null

try {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $logFile = Join-Path $LogDir "identity-userset-sync-$timestamp.log"
    $arguments = @()
    if ($TrustStorePath) {
        $arguments += "-Djavax.net.ssl.trustStore=$TrustStorePath"
    }
    if ($TrustStorePassword) {
        $arguments += "-Djavax.net.ssl.trustStorePassword=$TrustStorePassword"
    }
    if ($TrustStoreType) {
        $arguments += "-Djavax.net.ssl.trustStoreType=$TrustStoreType"
    }
    $arguments += @("-cp", $JarPath, "com.thales.usersets.tool.IdentityUserSetSyncTool", $ConfigFile)

    Write-Host "Starting identity userset sync"
    Write-Host "Config: $ConfigFile"
    Write-Host "Log: $logFile"
    if ($TrustStorePath) {
        Write-Host "TrustStore: $TrustStorePath"
    }

    & $JavaExe @arguments *>&1 | Tee-Object -FilePath $logFile
    exit $LASTEXITCODE
}
finally {
    if (Test-Path $LockDir) {
        Remove-Item -LiteralPath $LockDir -Force -Recurse
    }
}

#
# Script to find out license count for Oracle or MSSQL DB instances with the CAKM library loaded.
# Compatible with Windows environments using PowerShell.
#

param(
    # Specify the type of database to check: 'Oracle' or 'MSSQL'.
    # Defaults to 'Oracle'.
    [ValidateSet('Oracle', 'MSSQL')]
    [string]$DatabaseType = 'Oracle'
)

# Check for Administrator privileges, which are required for Get-Process -Module
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script requires administrative privileges to inspect process modules. Please re-run this script from an elevated PowerShell session (e.g., 'Run as Administrator')."
    # Using exit code 1 to indicate an error
    exit 1
}

# Initialize counter
$instanceCount = 0

# Build the service filter and library pattern dynamically based on the DatabaseType
$cakmLibPattern = ""
$serviceFilter = {}
if ($DatabaseType -eq 'Oracle') {
    $cakmLibPattern = "libcadp_pkcs11"
    $serviceFilter = {
        ($_.Name -like 'OracleService*') -and $_.Status -eq 'Running'
    }
} elseif ($DatabaseType -eq 'MSSQL') {
    $cakmLibPattern = "cakm_mssql_ekm"
    $serviceFilter = {
        ($_.Name -eq 'MSSQLSERVER' -or $_.Name -like 'MSSQL$*') -and $_.Status -eq 'Running'
    }
}

# Get all running database services to identify active instances
$dbServices = Get-Service | Where-Object $serviceFilter

if (-not $dbServices) {
    Write-Host "No running $DatabaseType services found."
    exit 0
}

Write-Host "Found running database services. Now checking for CAKM library..."

# Loop through each discovered service
foreach ($service in $dbServices) {
    $instanceId = ""
    $processName = ""
    
    Write-Host "----------------------------------------"
    Write-Host "Checking service: $($service.Name)"

    try {
        # Get the process associated with the service
        $serviceProcess = Get-CimInstance -ClassName Win32_Service -Filter "Name='$($service.Name)'" | Select-Object -ExpandProperty ProcessId
        
        if (-not $serviceProcess) {
            Write-Warning "Could not find process for the database service '$($service.Name)'. Skipping."
            continue
        }
        
        # Determine the DB type and find the main worker process
        if ($service.Name -like 'OracleService*') {
            $instanceId = $service.Name.Substring("OracleService".Length)
            $processName = "oracle.exe"
            Write-Host "Checking Oracle instance: $instanceId"
            $mainProcess = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$($serviceProcess)" | Where-Object { $_.Name -eq $processName }
            #Write-Host "mainProcess $mainProcess"
            if (-not $mainProcess) {
                Write-Warning "Could not find the main '$processName' process for service '$($service.Name)'. Skipping."
                continue
            }
        }
        elseif ($service.Name -eq 'MSSQLSERVER' -or $service.Name -like 'MSSQL$*') {
            # For MS SQL, the service process IS the main worker process.
            $instanceId = if ($service.Name -eq 'MSSQLSERVER') { 'MSSQLSERVER (Default)' } else { $service.Name.Substring("MSSQL$".Length) }
            $processName = "sqlservr.exe"
            Write-Host "Checking MS SQL instance: $instanceId"
            $mainProcess = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$($serviceProcess)" | Where-Object { $_.Name -eq $processName }
            if (-not $mainProcess) {
                Write-Warning "Could not find the main '$processName' process for SQL instance '$instanceId'. Skipping."
                continue
            }
        }

        $processId = $mainProcess.ProcessId
        Write-Host "Instance: $instanceId, Process Name: $processName, PID: $processId"

        # Get the list of loaded modules (DLLs) for the oracle.exe process
        # The -ErrorAction SilentlyContinue handles cases where the process exits unexpectedly or we lack permissions.
        $loadedModules = Get-Process -Id $processId -Module -ErrorAction SilentlyContinue
        #Write-Host "loadedModules $loadedModules"

        if ($null -eq $loadedModules) {
            Write-Warning "Could not inspect modules for process ID $processId due to insufficient permissions. Run as Administrator."
            continue
        }

        # Check if any loaded module matches the CAKM library pattern
        $cakmModule = $loadedModules | Where-Object { $_.ModuleName -match $cakmLibPattern }

        if ($cakmModule) {
            # In case multiple modules match, just use the first one for the message
            if ($DatabaseType -eq 'Oracle') {
                Write-Host "SUCCESS: CAKM for Oracle TDE is loaded for instance '$instanceId'."
            } else { # MSSQL
                Write-Host "SUCCESS: CAKM for SQLEKM is loaded for instance '$instanceId'."
            }
            $instanceCount++
        } else {
            Write-Host "INFO: CAKM library is NOT loaded for instance '$instanceId'."
        }

    } catch {
        Write-Warning "An error occurred while checking instance '$($service.Name)': $_"
    }
}

Write-Host "-------------------------------------------"
if ($DatabaseType -eq 'Oracle') {
    Write-Host "Total license count required for CAKM for Oracle TDE: $instanceCount"
} else {
    Write-Host "Total license count required for CAKM for SQLEKM: $instanceCount"
}
Write-Host "-------------------------------------------"


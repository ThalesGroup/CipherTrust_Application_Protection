#######################################################################################################################
# File:             Setup-CAKM_For_SQL.ps1                                                                            #
# Author:           Rick Leon, Professional Services                                                                  #
# Publisher:        Thales Group                                                                                      #
# Disclaimer:       THE SCRIPT IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT   #
#                   NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND            #
#                   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,      #
#                   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,    #
#                   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.           #
#                                                                                                                     #
# Copyright:        (c) 2024 Thales Group. All rights reserved.                                                       #
#                                                                                                                     #
#######################################################################################################################

<#
    .DESCRIPTION
    This script is designed to connect to a SQL server and automatically setup CipherTrust Application Key Management for Microsoft SQL. (CAKM for SQL)
    .PARAMETER SQLServer
    This is the target SQL Server where CAKM will be configured.
    .PARAMETER IntegratedAuth 
    Use the -IntegratedAuth switch to use the currently logged-on credential to connect to the SQL Sever.
    .PARAMETER SAUsername
    Enter the SA-Level user that will be used to connect to the SQL Server.
	.PARAMETER SAPass
    Enter the SA-Level Password. 
	WARNING This will pass a clear-text password. For full automation use the SQLServerCreds paramater and pass a PowerShell credential object.
	.PARAMETER SQLServerCreds
    Pass a PowerShell Credential object with the SQL Server Connection credentials.
    .PARAMETER Obfuscated
    Use CAKM Obfustraced Credentials for SQL Credential Username and Password.
    .PARAMETER ObfuscatedUser
    CAKM PassPhraseSecure Protected Username
    .PARAMETER ObfuscatedPass
    CAKM PassPhraseSecure Protected Password
    .PARAMETER CipherTrustCreds
    Pass a PowerShell Credential object with the CiphertTrust Manager username and password for the SQL Credential.
    .PARAMETER CMUser
    Enter CipherTrust Manager user name for SQL Credential
	.PARAMETER CMPass
    Enter CipherTrust Manager password
	WARNING This will pass a clear-text password. For full automation use the CipherTrustCreds paramater and pass a PowerShell credential object.
	.PARAMETER DomainUser
	Use this switch to user a CM Sub-domain User.
    .PARAMETER CMDomain
    (Optional) Specify the CipherTrust Manager domain where the key will be stored.
	.PARAMETER KeyDisposition
	Choose to Create a new Key or use an exisitng CipherTrust Manager Key.
    Options:
        - CREATE_NEW
        - OPEN_EXISITNG
        - MIGRATING_FROM_DSM
	.PARAMETER KeyName
	Name of Asymmetric Key for TDE
    .PARAMETER Force
    Use the -force switch to remove any prompts and run the command with the in-line paramaters. Any missing parameters will cause the setup to fail.
    .EXAMPLE
    This exmaples show's a completed command using generic usernames and passwords.
    
    .\Setup-CAKM_For_SQL.ps1 -SQLServer 192.168.1.18 -SAUsername sa -SAPass Thales123! -CMUser sqltdeuser -CMPass Thales123! -DomainUser -CMDomain DEV -KeyDisposition CREATE_NEW -KeyName CAKM_SETUP_SCRIPT_1_240613 -Force
#>
param(
    [Parameter()] [string] $SQLServer,
    [Parameter()] [switch] $Integratedauth,
    [Parameter()] [string] $SAUsername,
    [Parameter()] [string] $SAPass,
    [Parameter()] [pscredential] $SQLServerCreds,
    [Parameter()] [switch] $Obfuscated,
    [Parameter()] [string] $ObfuscatedUser,
    [Parameter()] [string] $ObfuscatedPass,
    [Parameter()] [pscredential] $CipherTrustCreds,
    [Parameter()] [string] $CMUser,
    [Parameter()] [string] $CMPass,
    [Parameter()] [switch] $DomainUser,
    [Parameter()] [string] $CMDomain,
    [Parameter()] [string] $KeyDisposition,
    [Parameter()] [string] $KeyName,
    [Parameter()] [switch] $Force
)

class CTMCredential {
    [string] $username
    [securestring] $password
    [string] $domain
}

$CMCredential = [CTMCredential]::new()

function Get-UserPassword {
         
    if(!$ciphertrustcreds){
        if($CMUser){ 
            $CMCredential.username = $CMUser
        }else{
            $CMCredential.username = Read-Host "Enter CipherTrust Manager user name for SQL Credential" 
        }
        if($CMPass){ 
            $CMCredential.password = ConvertTo-SecureString $CMPass -AsPlainText -Force
        }else{
            $CMCredential.password = Read-Host "Enter CipherTrust Manager password" -AsSecureString 
        }
    }else{
        $CMCredential.username = $ciphertrustcreds.UserName
        $CMCredential.password = $ciphertrustcreds.Password
    }
    if($DomainUser -and $CMDomain){
        $CMCredential.domain = $CMDomain
    }elseif($DomainUser -and !$CMDomain){ 
        $CMCredential.domain = Read-Host "Enter desired domain"
    }elseif(!$DomainUser -and $CMDomain){
        $CMCredential.domain = "root"
    }elseif(!$DomainUser -and !$CMDomain){
        $IntoDomain = Read-Host "Are you using a domain? (Y/N)"
        if($IntoDomain -eq "y"){
            $CMCredential.domain = Read-Host "Enter desired domain"
        }
    }

    Write-Debug $CMCredential.username
    Write-Debug $CMCredential.password
    Write-Debug $CMCredential.domain
}


if(($Obfuscated -or $ObfuscatedUser -or $ObfuscatedPass) -and ($CMUser -or $CMPass -or $CMCredential)){ return "Cannot mix Obfuscated and non-Obfuscated Credentials." }
if(!$sqlserver){ $sqlserver = Read-Host "Enter Target SQL Server" }
if(!$sqlservercreds){
    if(!$SAUsername){ $sausername = Read-Host "Enter SA-level User account" }
    if(!$SAPass){ [securestring]$sapass = Read-Host "Enter SA-level User password" -AsSecureString }
}


# This is a simple user/pass connection string.
# Feel free to substitute "Integrated Security=True" for system logins.
if(!$integratedauth){
    if($sapass -is [securestring]){
        $connString = "Data Source=$($sqlserver);Database=master;User ID=$($sausername);Password=$([Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sapass)))"
    }else{
        $connString = "Data Source=$($sqlserver);Database=master;User ID=$($sausername);Password=$($sapass)"
    }
}else{
    $connString = "Data Source=$($sqlserver);Database=master;Integrated Security=True"
}

Write-Debug $connString

#Create a SQL connection object
$conn = New-Object System.Data.SqlClient.SqlConnection $connString

try{
    #Attempt to open the connection
    $conn.Open()
    if($conn.State -eq "Open"){
        $sqlcmd = $conn.CreateCommand()
        $query = "SELECT name, database_id FROM sys.databases"
        $sqlcmd.CommandText = $query
        $adp = New-Object System.Data.SqlClient.SqlDataAdapter $sqlcmd
        $data = New-Object System.Data.DataSet
        $adp.Fill($data) | Out-Null
        $queryOutput = $data.Tables[0]
        Write-Debug $queryOutput
        
        #$conn.Close()
    }else{
        return "Unable to connect to Database."
    }
}catch{}   


#Enable advanced SQL options. 
$SQLQueryShowAdvOpts = "
    sp_configure 'show advanced options', 1 ;  
    RECONFIGURE WITH OVERRIDE ;
    "
$sqlcmd.CommandText = $SQLQueryShowAdvOpts
Write-Debug "Running script`n$($SQLQueryShowAdvOpts)"
$sqlcmd.ExecuteNonQuery() | Out-Null

#Enable EKM provider
$SQLQueryEnableEKM = "
    sp_configure 'EKM provider enabled', 1 ;  
    RECONFIGURE WITH OVERRIDE;
    "
$sqlcmd.CommandText = $SQLQueryEnableEKM
Write-Debug "Running script`n$($SQLQueryEnableEKM)"
$sqlcmd.ExecuteNonQuery() | Out-Null

#################################################################################################################
# Create a cryptographic provider, which we have chosen to call "CAKMforSQLProvider", based on an EKM provider

Write-Host "Creating Cryptographic Provider..."

# Maybe make the DLL Path customizeable?

$SQLQueryCreateCryptoProv="
    CREATE CRYPTOGRAPHIC PROVIDER CAKMforSQLProvider   
    FROM FILE = 'C:\Program Files\CipherTrust\CAKM For SQLServerEKM\cakm_mssql_ekm.dll' ;
    "

$sqlcmd.CommandText = $SQLQueryCreateCryptoProv
Write-Debug "Running script`n$($SQLQueryCreateCryptoProv)"
$sqlcmd.ExecuteNonQuery() | Out-Null

###################################################################
#Create a credential that will be used by system administrators.  

Write-Host "`nCreating SQL Credential for SA-level Account.`nThis credential is used by an SA-level account to ADD/CREATE keys from the CipherTrust Manager to SQL Server.`nIt will add an ASymmetric Key to [master].[sys].[asymmetrickeys].`nThe credential uses an account with Key Admin/Key Users permission in the CipherTrust Manager.`n"

if(!$Obfuscated){
    Get-UserPassword

    if($CMCredential.domain){
        $IdentString = $CMCredential.domain + "||" + $CMCredential.username
        [string]$IdentPass = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($CMCredential.password))
        $SQLCredName = "sa_cakm_tde_cred_" + $CMCredential.domain + "_domain"
    }else{
        $IdentString = $CMCredential.username
        [string]$IdentPass = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($CMCredential.password))
        $SQLCredName = "sa_cakm_tde_cred_root"
    }
}else{
    $IdentString = $ObfuscatedUser
    [string]$IdentPass = $ObfuscatedPass

    if($DomainUser -and $CMDomain){
        $SQLCredName = "sa_cakm_tde_cred_" + $CMDomain + "_domain"
    }else{
        $SQLCredName = "sa_cakm_tde_cred_root"
    }
}

$SQLQueryCreateSACred = "
    CREATE CREDENTIAL " + $SQLCredName + "
    WITH IDENTITY = '" + $IdentString + "',
    SECRET = '" + $IdentPass + "' 
    FOR CRYPTOGRAPHIC PROVIDER CAKMforSQLProvider ;
    "
$sqlcmd.CommandText = $SQLQueryCreateSACred
Write-Debug "Running script`n$($SQLQueryCreateSACred)"
$sqlcmd.ExecuteNonQuery() | Out-Null

#Add SA Credential to SA Level User

$SQLQueryCreateSACred = "
    ALTER LOGIN " + $SAUsername + "  
    ADD CREDENTIAL " + $SQLCredName +";
    "
$sqlcmd.CommandText = $SQLQueryCreateSACred
Write-Debug "Running script`n$($SQLQueryCreateSACred)"
$sqlcmd.ExecuteNonQuery() | Out-Null


#Create SQL Asymmetric Key

if(!$KeyDisposition){
    Write-Host "`nThis process can either create a new asymmetric key in CipherTrust Manager or use an existing key."
    Write-Host "`n1. Create New Key`n2. Use an Existing Key`n3. Migrating_from_DSM`n"

    $KeyDisposition = Read-Host "Selection "
}

switch($KeyDisposition){
    "1"{
        if(!$KeyName){ $KeyName = Read-Host "NOTE: Key Names CANNNOT include dashes. For separation, use underscores.`nEnter new key name " }
        $SQLQueryCreateNewKey = "
        USE master ;  
        CREATE ASYMMETRIC KEY " + $KeyName + "
        FROM PROVIDER CAKMforSQLProvider
        WITH ALGORITHM = RSA_2048,
        PROVIDER_KEY_NAME = '" + $KeyName + "',
        CREATION_DISPOSITION=CREATE_NEW;
        "
    }
    "CREATE_NEW"{
        if(!$KeyName){ $KeyName = Read-Host "NOTE: Key Names CANNNOT include dashes. For separation, use underscores.`nEnter new key name " }
        $SQLQueryCreateNewKey = "
        USE master ;  
        CREATE ASYMMETRIC KEY " + $KeyName + "
        FROM PROVIDER CAKMforSQLProvider
        WITH ALGORITHM = RSA_2048,
        PROVIDER_KEY_NAME = '" + $KeyName + "',
        CREATION_DISPOSITION=CREATE_NEW;
        "
    }
    "2"{
        if(!$KeyName){ $KeyName = Read-Host "Enter existing key name " }
        $SQLQueryCreateNewKey = "
        USE master ;  
        CREATE ASYMMETRIC KEY " + $KeyName + "
        FROM PROVIDER CAKMforSQLProvider 
        PROVIDER_KEY_NAME = '" + $KeyName + "',
        CREATION_DISPOSITION=OPEN_EXISTING;
        "
    }
    "OPEN_EXISTING"{
        if(!$KeyName){ $KeyName = Read-Host "Enter existing key name " }
        $SQLQueryCreateNewKey = "
        USE master ;  
        CREATE ASYMMETRIC KEY " + $KeyName + "
        FROM PROVIDER CAKMforSQLProvider 
        PROVIDER_KEY_NAME = '" + $KeyName + "',
        CREATION_DISPOSITION=OPEN_EXISTING;
        "
    }
    "MIGRATING_FROM_DSM"{
        if(!$KeyName){ $KeyName = Read-Host "Enter DSM key name " }
        $SQLQueryCreateNewKey = "
        USE master ;  
        CREATE ASYMMETRIC KEY CM_" + $KeyName + "
        FROM PROVIDER CAKMforSQLProvider 
        PROVIDER_KEY_NAME = '" + $KeyName + "',
        CREATION_DISPOSITION=OPEN_EXISTING;
        "
    }
}

$sqlcmd.CommandText = $SQLQueryCreateNewKey
Write-Debug "Running script`n$($SQLQueryCreateNewKey)"
$sqlcmd.ExecuteNonQuery() | Out-Null

######################################################################
# Create a credential that will be used by the Database Engine.  

if($CMCredential.domain){
    $SQLCAKMCredName = "cakm_tde_cred_" + $CMCredential.domain + "_domain"
}else{
    $SQLCAKMCredName = "cakm_tde_cred_root"
}

$SQLQueryCreateCAKMCredential = "
    CREATE CREDENTIAL " + $SQLCAKMCredName + "
    WITH IDENTITY = '" + $IdentString + "', -- CM User
    SECRET = '" + $IdentPass + "'
    FOR CRYPTOGRAPHIC PROVIDER CAKMforSQLProvider ;
    "

$sqlcmd.CommandText = $SQLQueryCreateCAKMCredential
Write-Debug "Running script`n$($SQLQueryCreateCAKMCredential)"
$sqlcmd.ExecuteNonQuery() | Out-Null
    

#####################################################
# Add a login used by the internal SQL TDE precesses

if($CMCredential.domain){
    $SQLCAKMLoginName = "cakm_tde_cred_" + $CMCredential.domain + "_domain_" + $KeyName
}else{
    $SQLCAKMLoginName = "cakm_tde_cred_root_" + $KeyName
}

$SQLQueryCreateCAKMTDELogin = "
    CREATE LOGIN " + $SQLCAKMLoginName + "   
    FROM ASYMMETRIC KEY " + $KeyName + " ;
    "

$sqlcmd.CommandText = $SQLQueryCreateCAKMTDELogin
Write-Debug "Running script`n$($SQLQueryCreateCAKMTDELogin)"
$sqlcmd.ExecuteNonQuery() | Out-Null
    
################################################
# Add the new credential to the CAKM TDE login.

$SQLQueryAddCAKMCredToTDELogin = "
    ALTER LOGIN " + $SQLCAKMLoginName + "   
    ADD CREDENTIAL " + $SQLCAKMCredName + " ;
    "

$sqlcmd.CommandText = $SQLQueryAddCAKMCredToTDELogin
Write-Debug "Running script`n$($SQLQueryAddCAKMCredToTDELogin)"
$sqlcmd.ExecuteNonQuery() | Out-Null


$conn.Close()
if($conn.Open()) {write-host "Connection Still Open"}
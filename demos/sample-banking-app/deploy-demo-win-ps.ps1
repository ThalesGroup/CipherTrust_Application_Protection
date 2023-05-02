#Some house keeping stuff
add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    public class TrustAllCertsPolicy : ICertificatePolicy {
        public bool CheckValidationResult(
            ServicePoint srvPoint, X509Certificate certificate,
            WebRequest request, int certificateProblem) {
            return true;
        }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy

Import-Module powershell-yaml

#########################
## Change Variables below
#########################
$username = "<admin_username>" # Username for CipherTrust Manager (CM) that has access to create resources
$password = "<admin_password>" # Password of the user above
$kms = "<IP_or_FQDN>" # IP Address or FQDN of the CipherTrust Manager
$protocol = "https" # Can be http or https
$counter = "demo" # counter is a unique prefix that you can add the all the assets created by this script to ensure uniqueness of your resources
$sampleUserPassword = "<strong_password>" # sampleUserPassword is the password that will be applied to sample users created by this script
$host_machine = "localhost" # IP Address or FQDN where you want to deploy this demo application
################################################################
## End
## Changing anything below this point may have undesired effects
################################################################

Write-Output "-----------------------------------------------------------------"
Write-Output "Next few steps will create boilerplate config on your CM instance"
Write-Output "-----------------------------------------------------------------"

#Invoke API for token generation
Write-Output "Getting token from Thales CipherTrust Manager..."
$Url = "https://$kms/api/v1/auth/tokens"
$Body = @{
    grant_type = "password"
    username = $username
    password = $password
}
$response = Invoke-RestMethod -Method 'Post' -Uri $Url -Body $body
$jwt = $response.jwt

#Generic header for next set of API calls
$headers = @{
    Authorization="Bearer $jwt"
}

$url = "https://$kms/api/v1/auth/self/user"
$response = Invoke-RestMethod -Method 'Get' -Uri $url -Headers $headers -ContentType 'application/json'
$userID = $response.user_id

#Create DPG Key
Write-Output "Creating DPG Key"
$url = "https://$kms/api/v1/vault/keys2"
$body = @{
    'name' = "dpgKey-$counter"
    'usageMask' = 3145740
    'algorithm' = 'aes'
    'size' = 256
    'unexportable' = $false
    'undeletable' = $false
    'meta' = @{
        'ownerId' = $userID
        'versionedKey' = $true
    }
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'    
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Key already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}

$keyID = $response.id

#Fetching local root CA ID
$url = "https://$kms/api/v1/ca/local-cas?subject=/C=US/ST=TX/L=Austin/O=Thales/CN=CipherTrust Root CA"
$response = Invoke-RestMethod -Method 'Get' -Uri $url -Headers $headers -ContentType 'application/json'
$caID = $response.resources[0].uri

#Creating network interface NAE
Write-Output "Creating NAE network interface..."
$url = "https://$kms/api/v1/configs/interfaces"
$body = @{
    'cert_user_field' = 'CN'
    'mode' = 'tls-cert-pw-opt'
    'auto_gen_ca_id' = $caId
    'trusted_cas' = @{
        'local' = @(
            $caId
            )
        'external' = @()
    }
    'port' = 9005
    'network_interface' = 'all'
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
    Write-Debug "Response: $($response)" 
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Interface already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}


#Creating Character Set
Write-Output "Creating Character Set..."

$url = "https://$kms/api/v1/data-protection/character-sets"
$body = @{
    'name' = "DPGAlphaNum-$counter"
    'range' = @('0030-0039', '0041-005A', '0061-007A')
    'encoding' = 'UTF-8'
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Charset already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$charSetId = $response.id

#Creating CVV Protection Policy
Write-Output "Creating Protection Policy for CVV Number..."
$url = "https://$kms/api/v1/data-protection/protection-policies"
$body = @{
    'name' = "text_ProtectionPolicy-$counter"
    'key' = "dpgKey-$counter"
    'tweak' = '1628462495815733'
    'tweak_algorithm' = 'SHA1'
    'algorithm' = 'FPE/FF1v2/UNICODE'
    'character_set_id' = $charSetId
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Protection Policy already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$textPolicyId = $response.id

#Creating CC Number Protection Policy
Write-Output "Creating Protection Policy for Credit Card Number..."
$url = "https://$kms/api/v1/data-protection/protection-policies"
$body = @{
    'name' = "CC_ProtectionPolicy-$counter"
    'key' = "dpgKey-$counter"
    'tweak' = '9828462495846783'
    'tweak_algorithm' = 'SHA1'
    'algorithm' = 'FPE/FF1v2/CARD10'
    'allow_single_char_input' = $false
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Protection Policy already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$ccPolicyId = $response.id

Write-Output "Creating sample users..."
#ccaccountowner, cccustomersupport, everyoneelse --- password is same for all...$sampleUserPassword
$users = "cccustomersupport"
foreach ($user in $users)
{
    $url = "https://$kms/api/v1/usermgmt/users"
    $body = @{
        'email' = "$user@local"
        'name' = $user
        'username' = $user
        'password' = $sampleUserPassword
        'app_metadata' = @{}
        'user_metadata' = @{}
    }
    $jsonBody = $body | ConvertTo-Json -Depth 5
    try {
        Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
    }
    catch {
        $StatusCode = $_.Exception.Response.StatusCode
        if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
            Write-Error "Error $([int]$StatusCode) $($StatusCode): User already exists"
        }
        elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
            Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
        }
        else {
            Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
        }
    }
}

#Creating User Sets
Write-Output "Creating PlainText User Set..."
$url = "https://$kms/api/v1/data-protection/user-sets"
$body = @{
    'name' = "plainttextuserset-$counter"
    'description' = "plain text user set for card account owner"
    'users' = @()
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Userset already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$plainTextUserSetId = $response.id

Write-Output "Creating Masked Data User Set..."
$url = "https://$kms/api/v1/data-protection/user-sets"
$body = @{
    'name' = "maskedtextuserset-$counter"
    'description' = "masked text user set for CS exec"
    'users' = @('cccustomersupport')
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Userset already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$maskedTextUserSetId = $response.id

Write-Output "Creating Encrypted Data User Set..."
$url = "https://$kms/api/v1/data-protection/user-sets"
$body = @{
    'name' = "enctextuserset-$counter"
    'description' = "encrypted text user set for everyone else"
    'users' = @()
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Userset already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$encTextUserSetId = $response.id

#Creating masking policy
Write-Output "Creating masking policy for CC..."
$url = "https://$kms/api/v1/data-protection/masking-formats"
$body = @{
    'name' = "cc_masking_format-$counter"
    'starting_characters' = 0
    'ending_characters' = 4
    'show' = $true
    'mask_char' = 'x'
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Masking Format already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$maskingPolicyId = $response.id

#Creating Access Policies
Write-Output "Creating Access Policy for Credit Card use case..."
$url = "https://$kms/api/v1/data-protection/access-policies"
$body = @{
    'name' = "last_four_show_access_policy-$counter"
    'description' = "CC Access Policy for credit card user set"
    'default_reveal_type' = 'Ciphertext'
    'user_set_policy' = @(
        @{
            'user_set_id' = $plainTextUserSetId
            'reveal_type' = 'Plaintext'
        },
        @{
            'user_set_id' = $maskedTextUserSetId
            'reveal_type' = 'Masked Value'
            'masking_format_id' = $maskingPolicyId
        },
        @{
            'user_set_id' = $encTextUserSetId
            'reveal_type' = 'Ciphertext'
        }
    )
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Access Policy already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$accessPolicyId = $response.id

#Creating Access Policies
Write-Output "Creating Access Policy for cvv use case..."
$url = "https://$kms/api/v1/data-protection/access-policies"
$body = @{
    'name' = "all_enc_access_policy-$counter"
    'description' = "CC Access Policy for CVV user set"
    'default_reveal_type' = 'Ciphertext'
    'user_set_policy' = @(
        @{
            'user_set_id' = $plainTextUserSetId
            'reveal_type' = 'Plaintext'
        },
        @{
            'user_set_id' = $maskedTextUserSetId
            'reveal_type' = 'Ciphertext'
        },
        @{
            'user_set_id' = $encTextUserSetId
            'reveal_type' = 'Ciphertext'
        }
    )
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Access Policy already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$accessPolicyId = $response.id

#This is the interesting step...defining DPG policies for the API endpoints
Write-Output "Creating DPG Policy for CC use case..."
$url = "https://$kms/api/v1/data-protection/dpg-policies"
$body = @{
    'name' = "cc_policy-$counter"
    'description' = 'DPG policy for credit card attributes'
    'proxy_config' = @(
        @{
            'api_url' = '/api/account/details/save'
            'json_request_post_tokens' = @(
                @{
                    'name' = 'details.ssn'
                    'operation' = 'protect'
                    'protection_policy' = "text_ProtectionPolicy-$counter"
                },@{
                    'name' = 'details.dob'
                    'operation' = 'protect'
                    'protection_policy' = "text_ProtectionPolicy-$counter"
                }
            )
        },
        @{
            'api_url' = '/api/account/card/save'
            'json_request_post_tokens' = @(
                @{
                    'name' = 'ccNumber'
                    'operation' = 'protect'
                    'protection_policy' = "CC_ProtectionPolicy-$counter"
                },
                @{
                    'name' = 'cvv'
                    'operation' = 'protect'
                    'protection_policy' = "text_ProtectionPolicy-$counter"
                }
            )
        },
        @{
            'api_url' = '/api/account/cards/{id}'
            'json_response_get_tokens' = @(
                @{
                    'name' = 'accounts.[*].cvv'
                    'operation' = 'reveal'
                    'protection_policy' = "text_ProtectionPolicy-$counter"
                    'access_policy' = "all_enc_access_policy-$counter"
                },@{
                    'name' = 'accounts.[*].ccNumber'
                    'operation' = 'reveal'
                    'protection_policy' = "CC_ProtectionPolicy-$counter"
                    'access_policy' = "last_four_show_access_policy-$counter"
                }
            )
        },
        @{
            'api_url' = '/api/account/details/{id}'
            'json_response_get_tokens' = @(
                @{
                    'name' = 'details.ssn'
                    'operation' = 'reveal'
                    'protection_policy' = "text_ProtectionPolicy-$counter"
                    'access_policy' = "last_four_show_access_policy-$counter"
                },@{
                    'name' = 'details.dob'
                    'operation' = 'reveal'
                    'protection_policy' = "text_ProtectionPolicy-$counter"
                    'access_policy' = "last_four_show_access_policy-$counter"
                }
            )
        },
        @{
            'api_url' = '/api/user/create'
            'json_request_post_tokens' = @(
                @{
                    'name' = 'personal.ssn'
                    'operation' = 'protect'
                    'protection_policy' = "text_ProtectionPolicy-$counter"
                },@{
                    'name' = 'personal.dob'
                    'operation' = 'protect'
                    'protection_policy' = "text_ProtectionPolicy-$counter"
                },@{
                    'name' = 'card.ccNumber'
                    'operation' = 'protect'
                    'protection_policy' = "CC_ProtectionPolicy-$counter"
                },@{
                    'name' = 'card.cvv'
                    'operation' = 'protect'
                    'protection_policy' = "text_ProtectionPolicy-$counter"
                }
            )
        }
    )
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): DPG Policy already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$dpgPolicyId = $response.id

#Final setup...creating client application
Write-Output "Creating client profile..."
$url = "https://$kms/api/v1/data-protection/client-profiles"
$body = @{
    'name' = "CC_profile-$counter"
    'nae_iface_port' = 9005
    'app_connector_type' = 'DPG'
    'policy_id' = $dpgPolicyId
    'lifetime' = '30d'
    'cert_duration' = 730
    'max_clients' = 200
    'ca_id' = $caId
    'csr_parameters' = @{
        'csr_cn' = 'admin'
        'csr_country' = ''
        'csr_state' = ''
        'csr_city' = ''
        'csr_org_name' = ''
        'csr_org_unit' = ''
        'csr_email' = ''
    }
    'configurations' = @{
        'verify_ssl_certificate' = $false
        'use_persistent_connections' = $true
        'log_level' = 'DEBUG'
        'tls_to_appserver' = @{
            'tls_skip_verify' = $true
            'tls_enabled' = $true
        }
        'auth_method_used' = @{
            'scheme_name' = 'Basic'
        }
    }
}
$jsonBody = $body | ConvertTo-Json -Depth 5
try {
    $response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
}
catch {
    $StatusCode = $_.Exception.Response.StatusCode
    if ($StatusCode -EQ [System.Net.HttpStatusCode]::Conflict) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Client Profile already exists"
    }
    elseif ($StatusCode -EQ [System.Net.HttpStatusCode]::Unauthorized) {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): Unable to connect to CipherTrust Manager with current credentials"
    }
    else {
        Write-Error "Error $([int]$StatusCode) $($StatusCode): $($_.Exception.Response.ReasonPhrase)" -ErrorAction Stop
    }
}
$regToken = $response.reg_token

[string[]]$fileContent = Get-Content ".\docker-compose-template.yml"
$content = ''
foreach ($line in $fileContent) { $content = $content + "`n" + $line }
$yamlObj = ConvertFrom-YAML $content
$yamlObj.services.ciphertrust.environment = @(
    "REG_TOKEN=$regToken",
    "DESTINATION_URL=http://api:8080",
    "TLS_ENABLED=false",
    "KMS=$kms",
    "DPG_PORT=9005"
)
$yamlObj.services.api.environment = @(
    "CM_URL=${protocol}://$kms",
    "CM_USERNAME=$username",
    "CM_PASSWORD=$password",
    "CM_USER_SET_ID=$plainTextUserSetId"
)

$yamlObj.services.frontend.environment = @(
    "CM_URL=$host_machine"
)

$yaml = ConvertTo-YAML $yamlObj | yq
Set-Content -Path ".\docker-compose.yml" -Value $yaml

Write-Output "`n"
Write-Output ">>>>> Completed Configuring your CipherTrust Manager Instance <<<<<"
Write-Output " __________________________________________________________________________"
Write-Output "| Replaced below variables in the docker-compose.yml file in current folder |"
Write-Output "| REG_TOKEN: $regToken"
Write-Output "| KMS: $kms"
Write-Output "| CMIP: https://=$kms"
Write-Output "|__________________________________________________________________________|"

Write-Output "Running demo application now..."
sudo docker compose up
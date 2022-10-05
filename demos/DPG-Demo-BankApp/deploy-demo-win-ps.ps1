$username = "admin"
$password = "ChangeIt!"
$kms = "1.1.1.1"
$counter = "demo"

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

#Creating local CA
<#
Write-Output "Creating local CA..."
$url = "https://$kms/api/v1/ca/local-cas"
$body = @{
    'name' = "local-CA-$counter"
    'algorithm' = 'RSA'
    'size' = 4096
    'cn' = 'CM Root CA'
    'emailAddresses' = @('contact@thalesgroup.com')
    'names' = @(
        @{
            'O' = 'Thales'
            'C' = 'US'
            'ST' = 'TX'
            'L' = 'Austin'
        }
    )
}
$jsonBody = $body | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
$caId = 'kylo:kylo:naboo:localca:12b0233e-d233-4856-bb8a-e22a8ff6e614'

#Activate local CA
Write-Output "Activating above CA..."
$url = "https://$kms/api/v1/ca/local-cas/$caID/self-sign"
$body = @{
    'duration' = 365
}
$jsonBody = $body | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
#>

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
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'

#Creating Character Set
Write-Output "Creating Character Set..."

$url = "https://$kms/api/v1/data-protection/character-sets"
$body = @{
    'name' = "DPGAlphaNum-$counter"
    'range' = @('0030-0039', '0041-005A', '0061-007A')
    'encoding' = 'UTF-8'
}
$jsonBody = $body | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
$charSetId = $response.id

#Creating CVV Protection Policy
Write-Output "Creating Protection Policy for CVV Number..."
$url = "https://$kms/api/v1/data-protection/protection-policies"
$body = @{
    'name' = "cvv_ProtectionPolicy-$counter"
    'key' = 'dpgKey'
    'tweak' = '1628462495815733'
    'tweak_algorithm' = 'SHA1'
    'algorithm' = 'FPE/FF1v2/UNICODE'
    'character_set_id' = $charSetId
    'allow_single_char_input' = $false
}
$jsonBody = $body | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
$cvvPolicyId = $response.id

#Creating CC Number Protection Policy
Write-Output "Creating Protection Policy for Credit Card Number..."
$url = "https://$kms/api/v1/data-protection/protection-policies"
$body = @{
    'name' = "CC_ProtectionPolicy-$counter"
    'key' = 'dpgKey'
    'tweak' = '9828462495846783'
    'tweak_algorithm' = 'SHA1'
    'algorithm' = 'FPE/AES/CARD10'
    'allow_single_char_input' = $false
}
$jsonBody = $body | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
$ccPolicyId = $response.id

#Creating SSN Protection Policy
Write-Output "Creating Protection Policy for SSN..."
$url = "https://$kms/api/v1/data-protection/protection-policies"
$body = @{
    'name' = "SSN_ProtectionPolicy-$counter"
    'key' = 'dpgKey'
    'tweak' = '1628462495815733'
    'tweak_algorithm' = 'SHA1'
    'algorithm' = 'FPE/FF1v2/UNICODE'
    'character_set_id' = $charSetId
    'allow_single_char_input' = $false
}
$jsonBody = $body | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
$ssnPolicyId = $response.id

#Creating User Sets
Write-Output "Creating PlainText User Set..."
$url = "https://$kms/api/v1/data-protection/user-sets"
$body = @{
    'name' = "plainttextuserset-$counter"
    'description' = "plain text user set for card account owner"
    'users' = @('ccaccountowner')
}
$jsonBody = $body | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
$plainTextUserSetId = $response.id

Write-Output "Creating Masked Data User Set..."
$url = "https://$kms/api/v1/data-protection/user-sets"
$body = @{
    'name' = "maskedtextuserset-$counter"
    'description' = "masked text user set for CS exec"
    'users' = @('cccustomersupport')
}
$jsonBody = $body | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
$maskedTextUserSetId = $response.id

Write-Output "Creating Encrypted Data User Set..."
$url = "https://$kms/api/v1/data-protection/user-sets"
$body = @{
    'name' = "enctextuserset-$counter"
    'description' = "encrypted text user set for everyone else"
    'users' = @('everyoneelse')
}
$jsonBody = $body | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
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
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
$maskingPolicyId = $response.id

#Creating Access Policies
Write-Output "Creating Access Policy for Credit Card use case..."
$url = "https://$kms/api/v1/data-protection/access-policies"
$body = @{
    'name' = "cc_access_policy-$counter"
    'description' = "CC Access Policy for credit card user set"
    'default_reveal_type' = 'Error Replacement Value'
    'default_error_replacement_value' = '000000'
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
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
$accessPolicyId = $response.id

#This is the interesting step...defining DPG policies for the API endpoints
Write-Output "Creating DPG Policy for CC use case..."
$url = "https://$kms/api/v1/data-protection/dpg-policies"
$body = @{
    'name' = "cc_policy-$counter"
    'description' = 'DPG policy for credit card attributes'
    'proxy_config' = @(
        @{
            'api_url' = '/api/fakebank/account'
            'json_request_post_tokens' = @(
                @{
                    'name' = 'ccNumber'
                    'operation' = 'protect'
                    'protection_policy' = "CC_ProtectionPolicy-$counter"
                },
                @{
                    'name' = 'cvv'
                    'operation' = 'protect'
                    'protection_policy' = "cvv_ProtectionPolicy-$counter"
                },
                @{
                    'name' = 'ssn'
                    'operation' = 'protect'
                    'protection_policy' = "SSN_ProtectionPolicy-$counter"
                },@{
                    'name' = 'dob'
                    'operation' = 'protect'
                    'protection_policy' = "SSN_ProtectionPolicy-$counter"
                }
            )
        },
        @{
            'api_url' = '/api/fakebank/accounts/{id}'            
            'json_response_get_tokens' = @(
                @{
                    'name' = 'ccCvv'
                    'operation' = 'reveal'
                    'protection_policy' = "cvv_ProtectionPolicy-$counter"
                    'access_policy' = "cc_access_policy-$counter"
                },@{
                    'name' = 'ccNumber'
                    'operation' = 'reveal'
                    'protection_policy' = "CC_ProtectionPolicy-$counter"
                    'access_policy' = "cc_access_policy-$counter"
                },@{
                    'name' = 'ssn'
                    'operation' = 'reveal'
                    'protection_policy' = "SSN_ProtectionPolicy-$counter"
                    'access_policy' = "cc_access_policy-$counter"
                },@{
                    'name' = 'dob'
                    'operation' = 'reveal'
                    'protection_policy' = "SSN_ProtectionPolicy-$counter"
                    'access_policy' = "cc_access_policy-$counter"
                }
            )
        }
    )
}
$jsonBody = $body | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
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
$response = Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'
$regToken = $response.reg_token

#ohhh...this one is the final step...adding few users
Write-Output "Creating sample users..."
#ccaccountowner, cccustomersupport, everyoneelse --- password is same for all...KeySecure01!
$url = "https://$kms/api/v1/usermgmt/users"
$body = @{
    'email' = 'ccaccountowner@local'
    'name' = 'ccaccountowner'
    'username' = 'ccaccountowner'
    'password' = 'KeySecure01!'
    'app_metadata' = @{}
    'user_metadata' = @{}
}
$jsonBody = $body | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'

$url = "https://$kms/api/v1/usermgmt/users"
$body = @{
    'email' = 'cccustomersupport@local'
    'name' = 'cccustomersupport'
    'username' = 'cccustomersupport'
    'password' = 'KeySecure01!'
    'app_metadata' = @{}
    'user_metadata' = @{}
}
$jsonBody = $body | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'

$url = "https://$kms/api/v1/usermgmt/users"
$body = @{
    'email' = 'everyoneelse@local'
    'name' = 'everyoneelse'
    'username' = 'everyoneelse'
    'password' = 'KeySecure01!'
    'app_metadata' = @{}
    'user_metadata' = @{}
}
$jsonBody = $body | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method 'Post' -Uri $url -Body $jsonBody -Headers $headers -ContentType 'application/json'

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
$yaml = ConvertTo-YAML $yamlObj | .\yq.exe
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
docker compose up
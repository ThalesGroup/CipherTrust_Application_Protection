###
#Demo Script
###
using module CipherTrustManager

Import-Module -Name powershell-yaml -Force
#Import-Module CipherTrustManager -Force -ErrorAction Stop

$DebugPreference = 'SilentlyContinue'
#$DebugPreference = 'Continue'

$username = "<admin_username>"
$password = "<password>"
$kms = "<ipaddress_or_fqdn>"
#counter is a unique prefix that you can add the all the assets created by this script to ensure uniqueness of your resources
$counter = "<prefix>"
#sampleUserPassword is the password that will be applied to sample users created by this script
$sampleUserPassword = "<userPassword>"
$nae_port = 9005
$keyname = "dpgKey-$counter"
#$usageMask = 3145740
$usageMask = ([CipherTrustManager.UsageMaskTable]::Encrypt + [CipherTrustManager.UsageMaskTable]::Decrypt + [CipherTrustManager.UsageMaskTable]::FPEEncrypt + [CipherTrustManager.UsageMaskTable]::FPEDecrypt) #More HUMAN READABLE ;)
$algorithm = 'aes'
$size = 256

Write-Output "-----------------------------------------------------------------"
Write-Output "Next few steps will create boilerplate config on your CM instance"
Write-Output "-----------------------------------------------------------------"

#Initialize and authenticate a connection with CipherTrust Manager
Connect-CipherTrustManager `
    -server $kms `
    -user $username `
    -pass $password

#Getting user id of local|admin
$userList = Find-CMUsers -name "admin"
$ownerID = $userList.resources[0].user_id



#Create a key (need to get an owner... so WHO should own this key)
Write-Output "Creating a Key"
$keySuccess = New-CMKey  `
    -name $keyname `
    -usageMask $usageMask `
    -algorithm $algorithm `
    -size $size `
    -ownerId $ownerID
if (-NOT $keySuccess) {
    Write-Output "Key already created"
}
Write-Output "...Done"

#Get local root CA ID
$caID = Find-CMCAs `
    -subject "/C=US/ST=TX/L=Austin/O=Thales/CN=CipherTrust Root CA"
#if (-NOT $caID){
#    Write-Error "Unable to find CA" -ErrorAction Stop
#}

#Create an NAE network interface
Write-Output "Creating an NAE network interface"
$interfaceSuccess = New-CMInterface `
    -port $nae_port `
    -cert_user_field CN -mode 'tls-cert-pw-opt' `
    -auto_gen_ca_id $caId `
    -trusted_cas_local $caId `
    -network_interface 'all'
if (-NOT $interfaceSuccess) {
    Write-Output "NAE Interface already created"
}
Write-Output "...Done"

#Creating Character Set
Write-Output "Creating Character Set..."
$charSetId = New-CMCharacterSet `
    -name "DPGAlphaNum-$counter" `
    -range @('0030-0039', '0041-005A', '0061-007A') `
    -encoding 'UTF-8'
#if already exists... go get the id
if (-NOT $charSetId) {
    $charsetList = Find-CMCharacterSets `
        -name "DPGAlphaNum-$counter"
    $charSetId = $charsetList.resources[0].id
}
Write-Output "...Done"

### Creating Protection Policies
Write-Output "Creating Protection Policies...."
#Creating CVV Protection Policy
Write-Output "---Creating Protection Policy for CVV Number..."
$null = New-CMProtectionPolicy `
    -name "text_ProtectionPolicy-$counter" `
    -key "dpgKey-$counter" `
    -tweak '1628462495815733' `
    -tweak_algorithm 'SHA1' `
    -algorithm 'FPE/FF3/ASCII' `
    -character_set_id $charSetId 
Write-Output "---Done"

#Creating CC Number Protection Policy
Write-Output "---Creating Protection Policy for Credit Card Number..."
$null = New-CMProtectionPolicy `
    -name "CC_ProtectionPolicy-$counter" `
    -key "dpgKey-$counter" `
    -tweak '9828462495846783' `
    -tweak_algorithm 'SHA1' `
    -algorithm 'FPE/FF3/CARD10' 
Write-Output "---Done"

#Creating SSN Protection Policy
# Write-Output "---Creating Protection Policy for SSN..."
# $null = New-CMProtectionPolicy `
#     -name "SSN_ProtectionPolicy-$counter" `
#     -key "dpgKey-$counter" `
#     -tweak '1628462495815733' `
#     -tweak_algorithm 'SHA1' `
#     -algorithm 'FPE/FF3/UNICODE' `
#     -character_set_id $charSetId 
# Write-Output "---Done"
###Done Creating Protection Policies
Write-Output "...Done"

###Creating Users
Write-Output "Creating sample users..."
#ccaccountowner, cccustomersupport, everyoneelse, user1, user2, user3 --- password is same for all...$sampleUserPassword
$passwd = ConvertTo-SecureString $sampleUserPassword -AsPlainText
$users = @("cccustomersupport")
foreach ($user in $users) {
    Write-Output "---Creating account for $user..."
    $Cred = New-Object System.Management.Automation.PSCredential ($user, $passwd)
    New-CMUser `
        -email "$($user)@local" `
        -name $user `
        -ps_creds  $Cred    
    Write-Output "---Done"
}
###Done Creating Users
Write-Output "...Done"

#Creating User Sets
Write-Output "Creating PlainText User Set..."
$plainTextUserSetId = New-CMUserSet `
    -name "plainttextuserset-$counter" `
    -description "plain text user set for card account owner" `
    -users @()
#if already exists... go get the id
if (-NOT $plainTextUserSetId) {
    $userList = Find-CMUserSets  `
        -name "plainttextuserset-$counter"
    $plainTextUserSetId = $userList.resources[0].id
}
Write-Output "...Done"

Write-Output "Creating Masked Data User Set..."
$maskedTextUserSetId = New-CMUserSet `
    -name "maskedtextuserset-$counter" `
    -description "masked text user set for CS exec" `
    -users @('cccustomersupport')
#if already exists... go get the id
if (-NOT $maskedTextUserSetId) {
    $userList = Find-CMUserSets  `
        -name "maskedtextuserset-$counter"
    $maskedTextUserSetId = $userList.resources[0].id
}
Write-Output "...Done"

Write-Output "Creating Encrypted Data User Set..."
$encTextUserSetId = New-CMUserSet `
    -name "enctextuserset-$counter" `
    -description "encrypted text user set for everyone else" `
    -users @('everyoneelse')
#if already exists... go get the id
if (-NOT $encTextUserSetId) {
    $userList = Find-CMUserSets  `
        -name "enctextuserset-$counter"
    $encTextUserSetId = $userList.resources[0].id
}
Write-Output "...Done"
#Done Creating User Sets

#Creating Masking Policies
Write-Output "Creating masking policy for CC..."
$maskingPolicyId = New-CMMaskingFormat `
    -name "cc_masking_format-$counter" `
    -starting_characters 0 `
    -ending_characters 4 `
    -mask_char 'x' `
    -Show
#if already exists... go get the id
if (-NOT $maskingPolicyId) {
    $MaskingFormatList = Find-CMMaskingFormats `
        -name "cc_policy-$counter"
    $maskingPolicyId = $MaskingFormatList.resources[0].id
}
Write-Output "...Done"
#Done Creating Masking Policies

###Creatng User Set Policies
Write-Output "Creating User Set Policies for use of Access Policies..."
Write-Output "---Creating User Set Policy for Plaintext"
#Creating User Set Policies
$user_set_policies = @()
$user_set_policies = New-CMUserSetPolicy `
    -user_set_policy $user_set_policies `
    -user_set_id $plainTextUserSetId `
    -reveal_type Plaintext
#Write-HashtableArray $user_set_policies
Write-Output "---Done"

Write-Output "---Creating User Set Policy for Masked"
$user_set_policies = New-CMUserSetPolicy `
    -user_set_policy $user_set_policies `
    -user_set_id $maskedTextUserSetId `
    -reveal_type MaskedValue `
    -masking_format_id $maskingPolicyId
#Write-HashtableArray $user_set_policies
Write-Output "---Done"
    
Write-Output "---Creating User Set Policy for Ciphertext"
$user_set_policies = New-CMUserSetPolicy `
    -user_set_policy $user_set_policies `
    -user_set_id $encTextUserSetId `
    -reveal_type Ciphertext
#Write-HashtableArray $user_set_policies
Write-Output "---Done"
Write-Output "...Done"

    
###Creating Access Policies
Write-Output "Creating Access Policies for Credit Card use case..."
#$accessPolicyId = 
$null = New-CMAccessPolicy `
    -name "last_four_show_access_policy-$counter" `
    -description "CC Access Policy for credit card user set" `
    -default_reveal_type ErrorReplacement `
    -default_error_replacement_value '000000' `
    -user_set_policy $user_set_policies
Write-Output "...Done"
###Done Creating Access Policies

Write-Output "Creating Access Policies for cvv use case..."    
#$accessPolicyId = 
$null = New-CMAccessPolicy `
    -name "all_enc_access_policy-$counter" `
    -description "CC Access Policy for CVV user set" `
    -default_reveal_type Ciphertext `
    -user_set_policy $user_set_policies
###Done Creating Access Policies
Write-Output "...Done"

###Creating Proxy Config for DPG Policies....
Write-Output "Creating Proxy Config for DPG Policies...."
#Post Endpoint
Write-Output "---Creating POST REQUEST Endpoint configuration for 'api_url' = '/api/fakebank/account/personal'..."
$json_request_post_tokens_personal = @()
$json_request_post_tokens_personal = New-CMDPGJSONRequestResponse `
    -name 'details.ssn' `
    -operation Protect `
    -protection_policy "text_ProtectionPolicy-$counter"
$json_request_post_tokens_personal = New-CMDPGJSONRequestResponse `
    -json_tokens $json_request_post_tokens_personal `
    -name 'details.dob' `
    -operation Protect `
    -protection_policy "text_ProtectionPolicy-$counter"
Write-Output "---Done"

Write-Output "---Creating POST REQUEST Endpoint configuration for 'api_url' = '/api/fakebank/account/card'..."
$json_request_post_tokens_card = @()
$json_request_post_tokens_card = New-CMDPGJSONRequestResponse `
    -name 'ccNumber' `
    -operation Protect `
    -protection_policy "CC_ProtectionPolicy-$counter"
$json_request_post_tokens_card = New-CMDPGJSONRequestResponse `
    -json_tokens $json_request_post_tokens_card `
    -name 'cvv' `
    -operation Protect `
    -protection_policy "text_ProtectionPolicy-$counter"
Write-Output "---Done"

#Get Endpoint
Write-Output "---Creating GET RESPONSE Endpoint configuration for 'api_url' = '/api/fakebank/accounts/{id}'..."
$json_response_get_tokens_accounts = @()
$json_response_get_tokens_accounts = New-CMDPGJSONRequestResponse `
    -name 'accounts.[*].ccv' `
    -operation Reveal `
    -protection_policy "text_ProtectionPolicy-$counter" `
    -access_policy "all_enc_access_policy-$counter"
$json_response_get_tokens_accounts = New-CMDPGJSONRequestResponse `
    -json_tokens $json_response_get_tokens_accounts `
    -name 'accounts.[*].ccNumber' `
    -operation Reveal `
    -protection_policy "CC_ProtectionPolicy-$counter" `
    -access_policy "last_four_show_access_policy-$counter"
Write-Output "---Done"

Write-Output "---Creating GET RESPONSE Endpoint configuration for 'api_url' = '/api/fakebank/details/{id}'..."
$json_response_get_tokens_details = @()
$json_response_get_tokens_details = New-CMDPGJSONRequestResponse `
    -name 'details.ssn' `
    -operation Reveal `
    -protection_policy "CC_ProtectionPolicy-$counter" `
    -access_policy "last_four_show_access_policy-$counter"
$json_response_get_tokens_details = New-CMDPGJSONRequestResponse `
    -json_tokens $json_response_get_tokens_details `
    -name 'details.dob' `
    -operation Reveal `
    -protection_policy "CC_ProtectionPolicy-$counter" `
    -access_policy "last_four_show_access_policy-$counter"
Write-Output "---Done"

#Set Proxy Config
Write-Output "---Creating Proxy Config for POST REQUEST..."
#$proxy_config = @()
$proxy_config = New-CMDPGProxyConfig `
    -api_url '/api/fakebank/account/personal' `
    -json_request_post_tokens $json_request_post_tokens_personal
$proxy_config = New-CMDPGProxyConfig `
    -proxy_config $proxy_config `
    -api_url '/api/fakebank/account/card' `
    -json_request_post_tokens $json_request_post_tokens_card
Write-Output "---Done"

# Write-Output "---Creating Proxy Config for GET RESPONSE..."
$proxy_config = New-CMDPGProxyConfig `
    -proxy_config $proxy_config `
    -api_url '/api/fakebank/accounts/{id}' `
    -json_response_get_tokens $json_response_get_tokens_accounts
$proxy_config = New-CMDPGProxyConfig `
    -proxy_config $proxy_config `
    -api_url '/api/fakebank/details/{id}' `
    -json_response_get_tokens $json_response_get_tokens_details
Write-Output "---Done"
Write-Output "---proxy_config:"
Write-HashtableArray $proxy_config -DEBUG
Write-Output "...Done"

###Creating DPG Policy
#This is the interesting step...defining DPG policies for the API endpoints
Write-Output "Creating DPG Policy for CC use case..."
#Create DPG Policy
Write-Output "---Creating DPG Policy for CC use case..."
$dpgPolicyId = New-CMDPGPolicy `
    -name "cc_policy-$counter"  `
    -description 'DPG policy for credit card attributes' `
    -proxy_config $proxy_config
Write-Debug $dpgPolicyId -DEBUG
###Done Creating DPG Policy
Write-Output "---Done"
Write-Output "...Done"

###Creating Application Profile
#Final setup...creating client application
Write-Output "Creating client profile..."
$regToken = New-CMClientProfiles `
    -name "CC_profile-$counter" `
    -nae_iface_port  $nae_port `
    -app_connector_type DPG `
    -policy_id $dpgPolicyId `
    -lifetime '30d' `
    -cert_duration 730 `
    -max_clients 200 `
    -ca_id $caId `
    -csr_cn 'admin' `
    -UsePersistentConnections `
    -log_level DEBUG `
    -TLS_SkipVerify `
    -TLS_Enabled `
    -auth_method_scheme_name 'Basic'
###Done Creating Application Profile
Write-Output "...Done"



###Create Docker setup
Write-Output "Creating Docker Setup from Template..."
[string[]]$fileContent = Get-Content ".\docker-compose-template.yml"
$content = ''
foreach ($line in $fileContent) { $content = $content + "`n" + $line }
$yamlObj = ConvertFrom-YAML $content
$yamlObj.services.ciphertrust.environment = @(
    "REG_TOKEN=$regToken",
    "DESTINATION_URL=http://api:8080",
    "TLS_ENABLED=false",
    "KMS=$kms",
    "DPG_PORT=$nae_port"
)
$yamlObj.services.api.environment = @(
    "CMIP=https://$kms"
)

$yaml = ConvertTo-YAML $yamlObj | .\yq.exe
Set-Content -Path ".\docker-compose.yml" -Value $yaml
Write-Output "...Done"

Write-Output "`n"
Write-Output ">>>>> Completed Configuring your CipherTrust Manager Instance <<<<<"
Write-Output " __________________________________________________________________________"
Write-Output "| Replaced below variables in the docker-compose.yml file in current folder |"
Write-Output "| REG_TOKEN: $regToken"
Write-Output "| KMS: $kms"
Write-Output "| CMIP: https://=$kms"
Write-Output "|__________________________________________________________________________|"

Write-Output "Running demo application now..."
#docker compose up

###
#Undo Demo Script
###
using module CipherTrustManager

$DebugPreference = 'SilentlyContinue'
#$DebugPreference = 'Continue'

#########################
## Change Variables below
#########################
$username = "<admin_username>"
$password = "<password>"
$kms = "<ipaddress_or_fqdn>"
#counter is a unique prefix that you can add the all the assets created by this script to ensure uniqueness of your resources
$counter = "<prefix>"
$keyname = "dpgKey-$counter"
###########################################################################
## Do not change anything below unless you know what you are doing
###########################################################################

Write-Output "-----------------------------------------------------------------"
Write-Output "Next few steps will Deleting boilerplate config on your CM instance"
Write-Output "-----------------------------------------------------------------"

#Initialize and authenticate a connection with CipherTrust Manager
Write-Output "Connecting to CipherTrust Manager"
Connect-CipherTrustManager `
    -server $kms `
    -user $username `
    -pass $password
Write-Output "...Done"

###Deleting Application Profile
Write-Output "Deleting Client Profile..."
$appList = Find-CMClientProfiles `
    -name "CC_profile-$counter"
if ($appList.total -eq 1) {
    Remove-CMClientProfiles `
        -id $appList.resources[0].id
}
Write-Output "...Done"
###Done Deleting Application Profile

#Deleting DPG Policies (I think is automatic when app dies)
Write-Output "Deleting DPG Policy..."
$DPG_PolicyList = Find-CMDPGPolicies `
    -name "cc_policy-$counter"
if ($DPG_PolicyList.total -eq 1) {
    Remove-CMDPGPolicy `
        -id $DPG_PolicyList.resources[0].id
}
Write-Output "...Done"
###Done Deleting DPG Policy

###Deleting Access Policies
Write-Output "Deleting Access Policy..."
Write-Output "---Deleting Access Policy for for credit card user set..."
$AccessPolicyList = Find-CMAccessPolicies `
    -name "last_four_show_access_policy-$counter"
if ($AccessPolicyList.total -eq 1) {
    Remove-CMAccessPolicy `
        -id $AccessPolicyList.resources[0].id
}
Write-Output "---Done"

Write-Output "---Deleting Access Policy for for cvv user set..."
$AccessPolicyList = Find-CMAccessPolicies `
    -name "all_enc_access_policy-$counter"
if ($AccessPolicyList.total -eq 1) {
    Remove-CMAccessPolicy `
        -id $AccessPolicyList.resources[0].id
}
Write-Output "---Done"
Write-Output "...Done"
###Done Deleting Access Policies

#Deleting Masking Policy
Write-Output "Deleting Masking Formats"
$MaskingFormatList = Find-CMMaskingFormats `
    -name "cc_masking_format-$counter"
if ($MaskingFormatList.total -eq 1) {
    Remove-CMMaskingFormat `
        -id $MaskingFormatList.resources[0].id
}
Write-Output "...Done"
#Done Deleting Masking Policy

#Deleting User Sets
Write-Output "Deleting User Sets"
$userList = Find-CMUserSets  `
    -name "enctextuserset-$counter"
if ($userList.total -eq 1) {
    Remove-CMUserSet `
        -id $userList.resources[0].id
}
$userList = Find-CMUserSets  `
    -name "maskedtextuserset-$counter"
if ($userList.total -eq 1) {
    Remove-CMUserSet `
        -id $userList.resources[0].id
}
$userList = Find-CMUserSets  `
    -name "plainttextuserset-$counter"
if ($userList.total -eq 1) {
    Remove-CMUserSet `
        -id $userList.resources[0].id
}
Write-Output "...Done"
#Done Deleting User Sets

###Creating Users
Write-Output "Deleting sample users..."
#ccaccountowner, cccustomersupport, everyoneelse, user1, user2, user3 --- password is same for all...$password
$users = "ccaccountowner", "cccustomersupport", "everyoneelse", "user1", "user2", "user3"
foreach ($user in $users) {
    Write-Output "---Deleting account for $user..."
    $userList = Find-CMUsers `
        -email "$($user)@local"
    if ($userList.total -eq 1) {
        Remove-CMUser `
            -id $userList.resources[0].user_id
    }
    Write-Output "---Done"
}
###Done Creating Users
Write-Output "...Done"

#Deleting Protection Policies
Write-Output "Deleting Protection Policies"
#Remove-CMProtectionPolicy `
#    -name "SSN_ProtectionPolicy-$counter"
Remove-CMProtectionPolicy `
    -name "CC_ProtectionPolicy-$counter"
Remove-CMProtectionPolicy `
    -name "text_ProtectionPolicy-$counter"
Write-Output "...Done"
#Done Deleting Protection Policies

#Deleting Character Set
Write-Output "Deleting Character Sets"
$charsetList = Find-CMCharacterSets `
    -name "DPGAlphaNum-$counter"
if ($charsetList.total -eq 1) {
    Remove-CMCharacterSet `
        -id $charsetList.resources[0].id
}
Write-Output "...Done"
#Done Deleting Character Set

#Deleting an NAE network interface
Write-Output "Deleting Interfaces"
$interfaceList = Find-CMInterfaces `
    -name "nae_all_9005"
if ($interfaceList.total -eq 1) {
    #    Remove-CMInterface `
    #        -id $interfaceList.resources[0].id
    #Looks like it wants NAME and not ID ... WHA???
    Remove-CMInterface `
        -name "nae_all_9005"
}
Write-Output "...Done"
#Done Deleting an NAE network interface

#Deleting a key
Write-Output "Deleting Keys"
$keyList = Find-CMKeys  `
    -name $keyname
if ($keyList.total -eq 1) {
    Remove-CMKey `
        -id $keyList.resources[0].id
}
else {
    Write-Output "$($keyname) not found"
}
Write-Output "...Done"
#Done Deleting a key

Write-Output "-----------------------------------------------------------------"
Write-Output " Finished deleting boilerplate config on your CM instance"
Write-Output "-----------------------------------------------------------------"

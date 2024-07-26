<#
.DESCRIPTION
    ###################################################################
    # File:             Secure_PassPhrase.ps1                         #
    # Author:           Rick Leon, Professional Services              #
    # Publisher:        Thales Group                                  #
    # Copyright:        (c) 2024 Thales Group. All rights reserved.   #
    # Disclaimer:       THIS SOFTWARE IS FREE AND UNSUPPORTED.        #
    ###################################################################
.PARAMETER userString
    Plain-text user value to be obfuscated.
#>

param(
    [Parameter()] [string] $userString
)

function Get-ObfuscatedValue($path,$myString){
    $psi = New-object System.Diagnostics.ProcessStartInfo 
    $psi.CreateNoWindow = $true 
    $psi.UseShellExecute = $false 
    $psi.RedirectStandardOutput = $true 
    $psi.FileName = $path
    $psi.Arguments = @("-txt $($mystring)") 
    $process = New-Object System.Diagnostics.Process 
    $process.StartInfo = $psi 
    [void]$process.Start()
    $output = $process.StandardOutput.ReadToEnd() 
    $process.WaitForExit() 
    return $output
}

if(Test-Path -Path ".\PassPhraseSecure.exe"){
    $appLocation = ".\PassPhraseSecure.exe"
}else{
    Write-Host "Checking for CAKM Installation Directory..."
    
    #Check for CAKM Installation
    $reg = [Microsoft.Win32.RegistryKey]::OpenBaseKey('LocalMachine',0)
    $apps = $reg.OpenSubKey("SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall").GetSubKeyNames()
    if($apps.Contains("{F88BDC0D-9BAE-4133-924E-211A934C0409}")){
        $InstallPath = (Get-ItemProperty -Path "HKLM:SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{F88BDC0D-9BAE-4133-924E-211A934C0409}" -Name InstallLocation).InstallLocation
        Write-Host "CAKM Installation found at $($installPath)"
        $appLocation = $InstallPath + "utilities\PassPhraseSecure.exe"
    }else{
        Write-Host "CAKM Installation Not Found"
        $InstallPath = Read-Host "Enter full path to PassPhraseSecure.`nExample: C:\Temp\`nPath"
        if(($NULL -eq $InstallPath) -or ($InstallPath -eq "") ){
            Write-Host "No directory entered.."
            exit 
        }else{
            if($InstallPath[-1] -ne "\"){ $InstallPath += "\"}
            $appLocation = $InstallPath + "PassPhraseSecure.exe"
            if(!(Test-Path -Path $appLocation)){
                Write-Host "PassPhraseSecure not found at provided location. Please try again."
                exit 
            }
        }
    }
}

Write-Host "`nThis script will obfuscate user and password strings to be used with Thales Key Providers.`n"
if(!$userString){
    if((Read-Host "Are you protecting a user string?") -eq "y"){
        Write-Host "Obfuscated User String is: $(Get-ObfuscatedValue $appLocation (Read-Host "Enter user string") ) "
    }
}else{
    Write-Host "Obfuscated User String is: $(Get-ObfuscatedValue $appLocation $userString) "
}

Write-Host "Obfuscated Passphsrase is: $(Get-ObfuscatedValue $appLocation ([System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR((Read-Host -assecurestring "Please enter passphrase string")))))"

Clear-Variable appLocation, InstallPath, reg, apps
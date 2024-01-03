#==================================================================================================
# Script that takes the newest file in a specified folder and creates a backup on a Sharepoint Site
#==================================================================================================

function Write-Log {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - $Message"
    $logEntry | Out-File $logFile -Append
}

$module = Get-Module -ListAvailable -Name PNP.powershell

# Custom parameters
# Url of a Sharepoint site
$sharepointSiteUrl = "sharepoint-site-url"

# Backup folder on a Sharepoint site 
$backupFolder = "Shared Documents/path/to/folder/on/sharepoint"

# Folder where the files you want to backup are stored
$folderPath = "C:\path\to\folder"

# Log file
$logFile = "log.txt"

$password = ConvertTo-SecureString "supersecurepassword" -AsPlainText -Force
$username = "service-account-username"
$creds = New-Object -TypeName System.Management.Automation.PSCredential -argumentlist $username,$password

if ($module) {
    Import-Module -Name PNP.Powershell

    $latestFile = Get-ChildItem -Path $folderPath -File | Sort-Object CreationTime -Descending | Select-Object -First 1
    Write-Output $latestFile.FullName
    
    try {
        Write-Output "Connecting to Sharepoint site"
        Connect-PnPOnline -Url $sharepointSiteUrl -Credentials $creds
        Add-PnPFile -Path $latestFile.FullName -Folder $backupFolder
	Write-Log "Backup successful"
    }
    catch {
        Write-Log $_
    }  
    
} else {
    Write-Log "PNP.Powershell not installed"
    exit
}


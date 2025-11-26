# Check if the Web Server (IIS) role is already installed
$role = Get-WindowsFeature Web-Server
if ($role.Installed -ne $true) {
    # Install the Web Server (IIS) role
    Install-WindowsFeature -Name Web-Server -IncludeManagementTools
} else {
    Write-Output "The Web Server (IIS) role is already installed."
}

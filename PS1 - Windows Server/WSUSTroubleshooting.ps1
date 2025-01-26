# 1. Check Windows Update service status
Get-Service wuauserv | Select-Object Name, Status, StartType

# 2. Restart Windows Update service
Restart-Service wuauserv -Force

# 3. Check WSUS server settings
Get-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" | Select-Object WUServer, WUStatusServer

# 4. Force a detection of available updates
wuauclt /detectnow
wuauclt /reportnow

# 5. Reset Windows Update components
net stop wuauserv
net stop cryptSvc
net stop bits
net stop msiserver

ren C:\Windows\SoftwareDistribution SoftwareDistribution.old
ren C:\Windows\System32\catroot2 catroot2.old

net start wuauserv
net start cryptSvc
net start bits
net start msiserver

# 6. Check for any pending reboots
$pendingReboot = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager" -Name PendingFileRenameOperations -ErrorAction SilentlyContinue
if ($pendingReboot) {
    Write-Host "Pending reboot detected"
} else {
    Write-Host "No pending reboot detected"
}

# 7. Check Windows Update log
Get-WindowsUpdateLog

# 8. Get update history
Get-WmiObject -Class Win32_QuickFixEngineering | Select-Object Description, HotFixID, InstalledOn

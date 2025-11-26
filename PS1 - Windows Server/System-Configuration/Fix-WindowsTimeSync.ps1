<# 
.SYNOPSIS
  Resets Windows Time service and validates sync against Amazon Time Sync Service.

.DESCRIPTION
  - Points NTP to 169.254.169.123 (Amazon Time Sync) by default
  - Resets the w32time service (unregister/register)
  - Forces resync
  - Shows current source, status, and drift vs AWS

.PARAMETER NtpServer
  NTP server to configure. Default is Amazon Time Sync with 0x9 flags.

.PARAMETER Samples
  Number of stripchart samples to collect against the NTP server.

.EXAMPLE
  .\Fix-WindowsTimeSync.ps1

.EXAMPLE
  .\Fix-WindowsTimeSync.ps1 -NtpServer "169.254.169.123,0x9" -Samples 10
#>

param(
    [string]$NtpServer = "169.254.169.123,0x9",
    [int]$Samples = 5
)

Write-Host "=== Windows Time Sync Fix ===" -ForegroundColor Cyan
Write-Host "Configuring NTP server: $NtpServer" -ForegroundColor Yellow

# 1. Configure NTP server
w32tm /config /manualpeerlist:"$NtpServer" /syncfromflags:manual /reliable:yes /update | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Warning "w32tm /config returned exit code $LASTEXITCODE. Check output above."
} else {
    Write-Host "NTP server configured successfully." -ForegroundColor Green
}

# 2. Reset Windows Time service
Write-Host "Stopping w32time service..." -ForegroundColor Yellow
Stop-Service w32time -ErrorAction SilentlyContinue

Write-Host "Unregistering w32time..." -ForegroundColor Yellow
w32tm /unregister | Out-Null

Write-Host "Registering w32time..." -ForegroundColor Yellow
w32tm /register | Out-Null

Write-Host "Starting w32time service..." -ForegroundColor Yellow
Start-Service w32time

# 3. Resync (rediscover + force)
Write-Host "Forcing time resync (rediscover + force)..." -ForegroundColor Yellow
w32tm /resync /rediscover | Out-Null
w32tm /resync /force | Out-Null

Write-Host "Resync commands completed." -ForegroundColor Green

# 4. Show configuration type & NTP server
Write-Host "`n=== Current Time Configuration ===" -ForegroundColor Cyan
w32tm /query /configuration | findstr /i "Type NtpServer"

# 5. Show current time source and status
Write-Host "`n=== Current Time Source ===" -ForegroundColor Cyan
w32tm /query /source

Write-Host "`n=== Current Time Status ===" -ForegroundColor Cyan
w32tm /query /status

# 6. Stripchart vs Amazon Time Sync
Write-Host "`n=== Drift vs $NtpServer (stripchart) ===" -ForegroundColor Cyan
# Extract just the IP/hostname portion from NtpServer (before comma if present)
$Target = $NtpServer.Split(",")[0]

w32tm /stripchart /computer:$Target /samples:$Samples /dataonly

Write-Host "`nCompleted Windows Time Sync routine." -ForegroundColor Green

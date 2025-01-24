# Get basic disk info for C:\ drive
$disk = Get-PSDrive -Name C
$volume = Get-Volume -DriveLetter C
$freeSpacePercent = ($disk.Free / $disk.Used) * 100

# Display disk info in console
Write-Host "`n=== Disk Space Report for C:\ Drive ===`n"
Write-Host "Drive Letter  : C:"
Write-Host "File System   : $($volume.FileSystemLabel)"
Write-Host "Total Size    : $([math]::Round($volume.Size/1GB,2)) GB"
Write-Host "Free Space    : $([math]::Round($volume.SizeRemaining/1GB,2)) GB"
Write-Host "Free Space %  : $([math]::Round($freeSpacePercent,2))%`n"

# Get disk space using WMIC for verification
$wmicOutput = wmic logicaldisk where "DeviceID='C:'" get DeviceID,Size,FreeSpace
Write-Host "`n=== WMIC Output for Verification ==="
Write-Host $wmicOutput

# Save results to CSV file
$diskReport = [PSCustomObject]@{
    DriveLetter  = "C:"
    FileSystem   = $volume.FileSystemLabel
    TotalSizeGB  = [math]::Round($volume.Size/1GB,2)
    FreeSpaceGB  = [math]::Round($volume.SizeRemaining/1GB,2)
    FreeSpacePct = [math]::Round($freeSpacePercent,2)
}
$diskReport | Export-Csv -Path C:\disk_space_report.csv -NoTypeInformation

Write-Host "`n✅ Report saved to C:\disk_space_report.csv`n"


#How to run
# as admin: Set-ExecutionPolicy Unrestricted -Scope Process
# execute: .\Check-DiskSpace.ps1
# saves to: C:\disk_space_report.csv

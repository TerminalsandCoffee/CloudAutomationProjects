#First I want to define the recycle bin variable
#The "Namespace(0xA) is defined as the recycle bin. 
#I will add an article soon with all namespaces that you might need. 
$recycleBinShell = New-Object -ComObject Shell.Application
$recycleBinFolder = $recycleBinShell.Namespace(0xA)

#Second I want to define the %temp% (AppData\Local\Temp) folder. 
$tempFilesENV = Get-ChildItem "env:\TEMP"
$tempFiles = $tempFilesENV.Value

#Third I want to define the Windows Temp directory
$windowsTemp = "C:\Windows\Temp\*"

#Finally I want to define the Windows Software Distribution Folder
$winDist = "C:\Windows\SoftwareDistribution"

#Now the magic begins

#Remove items from the recycle bin
$recycleBinFolder.item() | %{Remove-Item $_.path -Recurse -Confirm:$false}

#Remove the temp files in AppData\Local\Temp
Remove-Item -Recure "$tempFiles\*"

#Remove old Windows Updates
#Note: By removing this you will lose the Updates History and it might 
#redownload everything at the next update if you already haven't installed it
Get-Service -Name WUAUSERV | Stop-Service
Remove-Item -Path $winDist -Recurse -Force
Get-Service -Name WUAUSERV | Start-Service

#Disk Clean up Tool
cleanmgr /sagerun:1 /VeryLowDisk /AUTOCLEAN | Out-Null

#DISM
#First... let's repair what's broken
dism.exe /Online /Cleanup-Image /RestoreHealth

#Analyze (probably not needed)
dism.exe /Online /Cleanup-Image /AnalyzeComponentStore

#Delete junk
dism.exe /Online /Cleanup-Image /StartComponentCleanup

#Delete superseded junk
dism.exe /Online /Cleanup-Image /SPSuperseded




#credit https://prosystech.nl/powershell-clean-up-hard-drive-c/

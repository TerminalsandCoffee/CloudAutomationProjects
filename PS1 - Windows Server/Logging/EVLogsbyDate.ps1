#date format 01/01/2023

$startDate = Get-Date "insert date"

$logs = @("Application", "System", "Security")

ForEach ($log in $logs)
{
    $events = Get-WinEvent -LogName $log -ComputerName brink `
              -FilterHashtable @{LogName=$log; StartTime=$startDate}
    $events | Export-Csv -Path "$log Events.csv" -NoTypeInformation
}

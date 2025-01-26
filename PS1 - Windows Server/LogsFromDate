# Get Application logs from April 7th and 8th, 2023 and export to CSV
Get-EventLog -LogName Application -After '2023-04-07 00:00:00' -Before '2023-04-09 00:00:00' | Export-Csv -Path 'C:\Documents\ApplicationLogs.csv' -NoTypeInformation

# Get System logs from April 7th and 8th, 2023 and export to CSV
Get-EventLog -LogName System -After '2023-04-07 00:00:00' -Before '2023-04-09 00:00:00' | Export-Csv -Path 'C:\Documents\SystemLogs.csv' -NoTypeInformation

# Get Security logs from April 7th and 8th, 2023 and export to CSV
Get-EventLog -LogName Brink -After '2023-04-07 00:00:00' -Before '2023-04-09 00:00:00' | Export-Csv -Path 'C:\Documents\BrinkLogs.csv' -NoTypeInformation

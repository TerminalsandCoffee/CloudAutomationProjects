$appName = "Application Name" # Replace this with the name of the application you want to remove

$shell = New-Object -ComObject ("Shell.Application")
$folder = $shell.NameSpace("shell:::{4234d49b-0245-4df3-b780-3893943456e1}")
$items = $folder.Items()
$item = $items | Where-Object {$_.Name -eq $appName}

if ($item -ne $null) {
    $verb = $item.Verbs() | Where-Object {$_.Name.Replace("&", "") -eq "Unpin from Start"}
    if ($verb -ne $null) {
        $verb.DoIt()
        Write-Output "Successfully unpinned application '$appName' from startup"
    }
    else {
        Write-Error "Unable to find 'Unpin from Start' verb for application '$appName'"
    }
}
else {
    Write-Error "Unable to find application '$appName' in startup folder"
}

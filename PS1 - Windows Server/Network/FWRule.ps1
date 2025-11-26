# Specify the name of the firewall rule you want to modify
$RuleName = "My Firewall Rule"

# Get the Windows Firewall object
$Firewall = New-Object -ComObject HNetCfg.FwPolicy2

# Find the rule by name
$Rule = $Firewall.Rules | Where-Object {$_.Name -eq $RuleName}

# If the rule was found, modify it to allow inbound traffic
if ($Rule -ne $null) {
    $Rule.Enabled = $true
    $Rule.Action = 1  # Allow
    $Rule.Direction = 1  # Inbound
    $Firewall.Rules | Where-Object {$_.Name -eq $RuleName} | Set-NetFirewallRule -Enabled True
    Write-Host "Firewall rule '$RuleName' has been updated to allow inbound traffic."
}
else {
    Write-Host "Firewall rule '$RuleName' not found."
}

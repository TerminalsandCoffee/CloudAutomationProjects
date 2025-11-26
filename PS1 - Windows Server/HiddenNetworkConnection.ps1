# Replace these variables with your network's SSID and passphrase
$SSID = "PBPV"
$Passphrase = "YourPassphrase"

# Configure the wireless network profile
$ProfileName = "MyHiddenNetwork"
Add-WirelessProfile -Name $ProfileName -SSID $SSID -Authentication WPA2PSK -Cipher AES -KeyMaterial $Passphrase -ConnectionType Infrastructure -Hidden $true

# Connect to the hidden network
Connect-WirelessProfile -Name $ProfileName

# Check if the connection was successful
if (Get-NetConnectionProfile | Where-Object { $_.Name -eq $ProfileName -and $_.ConnectionStatus -eq "Connected" }) {
    Write-Host "Connected to the hidden network: $SSID"
} else {
    Write-Host "Failed to connect to the hidden network: $SSID"
}

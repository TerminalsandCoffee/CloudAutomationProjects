#use the New-NetIPAddress cmdlet to assign a static IP address to a network adapter.


New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.168.2.100 -PrefixLength 24 -DefaultGateway 192.168.2.254



#InterfaceAlias is the name of the network adapter you want to configure.
#IPAddress is the static IP address you want to assign.
#PrefixLength is the subnet mask for the IP address.
#DefaultGateway is the IP address of the default gateway for the network.

$adapter = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}
New-NetIPAddress -InterfaceIndex $adapter.ifIndex -IPAddress 192.168.2.100 -PrefixLength 24 -DefaultGateway 192.168.2.254


#add dns 

$dnsServer = @("8.8.8.8","8.8.4.4")
Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses $dnsServer

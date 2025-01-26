$driverName = "DriverName.inf"  # Replace with the name of the driver you want to remove

# Get the driver's published name
$driverPublishedName = (pnputil /enum-drivers | Select-String -Pattern $driverName).Line.Trim() -replace ".*\\", ""

# Remove the driver
pnputil /delete-driver $driverPublishedName


#add it back in
$installerPath = "C:\Path\to\DriverInstaller.exe"  # Replace with the path to the driver installer executable

# Run the installer
Start-Process -FilePath $installerPath -ArgumentList "/quiet" -Wait

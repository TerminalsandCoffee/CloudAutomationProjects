#When installing remotely, use a Universal Naming Convention (UNC) network path to specify the path to the .msi package, 
#because the WMI subsystem does not understand PowerShell paths. 
#For example, to install the NewPackage.msi package located in the network share \\AppServ\dsp on the remote computer PC01, type the following command at the PowerShell prompt:

Invoke-CimMethod -ClassName Win32_Product -MethodName Install -Arguments @{PackageLocation='\\AppSrv\dsp\NewPackage.msi'}


#Removing a Windows Installer package using PowerShell works in approximately the same way as installing a package.
Get-CimInstance -Class Win32_Product -Filter "Name='ILMerge'" | Invoke-CimMethod -MethodName Uninstall

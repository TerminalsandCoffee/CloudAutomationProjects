# Windows Server Automation Scripts

A collection of PowerShell scripts for automating Windows Server management, deployment, and maintenance tasks. These scripts are designed to streamline operations in enterprise environments, with particular focus on supporting .NET backend infrastructure and applications.

## Overview

This repository contains production-ready PowerShell scripts that automate common Windows Server administration tasks. These scripts are especially valuable for:
- **.NET Application Deployment**: Automating IIS configuration, environment setup, and application lifecycle management
- **Infrastructure as Code**: Supporting CI/CD pipelines for .NET applications
- **Server Maintenance**: Disk management, log collection, and system health monitoring
- **Security & Compliance**: Password management, firewall configuration, and audit logging

## Organization

This repository is organized by service/functionality to improve maintainability and discoverability. Each service folder contains scripts specific to that Windows Server component or task category.

## Service Directories

### [IIS](./IIS/)
Scripts for managing Internet Information Services (IIS) and web server configuration.

**Scripts:**
- `IISInstall.ps1` - Installs and configures IIS with management tools for hosting .NET Framework and .NET Core applications

**Use Cases:**
- Setting up new web servers for .NET deployments
- Preparing servers for ASP.NET applications
- Automated infrastructure provisioning

**Example:**
```powershell
cd IIS
.\IISInstall.ps1
```

---

### [Azure-AD](./Azure-AD/)
Scripts for managing Azure Active Directory and identity management.

**Scripts:**
- `AZ_Password_Reset.ps1` - Bulk password reset utility for Azure AD users with automated password rotation support

**Security Note:** This script contains placeholder credentials. Always use secure credential management (Azure Key Vault, Managed Identities, or secure parameter passing) in production environments.

**Use Cases:**
- Onboarding new users
- Automated password rotation
- Integration with .NET applications using Azure AD authentication

**Example:**
```powershell
# Requires AzureAD module: Install-Module -Name AzureAD
cd Azure-AD
.\AZ_Password_Reset.ps1
```

---

### [Network](./Network/)
Scripts for network configuration, firewall management, and connectivity.

**Scripts:**
- `StaticIP.ps1` - Configures static IP addresses and DNS settings for network adapters
- `FWRule.ps1` - Manages Windows Firewall rules programmatically
- `HiddenNetworkConnection.ps1` - Configures connections to hidden wireless networks

**Use Cases:**
- Configuring application servers with fixed IPs
- Setting up load balancer targets
- Opening ports for web applications (80, 443, custom ports)
- Configuring firewall rules for .NET services
- Security hardening automation

**Example:**
```powershell
cd Network
.\StaticIP.ps1
.\FWRule.ps1
```

---

### [Disk-Storage](./Disk-Storage/)
Scripts for disk space management, cleanup, and monitoring.

**Scripts:**
- `Windows-Server-DiskReport.ps1` - Generates comprehensive disk space reports with CSV export
- `DiskCleanup.ps1` - Comprehensive cleanup utility (temp files, recycle bin, Windows Update cleanup, DISM)
- `ClearTempDirectory.ps1` - Quick cleanup script for temporary directories

**Use Cases:**
- Monitoring disk usage for application servers
- Capacity planning for .NET application deployments
- Freeing disk space on application servers
- Pre-deployment server preparation
- Automated health checks

**Example:**
```powershell
# Run as Administrator
cd Disk-Storage
.\Windows-Server-DiskReport.ps1
# Output: C:\disk_space_report.csv

.\DiskCleanup.ps1
```

---

### [Windows-Update](./Windows-Update/)
Scripts for managing Windows Update service and troubleshooting update issues.

**Scripts:**
- `WSUSTroubleshooting.ps1` - Comprehensive Windows Update Service troubleshooting script that resets update components and checks for pending reboots

**Use Cases:**
- Resolving Windows Update issues on production servers
- Pre-deployment server preparation
- Automated troubleshooting workflows
- System maintenance automation

**Example:**
```powershell
# Run as Administrator
cd Windows-Update
.\WSUSTroubleshooting.ps1
```

---

### [Logging](./Logging/)
Scripts for collecting, exporting, and archiving Windows Event Logs and application logs.

**Scripts:**
- `EVLogsbyDate.ps1` - Exports Windows Event Logs (Application, System, Security) for a specific date range to CSV
- `LogsFromDate.ps1` - Alternative event log export script with date range filtering
- `logpull.ps1` - Batch script for pulling and archiving event logs, application data files, and creating compressed backups

**Use Cases:**
- Collecting logs for .NET application troubleshooting
- Security audits and compliance
- Incident investigation
- Log archival and backup

**Example:**
```powershell
cd Logging
# Modify the date in the script before running
.\EVLogsbyDate.ps1
.\logpull.ps1
```

---

### [System-Configuration](./System-Configuration/)
Scripts for system-level configuration, environment variables, time synchronization, and system repair.

**Scripts:**
- `Insert_EnvPath.ps1` - Adds directories to the system PATH environment variable
- `Fix-WindowsTimeSync.ps1` - Fixes Windows time synchronization issues
- `TimeFix.bat` - Batch script for time synchronization (legacy)
- `FixWindowsIssues.bat` - Batch script that runs SFC and DISM to repair Windows system files

**Use Cases:**
- Adding .NET SDK to PATH
- Configuring development environments
- Application deployment automation
- System time synchronization
- Windows system file repair

**Example:**
```powershell
cd System-Configuration
# Modify the path in the script before running
.\Insert_EnvPath.ps1
.\Fix-WindowsTimeSync.ps1
```

---

### [Software-Management](./Software-Management/)
Scripts for installing, uninstalling, and managing software and drivers.

**Scripts:**
- `InstallSoftware.ps1` - Installs and uninstalls Windows Installer (.msi) packages using WMI/CIM with remote installation support via UNC paths
- `RemoveDriver.ps1` - Removes and reinstalls Windows drivers using pnputil
- `RemovePinned.ps1` - Removes applications from the Windows Start menu

**Use Cases:**
- Installing .NET Framework or .NET Runtime
- Deploying application dependencies
- Automated software provisioning
- Driver management and troubleshooting

**Example:**
```powershell
cd Software-Management
# Install from network share
.\InstallSoftware.ps1

# Uninstall example (modify script):
# Get-CimInstance -Class Win32_Product -Filter "Name='ApplicationName'" | Invoke-CimMethod -MethodName Uninstall
```

---

### [Utilities](./Utilities/)
General-purpose utility scripts for file management and miscellaneous tasks.

**Scripts:**
- `RenameFile.ps1` - File renaming utilities (contains multiple language examples - batch and Python)

**Use Cases:**
- File management automation
- Batch file operations

---

## Getting Started

### Prerequisites

- Windows Server 2016+ or Windows 10/11
- PowerShell 5.1+ (Windows PowerShell) or PowerShell 7+ (PowerShell Core)
- Appropriate administrative privileges for system-level operations

### Execution Policy

Some scripts may require adjusting PowerShell execution policy:

```powershell
# For current session only (recommended)
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Or for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Module Requirements

Some scripts require additional PowerShell modules:

```powershell
# Azure AD (for Azure-AD/AZ_Password_Reset.ps1)
Install-Module -Name AzureAD -Force

# IIS Management (for IIS/IISInstall.ps1)
# Included in Windows Server by default
```

---

## Security Best Practices

1. **Never hardcode credentials** - Use secure parameter passing, Azure Key Vault, or Managed Identities
2. **Run with least privilege** - Only use administrator privileges when necessary
3. **Review scripts before execution** - Understand what each script does before running
4. **Use signed scripts** - Consider code signing for production environments
5. **Audit and log** - Enable PowerShell logging for security auditing

---

## Integration with .NET Applications

These scripts are designed to support .NET application deployments and operations:

### CI/CD Pipeline Integration

```yaml
# Example Azure DevOps Pipeline Step
- task: PowerShell@2
  displayName: 'Configure IIS for .NET App'
  inputs:
    filePath: '$(System.DefaultWorkingDirectory)/scripts/IIS/IISInstall.ps1'
    pwsh: true
```

### Application Deployment Workflow

1. **Pre-deployment**: Run `Disk-Storage/DiskCleanup.ps1` and `Disk-Storage/Windows-Server-DiskReport.ps1` to ensure adequate resources
2. **Configuration**: Use `IIS/IISInstall.ps1` and `Network/FWRule.ps1` to set up web server
3. **Post-deployment**: Use `Logging/EVLogsbyDate.ps1` to verify application startup logs

### Monitoring & Maintenance

- Schedule `Disk-Storage/Windows-Server-DiskReport.ps1` for capacity monitoring
- Use `Logging/EVLogsbyDate.ps1` for application log collection
- Run `Disk-Storage/DiskCleanup.ps1` as part of regular maintenance windows

---

## Script Categories

### Web Server Management
- `IIS/IISInstall.ps1` - IIS installation and configuration

### Identity & Security
- `Azure-AD/AZ_Password_Reset.ps1` - Azure AD user management
- `Network/FWRule.ps1` - Firewall rule management

### System Health & Maintenance
- `Disk-Storage/Windows-Server-DiskReport.ps1` - Disk space monitoring
- `Disk-Storage/DiskCleanup.ps1` - Comprehensive cleanup
- `Windows-Update/WSUSTroubleshooting.ps1` - Update service troubleshooting
- `System-Configuration/FixWindowsIssues.bat` - System file repair

### Operations & Monitoring
- `Logging/EVLogsbyDate.ps1` - Event log collection
- `Logging/logpull.ps1` - Log archival

### Infrastructure Automation
- `Network/StaticIP.ps1` - Network configuration
- `Software-Management/InstallSoftware.ps1` - Software deployment
- `System-Configuration/Insert_EnvPath.ps1` - Environment configuration

---

## Naming Conventions

Scripts follow PowerShell best practices where applicable:
- **Verb-Noun format**: `Get-*`, `Set-*`, `Install-*`, `Remove-*`
- **Descriptive names**: Clear indication of script purpose
- **Consistent extensions**: All scripts use `.ps1` extension (batch files use `.bat`)

---

## Contributing

When adding new scripts:

1. **Place in appropriate service folder** - If a script spans multiple services, place in `Utilities/`
2. **Follow PowerShell best practices** - Use proper coding standards and conventions
3. **Include comment-based help** - Add `<# ... #>` help blocks
4. **Add error handling** - Use `try-catch` blocks and meaningful error messages
5. **Use parameters** - Avoid hardcoded values, use parameters instead
6. **Document use cases** - Include examples and use case descriptions

---

## Additional Resources

- [PowerShell Documentation](https://docs.microsoft.com/powershell/)
- [.NET on Windows Server](https://dotnet.microsoft.com/download)
- [IIS Configuration for .NET](https://docs.microsoft.com/iis)
- [Azure PowerShell](https://docs.microsoft.com/powershell/azure/)

---

## Disclaimer

These scripts are provided as-is for educational and operational purposes. Always test scripts in a non-production environment before deployment. The authors are not responsible for any damage or data loss resulting from the use of these scripts.

---

**Built for Windows Server automation with .NET applications in mind**

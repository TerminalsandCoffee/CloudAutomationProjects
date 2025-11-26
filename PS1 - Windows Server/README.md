# Windows Server Automation Scripts

A collection of PowerShell scripts for automating Windows Server management, deployment, and maintenance tasks. These scripts are designed to streamline operations in enterprise environments, with particular focus on supporting .NET backend infrastructure and applications.

## 🎯 Overview

This repository contains production-ready PowerShell scripts that automate common Windows Server administration tasks. These scripts are especially valuable for:
- **.NET Application Deployment**: Automating IIS configuration, environment setup, and application lifecycle management
- **Infrastructure as Code**: Supporting CI/CD pipelines for .NET applications
- **Server Maintenance**: Disk management, log collection, and system health monitoring
- **Security & Compliance**: Password management, firewall configuration, and audit logging

## 📋 Scripts

### Application & Web Server Management

#### `IISInstall.ps1`
Installs and configures Internet Information Services (IIS) with management tools. Essential for hosting .NET Framework and .NET Core applications.

**Use Cases:**
- Setting up new web servers for .NET deployments
- Preparing servers for ASP.NET applications
- Automated infrastructure provisioning

**Example:**
```powershell
.\IISInstall.ps1
```

---

### Azure & Identity Management

#### `AZ_Password_Reset.ps1`
Bulk password reset utility for Azure AD users. Supports automated password rotation and user onboarding workflows.

**⚠️ Security Note:** This script contains placeholder credentials. Always use secure credential management (Azure Key Vault, Managed Identities, or secure parameter passing) in production environments.

**Use Cases:**
- Onboarding new users
- Automated password rotation
- Integration with .NET applications using Azure AD authentication

**Example:**
```powershell
# Requires AzureAD module: Install-Module -Name AzureAD
.\AZ_Password_Reset.ps1
```

---

### Network Configuration

#### `StaticIP.ps1`
Configures static IP addresses and DNS settings for network adapters. Critical for servers hosting .NET applications that require consistent network endpoints.

**Use Cases:**
- Configuring application servers with fixed IPs
- Setting up load balancer targets
- Network infrastructure automation

**Example:**
```powershell
.\StaticIP.ps1
```

#### `FWRule.ps1`
Manages Windows Firewall rules programmatically. Useful for opening ports required by .NET applications (HTTP/HTTPS, custom ports).

**Use Cases:**
- Opening ports for web applications (80, 443, custom ports)
- Configuring firewall rules for .NET services
- Security hardening automation

**Example:**
```powershell
.\FWRule.ps1
```

#### `HiddenNetworkConnection.ps1`
Configures connections to hidden wireless networks. Useful for development and testing environments.

---

### System Maintenance & Monitoring

#### `Windows-Server-DiskReport.ps1`
Generates comprehensive disk space reports for Windows Server volumes. Exports data to CSV for analysis and monitoring.

**Use Cases:**
- Monitoring disk usage for application servers
- Capacity planning for .NET application deployments
- Automated health checks

**Example:**
```powershell
.\Windows-Server-DiskReport.ps1
# Output: C:\disk_space_report.csv
```

#### `DiskCleanup.ps1`
Comprehensive disk cleanup utility that removes temporary files, clears recycle bins, and performs Windows Update cleanup. Uses DISM for component store cleanup.

**Use Cases:**
- Freeing disk space on application servers
- Pre-deployment server preparation
- Maintenance automation

**Example:**
```powershell
# Run as Administrator
.\DiskCleanup.ps1
```

#### `ClearTempDirectory.ps1`
Quick cleanup script for temporary directories. Useful for freeing space before deployments.

---

### Logging & Troubleshooting

#### `WSUSTroubleshooting.ps1`
Comprehensive Windows Update Service troubleshooting script. Resets update components and checks for pending reboots.

**Use Cases:**
- Resolving Windows Update issues on production servers
- Pre-deployment server preparation
- Automated troubleshooting workflows

**Example:**
```powershell
# Run as Administrator
.\WSUSTroubleshooting.ps1
```

#### `EVLogsbyDate.ps1`
Exports Windows Event Logs (Application, System, Security) for a specific date range. Exports to CSV format.

**Use Cases:**
- Collecting logs for .NET application troubleshooting
- Security audits and compliance
- Incident investigation

**Example:**
```powershell
# Modify the date in the script before running
.\EVLogsbyDate.ps1
```

#### `LogsFromDate.ps1`
Alternative event log export script with date range filtering.

#### `logpull.ps1`
Batch script for pulling and archiving event logs, application data files, and creating compressed backups.

---

### System Configuration

#### `Insert_EnvPath.ps1`
Adds directories to the system PATH environment variable. Useful for adding .NET SDK paths, custom tools, or application binaries.

**Use Cases:**
- Adding .NET SDK to PATH
- Configuring development environments
- Application deployment automation

**Example:**
```powershell
# Modify the path in the script before running
.\Insert_EnvPath.ps1
```

#### `StaticIP.ps1`
Configures static IP addresses and DNS servers for network adapters.

#### `TimeFix.bat`
Batch script for time synchronization (legacy script).

---

### Software Management

#### `InstallSoftware.ps1`
Installs and uninstalls Windows Installer (.msi) packages using WMI/CIM. Supports remote installation via UNC paths.

**Use Cases:**
- Installing .NET Framework or .NET Runtime
- Deploying application dependencies
- Automated software provisioning

**Example:**
```powershell
# Install from network share
.\InstallSoftware.ps1

# Uninstall example (modify script):
# Get-CimInstance -Class Win32_Product -Filter "Name='ApplicationName'" | Invoke-CimMethod -MethodName Uninstall
```

#### `RemoveDriver.ps1`
Removes and reinstalls Windows drivers using pnputil.

#### `RemovePinned.ps1`
Removes applications from the Windows Start menu.

---

### File Management

#### `RenameFile.ps1`
Batch and Python scripts for renaming files (legacy - contains multiple language examples).

#### `FixWindowsIssues.bat`
Batch script that runs SFC and DISM to repair Windows system files.

---

## 🚀 Getting Started

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
# Azure AD (for AZ_Password_Reset.ps1)
Install-Module -Name AzureAD -Force

# IIS Management (for IISInstall.ps1)
# Included in Windows Server by default
```

---

## 🔒 Security Best Practices

1. **Never hardcode credentials** - Use secure parameter passing, Azure Key Vault, or Managed Identities
2. **Run with least privilege** - Only use administrator privileges when necessary
3. **Review scripts before execution** - Understand what each script does before running
4. **Use signed scripts** - Consider code signing for production environments
5. **Audit and log** - Enable PowerShell logging for security auditing

---

## 🏗️ Integration with .NET Applications

These scripts are designed to support .NET application deployments and operations:

### CI/CD Pipeline Integration

```yaml
# Example Azure DevOps Pipeline Step
- task: PowerShell@2
  displayName: 'Configure IIS for .NET App'
  inputs:
    filePath: '$(System.DefaultWorkingDirectory)/scripts/IISInstall.ps1'
    pwsh: true
```

### Application Deployment Workflow

1. **Pre-deployment**: Run `DiskCleanup.ps1` and `Windows-Server-DiskReport.ps1` to ensure adequate resources
2. **Configuration**: Use `IISInstall.ps1` and `FWRule.ps1` to set up web server
3. **Post-deployment**: Use `EVLogsbyDate.ps1` to verify application startup logs

### Monitoring & Maintenance

- Schedule `Windows-Server-DiskReport.ps1` for capacity monitoring
- Use `EVLogsbyDate.ps1` for application log collection
- Run `DiskCleanup.ps1` as part of regular maintenance windows

---

## 📝 Naming Conventions

Scripts follow PowerShell best practices where applicable:
- **Verb-Noun format**: `Get-*`, `Set-*`, `Install-*`, `Remove-*`
- **Descriptive names**: Clear indication of script purpose
- **Consistent extensions**: All scripts use `.ps1` extension

---

## 🤝 Contributing

When adding new scripts:
1. Follow PowerShell best practices and coding standards
2. Include comment-based help (`<# ... #>`)
3. Add error handling with `try-catch` blocks
4. Use parameters instead of hardcoded values
5. Document use cases and examples

---

## 📚 Additional Resources

- [PowerShell Documentation](https://docs.microsoft.com/powershell/)
- [.NET on Windows Server](https://dotnet.microsoft.com/download)
- [IIS Configuration for .NET](https://docs.microsoft.com/iis)
- [Azure PowerShell](https://docs.microsoft.com/powershell/azure/)

---

## ⚠️ Disclaimer

These scripts are provided as-is for educational and operational purposes. Always test scripts in a non-production environment before deployment. The authors are not responsible for any damage or data loss resulting from the use of these scripts.

---

## 📧 Contact

For questions or contributions, please refer to the main repository README.

---

**Built for Windows Server automation with .NET applications in mind** 🚀

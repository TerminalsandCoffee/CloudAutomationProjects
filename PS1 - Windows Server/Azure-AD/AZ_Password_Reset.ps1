<#
.SYNOPSIS
  Reset Azure AD user passwords from a caller-supplied list.

.NOTES
  Do not hardcode passwords or UPNs. Requires the AzureAD module and an
  interactive admin login. Generate unique passwords per user in production
  and store them in a secret store, not in this script.
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
  [Parameter(Mandatory)]
  [string[]]$Users,

  [Parameter(Mandatory)]
  [SecureString]$NewPassword,

  [bool]$ForceChangePasswordNextSignIn = $true
)

Connect-AzureAD

foreach ($user in $Users) {
  if ($PSCmdlet.ShouldProcess($user, 'Reset Azure AD password')) {
    Set-AzureADUserPassword -ObjectId $user -Password $NewPassword -ForceChangePasswordNextSignIn $ForceChangePasswordNextSignIn
    Write-Host "Password reset issued for $user"
  }
}

# Connect to Azure AD
Connect-AzureAD

# List of users
$users = @(
    "user1@terminalsandcoffee.com",
    "user2@terminalsandcoffee.com",
    "user3@terminalsandcoffee.com",
    "user4@terminalsandcoffee.com",
    "user5@terminalsandcoffee.com"

)

# Loop through each user and reset the password
foreach ($user in $users) {
    $newPassword = "PassW0rd!"
    Set-AzureADUserPassword -ObjectId $user -Password $newPassword -ForceChangePasswordNextSignIn $true
    Write-Host "Password reset for $user"
}

# Specify the new path you want to add
$newPath = "C:\Program Files\Terraform"

# Get the current PATH environment variable
$currentPath = [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::Machine)

# Check if the path already exists in the PATH variable
if ($currentPath -notlike "*$newPath*") {
    # Add the new path to the existing PATH variable
    $newPathToAdd = $currentPath + ";" + $newPath
    [System.Environment]::SetEnvironmentVariable("PATH", $newPathToAdd, [System.EnvironmentVariableTarget]::Machine)

    Write-Host "Path added successfully. Please restart any relevant applications to apply the changes."
} else {
    Write-Host "The path is already present in the PATH variable."
}

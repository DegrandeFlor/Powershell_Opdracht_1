# # # Description: This script is used to customize the first run of the RPI.

# # Variables
# Variables for the drive where the firstrun.sh script is located
$driveLabel = "bootfs"
$drive = Get-Volume -FileSystemLabel $driveLabel

# Variables for the nmcli firstrun.sh script
$fileName = "Static_IP.nmconnection"

# Variables for the nmcli connection
$connectionId = "Static_IP"
$connectionType = "ethernet"
$connectionInterface = "eth0"

# Variables for the nmcli ipv4 connection settings
$ipv4Method = "manual"
$ipv4Address = "192.168.88.2/24,192.168.88.1"
$ipv4DNS = "172.20.4.140;172.20.4.141"

# Variables for the nmcli ipv6 connection settings
$ipv6AddrGenMode = "default"
$ipv6Method = "auto"

# Variables for the nmcli proxy settings
$proxy = ""

# # Create the nmcli text
$nmcli = @"
cat >/etc/NetworkManager/system-connections/$fileName <<'$connectionId'
[connection]
id=$connectionId
type=$connectionType
interface-name=$connectionInterface

[ethernet]

[ipv4] 
address1=$ipv4Address
dns=$ipv4DNS
method=$ipv4Method
[ipv6]
addr-gen-mode=$ipv6AddrGenMode
method=$ipv6Method

[proxy]
$proxy

chmod 0600 /etc/NetworkManager/system-connections/*
chown root:root /etc/NetworkManager/system-connections/*

"@

# # Write the nmcli text to the correct position (above the line containing rm -f /boot/firstrun.sh) in the firstrun.sh script to the bootfs drive
# Check if the drive and file exist
if (-not $drive -and -not (Test-Path -Path "$($drive.DriveLetter):\firstrun.sh")) {
    Write-Host "The drive with the label $driveLabel does not exist or the firstrun.sh script does not exist on the drive."
    return
}

# Check if dos2unix is installed
if (-not (Get-Command dos2unix -ErrorAction SilentlyContinue)) {
    Write-Host "dos2unix is not installed. Please install dos2unix and run the script again."
    return
}

# Convert the firstrun.sh script to Unix format
& dos2unix "$($drive.DriveLetter):\firstrun.sh"

# Get the content of the firstrun.sh script
$script = Get-Content -Path "$($drive.DriveLetter):\firstrun.sh"

# Check if the text is already in the script
if ($script -match $nmcli) {
    Write-Host "The nmcli text is already in the firstrun.sh script."
    return
}

# Replace the line containing rm -f /boot/firstrun.sh with the nmcli text
$script = $script -replace 'rm -f /boot/firstrun.sh', "$nmcli`n`$&"

# Save the modified script back to the file
$script | Set-Content -Path "$($drive.DriveLetter):\firstrun.sh"

# Convert the modified script to Unix format again
& dos2unix "$($drive.DriveLetter):\firstrun.sh"
AI GENERATED

# Libvirt Virtual Machine Extension for Ulauncher

This extension allows you to quickly search and manage your libvirt virtual machines from Ulauncher.

## Features

- Lists all virtual machines (running and stopped)
- Shows VM state with visual indicators:
  - 🟢 Running
  - 🔴 Shut off/Stopped  
  - 🟡 Paused/Suspended
  - ⚪ Other states
- Shows autostart status with 🔄 indicator
- Opens selected VM in virt-manager when selected
- Supports filtering VMs by name

## Requirements

- libvirt installed and configured
- virt-manager installed
- `virsh` command available in PATH
- Appropriate permissions to access libvirt (user should be in libvirt group)

## Installation

1. Copy this directory to your Ulauncher extensions folder:
   ```
   ~/.local/share/ulauncher/extensions/libvirt/
   ```

2. Restart Ulauncher or reload extensions

3. The extension will be available with the keyword `vm` (configurable in preferences)

## Usage

1. Open Ulauncher (usually Alt+Space)
2. Type `vm` followed by optional VM name to filter
3. Select a VM from the list to open it in virt-manager

## Configuration

You can change the keyword in Ulauncher preferences:
- Open Ulauncher preferences
- Go to Extensions tab
- Find "Libvirt VMs" extension
- Change the keyword as desired

## Troubleshooting

If no VMs are shown:
1. Ensure libvirt is running: `sudo systemctl status libvirtd`
2. Check if you have permission: `virsh list --all`
3. Add your user to libvirt group: `sudo usermod -a -G libvirt $USER`
4. Log out and back in for group changes to take effect

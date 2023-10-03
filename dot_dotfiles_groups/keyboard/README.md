
Linux install
Florian Didron edited this page Sep 5, 2023 · 22 revisions
Pages 4

Home
Linux install

    1. Install the required dependencies.
    1.1 Arch and its derivatives (Manjaro, Antergos, ...)
    1.2 Debian and its derivatives (Ubuntu, Kali, Mint, ...)
    1.3 Red Hat / Fedora and its derivatives (Centos, Scientific Linux, ...)
    2. Create a udev rule file
    3. Download the latest binary and run it

Live training on Linux

    Wally on ChromeOS

Clone this wiki locally

In order to use Keymapp or Wally and flash your board on Linux, you need to:

    Install the required dependencies.
    Add a udev rule file to your distro.
    Download the Keymapp or Wally binary.

1. Install the required dependencies.

Note some distributions might already have these dependencies installed (ex: Ubuntu)

Keymapp/Wally's GUI requires three dependencies to run properly: gtk3, webkit2gtk and libusb. If you plan to use the CLI version only, then only libusb is required.
1.1 Arch and its derivatives (Manjaro, Antergos, ...)

sudo pacman -S libusb webkit2gtk gtk3

1.2 Debian and its derivatives (Ubuntu, Kali, Mint, ...)

sudo apt install libusb-1.0-0-dev

1.3 Red Hat / Fedora and its derivatives (Centos, Scientific Linux, ...)

sudo yum install gtk3 webkit2gtk3 libusb

2. Create a udev rule file

While low-level device communication is handled by the kernel, device-related events are managed in userspace by udevd. Custom .rules files can be defined in order to get access to those events without elevated privileges.

In /etc/udev/rules.d/ create a file named 50-zsa.rules:

sudo touch /etc/udev/rules.d/50-zsa.rules

And paste the following configuration inside:

# Rules for Oryx web flashing and live training
KERNEL=="hidraw*", ATTRS{idVendor}=="16c0", MODE="0664", GROUP="plugdev"
KERNEL=="hidraw*", ATTRS{idVendor}=="3297", MODE="0664", GROUP="plugdev"

# Legacy rules for live training over webusb (Not needed for firmware v21+)
  # Rule for all ZSA keyboards
  SUBSYSTEM=="usb", ATTR{idVendor}=="3297", GROUP="plugdev"
  # Rule for the Moonlander
  SUBSYSTEM=="usb", ATTR{idVendor}=="3297", ATTR{idProduct}=="1969", GROUP="plugdev"
  # Rule for the Ergodox EZ
  SUBSYSTEM=="usb", ATTR{idVendor}=="feed", ATTR{idProduct}=="1307", GROUP="plugdev"
  # Rule for the Planck EZ
  SUBSYSTEM=="usb", ATTR{idVendor}=="feed", ATTR{idProduct}=="6060", GROUP="plugdev"

# Wally Flashing rules for the Ergodox EZ
ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="04[789B]?", ENV{ID_MM_DEVICE_IGNORE}="1"
ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="04[789A]?", ENV{MTP_NO_PROBE}="1"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="04[789ABCD]?", MODE:="0666"
KERNEL=="ttyACM*", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="04[789B]?", MODE:="0666"

# Keymapp / Wally Flashing rules for the Moonlander and Planck EZ
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="df11", MODE:="0666", SYMLINK+="stm32_dfu"
# Keymapp Flashing rules for the Voyager
SUBSYSTEMS=="usb", ATTRS{idVendor}=="3297", MODE:="0666", SYMLINK+="ignition_dfu"

Note: The snippet above defines rules for all ZSA's keyboards. Feel free to only copy the block relevant to you.

Make sure your user is part of the plugdev group (it might not be the default on some distros):

$> sudo groupadd plugdev
$> sudo usermod -aG plugdev $USER

Make sure to logout once after that. If that doesn't do the trick, fully reboot your machine and try again.
3. Download the latest binary and run it

Download the latest Keymapp linux version available from here, make it executable (chmod +x wally) and execute it.

or

Download the latest Wally linux version available from here, make it executable (chmod +x wally) and execute it.

Ran into an issue while following this guide? Feel free to contact us and we'll help!
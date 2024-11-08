# Manual

Uninstall `xdg-desktop-portal-gnome` (if you can't instead disable it with: `systemctl --user disable xdg-desktop-portal-gnome.service`)

https://github.com/regolith-linux/regolith-desktop/issues/920
https://github.com/flameshot-org/flameshot/blob/master/docs/Sway%20and%20wlroots%20support.md

# Set 

`sudo nano /usr/bin/regolith-session-wayland`

add `exec dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP=sway` before
the sway startup code
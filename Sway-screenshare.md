# Manual



Uninstall `xdg-desktop-portal-gnome` (if you can't instead disable it with: `systemctl --user disable xdg-desktop-portal-gnome.service`)

`sudo apt remove pop-desktop -y --allow-remove-essential`

https://github.com/regolith-linux/regolith-desktop/issues/920
https://github.com/flameshot-org/flameshot/blob/master/docs/Sway%20and%20wlroots%20support.md

# Set 

`sudo nano /usr/bin/regolith-session-wayland`

Put `export XDG_CURRENT_DESKTOP="sway"` before start of sway 

~~add `exec dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP=sway` before
the sway startup code~~

# Now firefox works... 

# What about zoom?

Yes but you need 6.0.12, newer ones break pipewire

https://community.zoom.com/t5/Zoom-Meetings/share-screen-linux-wayland-broken/m-p/191795
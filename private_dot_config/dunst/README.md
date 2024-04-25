# How to test?

systemctl --user restart dunst && notify-send "hello there"

# Install latest version 

Get deb from https://launchpad.net/ubuntu/+source/dunst

Current version in ubuntu doesn't support `origin` to change where the notifications happen.

```bash
wget https://launchpad.net/ubuntu/+archive/primary/+files/dunst_1.9.2-1_arm64.deb
sudo apt install ./dunst_1.9.2-1_amd64.deb 
```
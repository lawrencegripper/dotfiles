snap install alacritty --classic 

sudo add-apt-repository universe
sudo apt update
sudo apt install fonts-firacode

# Install regolith
sudo add-apt-repository ppa:regolith-linux/release
sudo apt install regolith-desktop-standard

# Install GH cli
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/etc/apt/trusted.gpg.d/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/trusted.gpg.d/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Kitty
mkdir -p ~/.local/bin/
ln -s ~/.local/kitty.app/bin/kitty ~/.local/bin/
# Place the kitty.desktop file somewhere it can be found by the OS
cp ~/.local/kitty.app/share/applications/kitty.desktop ~/.local/share/applications/
# Update the path to the kitty icon in the kitty.desktop file
sed -i "s|Icon=kitty|Icon=/home/$USER/.local/kitty.app/share/icons/hicolor/256x256/apps/kitty.png|g" ~/.local/share/applications/kitty.desktop
curl -L https://sw.kovidgoyal.net/kitty/installer.sh | sh /dev/stdin

# Install code
sudo snap install code --classic 

# Disable Super+P display switch hotkey
gsettings set org.gnome.mutter.keybindings switch-monitor "[]"

# Install emote emoji picker
sudo snap install emote

# Install signal
sudo snap install signal

# Install apple music 
snap install --edge cider

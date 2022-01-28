# Install starship config
ln -sf $ZSH/terminal/starship.toml.symlink ~/.config/starship.toml

# Configure alacritty if installed
if test $(which alacritty)
then
    # Link alacritty settings
    mkdir -p ~/.config/alacritty
    ln -sf $ZSH/terminal/alacritty.yml.symlink ~/.config/alacritty/alacritty.yml

    infocmp alacritty 
    if [ "$?" -eq "0" ]
    then
        echo "term info for alacritty already installed"
    else
        echo "installing alacritty term info"
        # Install alcritty terminfo (if this returns an error you need to do it `infocmp alacritty`)
        git clone https://github.com/alacritty/alacritty.git
        cd alacritty

        # setup terminfo
        sudo tic -xe alacritty,alacritty-direct extra/alacritty.info
        # cleanup
        cd .. && rm -rf alacritty
    fi
fi
